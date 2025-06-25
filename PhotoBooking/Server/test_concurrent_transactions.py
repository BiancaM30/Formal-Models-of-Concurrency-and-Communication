import threading
import requests
import time

API_URL = "http://127.0.0.1:5000/bookings"

def attempt_booking(transaction_id, timeslot_id, client_id, location):
    payload = {
        "TransactionID": transaction_id,
        "TimeslotID": timeslot_id,
        "ClientID": client_id,
        "Location": location
    }
    try:
        response = requests.post(API_URL, json=payload)
        print(f"Transaction {transaction_id}: Response - {response.json()}")
    except Exception as e:
        print(f"Transaction {transaction_id}: Error - {e}")

# Simulate two transactions trying to book the same timeslot
timeslot_id = 4  # Assume Timeslot 5 is available
client_1 = 1
client_2 = 2

thread1 = threading.Thread(target=attempt_booking, args=(1001, timeslot_id, client_1, "Paris"))
thread2 = threading.Thread(target=attempt_booking, args=(1002, timeslot_id, client_2, "London"))

thread1.start()
thread2.start()

thread1.join()
thread2.join()
