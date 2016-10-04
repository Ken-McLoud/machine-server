'''
shotgun cell dashboard

'''

#imports
from datetime import datetime,time,timedelta
from app import db, models


##################
##  Cell Class  ##
##################
class Cell():
    '''class for holding information about the cell

    Attributes:
    day: an int for the day of the month when this shift started
    shift: an int for the current shift
    machines: a dict of Machine objects for the cell
    changed: a dict of machine objects that has changed
    shifts: a shift dict from the db
    takt: an int for the cell's takt time
    
    '''

    def __init__(self):
        '''inits the cell'''

        #pull cell config out of db
        db_info=models.cell_info.query.order_by(
            models.cell_info.id.desc()).first()

        self.takt=db_info.takt
        self.shifts=db_info.shifts

        #pull in machine data out of db
        machs=models.machines.query.all()
        self.machines={}
        for m in machs:
            self.machines[m.name]=Machine(m.name,m.ident)

        #the object is new so everything has changed
        self.changed=self.machines


    def get_data(self):
        '''method to get data for cell dashboard
            returns:
              dash_data: a dict with machine names as keys
                         each value is a dict of data label / value pairs
        '''
        self.update()
        dash_data={}
        for mach in self.machines:
            dash_data[self.machines[mach].name]={}
            for data_label in self.machines[mach].data:
                dash_data[self.machines[mach].name][data_label]=self.machines[mach].data[data_label]

        return dash_data


    def update(self):
        '''update's the cell's attributes'''

        def get_time_obj(t):
            '''fuction to take time strings from the db and return time objs
                Args:
                  t: a time in 'HH:MM' format (24 hr clock)

                Returns:
                  time_obj: a time object for that time'''
            return time(int(t[:t.index(':')]),int(t[t.index(':')+1:]))

        #determine what shift we're in
        sh_list = [] #a list of shift start time objects
        for shift in self.shifts:
            sh_list.append(get_time_obj(shift['start']))
                           

        now_dt=datetime.now()
        now=time(now_dt.hour,now_dt.minute)

        if now < sh_list[0]:
            #you must be at the last shift of the previous day
            sh_start=datetime(now_dt.year,
                                now_dt.month,
                                now_dt.day,
                                sh_list[-1].hour,
                                sh_list[-1].minute,
                                0,0)-timedelta(1)
        elif now>sh_list[-1]:
            #you must be in the last shift of today            
            sh_start=datetime(now_dt.year,
                                now_dt.month,
                                now_dt.day,
                                sh_list[-1].hour,
                                sh_list[-1].minute,
                                0,0)
        else:
            #you must be in one of the earlier shifts
            for i in range(len(sh_list)-1):
                aft_beg=now>sh_list[i]
                bef_next_beg=now<sh_list[i+1]
                if aft_beg and bef_next_beg:
                    sh_start=datetime(now_dt.year,
                                      now_dt.month,
                                      now_dt.day,
                                      sh_list[i].hour,
                                      sh_list[i].minute,
                                      0,0)
                    
        #update all the machine objects
        for mach in self.machines:
            self.machines[mach].update(sh_start,self.takt)




        
        
       

        

#####################
##  Machine Class  ##
#####################
class Machine():
    '''class for holding information about each machine

    Attributes:
    name: a string containing the machines name
    ident: a string containing the machinds db ident
    has_changed: a boolean to indicate whether the data has changed since last
        update
    num_cycles: integer of how many cycles have been run this shift
    data: a dict containing the data for this machine
        keys: a string describing the data
        values: a string or int containing the actual data
    '''

    def __init__(self,my_name,my_ident):
        '''inits the machine'''
        self.name=my_name
        self.ident=my_ident #needs to be set up
        self.has_changed=True        
        self.num_cycles=0
        self.data={'Parts Today':0}

    def update(self,shift_start,takt):
        '''a method to update all of the machine's information
    
        Args:
          shift_start: a datetime object for when this shift started
          takt: an int describing the takt time in seconds
        '''

        #get all of the records for this machine since the start of the shift
        data=models.data_log.query.filter(models.data_log.time>shift_start
            ).filter_by(source=self.ident
                ).filter_by(datatype='tool life').all()
        
        #if record is new, re-compute stats, set has_changed
        if len(data) > self.data['Parts Today']:
            self.has_changed=True
            self.data['Parts Today'] = len(data)
            #build array of cycle times
            times=[takt]
            for i in range(1,len(data)):
                td=data[i].time-data[i-1].time
                times.append(td.total_seconds)
            self.data['Avg Cycle']=sum(times)/len(times)
            self.data['St. Dev']=std(times)
            self.data['Last Cycle']=times[-1]               
                
        #if not, set has_changed
        else:
            self.has_changed=False

    def std(nums):
        '''take list of numbers, return st dev'''
        squares=[]
        avg=sum(nums)/len(nums)
        for num in nums:
            squares.append((num-avg)**2)
        sumsq=sum(squares)
        return sumsq**.5    
        

        
                   
if __name__ =='__main__':
    mycell=Cell()
    print(mycell.get_data())





