from fastapi import FastAPI
from routes import router

app = FastAPI(
    title="NaturalSQL API",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "NaturalSQL Backend"
    }