from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router

app = FastAPI(
    title="NotaryFlow API",
    version="0.1.0",
)

app.include_router(api_v1_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "notaryflow-api",
    }