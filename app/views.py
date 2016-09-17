from app import app
from flask import request
from app import db, models
from datetime import datetime

@app.route('/')
def index():
    return "hello world"

@app.route('/submit_data', methods=['GET','POST'])
def submit_data():
    if request.method == 'GET':
        return 'Submit data here'
    if request.method == 'POST':
        form_data = request.form
        d = models.data_log(source=form_data['source'],
                            datatype=form_data['datatype'],
                            time=datetime.now(),
                            payload=form_data['payload'])
        db.session.add(d)
        db.session.commit()
        return '200 OK'
