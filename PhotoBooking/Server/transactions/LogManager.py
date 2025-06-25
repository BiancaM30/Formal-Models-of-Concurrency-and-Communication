import os
import json

class LogManager:
    def __init__(self, log_dir="logs"):
        """
        Initialize the LogManager to handle transaction logs.
        Logs are stored in JSON files, one per transaction, within the specified directory.
        """
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.log_dir = os.path.join(project_root, log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
    def create_log(self, transaction_id):
        """
        Create a new log file for a transaction. The log file is initialized with the
        transaction ID and an empty list of logs.
        """
        try:
            log_file = os.path.join(self.log_dir, f"transaction_{transaction_id}.json")
            with open(log_file, "w") as f:
                json.dump({"transaction_id": transaction_id, "logs": []}, f)
        except Exception as e:
            print(f"Error creating log file: {e}")
            raise

    def append_log(self, transaction_id, table, record_id, data):
        """
        Append an entry to the log file of a transaction. Each entry contains information
        about the table, record ID, and the state of the data.
        """
        try:
            log_file = os.path.join(self.log_dir, f"transaction_{transaction_id}.json")
            with open(log_file, "r+") as f:
                log_data = json.load(f)
                log_data["logs"].append({"table": table, "record_id": record_id, "data": data})
                f.seek(0)
                json.dump(log_data, f, indent=4)
        except Exception as e:
            print(f"Error appending to log file: {e}")
            raise

    def get_log(self, transaction_id):
        """
                Retrieve the contents of a transaction log file.
        """
        log_file = os.path.join(self.log_dir, f"transaction_{transaction_id}.json")
        with open(log_file, "r") as f:
            return json.load(f)

    def delete_log(self, transaction_id):
        """
        Delete the log file of a transaction, after the transaction has been committed or rolled back.
        """
        log_file = os.path.join(self.log_dir, f"transaction_{transaction_id}.json")
        if os.path.exists(log_file):
            os.remove(log_file)
