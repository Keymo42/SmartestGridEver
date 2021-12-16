import time
import threading
import socket
import json
import datetime
#import mysql.connector
import requests
#import pitop


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
        #self.database = mysql.connector.connect(
        #    host="localhost",
        #    user="root",
        #    password="bmxk2000",
        #    database="smartgriddata"
        #)
        #self.db = self.database.cursor()
        #self.db.execute('truncate wohnblock_raw_data;')
        #self.db.execute('truncate krankenhaus_raw_data;')
        # self.db.execute('select * from central_data;')
        # print(self.db.fetchall())

        # self.lighsensor = pitop.Lightsensor('A0')
        self.lightsensor = {
            'reading': 550
        }
        #self.led_red = pitop.LED('D0')
        self.led_red = {
            'is_lit': False
        }
        #self.led_yellow = pitop.LED('D1')
        self.led_yellow = {
            'is_lit': False
        }
        #self.led_green = pitop.LED('D2')
        self.led_green = {
            'is_lit': True
        }
        #self.potentiometer = pitop.Potentiometer('A1')
        self.potentiometer = {
            'position': 550
        }
        #self.buzzer = pitop.Buzzer('D3')
        self.buzzer = {
            'value': 1
        }
        #self.button = pitop.Button('D4')
        self.button = {
            'is_pressed': True
        }


        self.uhrzeit = datetime.datetime(2069, 1, 1)
        self.waiting_krankenhaus = True
        self.waiting_wohnblock = True
        self.wohnblock_data = None
        self.krankenhaus_data = None

        self.stromspeichermax = 10000 #kW/h
        self.stromspeicher = 10000 #kw/h
        self.stromspeicherProzent = Helper.calculateBatteryPercentage(self.stromspeichermax, self.stromspeicher)
        self.kiloWattPeak = 50 #kw/h
        self.kiloWattPeakSolar = 50 #kW/h
        self.benutzeGas = False
        self.produceGas = False
        self.usage = 50 #kW/h

        self.gasKraftwerk = Gaskraftwerk()

        self.CENTRAL_SERVER = ('0.0.0.0', 8082)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.CENTRAL_SERVER)

        self.wohnblock_adr = ('127.0.0.1', 8083)
        self.krankenhaus_adr = ('127.0.0.1', 8084)

        self.socket.sendto(bytes(json.dumps({
            'sender': 'Server'
        }), 'utf-8'), self.wohnblock_adr)

        self.socket.sendto(bytes(json.dumps({
            'sender': 'Server'
        }), 'utf-8'), self.krankenhaus_adr)

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
            self.wohnblock_enough_energy = True
            self.krankenhaus_enough_energy = True

            self.payload = {}
            self.payload['general'] = {}
            self.payload['central'] = {}

            self.payload['general']['energy_production'] = 0
            self.payload['general']['energy_usage'] = 0
            self.payload['general']['energy_netto'] = 0


            #self.saveRawSensorData(self.wohnblock_data, self.krankenhaus_data)

            print('Es ist', self.uhrzeit, 'Uhr.')


            self.solarPowerInfo = Helper.calculateSolarEnergy(self.uhrzeit.hour)
            self.payload['central']['weather'] = self.solarPowerInfo['Wetter']
            self.payload['central']['solar_production'] = self.solarPowerInfo['Effizienz'] * self.kiloWattPeakSolar
            self.payload['central']['coal_production'] = self.kiloWattPeak
            self.payload['central']['energy_production'] = self.payload['central']['solar_production'] + self.payload['central']['coal_production']
            self.payload['central']['energy_usage'] = self.usage
            self.payload['central']['energy_netto'] = self.payload['central']['energy_production'] - self.payload['central']['energy_usage']

            self.payload['general']['energy_production'] += self.payload['central']['energy_production']
            self.payload['general']['energy_netto'] += self.payload['central']['energy_production'] + self.payload['central']['energy_usage']


            self.stromspeicher += self.payload['central']['energy_netto']


            energy_after_krankenhaus = self.stromspeicher - self.krankenhaus_data['energy_netto']
            if energy_after_krankenhaus < 0:
                self.krankenhaus_enough_energy = False
            else:
                self.stromspeicher = self.stromspeicher - self.krankenhaus_data['energy_netto']

            self.payload['krankenhaus'] = self.krankenhaus_data
            self.payload['general']['energy_production'] += self.krankenhaus_data['energy_production']
            self.payload['general']['energy_usage'] += self.krankenhaus_data['energy_usage']
            self.payload['general']['energy_netto'] += self.krankenhaus_data['energy_netto']


            energy_after_wohnblock = self.stromspeicher - self.wohnblock_data['energy_netto']
            if energy_after_wohnblock < 0:
                self.wohnblock_enough_energy = False
            else:
                self.stromspeicher = self.stromspeicher - self.wohnblock_data['energy_netto']

            self.payload['wohnblock'] = self.wohnblock_data
            self.payload['general']['energy_production'] += self.wohnblock_data['energy_production']
            self.payload['general']['energy_usage'] += self.wohnblock_data['energy_usage']
            self.payload['general']['energy_netto'] += self.wohnblock_data['energy_netto']


            self.stromspeicherProzent = Helper.calculateBatteryPercentage(self.stromspeichermax, self.stromspeicher)


            if self.stromspeicherProzent < 10:
                self.benutzeGas = True
            elif self.benutzeGas and self.stromspeicherProzent >= 100:
                self.benutzeGas = False
            elif  not self.benutzeGas and self.stromspeicherProzent >= 100:
                Gaskraftwerk.convertEnergyToGas(self.stromspeichermax - self.stromspeicher)
                self.stromspeicher = self.stromspeichermax
                self.stromspeicherProzent = 100


            self.payload['GasEnergy'] = {}
            if self.benutzeGas:
                gas = self.gasKraftwerk.use_gas()
                self.stromspeicher += gas.get('energy')
                self.payload['GasEnergy'] = gas



            self.socket.sendto(bytes(json.dumps({
                'enough_energy': self.wohnblock_enough_energy
            }), 'utf-8'), self.wohnblock_adr)

            self.socket.sendto(bytes(json.dumps({
                'enough_energy': self.krankenhaus_enough_energy
            }), 'utf-8'), self.krankenhaus_adr)

            # self.setBatteryLEDStatus()

            print(self.payload)

            move_on = False
            while not move_on:
                try:
                    temp = requests.post(url, json={
                       'data': self.payload
                    })
                finally:
                   print('Connection error')
                if temp:
                    move_on = True
                else:
                    time.sleep(0.1)

            print('Speicher ist: ', self.stromspeicherProzent, '%\n')

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

            # print(data)

            if data['sender'] == 'Wohnblock':
                self.waiting_wohnblock = False
                self.wohnblock_data = data
                # self.wohnblock_adr = adr
            elif data['sender'] == 'Krankenhaus':
                self.waiting_krankenhaus = False
                self.krankenhaus_data = data
                # self.krankenhaus_adr = adr

    def collect_sensor_data(self) -> None:
        self.temp_raw_data = {
            'lightsensor': self.lightsensor['reading'],
            'led_red': self.led_red['is_lit'],
            'led_yellow': self.led_yellow['is_lit'],
            'led_green': self.led_green['is_lit'],
            'potentiometer': self.potentiometer['position'],
            'buzzer': self.buzzer['value'],
            'button': self.button['is_pressed']
        }

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

    def setBatteryLEDStatus(self):
        self.led_red.off()
        self.led_yellow.off()
        self.led_green.off()

        if self.stromspeicherProzent >= 80:
            self.led_green.on()
        elif self.stromspeicherProzent < 80 and self.stromspeicherProzent >= 30:
            self.led_yellow.on()
        else:
            self.led_red.on()



central_py()