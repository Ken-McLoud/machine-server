from app import app
from flask import request
from flask import render_template
from app import db, models
from datetime import datetime
from chk_tools import check_tools
from util_funcs import check_cell_info, check_ignore


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

@app.route('/mach_settings',methods=['GET','POST'])
def mach_settings():
    if request.method =='GET':
        machs = models.machines.query.all()   
        return render_template('mach_settings.html',title='Machine Settings',
                               cell='American Shotgun',
                               m=machs)
    elif request.method=='POST':
        form_data = request.form
        machs=models.machines.query.all()
        form_dict ={}
        for item in form_data:
            if 'ident' in item:
                num=item[:item.index('_')]
                form_dict[form_data[item]]={'name':form_data[num+'_name'],
                                            'ignore':form_data[num+'_ignore']}

        #check if ident from db is not in form, delete from db
        db_idents=[]
        for mach in machs:            
            if not mach.ident in form_dict:                
                db.session.delete(mach)
            else:
                db_idents.append(mach.ident)

        #check if ident from form is not in db, add to db
        for mach in form_dict:
            if not mach in db_idents:
                new_mach=models.machines(name=form_dict[mach]['name'],
                                         ident=mach,
                                         ignore=
                                         check_ignore(form_dict[mach]['ignore']))
                
                db.session.add(new_mach)
            else:
                #check if an ident's name is not the same ad db, update db
                for machine in machs:
                    if machine.ident==mach:
                        db_name=machine.name
                        db_ignore=machine.ignore
                        old_obj=machine
                        break
                name_chngd = not db_name==form_dict[mach]['name']
                ignore_chngd = not db_ignore==form_dict[mach]['ignore']
                if name_chngd or ignore_chngd:                    
                    new_mach=models.machines(name=form_dict[mach]['name'],
                                             ident=mach,
                                             ignore=
                                             check_ignore(
                                                 form_dict[mach]['ignore']))
                    
                    db.session.delete(old_obj)
                    db.session.add(new_mach)               

        db.session.commit()

        return '<meta http-equiv="refresh" content="0; url=/mach_settings" />'
                




@app.route('/cell_settings', methods=['GET','POST'])
def cell_settings():
    if request.method == 'GET':
        cell=models.cell_info.query.order_by(models.cell_info.id.desc()).first()
            
        return render_template('cell_settings.html',title='Cell Settings',
                               cell='American Shotgun',
                               c=cell)
    
    elif request.method == 'POST':
        form_data = request.form
        #get current cell info
        cell=models.cell_info.query.order_by(models.cell_info.id.desc()).first()
        shft=cell.shifts
        changed=False
        new_shifts=[]

        #check if anything has changed 
        for item in form_data:
            if 'break' in item:
                shift=int(item[5])
                while len(new_shifts)<shift:
                    new_shifts.append({'breaks':[]})
                brk=int(item[12])
                while len(new_shifts[shift-1]['breaks'])<brk:
                    new_shifts[shift-1]['breaks'].append(['',''])
                if 'start' in item:
                    #check break start time
                    old_value=shft[shift-1]['breaks'][brk-1][0]
                    new_shifts[shift-1]['breaks'][brk-1][0]=form_data[item]
                else:
                    #check break end time
                    old_value=shft[shift-1]['breaks'][brk-1][1]
                    new_shifts[shift-1]['breaks'][brk-1][1]=form_data[item]
            elif 'shift' in item:
                shift=int(item[5])
                while len(new_shifts)<shift:
                    new_shifts.append({'breaks':[]})                    
                if 'start' in item:
                    #check shift start time
                    old_value=shft[shift-1]['start']
                    new_shifts[shift-1]['start']=form_data[item]
                else:
                    #check shift end time
                    old_value=shft[shift-1]['end']
                    new_shifts[shift-1]['end']=form_data[item]
            elif 'name' in item:
                #check name
                old_value=cell.name
            elif 'takt' in item:
                #check takt
                old_value=str(cell.takt)

            if form_data[item]!=old_value:
                changed=True               
                

        if changed:
            #create new cell info object
            new_cell = models.cell_info(name=str(form_data['cell_name']),
                                 takt=str(form_data['cell_takt']),
                                 shifts=new_shifts)

            #check if object is valid
            chk=check_cell_info(new_cell)
            if len(chk)==0:
                #if valid, commit to db
                db.session.add(new_cell)
                db.session.commit()
                return '<meta http-equiv="refresh" content="0; url=/cell_settings" />'
            else:
                #if not valid send errors to browser
                return chk
        else:
            return '<meta http-equiv="refresh" content="0; url=/cell_settings" />'



