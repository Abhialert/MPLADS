from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

# Use SQLite database file in project directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "mplad_integrity.db")
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# Create engine with SQLite
engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()