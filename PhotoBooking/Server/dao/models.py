from sqlalchemy import Column, Integer, String, ForeignKey, Time, Date
from sqlalchemy.ext.declarative import declarative_base

# Base for MFCC_db1 (Photographers and Timeslots)
Base1 = declarative_base()

# Base for MFCC_db2 (Clients and Bookings)
Base2 = declarative_base()

class Photographer(Base1):
    __tablename__ = 'Photographers'
    PhotographerID = Column(Integer, primary_key=True, index=True)
    Name = Column(String, nullable=False)
    Specialty = Column(String)

class Timeslot(Base1):
    __tablename__ = 'Timeslots'
    TimeslotID = Column(Integer, primary_key=True, index=True)
    PhotographerID = Column(Integer, ForeignKey("Photographers.PhotographerID"), nullable=False)
    AvailableDate = Column(Date, nullable=False)
    StartTime = Column(Time, nullable=False)
    EndTime = Column(Time, nullable=False)
    Status = Column(String, default="Available", nullable=False)

class Client(Base2):
    __tablename__ = 'Clients'
    ClientID = Column(Integer, primary_key=True, index=True)
    Name = Column(String, nullable=False)
    Email = Column(String, unique=True, nullable=False)
    Phone = Column(String, nullable=False)

class Booking(Base2):
    __tablename__ = 'Bookings'
    BookingID = Column(Integer, primary_key=True, index=True)
    TimeslotID = Column(Integer, nullable=False)
    ClientID = Column(Integer, ForeignKey("Clients.ClientID"), nullable=False)
    Location = Column(String)
    Status = Column(String, default="Scheduled", nullable=False)