@app.route('/change_shift')
def change_shift():
    '''
    rest api point for accepting http gets for adding or removing shifts

    args:
      cmd: string reading add or remove
      shift_num: (optional)string containing the shift number, starting at 1
      
    '''
    if request.args.get('cmd')=='add':        
        cell=models.cell_info.query.order_by(models.cell_info.id.desc()).first()
        if len(cell.shifts)<1:
            new_shifts=[{'start':'00:00','breaks':[],'end':'00:00'}]
        else:
            prev_end=cell.shifts[-1]['end']
            cell.shifts.append({'start':prev_end,'breaks':[],'end':prev_end})
            new_shifts=cell.shifts
            

        new_cell=models.cell_info(name=cell.name,
                                  takt=cell.takt,
                                  shifts=new_shifts)
        chk=check_cell_info(new_cell)
        if len(chk)==0:
            db.session.add(new_cell)
            db.session.commit()
            return '<meta http-equiv="refresh" content="0; url=/cell_settings" />'
        else:
            return chk
            
    elif request.args.get('cmd')=='remove':
        
        shift_num=int(request.args.get('shift_num'))
        cell=models.cell_info.query.order_by(models.cell_info.id.desc()).first()
        del cell.shifts[shift_num-1]
        ncell=models.cell_info(name=cell.name,
                               takt=cell.takt,
                               shifts=cell.shifts)
        db.session.add(ncell)
        db.session.commit()
        return '<meta http-equiv="refresh" content="0; url=/cell_settings" />'
    
    

@app.route('/change_break')
def change_break():
    '''
    rest api point for accepting http gets for adding or removing breaks

    args:
      cmd: string reading add or remove
      shift_num: string containing the shift number, starting at 1
      break_num: (optional) string containing the break number to remove
                  starting at 1
    '''
    if request.args.get('cmd')=='add':        
        cell=models.cell_info.query.order_by(models.cell_info.id.desc()).first()
        shift_num=int(request.args.get('shift_num'))
        if len(cell.shifts[shift_num-1]['breaks'])<1:
            prev_end=cell.shifts[shift_num-1]['start']
        else:
            prev_end = cell.shifts[shift_num-1]['breaks'][-1][1]
        cell.shifts[shift_num-1]['breaks'
                                 ].append([prev_end,
                                           cell.shifts[shift_num-1]['end']])

        new_cell=models.cell_info(name=cell.name,
                                  takt=cell.takt,
                                  shifts=cell.shifts)
        
        chk=check_cell_info(new_cell)
        if len(chk)==0:
            db.session.add(new_cell)
            db.session.commit()
            return '<meta http-equiv="refresh" content="0; url=/cell_settings" />'
        else:
            return chk
        
    elif request.args.get('cmd')=='remove':        
        shift_num=int(request.args.get('shift_num'))
        break_num=int(request.args.get('break_num'))
        cell=models.cell_info.query.order_by(models.cell_info.id.desc()).first()
        del cell.shifts[shift_num-1]['breaks'][break_num-1]
        ncell=models.cell_info(name=cell.name,
                               takt=cell.takt,
                               shifts=cell.shifts)
        db.session.add(ncell)
        db.session.commit()
        
    return '<meta http-equiv="refresh" content="0; url=/cell_settings" />'

 

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



@app.route('/change_machine')
def change_machine():
    '''
    rest api point for accepting http gets for adding or removing machines

    args:
      cmd: string reading add or remove
      mach_ident: (optional)string containing the machine ident    
    '''
    
    if request.args.get('cmd')=='add':        
        new_mach=models.machines(name='New Machine',
                                 ident='NEW_MACHINE',
                                 ignore = '')        
        
        db.session.add(new_mach)
        db.session.commit()
        return '<meta http-equiv="refresh" content="0; url=/mach_settings" />'
    
        
    elif request.args.get('cmd')=='remove':        
        mach_ident=request.args.get('mach_ident')    
        machs=models.machines.query.all()
        
        for mach in machs:
            if mach.ident==mach_ident:
                db.session.delete(mach)
            
        db.session.commit()
        
    return '<meta http-equiv="refresh" content="0; url=/mach_settings" />'


