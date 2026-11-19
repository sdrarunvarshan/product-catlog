from sqlalchemy import create_engine, MetaData
from databases import Database

# SQLite URL format
DATABASE_URL = "sqlite:///./test.db"

# Create database connection
database = Database(DATABASE_URL)
metadata = MetaData()
engine = create_engine(DATABASE_URL)
