def check_tools(models,debug):
    from sqlalchemy import desc
    from datetime import datetime


    
    #get list of machines
    machs=models.machines.query.all()

    #get ignored toools
    ignored={}
    for mach in machs:
        ignored[mach.name]=mach.ignore.split(',')
    

    #get remaining tool life data for each machine
    remaining={}
    for mach in machs:
        latest=models.data_log.query.filter_by(source=mach.ident).filter_by(
            datatype='tool life').order_by(desc(models.data_log.time)).first()
        remaining[mach.name]={}
        has_data=True
        try:
            tooldata=latest.payload.split('T')
        except AttributeError:
            has_data=True
        if has_data:
            for item in tooldata:
                info =item.split(',')
                if len(info)>=3:
                    toolnum='T'+info[0]
                    if int(info[2]) != 0:
                        rem = int(info[2])-int(info[1])
                        remaining[mach.name][toolnum]= rem
            
    if debug:
        print(remaining)
  

    #get parts to break after next
    #get cell info
    cell=models.cell_info.query.order_by(models.cell_info.id.desc()).first()
            
    #assemble list of work periods as strings
    wrk_prds=[]
    for shift in cell.shifts:
        if len(shift['breaks'])>0:
            wrk_prds.append([shift['start'],shift['breaks'][0][0]])
            for i in range(len(shift['breaks'])-1):
                wrk_prds.append([shift['breaks'][i][1],shift['breaks'][i+1][0]])
            wrk_prds.append([shift['breaks'][-1][1],shift['end']])
        else:
            wrk_prds.append([shift['start'],shift['end']])
    if debug:
        print(wrk_prds)

    #split each string into a list of two string [hr,min]
    wrk_prds2=[]
    for prd in wrk_prds:
        wrk_prds2.append([prd[0].split(':'),prd[1].split(':')])

    #convert into ints
    wrk_prd=[]
    for prd in wrk_prds2:
        if debug:
            print(prd)
        wrk_prd.append([[int(prd[0][0]),int(prd[0][1])],\
                        [int(prd[1][0]),int(prd[1][1])]])

    #if any times are before start of 1st, add 24hrs to them
    for i in range(len(wrk_prd)):
        for j in [0,1]:
            if wrk_prd[i][j][0] < wrk_prd[0][0][0] and \
               wrk_prd[i][j][1] < wrk_prd[0][0][1]:
                wrk_prd[i][j][0] += 24
    if debug:
        print(wrk_prd)

        

    #find remaining time in this work period
    #get current time as a time object
    dtnow = datetime.now()
    now=[dtnow.hour,dtnow.minute]
    if now[0]<wrk_prd[0][0][0] and now[1]<wrk_prd[0][0][1]:
        now[0]+=24

    #find current work period
    cur_prd=0
    for i in range(len(wrk_prd)):
        hr_aft_st=now[0]>=wrk_prd[i][0][0]
        min_aft_st=now[1]>wrk_prd[i][0][1]
        after_start = hr_aft_st and min_aft_st
        #accound for end of final work period
        if i==len(wrk_prd)-1:
            j=i
        else:
            j=i+1
        hr_bf_end=now[0]<=wrk_prd[j][0][0]
        min_bf_end=now[1]<wrk_prd[j][0][1]
        before_end=hr_bf_end and min_bf_end
        if after_start and before_end:
            cur_prd=i
            break

    if debug:
        print('cur_prd: '+str(cur_prd))
        
    #find seconds left in this work period
    hrs_left = wrk_prd[cur_prd][1][0]-now[0]
    mins_left = wrk_prd[cur_prd][1][1]-now[1]
    secs_left=mins_left*60+hrs_left*60*60

    #find time duration of next work period
    hrs_next = wrk_prd[cur_prd+1][1][0]-wrk_prd[cur_prd+1][0][0]
    mins_next = wrk_prd[cur_prd+1][1][1]-wrk_prd[cur_prd+1][0][1]
    secs_next=mins_next*60+hrs_next*60*60
    
    #calculate number of parts until break after next
    num_parts=(secs_left+secs_next)/cell.takt
    if debug:
        print('num_parts: '+str(num_parts))

    to_change={}
    #compare to available tool life
    for mach in remaining:
        tool_needs=''
        for tool in remaining[mach]:
            not_ignored= not tool in ignored[mach]
            needs_changing=remaining[mach][tool]<num_parts
            if needs_changing and not_ignored:
                if len(tool_needs) != 0:
                    tool_needs+=', '
                tool_needs+=str(tool)
        to_change[mach]=tool_needs
    if debug:
        print(to_change)
            

    return to_change
    
