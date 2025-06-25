from dao.db import Session1, Session2
from sqlalchemy.exc import SQLAlchemyError
from dao.models import Timeslot, Booking, Photographer, Client
from transactions.TransactionManager import TransactionManager

transaction_manager = TransactionManager()


class DaoOperations:
    @staticmethod
    def schedule_booking(transaction_id, booking_data):
        """
        Schedule a booking for a client.
        Checks the availability of the timeslot and creates a booking if available.
        """
        print(f"Transaction {transaction_id}: Scheduling booking with data {booking_data}.")
        session1 = Session1()  # Connection to MFCC_db1
        session2 = Session2()  # Connection to MFCC_db2

        try:
            # Start the transaction
            transaction_manager.start_transaction(transaction_id)

            # Acquire lock for the timeslot
            resource = f"Timeslot_{booking_data['TimeslotID']}"
            if not transaction_manager.acquire_lock(transaction_id, resource, "write"):
                print(f"Transaction {transaction_id}: Waiting for lock on {resource}.")
                raise Exception("Lock acquisition failed. Transaction is waiting.")

            print(f"Transaction {transaction_id}: Lock acquired on {resource}.")

            # Check if the timeslot exists and is available
            timeslot = session1.query(Timeslot).filter_by(
                TimeslotID=booking_data["TimeslotID"],
                Status="Available"
            ).first()

            if not timeslot:
                raise ValueError("Timeslot is not available or does not exist.")

            # Log timeslot status change
            transaction_manager.log_manager.append_log(
                transaction_id,
                "Timeslots",
                timeslot.TimeslotID,
                {"Status": timeslot.Status}
            )

            # Update timeslot status to "Booked"
            timeslot.Status = "Booked"
            session1.commit()

            print(f"Transaction {transaction_id}: Timeslot {timeslot.TimeslotID} booked.")

            # Create a new booking
            new_booking = Booking(
                TimeslotID=timeslot.TimeslotID,
                ClientID=booking_data["ClientID"],
                Location=booking_data["Location"],
                Status="Scheduled"
            )

            # Log the booking creation
            transaction_manager.log_manager.append_log(
                transaction_id,
                "Bookings",
                None,
                {
                    "TimeslotID": timeslot.TimeslotID,
                    "ClientID": booking_data["ClientID"],
                    "Location": booking_data["Location"],
                    "Status": "Scheduled"
                }
            )

            # Insert booking into the database
            session2.add(new_booking)
            session2.commit()

            # Commit the transaction and release locks
            transaction_manager.commit_transaction(transaction_id)
            print(f"Transaction {transaction_id}: Committed successfully.")
            return new_booking.BookingID
        except Exception as e:
            # Rollback the transaction on failure
            print(f"Transaction {transaction_id}: ERROR - {e}. Rolling back.")
            session1.rollback()
            session2.rollback()
            DaoOperations.rollback(transaction_id)
            raise Exception(f"Error scheduling booking: {e}")
        finally:
            session1.close()
            session2.close()

    @staticmethod
    def cancel_booking(transaction_id, booking_id):
        """
        Cancel a booking and mark the corresponding timeslot as available.
        """
        print(f"Transaction {transaction_id}: Canceling booking with ID {booking_id}.")
        session1 = Session1()  # Connection to MFCC_db1
        session2 = Session2()  # Connection to MFCC_db2

        try:
            # Start the transaction
            transaction_manager.start_transaction(transaction_id)

            # Acquire lock for the booking
            resource = f"Booking_{booking_id}"
            if not transaction_manager.acquire_lock(transaction_id, resource, "write"):
                raise Exception("Lock acquisition failed. Transaction is waiting.")

            # Fetch the booking record
            booking_record = session2.query(Booking).filter_by(BookingID=booking_id).first()
            if not booking_record:
                raise ValueError("Booking not found.")

            # Log the booking deletion
            transaction_manager.log_manager.append_log(transaction_id, "Bookings", booking_record.BookingID, {
                "TimeslotID": booking_record.TimeslotID,
                "ClientID": booking_record.ClientID,
                "Location": booking_record.Location,
                "Status": booking_record.Status
            })

            # Delete the booking
            session2.delete(booking_record)
            session2.commit()

            # Update the corresponding timeslot to "Available"
            timeslot = session1.query(Timeslot).filter_by(TimeslotID=booking_record.TimeslotID).first()
            if timeslot:
                transaction_manager.log_manager.append_log(transaction_id, "Timeslots", timeslot.TimeslotID, {
                    "Status": timeslot.Status
                })
                timeslot.Status = "Available"
                session1.commit()

            # Commit the transaction and release locks
            transaction_manager.commit_transaction(transaction_id)
            return "Booking canceled successfully."
        except Exception as e:
            # Rollback the transaction on failure
            session1.rollback()
            session2.rollback()
            DaoOperations.rollback(transaction_id)
            raise Exception(f"Error canceling booking: {e}")
        finally:
            session1.close()
            session2.close()

    @staticmethod
    def create_availability(transaction_id, photographer_id, availability_data):
        session = Session1()
        try:
            # Start the transaction
            transaction_manager.start_transaction(transaction_id)

            # Acquire lock for the resource
            resource = f"Timeslot_{photographer_id}"
            if not transaction_manager.acquire_lock(transaction_id, resource, "write"):
                raise Exception("Lock acquisition failed. Transaction is waiting.")

            # Create a new timeslot entry
            new_timeslot = Timeslot(
                PhotographerID=photographer_id,
                AvailableDate=availability_data["AvailableDate"],
                StartTime=availability_data["StartTime"],
                EndTime=availability_data["EndTime"],
                Status="Available"
            )

            # Log the creation
            transaction_manager.log_manager.append_log(transaction_id, "Timeslots", None, {
                "PhotographerID": photographer_id,
                "AvailableDate": availability_data["AvailableDate"],
                "StartTime": availability_data["StartTime"],
                "EndTime": availability_data["EndTime"],
                "Status": "Available"
            })

            # Add to database
            session.add(new_timeslot)
            session.commit()

            # Commit the transaction
            transaction_manager.commit_transaction(transaction_id)
            return new_timeslot.TimeslotID
        except Exception as e:
            # Rollback the transaction on failure
            session.rollback()
            DaoOperations.rollback(transaction_id)
            raise Exception(f"Error creating timeslot: {e}")
        finally:
            session.close()

    @staticmethod
    def update_booking(transaction_id, booking_id, updates):
        session = Session2()
        try:
            # Start the transaction
            transaction_manager.start_transaction(transaction_id)

            # Acquire lock for the booking
            resource = f"Booking_{booking_id}"
            if not transaction_manager.acquire_lock(transaction_id, resource, "write"):
                raise Exception("Lock acquisition failed. Transaction is waiting.")

            # Fetch the booking
            booking_record = session.query(Booking).filter_by(BookingID=booking_id).first()
            if not booking_record:
                raise ValueError("Booking not found.")

            # Log the current state
            transaction_manager.log_manager.append_log(transaction_id, "Bookings", booking_record.BookingID, {
                "TimeslotID": booking_record.TimeslotID,
                "ClientID": booking_record.ClientID,
                "Location": booking_record.Location,
                "Status": booking_record.Status
            })

            # Apply updates
            for key, value in updates.items():
                setattr(booking_record, key, value)
            session.commit()

            # Commit the transaction
            transaction_manager.commit_transaction(transaction_id)
            return "Booking updated successfully."
        except Exception as e:
            # Rollback the transaction on failure
            session.rollback()
            DaoOperations.rollback(transaction_id)
            raise Exception(f"Error updating booking: {e}")
        finally:
            session.close()

    def list_available_photographers(date):
        """
        List photographers available for a given date, including their details.
        """
        session = Session1()
        try:
            results = (
                session.query(
                    Timeslot.TimeslotID,
                    Timeslot.PhotographerID,
                    Timeslot.StartTime,
                    Timeslot.EndTime,
                    Photographer.Name,
                    Photographer.Specialty
                )
                .join(Photographer, Photographer.PhotographerID == Timeslot.PhotographerID)
                .filter(
                    Timeslot.AvailableDate == date,
                    Timeslot.Status == "Available"
                )
                .all()
            )
            return [
                {
                    "TimeslotID": result.TimeslotID,
                    "PhotographerID": result.PhotographerID,
                    "StartTime": str(result.StartTime),
                    "EndTime": str(result.EndTime),
                    "Name": result.Name,
                    "Specialty": result.Specialty,
                }
                for result in results
            ]
        except SQLAlchemyError as e:
            raise Exception(f"Error listing available photographers: {e}")
        finally:
            session.close()

    @staticmethod
    def list_bookings_for_client(client_id):
        """
        Retrieve all bookings made by a specific client.
        """
        session = Session2()
        try:
            results = session.query(Booking).filter_by(ClientID=client_id).all()
            return [
                {
                    "BookingID": record.BookingID,
                    "TimeslotID": record.TimeslotID,
                    "ClientID": record.ClientID,
                    "Location": record.Location,
                    "Status": record.Status
                }
                for record in results
            ]
        except SQLAlchemyError as e:
            raise Exception(f"Error listing bookings for client: {e}")
        finally:
            session.close()

    @staticmethod
    def get_all_clients():
        session = Session2()
        try:
            clients = session.query(Client).all()
            if not clients:
                return []
            return [
                {
                    "ClientID": c.ClientID,
                    "Name": c.Name,
                    "Email": c.Email,
                    "Phone": c.Phone
                }
                for c in clients
            ]
        except Exception as e:
            print(f"Error fetching clients: {e}")
            raise Exception(f"Error fetching clients: {e}")
        finally:
            session.close()

    @staticmethod
    def get_all_photographers():
        session = Session1()
        try:
            photographers = session.query(Photographer).all()
            return [{"PhotographerID": p.PhotographerID, "Name": p.Name, "Specialty": p.Specialty} for p in
                    photographers]
        except Exception as e:
            raise Exception(f"Error fetching photographers: {e}")
        finally:
            session.close()
    @staticmethod
    def get_available_timeslots_for_photographer(photographer_id):
        session = Session1()
        try:
            timeslots = session.query(Timeslot).filter_by(PhotographerID=photographer_id, Status="Available").all()
            return [
                {
                    "TimeslotID": t.TimeslotID,
                    "AvailableDate": str(t.AvailableDate),
                    "StartTime": str(t.StartTime),
                    "EndTime": str(t.EndTime),
                    "Status": t.Status
                }
                for t in timeslots
            ]
        except Exception as e:
            raise Exception(f"Error fetching available timeslots for photographer: {e}")
        finally:
            session.close()

    @staticmethod
    def rollback(transaction_id):
        """
        Rollback the changes made by a transaction using the logs.
        This method ensures the database state is restored to its pre-transaction state.
        """
        session1 = Session1()  # For MFCC_db1
        session2 = Session2()  # For MFCC_db2
        try:
            # Fetch the log data for the transaction
            log_data = transaction_manager.log_manager.get_log(transaction_id)
            for log_entry in reversed(log_data["logs"]):  # Reverse to undo operations in reverse order
                table = log_entry["table"]
                record_id = log_entry["record_id"]
                data = log_entry["data"]

                if table == "Timeslots":
                    record = session1.query(Timeslot).filter_by(TimeslotID=record_id).first()
                    if record:
                        # Restore the state of the record
                        for key, value in data.items():
                            setattr(record, key, value)
                    else:
                        # If the record was deleted, reinsert it
                        restored_record = Timeslot(**data)
                        session1.add(restored_record)

                elif table == "Bookings":
                    record = session2.query(Booking).filter_by(BookingID=record_id).first()
                    if record:
                        # Restore the state of the record
                        for key, value in data.items():
                            setattr(record, key, value)
                    else:
                        # If the record was deleted, reinsert it
                        restored_record = Booking(**data)
                        session2.add(restored_record)

            # Commit changes to both databases
            session1.commit()
            session2.commit()

            # Remove the log after successful rollback
            transaction_manager.log_manager.delete_log(transaction_id)
        except Exception as e:
            # Rollback both sessions in case of an error
            session1.rollback()
            session2.rollback()
            raise Exception(f"Error during rollback: {e}")
        finally:
            # Close both sessions
            session1.close()
            session2.close()

    @staticmethod
    def get_timeslot_details(timeslot_id):
        """
        Retrieve details for a specific timeslot.
        """
        session = Session1()
        try:
            timeslot = (
                session.query(Timeslot, Photographer.Name, Photographer.Specialty)
                .join(Photographer, Photographer.PhotographerID == Timeslot.PhotographerID)
                .filter(Timeslot.TimeslotID == timeslot_id)
                .first()
            )
            if timeslot:
                timeslot_data, photographer_name, photographer_specialty = timeslot
                return {
                    "TimeslotID": timeslot_data.TimeslotID,
                    "PhotographerID": timeslot_data.PhotographerID,
                    "PhotographerName": photographer_name,
                    "Specialty": photographer_specialty,
                    "AvailableDate": str(timeslot_data.AvailableDate),
                    "StartTime": str(timeslot_data.StartTime),
                    "EndTime": str(timeslot_data.EndTime),
                    "Status": timeslot_data.Status,
                }
            return None
        except SQLAlchemyError as e:
            raise Exception(f"Error fetching timeslot details: {e}")
        finally:
            session.close()



