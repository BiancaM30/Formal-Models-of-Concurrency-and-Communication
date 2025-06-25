from dao.operations import DaoOperations


class Scheduler:
    def schedule_booking(self, transaction_id, session_data):
        """
        Schedule a new photography session.
        """
        try:
            session_id = DaoOperations.schedule_booking(transaction_id, session_data)
            return f"Session scheduled successfully with ID {session_id}."
        except Exception as e:
            raise ValueError(f"Error scheduling session: {e}")

    def cancel_booking(self, transaction_id, booking_id):
        """
        Cancel a photography booking
        """
        try:
            result = DaoOperations.cancel_booking(transaction_id, booking_id)
            return result
        except Exception as e:
            raise ValueError(f"Error canceling session: {e}")

    def create_availability(self, transaction_id, photographer_id, availability_data):
        """
        Create availability slots for a photographer.
        """
        try:
            availability_id = DaoOperations.create_availability(transaction_id, photographer_id, availability_data)
            return f"Availability created successfully with ID {availability_id}."
        except Exception as e:
            raise ValueError(f"Error creating availability: {e}")

    def get_available_photographers(self, date):
        """
        Fetch photographers available for a given date.
        """
        try:
            available_photographers = DaoOperations.list_available_photographers(date)
            return available_photographers
        except Exception as e:
            raise ValueError(f"Error fetching available photographers: {e}")

    def update_booking(self, transaction_id, session_id, updates):
        """
        Update a session's details.
        """
        try:
            result = DaoOperations.update_booking(transaction_id, session_id, updates)
            return result
        except Exception as e:
            raise ValueError(f"Error updating session: {e}")

    def list_bookings_for_client(self, client_id):
        """
        Retrieve all sessions booked by a specific client.
        """
        try:
            sessions = DaoOperations.list_bookings_for_client(client_id)
            return sessions
        except Exception as e:
            raise ValueError(f"Error retrieving sessions for client: {e}")

    def get_all_clients(self):
        """
        Fetch all clients.
        """
        try:
            clients = DaoOperations.get_all_clients()
            return clients
        except Exception as e:
            raise ValueError(f"Error fetching clients: {e}")

    def get_all_photographers(self):
        """
        Fetch all photographers.
        """
        try:
            photographers = DaoOperations.get_all_photographers()
            return photographers
        except Exception as e:
            raise ValueError(f"Error fetching photographers: {e}")

    def get_available_timeslots_for_photographer(self, photographer_id):
        """
        Fetch available timeslots for a specific photographer.
        """
        try:
            timeslots = DaoOperations.get_available_timeslots_for_photographer(photographer_id)
            return timeslots
        except Exception as e:
            raise ValueError(f"Error fetching available timeslots for photographer: {e}")

    def get_timeslot_details(self, timeslot_id):
        """
        Fetch details of a specific timeslot.
        """
        try:
            timeslot_details = DaoOperations.get_timeslot_details(timeslot_id)
            if not timeslot_details:
                raise ValueError("Timeslot not found.")
            return timeslot_details
        except Exception as e:
            raise ValueError(f"Error fetching timeslot details: {e}")


