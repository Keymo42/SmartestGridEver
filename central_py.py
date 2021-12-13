import time
import threading
import socket
import json
import datetime
import mysql.connector
import requests

url = 'http://localhost:6969/postData'

from helper import Helper
from Gaskraftwerk import Gaskraftwerk

class central_py:    
    def __init__(self) -> None:
        self.define_variables()

        sensor_thread = threading.Thread(target=self.listen_for_data)
        sensor_thread.daemon = True
        sensor_thread.start()

        dayloop_thread = threading.Thread(target=self.day_loop)
        dayloop_thread.daemon = True
        dayloop_thread.start()

        while True:
            time.sleep(1)

        
    def define_variables(self):
        self.database = mysql.connector.connect(
            host="localhost",
            user="root",
            password="bmxk2000",
            database="smartgriddata"
        )
        self.db = self.database.cursor()
        self.db.execute('truncate wohnblock_raw_data;')
        self.db.execute('truncate krankenhaus_raw_data;')
        # self.db.execute('select * from central_data;')
        # print(self.db.fetchall())


        self.uhrzeit = datetime.datetime(2069, 1, 1)
        self.waiting_krankenhaus = True
        self.waiting_wohnblock = True
        self.wohnblock_data = None
        self.krankenhaus_data = None
        self.effizienzen = [0, 0, 0, 0,
                            0, 0, 0, 0.3,
                            0.4, 0.5, 0.6, 0.7,
                            0.8, 0.7, 0.6, 0.5,
                            0.4, 0.3, 0.2, 0,
                            0, 0, 0, 0] # Faktoren für Effiezienzberechnung
        self.stromspeichermax = 10000 #kW/h
        self.stromspeicher = 10000 #kw/h
        self.stromspeicherProzent = Helper.calculateBatteryPercentage(self.stromspeichermax, self.stromspeicher)
        self.kiloWattPeak = 0 #kw/h
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
        UDP_PORT = 8082
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((UDP_IP, UDP_PORT))

    def day_loop(self):
        while True:
            print('Krankenhaus:')
            print(self.waiting_krankenhaus)
            print('Wohnblock:')
            print(self.waiting_wohnblock)
            if self.waiting_wohnblock or self.waiting_krankenhaus:
                time.sleep(0.1)
                continue

            self.waiting_wohnblock = True
            self.waiting_krankenhaus = True


            self.saveRawSensorData(self.wohnblock_data, self.krankenhaus_data)

            print('Es ist', self.uhrzeit, 'Uhr.')

            self.stromspeicher += Helper.calculateEnergy(Helper, self.kiloWattPeak, self.effizienzen[self.uhrzeit.hour])
            self.stromspeicher -= Helper.useEnergy(Helper, self.sensor_values)
            self.stromspeicherProzent = Helper.calculateBatteryPercentage(self.stromspeichermax, self.stromspeicher)
            print('Speicher ist: ', self.stromspeicherProzent, '%\n')


            if self.stromspeicherProzent < 10:
                self.benutzeGas = True
            elif self.benutzeGas and self.stromspeicherProzent >= 100:
                self.benutzeGas = False


            if self.benutzeGas:
                temp = self.gasKraftwerk.use_gas()
                self.stromspeicher += temp.get('energy')
                self.spent_money += temp.get('bought_gas') * 1

            self.socket.sendto(bytes(json.dumps({
                'enough_energy': True
            }), 'utf-8'), ("127.0.0.1", 8083))

            self.socket.sendto(bytes(json.dumps({
                'enough_energy': True
            }), 'utf-8'), ("127.0.0.1", 8084))

            move_on = False
            while not move_on:
                print('Test')
                try:
                    temp = requests.post(url, json={
                        'time': self.uhrzeit.hour,
                        'energy': self.stromspeicher
                    })
                finally:
                    print('Connection error')
                print(temp.content)
                if temp:
                    move_on = True
                else:
                    print('Wait')
                    time.sleep(0.1)
                print(move_on)

            
            if self.stromspeicher <= 0: #Batteriestand kann nicht negativ sein, sollte nie auftreten
                exit()



            self.uhrzeit = self.uhrzeit + datetime.timedelta(hours=1)
            time.sleep(1)

    def listen_for_data(self):
        while True:
            time.sleep(0.1)
            data, adr = self.socket.recvfrom(4096)
            data = data.decode('utf-8')
            data = json.loads(data)

            print(data['sender'])

            if data['sender'] == 'Wohnblock':
                self.waiting_wohnblock = False
                print('Should be False now Wohnblock')
                self.wohnblock_data = data
            elif data['sender'] == 'Krankenhaus':
                self.waiting_krankenhaus = False
                print('Should be False now Krankenhaus')
                self.krankenhaus_data = data

    def saveRawSensorData(self, wohnblock: dict, krankenhaus: dict) -> None:
        if wohnblock is not None:
            wohnblock = wohnblock.get('raw_data')
            query = 'insert into wohnblock_raw_data (time, extra_power_switch, lightsensor, potentiometer) VALUES (%s, %s, %s, %s);'
            values = (self.uhrzeit, wohnblock['extra_power_switch_on'], wohnblock['light_sensor'], wohnblock['potentiometer'])
            self.db.execute(query, values)

        if krankenhaus is not None:
            krankenhaus = krankenhaus.get('raw_data')
            query = 'insert into krankenhaus_raw_data (test, extra_power_switch, lightsensor, potentiometer, test_label) VALUES (%s, %s, %s, %s, %s);'
            values = (self.uhrzeit, krankenhaus['extra_power_switch_on'], krankenhaus['light_sensor'], krankenhaus['potentiometer'],
                      # (str(self.uhrzeit.hour) + ':' + str(self.uhrzeit.year) + ',' + str(self.uhrzeit.month) + ',' + str(self.uhrzeit.day)))
                      self.uhrzeit.hour)
            self.db.execute(query, values)

        self.database.commit()


central_py()