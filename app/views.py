from app import app
from flask import request
from flask import render_template
from app import db, models
from datetime import datetime
from chk_tools import check_tools
from .forms import Cell_info_form, Shift_info_form, Break_info_form

@app.route('/')
def index():
    return render_template('index.html',title='Home Page')

@app.route('/dash')
def dash():
    return render_template('dash.html',title='Dashboard',
                           cell='American Shotgun')


@app.route('/toolsetter')
def toolsetter():
 
    return render_template('toolsetter.html',title='Tool Setter',
                           cell='American Shotgun',
                           needed=check_tools(models,False))

@app.route('/logs')
def logs():
    return render_template('logs.html',title='Logs',
                           cell='American Shotgun')

@app.route('/mach_settings')
def mach_settings():
    machs = models.machines.query.all()
    #set_form = SettingsForm()
    return render_template('mach_settings.html',title='Machine Settings',
                           cell='American Shotgun',
                           m=machs)

@app.route('/cell_settings')
def cell_settings():
    cell=models.cell_info.query.order_by(models.cell_info.id.desc()).first()
    cell_info = Cell_info_form()
    shift_info = []
    break_info= []
    for shift in cell.shifts:
        shift_info.append(Shift_info_form())
        sh_breaks=[]
        for brk in shift['breaks']:
            sh_breaks.append(Break_info_form())
        break_info.append(sh_breaks)
    return render_template('cell_settings.html',title='Cell Settings',
                           cell='American Shotgun',
                           c=cell,cell_form=cell_info,shift_form=shift_info,
                           brk_info=break_info)

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


