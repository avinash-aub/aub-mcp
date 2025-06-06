from sqlalchemy import Column, Integer, String

from app.db import Base


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    no_of_bedrooms = Column(Integer, nullable=False)
    no_of_bathrooms = Column(Integer, nullable=False)
    carpet_area = Column(Integer, nullable=False)
    total_area = Column(Integer, nullable=False)
    country = Column(String, nullable=False)
    state = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    community = Column(String, nullable=True)
    building_name = Column(String, nullable=True)
    asking_price = Column(Integer, nullable=False)
