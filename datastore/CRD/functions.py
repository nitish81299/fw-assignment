import json
import fcntl
import threading
from os import path, makedirs
from datetime import datetime, timedelta
from dateutil.parser import parse

DEFAULT_DB_NAME = 'db.json'


class FileHandle:
    def __init__(self, file_path):
        self.file_path = file_path

    def create_folder(self):
        try:
            makedirs(self.file_path, mode=0o777, exist_ok=True)
        except PermissionError:
            return False
        return True



class DataStoreCRD:

    # Check whether data is still accessible or not
    def check_time_to_live(self, value):

        created_time = value['CreatedAt']

        created_time = parse(created_time)

        time_to_live = value['Time-To-Live']

        if time_to_live is not None:
            expired_datetime = created_time + timedelta(seconds=time_to_live)

            remaining_seconds = (expired_datetime - datetime.now()).total_seconds()

            if remaining_seconds <= 0:
                return False

        return value

    # Checks for the parameters - length, size and type of JSON data
    def check_create_data(self, json_data, db_path):
        if not isinstance(json_data, dict):
            return False, "Incorrect request data format."

        data_obj = json.dumps(json_data)

        if len(data_obj) > 1000000000:
            return False, "DataStore limit exceed 1GB size."

        for key, value in json_data.items():
            if len(key) > 32:
                return False, "The keys must be in 32 characters length."

            if not isinstance(value, dict):
                return False, "The values must be in JSON object formats."

            value_obj = json.dumps(value)

            if len(value_obj) > 16384:
                return False, "The values must be in 16KB size."

        # Checks if DataStore exists.
        datastore = path.join(db_path, DEFAULT_DB_NAME)
        data = {}
        if path.isfile(datastore):
            with open(datastore) as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                data = json.load(f)
            
                fcntl.flock(f, fcntl.LOCK_UN)

                prev_data_obj = json.dumps(data)
                if len(prev_data_obj) >= 1000000000:
                    return False, "File Size Exceeded 1GB."


        have_key = any(x in json_data.keys() for x in data.keys())
        if have_key:
            return False, "Key already exist in DataStore."

        # Ensure thread proof
        def prepare_data_create(json_data_keys):
            for key in json_data_keys:
                singleton_json = json_data[key]
                singleton_json["CreatedAt"] = datetime.now().isoformat()
                singleton_json["Time-To-Live"] = singleton_json["Time-To-Live"] if 'Time-To-Live' in singleton_json else None
                data[key] = singleton_json

        thread_count = 4
        items = list(json_data.keys())

        split_size = len(items) // thread_count

        threads = []
        for i in range(thread_count):
            start = i * split_size
            end = None if i+1 == thread_count else (i+1) * split_size

            threads.append(threading.Thread(target=prepare_data_create, args=(items[start:end], ), name=f"t{i+1}"))
            threads[-1].start()

        for t in threads:
            t.join()

        # Write the new data.
        with open(datastore, 'w+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(data, f)
            fcntl.flock(f, fcntl.LOCK_UN)

        return True, "Data created in DataStore."

    # Check data if available
    def read_delete_preprocess(self, key, db_path):
        datastore = path.join(db_path, DEFAULT_DB_NAME)

        if not path.isfile(datastore):
            return False, "Empty DataStore. Data not found for the key."

        with open(datastore) as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            data = json.load(f)
            fcntl.flock(f, fcntl.LOCK_UN)

        if key not in data.keys():
            return False, "No data found for the key provided."

        target = data[key]
        target_active = self.check_time_to_live(target)
        if not target_active:
            return False, "Requested data is expired for the key."

        return True, data

    # Read Data from the datastore
    def check_read_data(self, key, db_path):

        status, message = self.read_delete_preprocess(key, db_path)
        if not status:
            return status, message

        data = message[key]

        del data['CreatedAt']

        return status, data

    # Delete Data from datastore
    def check_delete_data(self, key, db_path):
        status, message = self.read_delete_preprocess(key, db_path)
        if not status:
            return status, message

        datastore = path.join(db_path, DEFAULT_DB_NAME)

        del message[key]

        with open(datastore, 'w+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(message, f)
            fcntl.flock(f, fcntl.LOCK_UN)

        return True, "Data is deleted from the datastore."
