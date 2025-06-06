from fastapi import FastAPI
from app.routes import router
from app.db import lifespan

app = FastAPI(lifespan=lifespan)
app.include_router(router)
