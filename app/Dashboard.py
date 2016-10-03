'''
shotgun cell dashboard

'''
def get_dash_data():
    #imports
    import time
    import tkinter
    from tkinter.constants import *
    from tkinter import font
    from datetime import datetime
    import os.path
    import calendar
    import json


    ##################
    ##  Cell Class  ##
    ##################
    class Cell():
        '''class for holding information about the cell

        Attributes:
        day: an int for the day of the month when this shift started
        log_path: a string containing the path to the relevant logs
        shift: an int for the current shift
        machines: a dict of Machine objects for the cell
        changed: a dict of machine objects that has changed
        end_first: an int for the number of min past midnight when 1st shift ends
        end_second: an int for the number of min past midnight when 2nd shift ends
        takt: an int for the cell's takt time
        goal: an int for the cell's current goal
        '''

        def __init__(self):
            '''inits the cell'''
            
            #read cell config file
            conf_path = '/home/pi/Desktop/server_side/config/'
            with open(conf_path+'cell_conf.txt','r') as conf_file:
                cconf=conf_file.readlines()

            #get cell takt
            self.takt=int(cconf[0])
            
            #get end_first time
            self.end_first = self.midnight(cconf[9])

            #get end_second time
            self.end_second = self.midnight(cconf[17])

            #read cell config file        
            with open(conf_path+'mach_conf.txt','r') as conf_file:
                mconf=conf_file.readlines()

            #create dict of machines
            self.machines={}
            for line in mconf:
                if not line.isspace():
                    mname= line.split(',')[0]
                    self.machines[mname]=Machine(mname,self.takt)
                
            
            #the object is new so everything has changed
            self.changed=self.machines

            #initialize goal
            self.goal=35
            


        def update(self):
            '''update's the cell's attributes'''
            #get current time in minutes past midnight        
            cur_time_obj = datetime.now()
            self.day=cur_time_obj.day
            now = 60*cur_time_obj.hour+cur_time_obj.minute
            
            #determine shift and day
            #if 2nd runs past midnight
            if self.end_second <self.end_first:
                if now>self.end_second and now<self.end_first:
                    self.shift = 1
                else:
                    self.shift=2
                    if now<self.end_second and now<self.end_first:
                        self.day=cur_time_obj.day-1                    
            else: #otherwise
                if now<end_first:
                    self.shift=1
                else:
                    self.shift=2
            
            #check for crossing end of month
            if self.day==0:
                month=cur_time_obj.month-1
                self.day=calendar.monthrange(cur_time_obj.year,month)[1]
            else:
                month=cur_time_obj.month
        
            #assemble log path
            self.log_path = '/home/pi/Desktop/server_side/machine_logs'+'/'+\
                            str(month)+'-'+str(cur_time_obj.year)

            #update machines and assemble changed dict
            self.changed={}
            for machine in self.machines:
                self.machines[machine].update(self.log_path,self.day,self.takt)
                if self.machines[machine].has_changed:
                    self.changed[self.machines[machine].name] = self.machines[machine]

            

        def midnight(self,clocktime):
            '''a method to convert a HH:MM time string into minutes since midnight

            Args:
            clocktime: a string of the format HH:MM or H:MM

            Returns:
            t_since: an int for the number of minutes since midnight that string 
            represents
            '''
            hm = clocktime.split(':')
            t_since = 60*int(hm[0])+int(hm[1])
            return t_since
            


            

    #####################
    ##  Machine Class  ##
    #####################
    class Machine():
        '''class for holding information about each machine

        Attributes:
        name: a string containing the machines name
        last_cycle: an int containing the last cycle time in seconds
        avg_cycle: an int containing the average cycle time that shift
        st_dev: an int containing the standard deviation of the cycle times
        has_changed: a boolean to indicate whether the data has changed since last
            update
        last_entry: string containing last log entry
        num_cycles: integer of how many cycles have been run this shift
        data: a dict containing the data for this machine
            keys: a string describing the data
            values: a string or int containing the actual data
        '''

        def __init__(self,my_name,takt):
            '''inits the machine'''
            self.name=my_name
            self.last_cycle=takt
            self.avg_cycle=takt 
            self.st_dev=0
            self.has_changed=True
            self.last_entry=-1
            self.num_cycles=0
            self.data={}
            self.history=[]

        def update(self,log_path,day,takt):
            '''updates the machine's attributes

            Args:
            log_path: a string for the path where the logs can be found
            day: an int for the day's logs to use
            '''
            
            def t_since(log_entry):
                '''a function to extract the time out of log strings

                Args:
                log_entry: a string comprising a log entry

                Returns:
                time_since: the time of that log in seconds since epoch
                '''
                date_str = log_entry.split(',')[0]
                time_since = calendar.timegm(time.strptime(date_str,
                                                           '%Y-%m-%d %H:%M:%S'))
                return time_since

            #assemble log path
            log_path=log_path+'/'+self.name.upper()+'-'+str(day)+'.txt'
            
            #if log exists, read into memory
            if os.path.isfile(log_path):
                with open(log_path,'r') as log_file:
                    log=log_file.readlines()
            else:
                self.has_changed=False
                print('File does not exist: '+log_path)
                return

            #if new log entries, update parameters
            num_new = len(log)- self.num_cycles
           
            
            if num_new > 0:
                self.has_changed=True
                
                #slice off new entries
                new_entries = log[-1*num_new:]
                #loop through them
                for entry in new_entries:
                    #caclulate last cycle time
                    if self.last_entry ==-1:
                        self.last_cycle=takt
                    else:
                        self.last_cycle = t_since(entry)-self.last_entry
                        self.history.append(self.last_cycle)
                    

                    #update average cycle time
                    self.avg_cycle = int((self.avg_cycle*self.num_cycles
                                      + self.last_cycle)/(self.num_cycles+1))

                    #update standard deviation
                    dev = (self.avg_cycle-self.last_cycle)**2
                    self.st_dev=  int(((self.num_cycles*(self.st_dev**2)
                                   +dev)/(self.num_cycles+1))**.5)
                    

                    #convert to percent

                    #update num_cycles
                    self.num_cycles +=1

                    #update last_entry
                    self.last_entry = t_since(entry)
            else:
                self.has_changed=False

            self.data['Last Cycle']=self.last_cycle
            self.data['Avg Cycle']=self.avg_cycle
            self.data['Parts Today']=self.num_cycles
            self.data['Machine Name']=self.name
            self.data['St. Deviation']=self.st_dev
            return
                   
            


    this_cell=Cell()
    this_cell.update()
    dash_data={}
    for mach in this_cell.machines:
        dash_data[mach.name]={}
        for data_label in mach.data:
            dash_data[mach.name][data_label]=mach.data[data_label]

    return dash_data

