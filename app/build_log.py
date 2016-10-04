#imports
from datetime import datetime,time,timedelta
from app import db, models
from os import path

def build_log(form,root_dir):
    '''funtion to build a log file based on the users requests

    Args:
      form: a dict from the user form

    Return:
      nothing, but it creates a log.csv file in the app directory'''
    #create date time objects
    start_tm=datetime.strptime(form['start'],'%Y %m %d %H %M')
    end_tm=datetime.strptime(form['end'],'%Y %m %d %H %M')

    machs  = models.machines.query.all()

      
    #query the db
    data=models.data_log.query.filter(models.data_log.time>start_tm
            ).filter(models.data_log.time<end_tm
            ).filter_by(source=form['machine']).all()


    #write the file
    with open(path.join(root_dir,'log.csv'),'w') as log:
        log.write('Machine,Data Type,Time (YYYY MM DD HH MM SS),Data\n')
        for line in data:
            log.write(line.source)
            log.write(',')
            log.write(line.datatype)
            log.write(',')
            log.write(datetime.strftime(line.time,'%Y %m %d %H %M %S'))
            log.write(',')            
            log.write(line.payload)
            
