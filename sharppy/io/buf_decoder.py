import urllib2
import sys
import numpy as np
from datetime import datetime

class BufkitFile(object):

    def __init__(self, filename):
        self.filename = filename
        self.dates = []
        self.__readFile()
        self.num_profiles = 0

    def __readFile(self):
        # Try to open the file.  This is a dirty hack right now until 
        # I can figure out a cleaner way to make sure the file (either local or URL)
        # gets opened.
        try:
            f = urllib2.urlopen(self.filename)
        except:
            try:
                f = open(self.filename, 'r')
            except:
                print self.filename + " unable to be opened."
                sys.exit()
        data = np.array(f.read().split('\r\n'))
        data_idxs = []
        new_record = False
        begin_idx = 0
        
        # Figure out the indices for the data chunks
        for i in range(len(data)):
            if "STID" in data[i]:
                # Here is information about the record
                spl = data[i].split()
                self.station = spl[2]
                self.wmo_id = spl[5]
                self.dates.append(datetime.strptime(spl[8], '%y%m%d/%H%M'))
                self.slat = float(data[i+1].split()[2])
                self.slon = float(data[i+1].split()[5])
                self.selv = float(data[i+1].split()[8])
                self.stim = float(data[i+2].split()[2])
                print self.stim, self.station
                print data[i]
            if 'CFRL HGHT' in data[i] and new_record == False:
                # we've found a new data chunk
                new_record = True
                begin_idx = i+1
            elif 'STID' in data[i] and new_record == True:
                # We've found the end of the data chunk
                new_record = False
                data_idxs.append((begin_idx, i-1))
            elif 'STN' in data[i] and new_record == True:
                # We've found the end of the last data chunk of the file
                new_record = False
                data_idxs.append((begin_idx, i))
        
        # Make arrays to store the data
        self.profile_length = len(data[data_idxs[0][0]: data_idxs[0][1]])/2
        self.numProfiles = len(self.dates)
        self.hght = np.empty((self.numProfiles, self.profile_length), dtype=float)
        self.pres = np.empty((self.numProfiles, self.profile_length), dtype=float)
        self.tmpc = np.empty((self.numProfiles, self.profile_length), dtype=float)
        self.dwpc = np.empty((self.numProfiles, self.profile_length), dtype=float)
        self.wdir = np.empty((self.numProfiles, self.profile_length), dtype=float)
        self.wspd = np.empty((self.numProfiles, self.profile_length), dtype=float)
        
        # Parse out the profiles
        for i in range(len(data_idxs)):
            data_stuff = data[data_idxs[i][0]: data_idxs[i][1]]
            for j in np.arange(0, self.profile_length*2,2):
                self.hght[i,j/2] = float(data_stuff[j+1].split()[1])
                self.tmpc[i,j/2] = float(data_stuff[j].split()[1])
                self.dwpc[i,j/2] = float(data_stuff[j].split()[3])
                self.pres[i,j/2] = float(data_stuff[j].split()[0])
                self.wspd[i,j/2] = float(data_stuff[j].split()[6])
                self.wdir[i,j/2] = float(data_stuff[j].split()[5])
    
    def getNumProfiles(self):
        return self.numProfiles

    def getProfileLength(self):
        return self.profile_length


#d = BufkitFile('ftp://ftp.meteo.psu.edu/pub/bufkit/namm_p%236.buf')
#d = BufkitFile('ftp://ftp.meteo.psu.edu/pub/bufkit/RAP/15/rap_c34.buf')
#d = BufkitFile('ftp://ftp.meteo.psu.edu/pub/bufkit/HRRR/15/hrrr_c34.buf')
#d = BufkitFile('ftp://ftp.meteo.psu.edu/pub/bufkit/GFS/12/gfs3_c34.buf')
#d = BufkitFile('ftp://ftp.meteo.psu.edu/pub/bufkit/SREF/09/sref_end.buf')
#print d.pres
#print d.hght.shape
#print (d.dates)
