# main.py
# This file serves as the entry point for the FastAPI application, setting up the API server,
# configuring middleware, and integrating different route modules.

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.airbnbs import router as airbnbs_router
from routers.hotels import router as hotels_router
from dotenv import load_dotenv
from config.config import settings
import logging

# Configure logging for the application.
# Log messages will be displayed with a timestamp, log level, and the message content.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from a .env file.
# This is typically used for sensitive information like database connection strings or API keys.
load_dotenv()

# Asynchronous context manager for managing the application's lifespan (startup and shutdown events).
# This is where resources can be initialized or cleaned up.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on application startup
    logger.info("Application startup event triggered.")
    logger.info("Registered routes:")
    # Log all registered API routes for debugging and overview.
    for route in app.routes:
        logger.info(f"  {route.path} - {route.name}")
    yield  # The application will run here
    # Code to run on application shutdown
    logger.info("Application shutdown event triggered.")

# Initialize the FastAPI application.
# The 'lifespan' context manager is passed to handle startup/shutdown events.
app = FastAPI(lifespan=lifespan)

# Add CORS (Cross-Origin Resource Sharing) middleware.
# This is crucial for allowing frontend applications (like the index.html served locally)
# to make requests to this backend API without being blocked by browser security policies.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (e.g., http://localhost, file://). For production, specify your frontend domain(s).
    allow_credentials=True, # Allow cookies to be included in cross-origin HTTP requests.
    allow_methods=["*"],  # Allows all standard HTTP methods (GET, POST, PUT, DELETE, etc.).
    allow_headers=["*"],  # Allows all HTTP headers in cross-origin requests.
)

# Include routers from separate modules.
# This organizes API endpoints into logical groups (e.g., airbnbs.py for Airbnb-related endpoints).
# The 'prefix=""' means these routes are directly at the root, e.g., /find_airbnbs_near_hotel.
app.include_router(airbnbs_router, prefix="")
app.include_router(hotels_router, prefix="")

# Define a simple root endpoint to confirm the API is running.
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Accommodation Advisor API!"}