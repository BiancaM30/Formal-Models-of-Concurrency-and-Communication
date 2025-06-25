from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

server = "LAPTOP-FEJLOP6E\\SQLEXPRESS"
database1 = "MFCC_db1"
database2 = "MFCC_db2"
DATABASE_URL_1 = f"mssql+pyodbc://{server}/{database1}?driver=ODBC+Driver+17+for+SQL+Server"
DATABASE_URL_2 = f"mssql+pyodbc://{server}/{database2}?driver=ODBC+Driver+17+for+SQL+Server"

# Create SQLAlchemy engines
engine1 = create_engine(DATABASE_URL_1)
engine2 = create_engine(DATABASE_URL_2)

# Create session factories for both engines
Session1 = sessionmaker(bind=engine1)
Session2 = sessionmaker(bind=engine2)

# Create metadata objects and explicitly bind them to the engines
metadata1 = MetaData()
metadata1.bind = engine1
metadata2 = MetaData()
metadata2.bind = engine2
