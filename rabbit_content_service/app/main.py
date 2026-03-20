from fastapi import FastAPI

app = FastAPI(title="Rabbit Content Service")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "rabbit_content_service"}
