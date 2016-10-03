def check_cell_info(cell_obj):
    '''
    Function to validate a cell info object before it is allowed into the
    database

    Args:
      cell_obj: an instance of the Cell_info model class

    Returns:
      errs: a string describing the error
            (empty if none)
    '''
    def check_time(time_str,errs):
        '''
        Function to parse and validate a time string

        Args:
          time_str: the time string
          errs: a list containing strings describing the errors

        Returns:
          hr: an int describing the hour
              00 if not valid
          mn: an int describing the minutes
              00 if not valid
          errs: a list with any new errors appended

    '''
        
        if len(time_str)!=5:
            errs.append('Time values must be 5 characters long i.e. HH:MM')
        col=time_str.index(':')
        if col!=2:
            errs.append('The third character of time values must be\
                        a colon i.e. HH:MM')
            
        hr_str=time_str[:col]
        if not hr_str.isdigit():
            errs.append('the fist two characters of time values must be digits')
            hr='00'
        else:
            hr=int(hr_str)
            if hr>23:
                errs.append('hour values must be less than 24')
                
        mn_str=time_str[col+1:]
        if not mn_str.isdigit():
            errs.append('the last two characters of time values must be digits')
            mn='00'
        else:
            mn=int(mn_str)
            if mn>59:
                errs.append('minute values must be less than 60')
        
        return [hr, mn, errs]
        
    errs=[]
    #check takt
    print('checking cell')
    if type(cell_obj.takt)==str:
        if not cell_obj.takt.isdigit():
            errs.append('takt must be an integer')

    hrs=[]
    mns=[]
    #check all times
    for shift in cell_obj.shifts:
        [start_hr, start_mn, errs] = check_time(shift['start'],errs)
        hrs.append(start_hr)
        mns.append(start_mn)
        for brk in shift['breaks']:
            [start_hr, start_mn, errs] = check_time(brk[0],errs)
            hrs.append(start_hr)
            mns.append(start_mn)
            [end_hr, end_mn, errs] = check_time(brk[1],errs)
            hrs.append(end_hr)
            mns.append(end_mn)           
        [start_hr, start_mn, errs] = check_time(shift['end'],errs)
        

    if len(errs)<1:
        failed=False
        for i in range(1,len(hrs)):
            #correct crossing midnight
            same_hr=hrs[i]==hrs[0] and mns[i]<mns[0]
            if hrs[i]<hrs[0] or same_hr:
                hrs[i]+=24

            #check times
            if hrs[i] < hrs[i-1]:
                failed=True
            elif hrs[i] ==hrs[i-1] and mns[i]<mns[i-1]:
                failed=True

        if failed:
            print('err detected')
            errs.append('times are out of order, hour values need \
                    to be on the 24 hr clock')
            

    
    return '<br>'.join(errs)


def check_ignore(usr_str):
    '''fucntion to check the string submitted by the user for the tools to
    ignore, should be in 'T1,T2,T3' format

    Args:
      usr_str: a string that the user put into the form

    Returns:
      scrubbed: a scrubbed string safe to enter into the db
    '''
        
    usr_list=usr_str.split(',')

    output_list=[]
    for item in usr_list:
        tool_num=''
        for char in item:
            if char.isdigit():
                tool_num+=char
        if len(tool_num)>0:
            output_list.append('T'+tool_num)
            
    scrubbed=','.join(output_list)

    return scrubbed
    
    
if __name__=='__main__':
    print(check_ignore('T1,T2,T3'))
    print(check_ignore('t1,t2,t3'))
    print(check_ignore('tool1, tool2, tool3'))
    print(check_ignore('this is 4 times the junk'))
    print(check_ignore('db984fg7rnht 7hn 2'))
