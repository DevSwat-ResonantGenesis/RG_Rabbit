from fastapi import FastAPI

app = FastAPI(title="Rabbit Community Service")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "rabbit_community_service"}
