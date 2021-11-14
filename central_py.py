import time
import threading
import socket
import json
from helper import Helper
from Gaskraftwerk import Gaskraftwerk

class central_py:    
    def __init__(self) -> None:
        self.define_variables()

        sensor_thread = threading.Thread(target=self.listen_for_sensors)
        sensor_thread.daemon = True
        sensor_thread.start()

        dayloop_thread = threading.Thread(target=self.day_loop)
        dayloop_thread.daemon = True
        dayloop_thread.start()

        while True:
            time.sleep(1)

        
    def define_variables(self):
        self.uhrzeit = 0        #Start Uhrzeit (In Stundentakten)
        self.effizienzen = [0, 0, 0, 0,
                            0, 0, 0, 0.3,
                            0.4, 0.5, 0.6, 0.7,
                            0.8, 0.7, 0.6, 0.5,
                            0.4, 0.3, 0.2, 0,
                            0, 0, 0, 0] # Faktoren für Effiezienzberechnung
        self.stromspeichermax = 36000 #kW/h
        self.stromspeicher = 10000 #kw/h
        self.stromspeicherProzent = Helper.calculateBatteryPercentage(self.stromspeichermax, self.stromspeicher)
        self.kiloWattPeak = 24 #kw/h
        self.benutzeGas = False
        self.produceGas = False
        self.spent_money = 0
        
        self.gasKraftwerk = Gaskraftwerk()

        self.sensor_values = [
            {
                'name': 'Wohnblock',
                'energy': 30
            },
            {
                'name': 'Krankenhaus',
                'energy': 500
            }
        ]

        UDP_IP = "127.0.0.1"
        UDP_PORT = 8081
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((UDP_IP, UDP_PORT))

    def day_loop(self):
        while True:
            print('Es ist', self.uhrzeit, 'Uhr.')
        

            self.stromspeicher += Helper.calculateEnergy(Helper, self.kiloWattPeak, self.effizienzen[self.uhrzeit])
            self.stromspeicher -= Helper.useEnergy(self.sensor_values)
            self.stromspeicherProzent = Helper.calculateBatteryPercentage(self.stromspeichermax, self.stromspeicher)
            print('Speicher ist: ', self.stromspeicher, self.stromspeicherProzent, '\n')


            if self.stromspeicherProzent < 10:
                self.benutzeGas = True
            elif self.benutzeGas and self.stromspeicherProzent >= 100:
                self.benutzeGas = False


            if self.benutzeGas:
                temp = self.gasKraftwerk.use_gas()
                self.stromspeicher += temp.get('energy')
                self.spent_money += temp.get('bought_gas') * 1






            
            if self.stromspeicher <= 0: #Batteriestand kann nicht negativ sein, sollte nie auftreten
                exit()

            if self.uhrzeit == 23:
                self.uhrzeit = 0
            else:
                self.uhrzeit += 1
            time.sleep(1)

    def listen_for_sensors(self):
        while True:
            data, adr = self.socket.recvfrom(4096)
            data = data.decode('utf-8')
            print(data)



test = central_py()