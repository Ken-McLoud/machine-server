from app import app
from flask import request
from flask import render_template
from app import db, models
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html',title='Home Page')

@app.route('/submit_data', methods=['GET','POST'])
def submit_data():
    if request.method == 'GET':
        return 'Submit data here'
    if request.method == 'POST':
        form_data = request.form

        dt_obj = datetime.strptime(form_data['timestamp'],'%Y-%m-%d %H:%M:%S')
        
        #check if entry exists, doesn't work
        prev=models.data_log.query.filter_by(
            time=dt_obj).filter_by(source=form_data['source']).all()

        if len(prev)==0:
        
            d = models.data_log(source=form_data['source'],
                                datatype=form_data['datatype'],
                                time=dt_obj,
                                payload=form_data['payload'])
            db.session.add(d)
            db.session.commit()
            print('data entered')

        else:
            print('duplicate entry')
            
        return '200 OK'


