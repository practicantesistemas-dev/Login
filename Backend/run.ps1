# Detiene procesos uvicorn previos en el puerto 5000 y arranca el backend correcto
$port = 5000
$connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
$pids = @($connections | Select-Object -ExpandProperty OwningProcess -Unique)
foreach ($procId in $pids) {
    if ($procId) {
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 1
Write-Host "Iniciando backend en http://localhost:$port (Oracle BDLIGA)..."
Write-Host "Version esperada en /health: 2.10-oracle-admin"
Set-Location $PSScriptRoot
$env:PYTHONPATH = "."
python -m uvicorn main:app --reload --host 127.0.0.1 --port $port
