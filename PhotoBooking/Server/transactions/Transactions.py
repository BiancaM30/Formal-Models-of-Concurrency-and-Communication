from threading import Lock
import time


class Transactions:
    def __init__(self):
        """
        Initialize a structure to manage transaction metadata.
        """
        self.transactions = {}  # TransactionID -> {timestamp, status, operations}
        self.lock = Lock()

    def add_transaction(self, transaction_id):
        """
        Add a new transaction to the transaction manager. The transaction is initialized with the
        current timestamp, an active status, and an empty list of operations.
        """
        with self.lock:
            if transaction_id not in self.transactions:
                self.transactions[transaction_id] = {
                    "timestamp": time.time(),
                    "status": "active",
                    "operations": []
                }

    def update_status(self, transaction_id, status):
        """
        Update the status of a transaction (e.g., active, committed, aborted)
        """
        with self.lock:
            if transaction_id in self.transactions:
                self.transactions[transaction_id]["status"] = status

    def get_transaction(self, transaction_id):
        """
        Retrieve metadata for a specific transaction.
        """
        with self.lock:
            return self.transactions.get(transaction_id)

    def remove_transaction(self, transaction_id):
        """
        Remove a transaction from the transaction manager, when the transaction is completed or aborted.
        """
        with self.lock:
            if transaction_id in self.transactions:
                del self.transactions[transaction_id]
