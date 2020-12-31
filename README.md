# Key-value Datastore
A file based key-value data store that allows CRD (create, read and delete) operations on data.

# Setup
1. Create python virtual environment: `python3 -m venv venv`
2. Activate virtual environment: `source venv/bin/activate`
3. Install dependencies: `pip3 install -r requirements.txt`
4. Run app: `flask run`

# UI
1. To create new entry, enter data into text field and submit. The status of the operation will be shown in the green area. The format of the JSON data is as follows:
```
{
    "sample": {
        "data1": "value1",
        "data2": "value2",
        "data3": "value3",
        "Time-To-Live": 5000,
    },
}
```
2. To fetch an already existing data use `Read`.
3. Existing data can be deleted using `Delete` if not already destroyed.

# Tests
Run tests by running the `tests.py` file in `tests` directory.




