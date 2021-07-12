from __future__ import print_function
from datetime import datetime,timedelta
from time import strftime,sleep

class CryoMeas:
    def __init__(self):
        self.ttime=0
        self.tsample=0
        self.daq_ts=0 # sec Sampling time
        self.buf_size=0 # samples Buffer Size  => 10 s
        self.nplot=0
        self.meas_start=datetime.now()
        self.comment=""
    
    def get_Npoints(self):
        return int(self.ttime*60.0/self.tsample+1)
    
    def get_rate(self):
        return 1.0/self.daq_ts
    
    def get_read_size(self):
        return int(self.get_rate()*self.tsample)
        
    def get_filename(self):
        return self.meas_start.strftime("%Y%m%d_%H%M%S")
    
    def savetxt(self,filepath):
        filename=filepath+self.get_filename()
        with open(filename,'w') as f:
            f.write("# Measurement time (min): {:d}\n".format(self.ttime))
            f.write("# Sampling time (sec): {:d}\n".format(self.tsample))
            f.write("# DAQ sampling time (sec): {:.4f}\n".format(self.daq_ts))
            f.write("# Buffer size (samples): {:d}\n".format(self.buf_size))
            f.write("# Comment: {:s}\n".format(self.comment))