# Formal-Models-of-Concurrency-and-Communication

This repository contains the project developed for the **Formal Models of Concurrency and Communication** course. The system is a **distributed, multi-tier, concurrent application** for managing photography session bookings. It emphasizes **application-level transactional control** across **two separate databases**, using **Strong Two-Phase Locking (2PL)**, **rollback/commit mechanisms**, and **deadlock detection via Wait-For graphs**.

---

## Project Overview

The system manages photographers, clients, and photography sessions, enabling users to:
- Schedule or cancel photo sessions
- Assign or reassign photographers
- Generate reports and send reminders

All operations are transactional and may involve multiple databases. The main focus is **manual implementation of a transactional system**, not framework-based automation.

---

## Architecture

- **Type**: Distributed (Client-Server or Web-Based)
- **Layers**:
  - **Client/UI**: Web or desktop interface
  - **Business Layer**: Transaction coordination and concurrency control
  - **Data Layer**: Two distinct relational databases

---

## Database Design

### Database 1 – `MFCC_db1`
- `PhotographerAvailability(PhotographerID, DateTimeSlot, Status)`
- `Clients(ClientID, Name, Email, Phone)`

### Database 2 – `MFCC_db2`
- `Sessions(SessionID, PhotographerID, ClientID, DateTime, Location, Status)`

Each database includes at least 3 tables, and **distributed transactions span both databases**.

---

## Use Cases (8 Functionalities)

1. **Search available photographers**  
   ➤ Query `PhotographerAvailability` by specialty and time slot.

2. **Book a session**  
   ➤ Insert into `Sessions` (DB2)  
   ➤ Update `PhotographerAvailability.Status = 'Booked'` (DB1)

3. **Cancel a session**  
   ➤ Delete from `Sessions` (DB2)  
   ➤ Update `PhotographerAvailability.Status = 'Available'` (DB1)

4. **Add a new client**  
   ➤ Insert into `Clients` (DB1)

5. **Update session details**  
   ➤ Update session time, location, or photographer (DB2)

6. **Generate session reports**  
   ➤ Aggregate sessions by date or photographer (DB2)

7. **Transfer sessions between photographers**  
   ➤ Update `PhotographerID` in `Sessions` (DB2), update availability in `PhotographerAvailability` (DB1)

8. **Send reminders to clients**  
   ➤ Query upcoming sessions and notify clients (DB2 + DB1)

---

## Transactional System (Implemented in Business Layer)

### Concurrency Control
- **Strong Two-Phase Locking (2PL)**
  - Locks are acquired before executing SQL operations
  - Locks are released only after commit or rollback
  - Locking applies at the record level for both read and write operations
  - Uses a Wait-For graph for deadlock detection

### Deadlock Detection & Resolution
- The system builds a **Wait-For graph** in memory
- Cycles are detected:
  - Either periodically
  - Or immediately when a transaction must wait for a locked resource
- If a cycle is found:
  - One transaction is aborted
  - All its locks are released
  - It is restarted automatically

### Rollback Mechanism
- Two rollback strategies are implemented:
  1. **Undo Log**: Save the previous state of records before any write
  2. **Compensating SQL Operations**:
     - `INSERT` → `DELETE`
     - `UPDATE` → reverse `UPDATE`
     - `DELETE` → re-`INSERT` with old values

### Commit Mechanism
- Follows a **manual two-phase commit protocol**:
  1. **Prepare Phase**:
     - Execute all operations
     - Ensure no errors occurred
  2. **Commit Phase**:
     - Apply changes permanently in both databases
     - Release all acquired locks

---

## Example Distributed Transactions

### Book a Session
- `Database 1 (MFCC_db1)`  
  `UPDATE PhotographerAvailability SET Status = 'Booked' WHERE ...`
- `Database 2 (MFCC_db2)`  
  `INSERT INTO Sessions (...) VALUES (...)`
- `SELECT` session and confirmation details

### Cancel a Session
- `Database 2 (MFCC_db2)`  
  `DELETE FROM Sessions WHERE SessionID = ...`
- `Database 1 (MFCC_db1)`  
  `UPDATE PhotographerAvailability SET Status = 'Available' WHERE ...`

---

## Threading Model

- **One thread per transaction**
  - In web apps: 1 thread/request
  - In client-server apps: thread per connected client
- **Thread synchronization** for:
  - `Transactions`, `Locks`, and `Wait-For Graph`

---

##  Transaction Management Structures

| Structure      | Description                                    |
|----------------|------------------------------------------------|
| `Transactions` | ID, Timestamp, Status (active/abort/commit), optional list of operations |
| `Locks`        | LockType (Read/Write), Table, Record ID, Transaction ID |
| `WaitForGraph` | Tracks waiting relationships for deadlock detection |

