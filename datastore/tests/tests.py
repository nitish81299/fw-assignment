import unittest
from argparse import ArgumentParser
from flask import jsonify
from sys import exit
import sys
import os

sys.path.append(os.path.abspath(os.path.join('..', 'CRD')))

from functions import FileHandle, DataStoreCRD

db_path = 'test-db'

FileHandle(db_path).create_folder()

class TestOperations(unittest.TestCase):

    def test_create_data(self):

        test_json_data = {"test_data": { "data": "value", "Time-To-Live": 5000}}

        _valid_data, message = DataStoreCRD().check_create_data(test_json_data, db_path)
        self.assertEqual(message, 'Data created in DataStore.')
    
    def test_read_data(self):
        
        key = 'test_data'
        _data_found, message = DataStoreCRD().check_read_data(key, db_path)
        actual = {"data": "value", "Time-To-Live": 5000}
        self.assertEqual(message,  actual)

    def test_delete_data(self):

        key = 'no_data_key'
        _data_found, message = DataStoreCRD().check_delete_data(key, db_path)
        self.assertEqual(message, 'No data found for the key provided.')


if __name__ == '__main__':
    unittest.main()
