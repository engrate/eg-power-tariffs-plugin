from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="Power Tariffs Plugin",
    description="Plugin to provide power tariffs data and functionality",
)

Instrumentator().instrument(app).expose(app)