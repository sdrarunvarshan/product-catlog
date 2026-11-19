from fastapi import FastAPI
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Product
from schemas import Product as ProductSchema

# ---------------------------------------
# Database setup (SQLite for simplicity)
# ---------------------------------------
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

# ---------------------------------------
# FastAPI app setup
# ---------------------------------------
app = FastAPI(title="Product Catalog API")

# ---------------------------------------
# CRUD Router setup
# ---------------------------------------
router = SQLAlchemyCRUDRouter(
    schema=ProductSchema,           # Response model
    create_schema=ProductSchema,    # Create model
    db_model=Product,               # Database model
    db=(get_db := lambda: SessionLocal()),  # Database session
    prefix="products",              # URL prefix for routes
    tags=["Products"]
)

# Include the router in the app
app.include_router(router)

# ---------------------------------------
# Root route
# ---------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Product Catalog API!"}
