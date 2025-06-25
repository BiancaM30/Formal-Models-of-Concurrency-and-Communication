from threading import Lock

class Locks:
    def __init__(self):
        """
        Locks are stored in a dictionary with resources as keys, and each value is
        a dictionary containing the transaction ID and lock type (read/write)
        """
        self.locks = {}  # Resource -> {transaction_id, lock_type}
        self.lock = Lock()

    def acquire_lock(self, transaction_id, resource, lock_type):
        """
        Attempt to acquire a lock on a resource for a specific transaction.
        If the resource is not currently locked, grant the lock.
        If the resource is already locked by the same transaction, check if the lock type is compatible.
        Deny the lock if the resource is held by another transaction.
        """
        with self.lock:
            if resource not in self.locks:
                # Grant the lock
                self.locks[resource] = {"transaction_id": transaction_id, "lock_type": lock_type}
                return True

            # Check if the lock is compatible
            current_lock = self.locks[resource]
            if current_lock["transaction_id"] == transaction_id:
                # Transaction already holds the lock
                return True

            # Lock is held by another transaction
            return False

    def release_locks(self, transaction_id):
        """
        Release all locks held by a specific transaction. Iterate through the lock
        dictionary to find and remove all resources locked by the transaction.
        """
        with self.lock:
            resources_to_release = [res for res, lock in self.locks.items() if lock["transaction_id"] == transaction_id]
            for resource in resources_to_release:
                del self.locks[resource]

    def get_locks(self):
        with self.lock:
            return self.locks
