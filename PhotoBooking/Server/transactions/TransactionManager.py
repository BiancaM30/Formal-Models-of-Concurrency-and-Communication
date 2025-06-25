from transactions.Locks import Locks
from transactions.LogManager import LogManager
from transactions.Transactions import Transactions
from transactions.WaitForGraph import WaitForGraph


class TransactionManager:
    def __init__(self):
        """
        Initialize the Transaction Manager to handle distributed transactions.
        It manages transactions, locks, the wait-for graph, and logging.
        """
        self.transactions = Transactions()
        self.locks = Locks()
        self.wait_for_graph = WaitForGraph()
        self.log_manager = LogManager()

    def start_transaction(self, transaction_id):
        """
        Start a new transaction by adding it to the transaction manager and creating
        a corresponding log file for tracking changes.
        """
        self.transactions.add_transaction(transaction_id)
        self.log_manager.create_log(transaction_id)
        print(f"Transaction {transaction_id} started.")

    def acquire_lock(self, transaction_id, resource, lock_type):
        """
        Attempt to acquire a lock on a resource for the specified transaction. If the lock
        cannot be acquired, add the transaction to the wait-for graph and return False.
        """
        if not self.locks.acquire_lock(transaction_id, resource, lock_type):
            # Add to wait-for graph if lock cannot be granted
            current_lock = self.locks.get_locks().get(resource)
            if current_lock:
                self.wait_for_graph.add_edge(transaction_id, current_lock["transaction_id"])
                print(f"Transaction {transaction_id} waiting for {current_lock['transaction_id']} on resource {resource}.")
            return False
        print(f"Transaction {transaction_id} acquired {lock_type} lock on {resource}.")
        return True

    def release_locks(self, transaction_id):
        """
        Release all locks held by a transaction and remove the transaction from
        the wait-for graph. Ensures the transaction lifecycle ends properly.
        """
        self.locks.release_locks(transaction_id)
        self.wait_for_graph.remove_transaction(transaction_id)
        print(f"Transaction {transaction_id} released all locks.")

    def check_deadlock(self):
        """
        Check for deadlocks in the wait-for graph. If a cycle is detected, resolve it by
        aborting the youngest transaction in the cycle (the transaction with the latest timestamp).
        """
        cycle = self.wait_for_graph.detect_cycle()
        if cycle:
            print(f"Deadlock detected! Cycle: {cycle}")
            transaction_to_abort = max(cycle, key=lambda tid: self.transactions.get_transaction(tid)["timestamp"])
            print(f"Aborting transaction {transaction_to_abort} to resolve deadlock.")
            self.transactions.update_status(transaction_to_abort, "aborted")
            self.release_locks(transaction_to_abort)
            return transaction_to_abort
        return None

    def commit_transaction(self, transaction_id):
        """
        Commit a transaction by updating its status to "committed" and releasing all
        locks held by it
        """
        self.transactions.update_status(transaction_id, "committed")
        self.release_locks(transaction_id)