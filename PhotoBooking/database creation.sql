CREATE DATABASE MFCC_db1;
USE MFCC_db1;

CREATE TABLE Photographers (
    PhotographerID INT PRIMARY KEY IDENTITY(1,1),
    Name VARCHAR(100) NOT NULL,
    Specialty VARCHAR(100)
);

CREATE TABLE Timeslots (
	TimeslotID INT PRIMARY KEY IDENTITY(1,1),
    PhotographerID INT NOT NULL,
    AvailableDate DATE NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    Status VARCHAR(20) DEFAULT 'Available' CHECK (Status IN ('Available', 'Booked')),
    FOREIGN KEY (PhotographerID) REFERENCES Photographers(PhotographerID)
);

SELECT * FROM Photographers
SELECT * FROM Timeslots
-------------------------------------------------------------------------------------
CREATE DATABASE MFCC_db2;
USE MFCC_db2;

CREATE TABLE Clients (
    ClientID INT PRIMARY KEY IDENTITY(1,1),
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    Phone VARCHAR(15) NOT NULL
);

CREATE TABLE Bookings (
    BookingID INT PRIMARY KEY IDENTITY(1,1),
	TimeslotID INT NOT NULL,
    ClientID INT NOT NULL,
    Location VARCHAR(255),
    Status VARCHAR(20) DEFAULT 'Scheduled' CHECK (Status IN ('Scheduled', 'Completed', 'Canceled')),
	FOREIGN KEY (ClientID) REFERENCES Clients(ClientID)
);

SELECT * FROM Bookings;



USE MFCC_db2;
DROP TABLE Bookings
DROP TABLE Clients

USE MFCC_db1;
DROP TABLE Timeslots
DROP TABLE Photographers