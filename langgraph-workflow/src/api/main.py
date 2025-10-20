from fastapi import FastAPI
from .routes import router

app = FastAPI(title="Agentic Support Assistant")

app.include_router(router)
