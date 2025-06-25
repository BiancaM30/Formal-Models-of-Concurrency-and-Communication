from flask import Flask, request, jsonify
from flask_cors import CORS
from services.scheduler import Scheduler
from transactions.TransactionManager import TransactionManager
import logging
import threading
import time

# Initialize Flask app and Scheduler service
app = Flask(__name__)
CORS(app)
scheduler = Scheduler()

# Initialize TransactionManager
transaction_manager = TransactionManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Server is running"}), 200


@app.route('/bookings', methods=['POST'])
def create_booking():
    try:
        booking_data = request.json
        transaction_id = booking_data.get("TransactionID")
        if not transaction_id:
            return jsonify({"error": "Missing required field: 'TransactionID'"}), 400

        logger.info(f"Received booking creation request: {booking_data}")
        result = scheduler.schedule_booking(transaction_id, booking_data)
        return jsonify({"message": f"Booking created successfully with ID {result}"}), 201
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/bookings/<int:booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    try:
        transaction_id = request.args.get("TransactionID")
        if not transaction_id:
            return jsonify({"error": "Missing required parameter 'TransactionID'"}), 400

        logger.info(f"Received request to cancel booking with ID {booking_id}")
        result = scheduler.cancel_booking(transaction_id, booking_id)
        return jsonify({"message": result}), 200
    except Exception as e:
        logger.error(f"Error canceling booking: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/availability', methods=['POST'])
def create_availability():
    """
    Create availability slots for a photographer.
    Expects JSON payload with availability details.
    """
    try:
        availability_data = request.json
        transaction_id = availability_data.get("TransactionID")
        photographer_id = availability_data.get("PhotographerID")

        if not transaction_id or not photographer_id:
            return jsonify({"error": "Missing required fields: 'TransactionID', 'PhotographerID'"}), 400

        logger.info(f"Creating availability for photographer {photographer_id}")
        result = scheduler.create_availability(transaction_id, photographer_id, availability_data)
        return jsonify({"message": result}), 201
    except Exception as e:
        logger.error(f"Error creating availability: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/photographers/availability', methods=['GET'])
def get_available_photographers():
    """
    List available photographers for a given date.
    Query Params: date (YYYY-MM-DD)
    """
    try:
        date = request.args.get('date')
        if not date:
            return jsonify({"error": "Missing required parameter 'date'"}), 400

        logger.info(f"Fetching availability for date: {date}")
        available_photographers = scheduler.get_available_photographers(date)
        return jsonify({"available_photographers": available_photographers}), 200
    except Exception as e:
        logger.error(f"Error fetching photographer availability: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    """
    Update booking details.
    Path Params: booking_id (int)
    Expects JSON payload with updated booking details.
    """
    try:
        booking_data = request.json
        transaction_id = booking_data.get("TransactionID")
        if not transaction_id:
            return jsonify({"error": "Missing required field: 'TransactionID'"}), 400

        logger.info(f"Received update request for booking {booking_id}: {booking_data}")
        result = scheduler.update_booking(transaction_id, booking_id, booking_data)
        return jsonify({"message": result}), 200
    except Exception as e:
        logger.error(f"Error updating booking: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/clients/<int:client_id>/bookings', methods=['GET'])
def list_bookings_for_client(client_id):
    """
    Retrieve all bookings made by a specific client.
    Path Params: client_id (int)
    """
    try:
        logger.info(f"Fetching bookings for client {client_id}")
        bookings = scheduler.list_bookings_for_client(client_id)
        return jsonify({"bookings": bookings}), 200
    except Exception as e:
        logger.error(f"Error fetching bookings for client: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/clients', methods=['GET'])
def get_all_clients():
    """
    Retrieve all clients.
    """
    try:
        logger.info("Fetching all clients.")
        clients = scheduler.get_all_clients()
        return jsonify({"clients": clients}), 200
    except Exception as e:
        logger.error(f"Error fetching clients: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/photographers', methods=['GET'])
def get_all_photographers():
    """
    Retrieve all photographers.
    """
    try:
        logger.info("Fetching all photographers.")
        photographers = scheduler.get_all_photographers()
        return jsonify({"photographers": photographers}), 200
    except Exception as e:
        logger.error(f"Error fetching photographers: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/photographers/<int:photographer_id>/available-timeslots', methods=['GET'])
def get_available_timeslots_for_photographer(photographer_id):
    """
    Retrieve available timeslots for a specific photographer.
    Path Params: photographer_id (int)
    """
    try:
        logger.info(f"Fetching available timeslots for photographer {photographer_id}.")
        timeslots = scheduler.get_available_timeslots_for_photographer(photographer_id)
        return jsonify({"available_timeslots": timeslots}), 200
    except Exception as e:
        logger.error(f"Error fetching available timeslots for photographer: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/timeslots/<int:timeslot_id>', methods=['GET'])
def get_timeslot_details(timeslot_id):
    """
    Retrieve details for a specific timeslot.
    """
    try:
        logger.info(f"Fetching details for timeslot {timeslot_id}")
        timeslot = scheduler.get_timeslot_details(timeslot_id)
        if not timeslot:
            return jsonify({"error": "Timeslot not found"}), 404

        return jsonify(timeslot), 200
    except Exception as e:
        logger.error(f"Error fetching timeslot details: {e}")
        return jsonify({"error": str(e)}), 500


def deadlock_checker():
    while True:
        time.sleep(5)
        transaction_to_abort = transaction_manager.check_deadlock()
        if transaction_to_abort:
            # logger.info(f"Current Wait-for Graph: {transaction_manager.wait_for_graph}")
            logger.warning(f"Deadlock detected. Aborted transaction: {transaction_to_abort}")


if __name__ == '__main__':
    # Start the deadlock checker thread
    threading.Thread(target=deadlock_checker, daemon=True).start()

    app.run(host='0.0.0.0', port=5000, debug=True)
