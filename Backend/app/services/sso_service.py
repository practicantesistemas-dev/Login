import html
import re
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlparse

_sso_store: dict[str, dict] = {}
_form_cache: dict[str, dict] = {}
TTL_SECONDS = 8 * 60 * 60
FORM_CACHE_TTL = 60 * 60


def store_credentials(username: str, password: str, app_username: str | None = None) -> None:
    login_id = (app_username or username).strip()
    _sso_store[username.upper()] = {
        "password": password,
        "app_username": login_id,
        "expires_at": time.time() + TTL_SECONDS,
    }


def clear_credentials(username: str) -> None:
    _sso_store.pop(username.upper(), None)


def get_credentials(username: str) -> str | None:
    entry = _sso_store.get(username.upper())
    if not entry:
        return None
    if entry["expires_at"] < time.time():
        _sso_store.pop(username.upper(), None)
        return None
    return entry["password"]


def get_app_username(username: str) -> str | None:
    entry = _sso_store.get(username.upper())
    if not entry:
        return None
    if entry["expires_at"] < time.time():
        _sso_store.pop(username.upper(), None)
        return None
    return entry.get("app_username") or username


def resolve_sso_credentials(username: str) -> tuple[str, str] | None:
    """
    Obtiene usuario y contraseña para SSO.
    Usa caché en memoria; si expiró o el servidor reinició, las recupera desde Oracle.
    """
    password = get_credentials(username)
    app_username = get_app_username(username)
    if password and app_username:
        return app_username, password

    from app.services.db_service import get_sso_credentials as get_sso_credentials_from_db

    db_creds = get_sso_credentials_from_db(username)
    if not db_creds:
        return None

    store_credentials(
        username,
        db_creds["password"],
        db_creds["app_username"],
    )
    return db_creds["app_username"], db_creds["password"]


def _fetch_html(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Portal-Liga-SSO/1.0"},
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        return response.read().decode("utf-8", "ignore")


def _page_base_for_join(page_url: str) -> str:
    """Base URL para resolver action relativos (modulos/validacion.php)."""
    parsed = urlparse(page_url.strip())
    path = parsed.path or "/"

    if re.search(r"\.[a-z0-9]+$", path, re.I):
        path = path.rsplit("/", 1)[0]

    if not path.endswith("/"):
        path += "/"

    return f"{parsed.scheme}://{parsed.netloc}{path}"


def _parse_post_form(html: str, page_url: str) -> tuple[str, str, str] | None:
    form_match = re.search(
        r'<form[^>]*action=["\']([^"\']+)["\'][^>]*method=["\']post',
        html,
        re.I,
    ) or re.search(
        r'<form[^>]*method=["\']post["\'][^>]*action=["\']([^"\']+)["\']',
        html,
        re.I,
    )
    if not form_match:
        return None

    action_url = urljoin(_page_base_for_join(page_url), form_match.group(1).strip())
    lowered = html.lower()

    if 'name="u"' in lowered or "name='u'" in lowered:
        return action_url, "u", "co"
    if 'name="usuario"' in lowered or "name='usuario'" in lowered:
        return action_url, "usuario", "contrasena"

    return None


def _url_exists(url: str) -> bool:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Portal-Liga-SSO/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            return response.status < 400
    except urllib.error.HTTPError as exc:
        return exc.code < 400
    except Exception:
        return False


def _app_base_url(url: str) -> str:
    parsed = urlparse(url.strip())
    path = parsed.path.rstrip("/")

    if re.search(r"\.(php|asp|aspx|jsp|html?)$", path, re.I):
        path = path.rsplit("/", 1)[0]

    return f"{parsed.scheme}://{parsed.netloc}{path}".rstrip("/")


def _heuristic_laliga_targets(url: str) -> list[str]:
    base = _app_base_url(url)
    return [
        f"{base}/modulos/validacion.php",
        f"{base}/vistas/validacion.php",
    ]


def discover_login_target(app_url: str) -> tuple[str, str, str] | None:
    """Detecta action y campos del login leyendo la página de la aplicación."""
    cache_key = app_url.strip().lower()
    cached = _form_cache.get(cache_key)
    if cached and cached["expires_at"] > time.time():
        return cached["action"], cached["user_field"], cached["pass_field"]

    candidates = [
        app_url.strip(),
        urljoin(app_url, "index.php"),
        urljoin(app_url, "login.php"),
    ]

    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)

        try:
            html = _fetch_html(candidate)
            parsed = _parse_post_form(html, candidate)
            if parsed:
                _form_cache[cache_key] = {
                    "action": parsed[0],
                    "user_field": parsed[1],
                    "pass_field": parsed[2],
                    "expires_at": time.time() + FORM_CACHE_TTL,
                }
                return parsed
        except Exception:
            continue

    if "apps.laliga.org.co" in app_url.lower():
        for target in _heuristic_laliga_targets(app_url):
            if _url_exists(target):
                result = (target, "u", "co")
                _form_cache[cache_key] = {
                    "action": result[0],
                    "user_field": result[1],
                    "pass_field": result[2],
                    "expires_at": time.time() + FORM_CACHE_TTL,
                }
                return result

    return None


def _resolve_launch(url: str) -> tuple[str, str, str, bool]:
    """
    Devuelve action, user_field, pass_field, use_post.
    Si no hay formulario de login, abre la URL directamente.
    """
    target = url.strip()
    parsed = urlparse(target)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("URL no permitida")

    if "apps.laliga.org.co" not in target.lower():
        return target, "", "", False

    discovered = discover_login_target(target)
    if discovered:
        action, user_field, pass_field = discovered
        return action, user_field, pass_field, True

    return target, "", "", False


def build_launch_html(url: str, username: str, password: str) -> str:
    action_url, user_field, pass_field, use_post = _resolve_launch(url)
    safe_target = html.escape(url.strip(), quote=True)

    if not use_post:
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Abriendo aplicación...</title>
</head>
<body>
  <p>Abriendo aplicación...</p>
  <script>window.location.replace("{safe_target}");</script>
</body>
</html>"""

    safe_action = html.escape(action_url, quote=True)
    safe_user = html.escape(username, quote=True)
    safe_pass = html.escape(password, quote=True)
    safe_user_field = html.escape(user_field, quote=True)
    safe_pass_field = html.escape(pass_field, quote=True)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Accediendo...</title>
  <style>
    body {{
      font-family: Inter, Arial, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      background: #f5f5f7;
      color: #1a1a2e;
    }}
  </style>
</head>
<body>
  <p>Ingresando a la aplicación...</p>
  <form id="sso-form" class="form-signin" method="POST" action="{safe_action}">
    <input type="hidden" id="u" name="{safe_user_field}" value="{safe_user}" />
    <input type="hidden" id="co" name="{safe_pass_field}" value="{safe_pass}" />
  </form>
  <script>
    document.getElementById('sso-form').submit();
  </script>
</body>
</html>"""
