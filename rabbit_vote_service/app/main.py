from fastapi import FastAPI

app = FastAPI(title="Rabbit Vote Service")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "rabbit_vote_service"}
