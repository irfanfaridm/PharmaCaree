from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import datetime
import os

# Use the correct path for Docker volume
DATABASE_URL = "sqlite:///./instance/orders.db"

# Ensure the instance directory exists
os.makedirs('./instance', exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    drug_id = Column(Integer, nullable=False)
    drug_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    order_date = Column(DateTime, default=datetime.datetime.now)

class OrderItem(Base):
    __tablename__ = "order_item"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    drug_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine) 