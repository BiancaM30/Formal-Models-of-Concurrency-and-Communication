from threading import Lock
class WaitForGraph:
    def __init__(self):
        """
        Initialize the Wait-For Graph and a threading lock.
        The graph stores transaction dependencies as a dictionary where keys
        are transaction IDs and values are lists of transactions they are waiting for.
        """
        self.graph = {}  # TransactionID -> List of transactions it's waiting for
        self.lock = Lock()

    def add_edge(self, from_transaction, to_transaction):
        """
        Add a directed edge from one transaction to another, indicating that
        the first transaction is waiting for the second transaction to release a resource.
        """
        with self.lock:
            if from_transaction not in self.graph:
                self.graph[from_transaction] = []
            self.graph[from_transaction].append(to_transaction)
            print(f"Edge added: {from_transaction} -> {to_transaction}")

    def remove_edge(self, from_transaction, to_transaction):
        """
        Remove a directed edge between two transactions, indicating that the
        waiting dependency has been resolved.
        """
        with self.lock:
            if from_transaction in self.graph:
                self.graph[from_transaction].remove(to_transaction)

    def remove_transaction(self, transaction_id):
        """
        Remove a transaction from the graph and all its dependencies,
        when the transaction finishes or is aborted.
        """
        with self.lock:
            if transaction_id in self.graph:
                del self.graph[transaction_id]
            for waiters in self.graph.values():
                if transaction_id in waiters:
                    waiters.remove(transaction_id)

    def detect_cycle(self):
        """
        Detect cycles in the wait-for graph using topological sorting.
        :return: A list of transactions involved in the cycle if a deadlock is detected,
                 or None if no cycle is found.
        """
        with self.lock:
            print(f"Current Wait-For Graph: {self.graph}")
            in_degree = {tid: 0 for tid in self.graph}
            for tid, waiters in self.graph.items():
                for waiter in waiters:
                    in_degree[waiter] += 1

            queue = [tid for tid, degree in in_degree.items() if degree == 0]
            visited = 0

            while queue:
                current = queue.pop(0)
                visited += 1
                for waiter in self.graph.get(current, []):
                    in_degree[waiter] -= 1
                    if in_degree[waiter] == 0:
                        queue.append(waiter)

            # If not all transactions are visited, there's a cycle
            if visited != len(in_degree):
                cycle = [tid for tid, degree in in_degree.items() if degree > 0]
                return cycle
            return None
