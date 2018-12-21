import visa
import time
import os
import sys
from numpy import *
import threading
_FINISH = False

#initialization of visa, local variables, paths, etc.
rm = visa.ResourceManager()
rm.list_resources()

e = 1.6*10**(-19) #C
k = 1.381*10**(-23) #J/K

ABSPATH = 'C:\\Users\\student\\Documents\\Slab_3_Drew_Luke_ETE\\Data'
#os.path.join('C:','Users','student','Documents','Slab_3_Drew_Luke_ETE','Data')
FOLDER = '\\Data_12_4\\'
PATH = ABSPATH + FOLDER
#os.path.join(ABSPATH , FOLDER)
IDN = FOLDER[5:-1]

#definitions of functions
def pressure_low(volts):
    P = -0.02585 + 0.03767*volts + 0.04563*volts**2 + 0.1151*volts**3 - 0.04158*volts**4 + 0.008738*volts**5
    return P
def pressure_med(volts):
    a = -.1031
    b = -0.3986
    c = -0.02322
    d = 0.07438
    e = 0.07229
    f = -0.006866
    P = (a + c*volts + e*volts**2)/(1 + b*volts + d*volts**2 + f*volts**3)
    return P
def pressure_high(volts):
    a =  100.624
    b = -0.37679
    c = -20.5623
    d =  0.0348656
    P = (a + c*volts)/(1 + b*volts + d*volts**2)
    return P
def backspace(n):
    print('\r', end='')

def read_oscilloscope():
    inst_0 = 'USB0::0x1AB1::0x0588::DS1ET151205662::INSTR' #Rigol oscilloscope
    device_0 = rm.open_resource(inst_0)
    while True:
        #print("Enter a file name or quite to break:")
        filename = input("Enter a file name or quite to break:")
        if filename == 'quite':
            return False
        else:
            print('The file you chose to write to is' + filename + '\n')
            file = open(PATH + filename + '.txt', 'w')
            file.write("This file holds the data from oscilloscope.\n")
            file.write("Sample\tChannel 1 (V)\tChannel 2 (V)\tTime (s)\n")
            device_0.write(":STOP")
            time_div = float(device_0.query(":TIM:SCAL?"))
            volts_div_1 = float(device_0.query(":CHAN1:SCAL?")[0])
            volts_offset_1 =  float(device_0.query(":CHAN1:OFFS?")[0])
            volts_div_2 = float(device_0.query(":CHAN2:SCAL?")[0])
            volts_offset_2 =  float(device_0.query(":CHAN2:OFFS?")[0])
            time_offset = float(device_0.query(":TIM:OFFS?")[0])
            device_0.write(":WAV:DATA? CAHN1") #Request the data
            wave_data_1 = device_0.read_raw() #Read the block of data
            wave_data_1 = wave_data_1[10:]
            device_0.write(":WAV:DATA? CAHN2") #Request the data
            wave_data_2 = device_0.read_raw() #Read the block of data
            wave_data_2 = wave_data_2[10:]  #Drop the heading
            device_0.write(":RUN")
            time = []
            amplitude_1 = []
            amplitude_2 = []
            for index in range(len(wave_data_1)):
                t = (index - 1) * (time_div / 50) - ((time_div * 6) - time_offset)
                a_1 = ((240 - wave_data_1[index]) * (volts_div_1 / 25) - (volts_offset_1 + volts_div_1 * 4.6))
                a_2 = ((240 - wave_data_2[index]) * (volts_div_2 / 25) - (volts_offset_2 + volts_div_2 * 4.6))
                time.append(t)
                amplitude_1.append(a_1)
                amplitude_2.append(a_2)
            for i in range(len(time)):
                file.write(str(i) + "\t")
                file.write(str(amplitude_1[i])[:8] + "\t")
                file.write(str(amplitude_2[i])[:8] + "\t")
                file.write(str(time[i])[:8] + "\t\n")
            print('Closing {}:\n'.format(filename))
            file.close()
            print('Data from the Rigol was written to' + filename + '\n')
    print('Closing device_0\n')
    device_0.close()
def read_parani():
    i = 0
    t = 0.0
    inst_1 = 'ASRL3::INSTR' #BK precision 2831e 4 1/2 digit multimeter
    device_1 = rm.open_resource(inst_1)
    device_1.timeout = 50000

    #print("Enter a file name:")
    filename = input("Enter a file name:")
    print('The file name you chose is:' + filename + '\n')
    file = open(PATH + filename + '.txt', 'w')
    file.write("This file holds the data about the vacuum chamber.\n")
    file.write("Sample\t\tPressure (mTorr)\tTime (s)\n")
    while t < 21600.0 or _FALSE != True: # shuts off after 6 hrs unless intperupted.
        file.write(str(i) + "\t\t")
        t0 = time.time()
        d = float(device_1.query(":FETC?")[:-1])
        t = time.time() - t0
        volts = d
        if (volts >= 0.375 and volts <= 2.842):
            print(pressure_low(volts),end='')
            backspace(len(str(pressure_low(volts))))
            file.write(str(pressure_low(volts))[:8] + "\t\t")
        elif (volts > 2.842 and volts <= 4.945):
            print(pressure_med(volts),end='')
            backspace(len(str(pressure_med(volts))))
            file.write(str(pressure_med(volts))[:8] + "\t\t")
        elif (volts > 4.945 and volts <= 5.659):
            print(pressure_high(volts),end='')
            backspace(len(str(pressure_high(volts))))
            file.write(str(pressure_high(volts))[:8] + "\t\t")
        else:
            print("NAN",end='')
            backspace(len(s))
            file.write("NAN\t\t")
        #file.write(str(ERPA_Current))
        file.write(str(t)[:8] + "\n")
        i = i + 1
    file.close()
    print('Closing {}:\n'.format(filename))
    device_1.close()
    print('Closing device_1\n')
def main():
    global _FINISH
    t2 = threading.Thread(target = read_parani, args=(None,), name = 'Thread-2')
    t2.start()
    print('Thread-2 has begun\n')
    t1 = threading.Thread(target = read_oscilloscope, args=(None,), name = 'Thread-1')
    t1.start()
    print('Thread-1 has begun\n')
    while True:
        if t1.is_alive() == False:
            print('Thread-1 is no longer alive.\n')
            _FALSE = True
            print('Ending Thread-2.\n')
            t2.join()
            print('Thread-2 has closed.\n')
            #print("Done!\n")
            print("Closing Visa Resource Manager.\n")
            rm.close()
            print("Done!\n")
            return False
        else:
            pass

    print("Main thread Completed")
if __name__ == "__main__":
    main()
