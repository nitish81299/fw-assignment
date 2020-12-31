__author__ = 'nitish-sharma'

from flask import Flask, render_template, request
from CRD.functions import FileHandle, DataStoreCRD
import json

DEFAULT_DB_PATH = 'db'

db_path = DEFAULT_DB_PATH

# Create a datastore directory.
directory_created = FileHandle(db_path).create_folder()


app = Flask(__name__)

# home page
@app.route('/', methods = ['POST', 'GET'])
def main():
    return render_template('app.html')
    

# create method
@app.route('/create', methods = ['GET','POST'])
def create_Data():
    try:
        json_data = request.form['json-data']
        data = eval(json_data)

    except NameError:
        return render_template('app.html', result="Enter Valid JSON data")
    
    except SyntaxError:
        return render_template('app.html', result="Enter Valid JSON data")
        
    _data_found, message = DataStoreCRD().check_create_data(data, db_path)

    return render_template('app.html', result=message)


# read method
@app.route('/read', methods = ['POST'])
def read_Data():
    key = request.form.get('key')
    _data_found, message = DataStoreCRD().check_read_data(key, db_path)

    return render_template('app.html', result=message)


# delete method
@app.route('/delete', methods = ['GET', 'POST'])
def delete_Data():
    key = request.form['key']
    _data_found, message = DataStoreCRD().check_delete_data(key, db_path)

    return render_template('app.html', result=message)


# Initiates Flask Server
if __name__ == '__main__':
    app.run(host='localhost', port=5000)
