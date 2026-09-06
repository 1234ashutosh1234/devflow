from fastapi import FastAPI

from app.api.routes.auth import router as auth_router


app = FastAPI(
    title="DevFlow API",
    description="AI-powered developer collaboration and code review platform.",
    version="0.1.0",
)

app.include_router(auth_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}