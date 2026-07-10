from fastapi import FastAPI

app = FastAPI(title="Backend CRM Mercadeo")


@app.get("/health")
async def health():
    return {"status": "ok"}
