from fastapi import FastAPI

app = FastAPI(title="Rabbit Moderation Service")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "rabbit_moderation_service"}
