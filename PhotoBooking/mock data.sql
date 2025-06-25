USE MFCC_db1;

-- Insert photographers
INSERT INTO Photographers (Name, Specialty) VALUES
('Alice Johnson', 'Event'),
('Bob Smith', 'Portrait'),
('Charlie Brown', 'Wedding'),
('Diana Lee', 'Product');

-- Insert timeslots for Photographer Alice Johnson
INSERT INTO Timeslots (PhotographerID, AvailableDate, StartTime, EndTime, Status) VALUES
(1, '2025-02-03', '10:00:00', '12:00:00', 'Available'),
(1, '2025-02-03', '12:00:00', '14:00:00', 'Available'),
(1, '2025-02-05', '14:00:00', '16:00:00', 'Available');

-- Insert timeslots for Photographer Bob Smith
INSERT INTO Timeslots (PhotographerID, AvailableDate, StartTime, EndTime, Status) VALUES
(2, '2025-02-04', '09:00:00', '11:00:00', 'Available'),
(2, '2025-02-05', '11:00:00', '13:00:00', 'Available'),
(2, '2025-02-05', '13:00:00', '15:00:00', 'Available');

-- Insert timeslots for Photographer Charlie Brown
INSERT INTO Timeslots (PhotographerID, AvailableDate, StartTime, EndTime, Status) VALUES
(3, '2025-02-03', '08:00:00', '10:00:00', 'Available'),
(3, '2025-02-06', '10:00:00', '12:00:00', 'Available'),
(3, '2025-02-06', '12:00:00', '14:00:00', 'Available');


USE MFCC_db1;
SELECT * FROM Timeslots;

------------------------------------------------------------------

USE MFCC_db2;
-- Insert clients
INSERT INTO Clients (Name, Email, Phone) VALUES
('Emily Davis', 'emily.davis@example.com', '1234567890'),
('John Doe', 'john.doe@example.com', '0987654321'),
('Sophia Wilson', 'sophia.wilson@example.com', '5551234567'),
('Michael Taylor', 'michael.taylor@example.com', '5559876543');


USE MFCC_db2;
SELECT * FROM Clients;

USE MFCC_db2;
SELECT * FROM Bookings;

DELETE FROM Clients