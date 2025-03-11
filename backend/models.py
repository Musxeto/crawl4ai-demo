from sqlalchemy import DECIMAL, Column, Integer, String
from database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ranking = Column(Integer)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    image_url = Column(String(500))
    product_url = Column(String(500))