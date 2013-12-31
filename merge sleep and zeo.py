# -*- coding: utf-8 -*-
# <nbformat>2</nbformat>

# <codecell>

import pandas as pd
import copy
import datetime

# <codecell>

import matplotlib.pylab as pylab
pylab.rcParams['figure.figsize'] = 16, 8 

# <markdowncell>

# # Load sleep data

# <codecell>

zeodata = pd.read_csv( 'zeodata.csv' )

# <codecell>

sleepdata = pd.read_csv( 'selfdata.csv' )

# <markdowncell>

# # Clean up self-reported data

# <codecell>

sleepdata.columns

# <codecell>

sleepdata = sleepdata.rename( columns = { 'What time did you go to bed?' : 'BedTime',
       'How long do you think it took you to fall asleep?' : 'MinsToSleep',
       'How many times did you wake up?' : 'TimesAwaken',
       'What time did you wake up for the day?' : 'WakeupTime',
       'How alert did you feel upon waking up?' : 'Alertness',
       "How many times did you hit 'snooze' before starting your tests?" : 'TimesSnooze' } )
                   
                 

# <codecell>

sleepdata

# <codecell>

sleepdata.ix[0]

# <markdowncell>

# ## Create python datetime from timestamp

# <codecell>

def timestamp_to_datetime( timestamp ):
    return datetime.datetime.strptime( timestamp, '%m/%d/%Y %H:%M:%S' )

# <codecell>

sleepdata['DTimestamp'] = sleepdata['Timestamp'].map( lambda ts: timestamp_to_datetime( ts ) )

# <codecell>

sleepdata['DTimestamp'][:10]

# <markdowncell>

# ## Create SleepDate entry to correspond to Zeo data

# <codecell>

def datetime_to_date( dt ):
    timedelta = datetime.timedelta( days=-1 )
    return ( dt + timedelta ).date()

# <codecell>

sleepdata['SleepDate'] = sleepdata['DTimestamp'].map( lambda dt: datetime_to_date( dt ) )

# <codecell>

sleepdata[ ['DTimestamp', 'SleepDate'] ][:10]

# <markdowncell>

# ## Renormalize alertness

# <codecell>

sleepdata['Alertness'] = sleepdata['Alertness'].map( lambda x: x - 4 )

# <codecell>

sleepdata['Alertness'][:10]

# <markdowncell>

# ## Convert BedTime and WakeUpTime to timestamps

# <codecell>

def sleeptime_to_datetime( timestamp, sleeptime, isbed=True ):
    
    def create_time( current, hour, minute ):
        return datetime.datetime.combine( current.date(), datetime.time( hour, minute ) )
   
    if type( sleeptime ) is str:
        strparts = sleeptime.split(':')
        
        if len( strparts ) > 1:
            hour,minute = tuple( [ int( x ) for x in strparts[:-1] ] )
            return create_time( timestamp, hour, minute )
        else:
            sleeptime = int( sleeptime )
        
    hour = 0
    minute = 0 
    previous = False
    
    # is the hour
    if sleeptime < 24:
        hour = sleeptime
        previous = True
    # is the minutes
    elif sleeptime < 100:
        minute = sleeptime
        if not isbed:
            hour = 12
    # normal hour:minute time
    else:
        minute = sleeptime % 100
        hour = int( sleeptime / 100 )
        if isbed and hour == 11:
            hour = 23
        if isbed and hour == 12:
            hour = 0
    
    if previous:
        day_before = datetime.timedelta( days=-1 )
        timestamp = timestamp + day_before
        
    return create_time( timestamp, hour, minute )

# <codecell>

sleepdata['DBedTime'] = [ sleeptime_to_datetime( x,y ) 
for x,y in zip( sleepdata['DTimestamp'], sleepdata['BedTime'] ) ]

# <codecell>

sleepdata['DWakeupTime'] =  [ sleeptime_to_datetime( x,y,False ) 
for x,y in zip( sleepdata['DTimestamp'], sleepdata['WakeupTime'] ) ]

# <codecell>

dt = sleepdata['DWakeupTime'][39]
sleepdata['DWakeupTime'][39] = datetime.datetime( dt.year, dt.month, dt.day, 12, 15 )

# <codecell>

sleepdata[ ['DTimestamp','BedTime','DBedTime','WakeupTime','DWakeupTime'] ]

# <markdowncell>

# # Clean up Zeo data

# <codecell>

zeodata

# <codecell>

print zeodata.ix[0]

# <codecell>

zeodata['SleepDate'] = zeodata['Sleep Date'].map( lambda x: datetime.datetime.strptime( x, '%m/%d/%Y' ).date() )

# <codecell>

zeodata['SleepDate'][:10]

# <markdowncell>

# # Merge data

# <codecell>

mergedata      = pd.merge( sleepdata, zeodata, on='SleepDate' )
mergedata_full = pd.merge( sleepdata, zeodata, on='SleepDate', how='outer' )

# <codecell>

print len( sleepdata ), len( zeodata )

# <codecell>

print len( mergedata ), len( mergedata_full )

# <codecell>

epoch = datetime.datetime(1970,1,1)
dtsecs = mergedata['SleepDate'].map( lambda x: (x - epoch).total_seconds() )
pylab.hold( True )
pylab.plot(  dtsecs, 
            [ x.seconds / 3600. for x in mergedata['DWakeupTime'] - mergedata['DBedTime'] ] )
pylab.plot( mergedata[ 'Total Z' ] / 60. )
#pylab.axis( ymin=0 )
pylab.legend( ( 'self-reported', 'zeo' ) )
pylab.ylabel( 'Hours' )
pylab.hold( False )

# <codecell>

# pylab.plot( mergedata[ 'Total Z' ] / 60., mergedata[ 'Alertness' ], '.' )
# pylab.axis( ymin=-.5, ymax=3.5 )
# pylab.xlabel( 'Hours slept' )
# pylab.ylabel( 'Alertness' )

# # <codecell>

# pylab.plot( mergedata[ 'Total Z' ] / 60., mergedata[ 'TimesSnooze' ], '.' )
# pylab.axis( ymin=-.5, ymax=2.5 )
# pylab.xlabel( 'Hours slept' )
# pylab.ylabel( 'Times snoozed' )

# <codecell>


