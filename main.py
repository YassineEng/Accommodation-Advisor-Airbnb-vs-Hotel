from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers.airbnbs import router as airbnbs_router
from routers.hotels import router as hotels_router
from dotenv import load_dotenv
from config.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup event triggered.")
    logger.info("Registered routes:")
    for route in app.routes:
        logger.info(f"  {route.path} - {route.name}")
    yield
    logger.info("Application shutdown event triggered.")

app = FastAPI(lifespan=lifespan)

app.include_router(airbnbs_router, prefix="")
app.include_router(hotels_router, prefix="")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Accommodation Advisor API!"}