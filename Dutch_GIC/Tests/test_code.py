#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 09:30:14 2019

@author: out
"""
from Dutch_GIC.dutchgic import GIC
import pytest
import os

networkstring='/usr/people/out/Documents/380+220kV_extended' #change to your own location of powergrid csv files

def test_init(tmpdir):
    test=GIC(networkstring,tmpdir,tmpdir)
    assert test.samples == 0
    assert test.date is test.qdate is None
    assert os.path.exists('topo.cpt') is True
    assert os.path.exists(f'{networkstring}/spreadsheettrafo.csv') is True
    assert os.path.exists(f'{networkstring}/spreadsheetcables.csv') is True
    os.system(f'rm -rf {tmpdir}')
    
def test_download(tmpdir):
    test=GIC(networkstring,tmpdir,tmpdir,'31-12-2009')
    test.standard_download(['esk'])
    assert os.path.exists(f'{tmpdir}/31-12-2009/esk20091231dmin.min') is True
    assert os.path.exists(f'{tmpdir}/07-01-2010/esk20100107dmin.min') is True
    test=GIC(networkstring,tmpdir,tmpdir,'1-1-2000')
    test.standard_download(['esk'])
    assert os.path.exists(f'{tmpdir}/01-01-2000/esk20000101dmin.min') is True
    assert os.path.exists(f'{tmpdir}/22-12-1999/esk19991222dmin.min') is True
    assert test.download_data('1','1','2000','esk') is False
    os.system(f'rm -rf {tmpdir}')
           
def test_procedure(tmpdir,tmp_path):
    from Dutch_GIC.dutchgic import GIC
    test=GIC(networkstring,tmpdir,tmp_path,'12-03-1997')
    test.standard_download(['esk','fur'])
    assert test.qdate == "10-03-1997"
    assert os.path.exists(f'{tmpdir}/{test.qdate}') is True
    File=open(f'{test.quietpath}/esk19970310dmin.min','r')
    for counter,line in enumerate(File):
        words=line.split()
        if words[0]=='DATE':
            datastart=counter+2
            for counter2,letters in enumerate(words[3]):
                if counter2==3:
                    if letters=='H':
                        types=False
                        break
                    if letters=='X':
                        types=True
                        break
    assert datastart == 27
    assert types is False
    test.iteratestation()
    assert test.samples == 1440
    assert test.minute is True
    assert os.path.exists(f'{test.respath}/{test.date}/Eskdalemuir_{test.datevar}/allresults.csv') is True
    assert len([name for name in os.listdir(f'{test.respath}/{test.date}/Eskdalemuir_{test.datevar}')]) == 5
    
    statstring=[]
    os.system(f' ls -d {test.respath}/{test.date}/*{test.datevar} > {test.respath}/{test.date}/temp.txt') 
    f=open(f'{test.respath}/{test.date}/temp.txt')
    for item in f:
        item=item.strip('\n')
        statstring.append(item)
    f.close()
    os.system(f'rm {test.respath}/{test.date}/temp.txt')
    assert len(statstring) == 2 
    test.samples=3
    import logging
    import numpy as np
    import threading
    from threading import local
    import pandas as pd
    from multiprocessing import Process
    localvar=threading.local()
    RE=6371000
    
    string=(file for file in os.listdir(test.statpath) if os.path.isfile(os.path.join(test.statpath, file)))
    string=sorted(string) #sort alphabetically, otherwise problems later
    logging.warning(f'Used stations are: {string} \n')
    location=np.zeros((len(string),3))
    location[:,2]=RE
    for counter1,item in enumerate(string):
        File=open(f'{test.statpath}/{item}','r')
        for counter2,line in enumerate(File):
            if counter2==4:
                word=line.split()
                location[counter1,0]=word[2] #latitude
            if counter2==5:
                word=line.split()
                location[counter1,1]=word[2] #longitude 
                break
        File.close()
    string=[]
    os.system(f' ls -d {test.respath}/{test.date}/*{test.datevar} > {test.respath}/{test.date}/temp.txt') 
    f=open(f'{test.respath}/{test.date}/temp.txt')
    for item in f:
        item=item.strip('\n')
        string.append(item)
    string=sorted(string) #sort alphabetically, otherwise problems now
    assert len(string) == 2
    f.close()
    os.system(f'rm {test.respath}/{test.date}/temp.txt')
    try:
        os.mkdir(f'{test.respath}/{test.date}/interpolation')
    except:
        print('Directory is already created, data could be overwritten.')
        logging.info('Directory is already created, data could be overwritten.')
    n=3 #no more than 3 processors at a time for 16GB memory
    nrsteps=int(test.samples/n)
    threads=list()
    for index in range(n):
        q=Process(target=test.magnetic_time, args=(index+1, nrsteps*index, nrsteps*(index+1),location,string,localvar))
        threads.append(q)
        q.start()
    for thread in threads:
        thread.join()
    statstring=[]
    os.system(f' ls {test.respath}/{test.date}/interpolation > {test.respath}/{test.date}/temp.txt') 
    f=open(f'{test.respath}/{test.date}/temp.txt')
    for item in f:
        item=item.strip('\n')
        statstring.append(item)
    f.close()
    os.system(f'rm {test.respath}/{test.date}/temp.txt')
    assert len(statstring) == 6
    f=open(f'{test.respath}/{test.date}/interpolation/{statstring[0]}')
    for counter,item in enumerate(f):
        pass
    assert counter == 14965-1
    parts=item.split()
    assert len(parts) == 3
    localvar=local()

    # import magnetic field data in X/Y-direction (north)
    magnetic_Xfiles=[]
    magnetic_Yfiles=[]
    ############################# get the strings ###################################
    if test.minute==True:
        os.system(f"ls {test.respath}/{test.date}/interpolation/minute_????.csv > {test.respath}/{test.date}/tempX.txt")
        os.system(f"ls {test.respath}/{test.date}/interpolation/minute_????.csv.Y > {test.respath}/{test.date}/tempY.txt")
        f=open(f'{test.respath}/{test.date}/tempX.txt')
        for item in f:
            item=item.strip('\n')
            magnetic_Xfiles.append(item)
        f.close()
        os.system(f'rm {test.respath}/{test.date}/tempX.txt')
        f=open(f'{test.respath}/{test.date}/tempY.txt')
        for item in f:
            item=item.strip('\n')
            magnetic_Yfiles.append(item)
        f.close()
        os.system(f'rm {test.respath}/{test.date}/tempY.txt')
    else:
        for item in range(test.samples//10000+1):
            os.system(f"ls {test.respath}/{test.date}/interpolation/second_{item}????.csv >> {test.respath}/{test.date}/tempX.txt")
            os.system(f"ls {test.respath}/{test.date}/interpolation/second_{item}????.csv.Y >> {test.respath}/{test.date}/tempY.txt")
        f=open(f'{test.respath}/{test.date}/tempX.txt')
        for item in f:
            item=item.strip('\n')
            magnetic_Xfiles.append(item)
        f.close()
        os.system(f'rm {test.respath}/{test.date}/tempX.txt')
        f=open(f'{test.respath}/{test.date}/tempY.txt')
        for item in f:
            item=item.strip('\n')
            magnetic_Yfiles.append(item)
        f.close()
        os.system(f'rm {test.respath}/{test.date}/tempY.txt')

    magnetic_Xfiles=sorted(magnetic_Xfiles) #sort to number 0000-1440 or 86400
    magnetic_Yfiles=sorted(magnetic_Yfiles)
    assert len(magnetic_Xfiles) == len(magnetic_Yfiles) == 3
    for file in magnetic_Xfiles:
        Xfile=pd.read_csv(file, delimiter=' ', header=None)
        break
    for file in magnetic_Yfiles:
        Yfile=pd.read_csv(file, delimiter=' ', header=None)
        break
    assert len(Xfile) == len(Yfile) == 14965
    lat=np.zeros(len(Xfile))
    lon=np.zeros(len(Xfile))
    MX_matrix=np.zeros((len(magnetic_Xfiles),len(Xfile)))#matrix for storing values (vertical same place, horizontal same time)
    MX_parz=np.zeros((3*len(magnetic_Xfiles),len(Xfile)))
    MXft_matrix=np.zeros((int(3*len(magnetic_Xfiles)/2)+1,len(Xfile)),dtype='complex')
    EX_matrix=np.zeros((len(magnetic_Yfiles),len(Yfile)))
    EX_parz=np.zeros((3*len(magnetic_Yfiles),len(Yfile)))
    EXft_matrix=np.zeros((int(3*len(magnetic_Yfiles)/2)+1,len(Yfile)),dtype='complex')
    MY_matrix=np.zeros((len(magnetic_Yfiles),len(Yfile))) #matrix for storing values (vertical same place, horizontal same time)
    MY_parz=np.zeros((3*len(magnetic_Yfiles),len(Yfile)))
    MYft_matrix=np.zeros((int(3*len(magnetic_Yfiles)/2)+1,len(Yfile)),dtype='complex')
    EY_matrix=np.zeros((len(magnetic_Xfiles),len(Xfile)))
    EY_parz=np.zeros((3*len(magnetic_Xfiles),len(Xfile)))
    EYft_matrix=np.zeros((int(3*len(magnetic_Xfiles)/2)+1,len(Xfile)),dtype='complex')
    ################################################################################# 
    ########################### get the values ######################################
    ######################### first x-direction #####################################
    print('setting up matrices!')
    for counter,file in enumerate(magnetic_Xfiles):
        Xfile=pd.read_csv(file, delimiter=' ', header=None)
        values=Xfile.to_numpy()
        MX_matrix[counter,:]=values[:,2]/(10**9)
    lat=values[:,1]
    lon=values[:,0]
    for counter,file in enumerate(magnetic_Yfiles):
        Yfile=pd.read_csv(file, delimiter=' ', header=None)
        values=Yfile.to_numpy()
        MY_matrix[counter,:]=values[:,2]/(10**9)

    ############## start fourier transformation ######################
    print('starting fourier transformation')

# try Parzen window now
    MX_parz[0:len(magnetic_Xfiles),:]=MX_matrix[0,:]
    MX_parz[2*len(magnetic_Xfiles):,:]=MX_matrix[-1,:]
    MX_parz[len(magnetic_Xfiles):2*len(magnetic_Xfiles),:]=MX_matrix
    MY_parz[0:len(magnetic_Yfiles),:]=MY_matrix[0,:]
    MY_parz[2*len(magnetic_Yfiles):,:]=MY_matrix[-1,:]
    MY_parz[len(magnetic_Yfiles):2*len(magnetic_Yfiles),:]=MY_matrix
    assert len(MY_parz) == 3*len(MY_matrix)
    assert len(MX_parz) == 3*len(MX_matrix)
    for column in range(len(MX_matrix[0])):
        MXft_matrix[:,column]=np.fft.rfft(MX_parz[:,column]*test.Parzen(len(MX_parz))) #multiply with hanning window to reduce edge effects
    for column in range(len(MY_matrix[0])):
        MYft_matrix[:,column]=np.fft.rfft(MY_parz[:,column]*test.Parzen(len(MY_parz)))

    ######################### calculate Electric field in frequency direction #############################3
    # make frequencyvector in seconds
    df=1./(3*60.*test.days*3) # seconds! #aangepast
    fmax=1./(2*60.)
    freqvec=np.arange(0,fmax+0.5*df,df) 
    #filter signal for noise
    MXft_matrix=test.filt(freqvec,MXft_matrix)
    MYft_matrix=test.filt(freqvec,MYft_matrix)
    
    # t3_start=process_time() #1d conductivity model!
    for row in range(1,len(MXft_matrix)): #zero is not allowed, same row = same frequency
        EYft_matrix[row,:]=-1*MXft_matrix[row,:]*test.transferfunction(freqvec[row],7)
    for row in range(1,len(MYft_matrix)): #zero is not allowed
        EXft_matrix[row,:]=MYft_matrix[row,:]*test.transferfunction(freqvec[row],7)

    ######################## fourier transform back ####################################
    # t4_start=process_time()
    for column in range(len(EYft_matrix[0])):
        EY_parz[:,column]=np.fft.irfft(EYft_matrix[:,column],9)
    for column in range(len(EXft_matrix[0])):
        EX_parz[:,column]=np.fft.irfft(EXft_matrix[:,column],9)
        
    EX_matrix=EX_parz[len(magnetic_Xfiles):2*len(magnetic_Xfiles),:]
    EY_matrix=EY_parz[len(magnetic_Yfiles):2*len(magnetic_Yfiles),:]
    assert len(EX_matrix) == 3
    assert len(EX_matrix[0]) == 14965
    assert len(EY_matrix) == 3
    assert len(EY_matrix[0]) == 14965
    del MX_matrix, MX_parz, MXft_matrix, EX_parz, EXft_matrix, MY_matrix, MY_parz, MYft_matrix, EY_parz, EYft_matrix
    ######################### writing E field to files #################################
    # t5_start=process_time()
    try:
        os.mkdir(f'{test.respath}/{test.date}/electric_field_east')
    except:
        logging.warning('Directory is already created, data could be overwritten.')
    try:
        os.mkdir(f'{test.respath}/{test.date}/electric_field_north')
    except:
        logging.warning('Directory is already created, data could be overwritten.')

    n=3
    nrsteps=int(test.samples*test.days/n) #aangepast
    threads=list()
    for index in range(n):
        q=Process(target=test.writing_electric, args=(index+1, f'{test.respath}/{test.date}/electric_field_east', EY_matrix, nrsteps*index, nrsteps*(index+1), lon, lat, localvar))
        threads.append(q)
        q.start()
    for thread in threads:
        thread.join()
    assert os.path.exists(f'{test.respath}/{test.date}/electric_field_east/electric_0000.csv') is True
    assert os.path.exists(f'{test.respath}/{test.date}/electric_field_east/electric_0001.csv') is True
    assert os.path.exists(f'{test.respath}/{test.date}/electric_field_east/electric_0002.csv') is True

    threads=list()
    for index in range(n):
        q=Process(target=test.writing_electric, args=(index+1, f'{test.respath}/{test.date}/electric_field_north', EX_matrix, nrsteps*index, nrsteps*(index+1), lon, lat, localvar))
        threads.append(q)
        q.start()
    for thread in threads:
        thread.join()
    assert os.path.exists(f'{test.respath}/{test.date}/electric_field_north/electric_0000.csv') is True
    assert os.path.exists(f'{test.respath}/{test.date}/electric_field_north/electric_0001.csv') is True
    assert os.path.exists(f'{test.respath}/{test.date}/electric_field_north/electric_0002.csv') is True
    
    from multiprocessing import Lock
    lock=Lock()
    netwerk=pd.read_csv(f'{test.netpath}/spreadsheetcables.csv', delimiter = ';')
    coord2=pd.DataFrame(columns=['lon', 'lat'])
    coord1=pd.DataFrame(columns=['lon', 'lat'])
    for line in range(len(netwerk)): # put end locations under start location for gmt, so that you double the lines
        coord1.at[2*line,'lon']=netwerk.at[line,'strtlon'] 
        coord1.at[2*line,'lat']=netwerk.at[line,'strtlat'] 
        coord1.at[2*line+1,'lon']=netwerk.at[line,'eindlon']
        coord1.at[2*line+1,'lat']=netwerk.at[line,'eindlat'] 
        # if statement to spot discontinuities
        if line>0 and coord1.at[2*line-1,'lat']!=coord1.at[2*line,'lat'] and coord1.at[2*line-1,'lon']!=coord1.at[2*line,'lon']:
            coord3=pd.DataFrame([[coord1.at[2*line,'lon'], coord1.at[2*line,'lat']]], columns=['lon', 'lat']) #create new dataframe
            coord1.at[2*line,'lon']='>'+str(coord1.at[2*line,'lon']) #add > for gmt
            coord2=coord2.append(coord1.loc[2*line]) #append it
            coord2=coord2.append(coord3) #append old one, otherwise no line will be drawn
            coord2=coord2.append(coord1.loc[2*line+1]) #append the one after
            del coord3
        else:
            coord2=coord2.append(coord1.loc[2*line])
            coord2=coord2.append(coord1.loc[2*line+1])

    #write to a file with no header and column titles
    coord2.to_csv(path_or_buf=f'{test.netpath}/cables.csv', sep=' ', index=False, header=False)
    
    #################################### first reading in datasets #####################################################  
    try:
        os.mkdir(f'{test.respath}/{test.date}/GIC')
    except:
        logging.warning(f"Directory '{test.respath}/{test.date}/GIC' has already been created, data could be destroyed!")
        print(f"Directory '{test.respath}/{test.date}/GIC' has already been created, data could be destroyed!")
    logging.info('Reading in datasets!')
    Electric_Xfiles=[]
    Electric_Yfiles=[]
    if test.minute:
        os.system(f' ls {test.respath}/{test.date}/electric_field_north/*.csv > {test.respath}/{test.date}/tempX.txt')
        os.system(f' ls {test.respath}/{test.date}/electric_field_east/*.csv > {test.respath}/{test.date}/tempY.txt')
    else:
        for item in range(test.samples//10000+1):
            os.system(f' ls {test.respath}/{test.date}/electric_field_north/electric_{item}????.csv >> {test.respath}/{test.date}/tempX.txt')
            os.system(f' ls {test.respath}/{test.date}/electric_field_east/electric_{item}????.csv >> {test.respath}/{test.date}/tempY.txt')
        
    f=open(f'{test.respath}/{test.date}/tempX.txt')
    for item in f:
        item=item.strip('\n')
        Electric_Xfiles.append(item)
    f.close()
    
    f=open(f'{test.respath}/{test.date}/tempY.txt')
    for item in f:
        item=item.strip('\n')
        Electric_Yfiles.append(item)
    f.close()
    os.system(f'rm {test.respath}/{test.date}/tempX.txt')
    os.system(f'rm {test.respath}/{test.date}/tempY.txt')
    logging.debug('Electric files created!')

    for counter,file in enumerate(Electric_Xfiles):
        Xfile=pd.read_csv(file, delimiter=' ', header=None)
        values=Xfile.to_numpy()
        break
    EX_matrix=np.zeros((len(Electric_Xfiles),len(values)))    
    EY_matrix=np.zeros((len(Electric_Xfiles),len(values)))
    logging.debug('Electric matrices have been made in memory!')

    for counter,file in enumerate(Electric_Xfiles):
        Xfile=pd.read_csv(file, delimiter=' ', header=None)
        values=Xfile.to_numpy()
        EX_matrix[counter,:]=values[:,2]
    logging.debug('EX_matrix has been made!')
    lat=values[:,1]
    lon=values[:,0]
    for counter,file in enumerate(Electric_Yfiles):
        Yfile=pd.read_csv(file, delimiter=' ', header=None)
        values=Yfile.to_numpy()
        EY_matrix[counter,:]=values[:,2]
    del item, f, Xfile, values, Yfile

    ######################################### Getting the needed GIC matrices and code #################################
    logging.info('Starting with the GIC code!')
    kabels=pd.read_csv(test.netpath+'/spreadsheetcables.csv', delimiter = ';')
    trafo=pd.read_csv(test.netpath+'/spreadsheettrafo.csv', delimiter = ';')
    trafo_connect=np.zeros((len(trafo),len(trafo))) #connectivity trafo
    trafo_all_connections=np.zeros((len(trafo),len(kabels))) #connections possible between trafo and every cable
    trafo_cond=np.zeros((len(trafo),len(trafo))) # The conductivity matrix
    station_lat=np.zeros(len(trafo)) #latitude stations in degrees
    station_lon=np.zeros(len(trafo)) #longitude stations in degrees
    ground_cond=np.zeros(len(trafo))
    cable_icon=np.zeros(len(kabels)) # icon array for cable and trafo resp.
    trafo_icon=np.zeros(len(trafo))

    ##### connect trafo and cable number to position in matrix #####
    for line in range(len(kabels)):
        cable_icon[line]=kabels.at[line,'kabelnr']
    for line in range(len(trafo)):
        trafo_icon[line]=trafo.at[line,'trafonr']
    ##### make trafo-trafo connectivity matrix ######
    for line in range(len(trafo)): 
        temp=str(trafo.at[line,'verbonden trafo']) #get right column
        temp=temp.split(",") #split values
        assert type(temp) is list
        for item in temp:
            temp2=int(item)
            trafo_connect[line,np.where(trafo_icon == temp2)[0]]=True #check for connection other trafo
            del temp2
        del temp
    ###### make trafo-cable connectivity matrix ######
    for line in range(len(trafo)):
        temp=str(trafo.at[line,'alle aansluitingen'])
        temp=temp.split(",")
        assert type(temp) is list
        for item in temp:
            temp2=int(item)
            trafo_all_connections[line,np.where(cable_icon == temp2)[0]]=True
            del temp2
        del temp
    ###### make conductivity matrix ######
    for row,line in enumerate(trafo_connect):
        trafo_cond[row,row]=trafo.at[row,'conductivity total']
        for column,item in enumerate(line):
            if item:
                temp=trafo_all_connections[row,:]+trafo_all_connections[column,:]
                temp2=0
                for counter,value in enumerate(temp):
                    if value == 2: # if 2 then we have found the connecting cables
                        temp2+=1/(float(kabels.at[counter,'conductivity'])*kabels.at[counter,'kab/3'])  #because of serieschain we have to add 1/sigma

                trafo_cond[row,column]=-1/temp2 #add cable resistance to off-diagonal
                trafo_cond[row,row]+=1/temp2 #add cable resistance to trace
                del temp, temp2

    ######### get necessary arrays ########
    for item in range(len(trafo)):
        station_lat[item]=trafo.at[item,'lat']
        station_lon[item]=trafo.at[item,'lon']
        ground_cond[item]=trafo.at[item,'conductivity total']

    ############################### Run the function with multiple processors ##########################################
    logging.info('Start multiprocessing!')
    print("New data is added now!")
    n=3
    nrsteps=int(test.samples*test.days/n)
    threads=list()
    for index in range(n):
        q=Process(target=test.GICfunction, args=(index+1,nrsteps*index,nrsteps*(index+1),trafo,EX_matrix,EY_matrix,lat,lon,station_lat,station_lon,trafo_connect,trafo_cond,ground_cond,kabels,trafo_all_connections,80,localvar,lock,False))
        threads.append(q)
        q.start()
    for thread in threads:
        thread.join()
    os.system(f'ls {test.respath}/{test.date}/GIC > {test.respath}/{test.date}/tempgic.txt')
    f=open(f'{test.respath}/{test.date}/tempgic.txt')
    for counter,item in enumerate(f):
        item=item.strip('\n')
        assert os.path.exists(f'{test.respath}/{test.date}/GIC/GIC_000{counter}.csv') is True
    f.close()
    os.system(f'rm {test.respath}/{test.date}/tempgic.txt')
    assert counter == 3-1
    import matplotlib.pyplot as plt
    A=np.arange(3,21)
    B=np.arange(46,54,1)
    stationlist=np.hstack([0,1,A,28,29,32,33,35,43,44,B])
       
    #reading in all GIC files
    if test.minute:
        os.system(f"ls {test.respath}/{test.date}/GIC/GIC_*.csv > {test.respath}/{test.date}/temp.txt")
    else:
        for item in range(test.samples//10000+1):
            os.system(f"ls {test.respath}/{test.date}/GIC/GIC_{item}*.csv >> {test.respath}/{test.date}/temp.txt")
    f=open(f"{test.respath}/{test.date}/temp.txt")
    string=[]

    GIC_data=np.zeros((test.samples*test.days,test.lentrafo))

    for item in f:
        item=item.rstrip('\n')
        string.append(item)
    string=sorted(string)
    for counter,time in enumerate(string):
        GIC_file=pd.read_csv(time, delimiter=';')
        GIC=GIC_file.to_numpy()
        GIC_data[counter]=GIC[:,2]
    assert len(string) == 3
    os.system(f'rm {test.respath}/{test.date}/temp.txt')

    stationframe=pd.read_csv(f'{test.netpath}/spreadsheettrafo.csv', delimiter=';')
    # plot it, per station
    plt.rcParams.update({'font.size': 14}) 
    timevector=np.linspace(0,24*test.days,test.samples*test.days)
    fig1=plt.figure(figsize=(20,15))
    ax1=fig1.add_subplot()
    ax1.set_title(f'GIC during {test.date}')
    ax1.set_ylabel('GIC (A)')
    ax1.set_xlabel('Time (hours)')
    for station in stationlist:
        ax1.plot(timevector,GIC_data[:,station],label=stationframe.at[station,'naam'])
    # plt.subplots_adjust(left=0)
    lgd=ax1.legend(bbox_to_anchor=(1.01,1))
    plt.savefig(f'{test.respath}/{test.date}/GIC_allstations.png', bbox_extra_artists=(lgd,), bbox_inches='tight')
    assert os.path.exists(f'{test.respath}/{test.date}/GIC_allstations.png') is True
    os.system(f'rm -rf {tmpdir}')    
    
def test_GICindex(tmpdir,tmp_path):
    test=GIC(networkstring,tmpdir,tmp_path,'12-03-1997')
    test.standard_download(['esk','fur'])
    test.iteratestation()
    import os
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    g=open(f'{test.respath}/{test.date}/GIC_index.txt','w+')
    maxx=0
    maxy=0
    Xcomp=np.zeros(test.samples*test.days)
    XParz=np.zeros(test.samples*3*test.days)
    GICxft=np.zeros((int(test.samples/2*3*test.days)+1), dtype='complex')
    GICx=np.zeros(test.samples*3*test.days)
    Ycomp=np.zeros(test.samples*test.days)
    YParz=np.zeros(test.samples*3*test.days)
    GICyft=np.zeros((int(test.samples/2*3*test.days)+1), dtype='complex')
    GICy=np.zeros(test.samples*3*test.days)
    df=1/(60*60*24*3.*test.days) # *3 for Parzen window
    if test.minute:
        fmax=1/(2*60.)
    else:
        fmax=1/(2*1)
    freqvector=np.arange(0,fmax+df,df) #create frequency vector
    timevector=np.linspace(0,24*test.days,test.samples*test.days)
    assert len(timevector) == 1440
    figx=plt.figure(figsize=(15,10)) #initialize plotting GICx
    axx=figx.add_subplot()
    axx.set_title('GICx index')
    axx.set_ylabel('GICx')
    axx.set_xlabel('Time (h)')
    axx.axhline(16, linestyle='--', color='green')#, label='5%')
    axx.axhline(43, linestyle='--', color='yellow')#, label='35%')
    axx.axhline(114, linestyle='--', color='orange')#, label='65%')
    axx.axhline(304, linestyle='--', color='red')#, label='95%')
    figy=plt.figure(figsize=(15,10)) #initialize plotting GICy
    axy=figy.add_subplot()
    axy.set_title('GICy index')
    axy.set_ylabel('GICy')
    axy.set_xlabel('Time (h)')
    axy.axhline(39, linestyle='--', color='green')#, label='5%')
    axy.axhline(97, linestyle='--', color='yellow')#, label='35%')
    axy.axhline(241, linestyle='--', color='orange')#, label='65%')
    axy.axhline(600, linestyle='--', color='red')#, label='95%')
#         axx.legend(loc='upper right')
#         axy.legend(loc='upper right')
    
    os.system(f'ls -d {test.respath}/{test.date}/*{test.datevar}/ > {test.respath}/{test.date}/temp.txt') #get location
    f=open(f'{test.respath}/{test.date}/temp.txt')
    string=[]
    for item in f:
        item=item.strip("\n")
        string.append(item)
    string=sorted(string)
    assert len(string) == 2
    f.close()
    os.system(f'rm {test.respath}/{test.date}/temp.txt')
    os.system(f'ls -d {test.statpath}/*min.min > {test.respath}/{test.date}/temp.txt') #get coordinates
    f=open(f'{test.respath}/{test.date}/temp.txt')
    string2=[]
    for item in f:
        item=item.strip("\n")
        string2.append(item)
    string2=sorted(string2)
    assert len(string2) == 2
    lat=np.zeros(len(string2))
    lon=np.zeros(len(string2))
    stat=[]
    for counter2,item in enumerate(string2):
        File=open(item)
        for counter,line in enumerate(File):
            if counter==2:
                words=line.split()
                stat.append(words[2])
            if counter==4:
                words=line.split()
                lat[counter2]=float(words[2]) # latitude station
            if counter==5:
                words=line.split()
                lon[counter2]=float(words[2]) # longitude station
                break
    f.close()
    os.system(f'rm {test.respath}/{test.date}/temp.txt')
    for counter3,station in enumerate(string):
        if test.days==1:
            newfile=pd.read_csv(f'{station}/allresults.csv', delimiter=';')
        else:
            newfile=pd.read_csv(f'{station}/merged_allresults.csv', delimiter=';')
        Xcomp=newfile['B_theta (nt)'].to_numpy()
        Ycomp=newfile['B_phi (nt)'].to_numpy()
        XParz[:test.samples*test.days]=Xcomp[0] #make Parzen vector
        XParz[test.samples*test.days:test.samples*2*test.days]=Xcomp
        XParz[test.samples*2*test.days:]=Xcomp[-1]
        YParz[:test.samples*test.days]=Ycomp[0]
        YParz[test.samples*test.days:test.samples*2*test.days]=Ycomp
        YParz[test.samples*2*test.days:]=Ycomp[-1]
        Xft=np.fft.rfft(XParz*test.Parzen(test.samples*3*test.days)) #fourier transform into frequency domain
        Yft=np.fft.rfft(YParz*test.Parzen(test.samples*3*test.days))

        for counter,freq in enumerate(freqvector):
            GICxft[counter]=Yft[counter]*np.exp(1j*np.pi/4.)*np.sqrt(freq/fmax)
            GICyft[counter]=Xft[counter]*np.exp(1j*np.pi/4.)*np.sqrt(freq/fmax)
        GICx=np.fft.irfft(GICxft)
        GICy=np.fft.irfft(GICyft)

        g.write(f"{lon[counter3]} {lat[counter3]} {max(GICx[test.samples*test.days:test.samples*2*test.days])} {max(GICy[test.samples*test.days:test.samples*2*test.days])} {stat[counter3]}\n")
        axx.plot(timevector,GICx[test.samples*test.days:test.samples*2*test.days],label=f'{stat[counter3]}')
        axy.plot(timevector,GICy[test.samples*test.days:test.samples*2*test.days],label=f'{stat[counter3]}')
        if max(GICx)>maxx:
            maxx=max(GICx)
        if max(GICy)>maxy:
            maxy=max(GICy)
            
    g.close()
    axx.legend()
    axy.legend()
    axx.set_ylim(0,maxx+10)
    axy.set_ylim(0,maxy+10)
    figx.savefig(f'{test.respath}/{test.date}/GICx_index.png')
    figy.savefig(f'{test.respath}/{test.date}/GICy_index.png')
    assert os.path.exists(f'{test.respath}/{test.date}/GICx_index.png')
    assert os.path.exists(f'{test.respath}/{test.date}/GICy_index.png')
    os.system(f'rm -rf {tmpdir}') 