import serial
import os
import glob
import sys
import time
import datetime

N_ITEMS_PER_LINE = 4 # data sent through by the Arduino 

class SerialManager():

    def __init__(self):

        if sys.platform.startswith('win'):
                ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
                # this is to exclude your current terminal "/dev/tty"
                ports = glob.glob('/dev/ttyACM*')

        elif sys.platform.startswith('darwin'):
                ports = glob.glob('/dev/tty.usb*')

        else:
                raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
                try:
                        s = serial.Serial(port)
                        s.close()
                        result.append(port)
                except (OSError, serial.SerialException):
                        pass

        if len(result) > 1:
                print ('Too many ports, select one manually')
                currentNumber = 1
                for port in result:
                    print (str(currentNumber) + ' ' + str(port))
                    currentNumber+=1
                portNumber = int( input('port number?'))
                result = [result[portNumber-1]]
        if len(result) < 1:
                print ('No ports found')
                exit(0)
        if len(result) is 1:
                print ('Found serial port: ', result)

        strPort = result[0]
        print ('Found serial port: ', result)
        print ('Connecting...')

        try:
                self.ser = serial.Serial(strPort, 19200)
        except:
                print ('Unable to connect to the Arduino via Serial')
                exit(1)

        # wait for port to open
        while self.ser.isOpen() == 0:
                print ('...')
                time.sleep(1)
        time.sleep(2)

        self.recordData = False

        print ('Connected!')

    def startDataCapture(self):
        global storeDir
        print ('starting data capture')
        
        #send begin packet
        self.ser.write(b"b")  
        self.recordData = True

        #preinit storage of data
        data = []
        for x in range(0, N_ITEMS_PER_LINE): # this will basically be a0,a1,a2,a3,a4a5
            data.append( [] )

        i = 0
        try:
            while(True):
                if (i % 100) == 0:
                    print (i)
            
                line = self.ser.readline()
                print (line) 
                splitLine = [int(val) for val in line.split()]
                if(len(splitLine) == N_ITEMS_PER_LINE):
                        for x in range(0, N_ITEMS_PER_LINE):
                            data[x].append(splitLine[x])
                        i += 1
                #else:
                #	print 'bad data'
        except KeyboardInterrupt:
            self.ser.write(b"s")  

            #save data to file
            ts = time.time()
            filename = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d %H_%M_%S')

            if storeDir != '':
                f = open(os.path.join(storeDir, filename), 'w')
            else:
                f = open(filename, 'w')

            for i in range(0, len(data[0])): #samples
                for x in range(0, N_ITEMS_PER_LINE): #sensor number
                    f.write(str(data[x][i]))
                    f.write(' ')
                f.write('\n')
            f.close()

            sys.exit()

        #socket.sendto(data.upper(), self.client_address)

if __name__ == "__main__":

    newgest = False
    
    storeDir = ''
    
    try:
        storeDir = sys.argv[1]
        if not os.path.exists(storeDir):
            os.makedirs(storeDir)
    except:
        print ('Using current directory')



    SM = SerialManager()
    SM.startDataCapture()

