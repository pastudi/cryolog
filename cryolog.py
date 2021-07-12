from __future__ import print_function
import PyDAQmx as daq
import numpy as np
from ctypes import byref
from time import strftime,sleep
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import multiprocessing
import random
from Tkinter import *
from datetime import datetime,timedelta
from CryoMeas import CryoMeas

window=Tk()
filepath="C:/Users/Pablo/Dropbox/Proyectos/03 Mini Operation/05 Mediciones/08 Cryostat/"
meas=CryoMeas()

def main():
    
    global meas,filepath
    
    # General parameters
    meas.ttime=1;       # min
    meas.tsample=1;    # sec
    meas.nplot=1;      # num of samples when data is passed to graphics process
    meas.daq_ts=1e-2    # sec
    meas.buf_size=10000 # 100 sec buffer
    
    #File parameters
    
    # filepath="C:/Users/Pablo/Dropbox/Proyectos/03 Mini Operation/05 Mediciones/08 Cryostat/"
    # filename='run_'+strftime("%Y%m%d-%H%M%S")
    
    meas.savetxt(filepath)
    
    # Memory initialization
    N=meas.get_Npoints()
    
    # Instrument initialization 
    
    q=multiprocessing.Queue()

    acquire_data=multiprocessing.Process(None,data_acquisition,args=(q,meas))
    acquire_data.start()

    plot(N,meas.tsample)

    updateplot(q)

    window.mainloop()

    print('Done')
    # fig.savefig(filepath+"figs/"+meas.get_filename+".png")
    
    acquire_data.join()

def plot(Npoints,tsample):
    global line,ax,canvas,fig
    fig = matplotlib.figure.Figure()
    ax = fig.add_subplot(1,1,1)
    ax.set_xlabel('Time (sec)')
    ax.set_ylabel('Sensor voltage (V)')
    ax.set_title('Pressure curve')
    ax.grid()
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
    canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
    line, = ax.plot(np.linspace(0,Npoints-1,Npoints)*tsample, np.zeros(Npoints))
    canvas.draw()
    # return fig

def updateplot(q):
    global filepath,meas,fig
    # print("Entering updateplot")
    try:
        result=q.get_nowait()

        if result[0] != 'Q':
            # print(result)
            # line.set_ydata(result)
            # line.set_xdata(np.arange(len(result[1])))
            line.set_ydata(result[:,1])
            line.set_xdata(result[:,0])
            ax.set_ylim([min(result[:,1]),max(result[:,1])])
            ax.draw_artist(line)
            canvas.draw()
            # with open(filepath+meas.get_filename(),'a') as f:
                # np.savetxt(f,result)
            window.after(100,updateplot,q)
        else:
            print('Saving figure on: '+filepath+"figs/"+meas.get_filename()+".png")
            fig.savefig(filepath+"figs/"+meas.get_filename()+".png")
            print('Done')
    except:
        # print('Empty')
        window.after(1000,updateplot,q)


def data_acquisition(q,CryoMeas):

    global filepath

    read_size=CryoMeas.get_read_size() # int(rate*tsample) # num of samples to read
    N=CryoMeas.get_Npoints()
    
    analog_input = daq.Task()
    
    # DAQmx Configure Code
    analog_input.CreateAIVoltageChan("Dev1/ai0","",daq.DAQmx_Val_Cfg_Default,-10.0,10.0,daq.DAQmx_Val_Volts,None)
    analog_input.CfgSampClkTiming("",CryoMeas.get_rate(),daq.DAQmx_Val_Rising,daq.DAQmx_Val_ContSamps,CryoMeas.buf_size)
    
    # DAQmx Start Code
    analog_input.StartTask()
    
    read = daq.int32()
    data_daq = np.zeros((read_size,), dtype=np.float64)

    datos=np.zeros([N,2]) # mean read_size*daq_ts seconds
    # ydata=np.zeros(N)     # to plot
    
    # data=[[],[]]

    tstart=CryoMeas.meas_start
    # tactual=tstart

    for i in range(N):
        # datos[i,1]=random.random()+10
        sleep(CryoMeas.tsample)
        analog_input.ReadAnalogF64(read_size,10.0,daq.DAQmx_Val_GroupByChannel,data_daq,1000,byref(read),None)
        # data[0].append(datetime.now()-tstart)
        tlapsed=datetime.now()-tstart
        datos[i,0]=tlapsed.seconds+tlapsed.microseconds*1e-6
        datos[i,1]=np.mean(data_daq)
        # aux=np.mean(data_daq)
        # data[1].append(aux.tolist())
        # ydata[i]=datos[i,1]
        if (i+1)%CryoMeas.nplot==0:
           # print('Sending data to plot process')
           # q.put(ydata[0:i])
           q.put(datos[0:i,])
    
    print("Saving on: "+filepath+CryoMeas.get_filename())
    with open(filepath+CryoMeas.get_filename(),'a') as f:
        np.savetxt(f,datos)
    analog_input.StopTask()
    # np.savetxt(filepath+"data/"+filename,datos,fmt='%.2f',delimiter=',')
    q.put('Q')
    
    print('Acquisition Done')

if __name__ == '__main__':

    main()