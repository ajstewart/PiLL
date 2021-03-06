#!/usr/bin/python 
import pyrap.tables as pt 
import sys
import math

# on the offline cluster if you are in c ot tcsh type: 
# use Casa; use Pythonlibs; use LofIm; use Casacore

# Run this program as python split_ms_by_time.py
# or Run it as ./split_ms_by_time.py if the script is executable
# Pandey:v0.0:May2010 contact: pandey@astro.rug.nl
# edited for PiLL by A. Drabent alex@tls-tautenburg.de

####### START USER ENTRY #########
# Enter the correct input and output table names below
tablename = sys.argv[1]  # define input MS-file
outputname = sys.argv[2] # define output MS-file
chunksize  = float(sys.argv[3])

# Please Enter the start and end times in hours for the output measrement set 
#     relative to the start of input measurement set
# for example start = 1.0 means output measurement set will start, 1 hour from 
#     the start of input MS
# end = 3.0 will mean that output MS will stop 3 hours from the start of 
#    INPUT MS
# So output MS will have 2 hours of data in such a case

####### END USER ENTRY #########

print '###############################################'

t = pt.table(tablename)

starttime = t[0]['TIME']
endtime   = t[t.nrows()-1]['TIME']
chunks    = int((endtime-starttime)/(3600. * chunksize))
chunks    = 1 if chunks < 1 else chunks
zeros     = int(math.log10(chunks)) + 1

print '====================='

print 'Input Measurement Set is '+tablename
print 'Start time (sec) = '+str(starttime)
print 'End time   (sec) = '+str(endtime)
print 'Total time duration (hrs)  = '+str((endtime-starttime)/3600)

for chunk in range(chunks + 1):

	directory  = '/'.join(outputname.split('/')[:-1]) + '/'
	filename   = outputname.split('/')[-1]
	outputfile = directory + '.'.join(filename.split('.')[:-1]) + '_TC' + str(chunk).zfill(zeros) + '.' + filename.split('.')[-1]
	
	start_out = chunk * chunksize  # hour to start
	end_out   = chunk * chunksize + chunksize # hour to end
	
	print '====================='
	print 'Output Measurement Set is '+outputfile
	print 'Start time = '+str(start_out)
	print 'End time   = '+str(end_out)
	print 'Total time duration (hrs)  = '+str(end_out - start_out)

	print '====================='

	print 'Now going to do the query to select the required time range'

	t1 = t.query('TIME > ' + str(starttime+start_out*3600) + ' && TIME < ' + str(starttime+end_out*3600), sortlist='TIME,ANTENNA1,ANTENNA2')

	print 'Total rows in input MS  = '+str(t.nrows())
	print 'Total rows in output MS = '+str(t1.nrows())

	print 'Now writing the output MS'
	t1.copy(outputfile, True)
	t1.close()
	
	pass

t.close()
print 'Copying completed... Thanks for using the script! '
print '###############################################'