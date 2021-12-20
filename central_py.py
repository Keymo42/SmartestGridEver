import time
import threading
import socket
import json
import datetime
import sys
import requests
import pitop
import mysql.connector

from helper import Helper
from Gaskraftwerk import Gaskraftwerk


class CentralPy:
    def __init__(self) -> None:
        self.LOCAL_TEST = False
        if '--test' in sys.argv:
            self.LOCAL_TEST = True


        if self.LOCAL_TEST:
            print('Not connecting to Database')
        else:
            self.database = mysql.connector.connect(
               host="localhost",
               user="root",
               password="smartgrid",
               database="smartgrid_data"
            )
            self.db = self.database.cursor()
            self.db.execute('truncate wohnblock_raw_data;')
            self.db.execute('truncate krankenhaus_raw_data;')
            self.db.execute('truncate central_raw_data;')
            self.db.execute('truncate general_data;')
            self.db.execute('truncate central_data;')
            self.db.execute('truncate wohnblock_data;')
            self.db.execute('truncate krankenhaus_data;')

        self.helper = Helper()
        self.gasKraftwerk = Gaskraftwerk()

        self.define_variables()

        #sensor_thread = threading.Thread(target=self.listen_for_data)
        #sensor_thread.daemon = True
        #sensor_thread.start()

        sensor_thread = threading.Thread(target=self.emergencyBuzzer)
        sensor_thread.daemon = True
        sensor_thread.start()

        dayloop_thread = threading.Thread(target=self.day_loop)
        dayloop_thread.daemon = True
        dayloop_thread.start()

        while True:
           time.sleep(0.01)


    def define_variables(self):
        self.uhrzeit = datetime.datetime(2069, 1, 1)

        self.waiting_krankenhaus = True
        self.waiting_wohnblock = True
        self.wohnblock_data = None
        self.krankenhaus_data = None

        self.stromspeichermax = 300 #kWh
        self.stromspeicher = 250 #kwh
        self.stromspeicherProzent = self.helper.calculateBatteryPercentage(self.stromspeichermax, self.stromspeicher)
        self.kiloWattPeak = 50 #kwh
        self.kiloWattPeakSolar = 4.566 #kW/h
        self.benutzeGas = False
        self.produceGas = False
        self.usage = 2 #kWh
        self.blockCoal = False

        self.loop_counter = 1
        self.energy_production_average = 0
        self.energy_usage_average = 0
        self.energy_netto_average = 0
        self.general_energy_netto_average = 0

        self.setUpSensors()

        self.blockWohnblock = False

        self.SERVER_URL = 'http://localhost:6969/postData'
        self.CENTRAL_SERVER = ('0.0.0.0', 8082)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.CENTRAL_SERVER)

        self.wohnblock_adr = ('172.16.220.249', 8083)
        self.krankenhaus_adr = ('172.16.213.214', 8084)

        if self.LOCAL_TEST:
            self.wohnblock_adr = ('127.0.0.1', 8083)
            self.krankenhaus_adr = ('127.0.0.1', 8084)

        self.socket.sendto(bytes(json.dumps({
            'sender': 'Server'
        }), 'utf-8'), self.wohnblock_adr)

        self.socket.sendto(bytes(json.dumps({
            'sender': 'Server'
        }), 'utf-8'), self.krankenhaus_adr)

    def setUpSensors(self):
        if self.LOCAL_TEST:
            self.lightsensor = {
                'reading': 550
            }

            self.led_red = {
                'is_lit': False
            }

            self.led_yellow = {
                'is_lit': False
            }

            self.led_green = {
                'is_lit': True
            }

            self.potentiometer = {
                'position': 550
            }

            self.buzzer = {
                'value': 1
            }

            self.button = {
                'is_pressed': True
            }

            self.button_led = {
                'is_lit': True
            }
        else:
            self.lightsensor = pitop.LightSensor('A0')      # Acts as a solar panel
            self.led_red = pitop.LED('D0')                  # Lights up when battery below 30%
            self.led_yellow = pitop.LED('D1')               # Lights up when battery above 30% and below 80%
            self.led_green = pitop.LED('D2')                # Lights up when battery above 80%
            self.potentiometer = pitop.Potentiometer('A1')  # Used a multiplier for Energy Usage
            self.buzzer = pitop.Buzzer('D3')                # Beeps when battery below 30%
            self.button = pitop.Button('D4')                # Turns off the coal generator
            self.button_led = pitop.LED('D5')            # Lights up when Button is active

            self.button.when_pressed = self.toggleCoalUsage

    def sendDataToServer(self):
        move_on = False
        while not move_on:
            temp = None
            try:
                temp = requests.post(self.SERVER_URL, json={
                    'data': self.payload
                })
            except:
                print('Connection error')

            if temp is not None:
                move_on = True
            else:
                time.sleep(0.01)

        return

    def setUpPayload(self, solarPowerInfo: dict, energy: dict):
        self.payload = {}
        self.payload['time'] = self.uhrzeit.hour
        self.payload['general'] = {}
        self.payload['central'] = {}

        self.payload['general']['energy_production'] = 0
        self.payload['general']['energy_usage'] = 0
        self.payload['general']['energy_netto'] = 0

        self.payload['central']['weather'] = solarPowerInfo['Wetter']
        self.payload['central']['solar_production'] = solarPowerInfo['Effizienz'] * energy['solar_energy']
        self.payload['central']['coal_production'] = energy['coal_energy']
        self.payload['central']['energy_production'] = self.payload['central']['solar_production'] + \
                                                       self.payload['central']['coal_production']
        self.payload['central']['energy_usage'] = self.usage
        self.payload['central']['energy_netto'] = self.payload['central']['energy_production'] - \
                                                  self.payload['central']['energy_usage']
        self.payload['central']['energy_production_average'] = self.energy_production_average
        self.payload['central']['energy_usage_average'] = self.energy_usage_average
        self.payload['central']['energy_netto_average'] = self.energy_netto_average

        self.payload['general']['energy_production'] += self.payload['central']['energy_production']
        self.payload['general']['energy_netto'] += (
                    self.payload['central']['energy_production'] - self.payload['central']['energy_usage'])
        self.payload['general']['energy_netto_average'] = self.general_energy_netto_average

    def useGridEnergy(self):
        energy_after_krankenhaus = self.stromspeicher - self.krankenhaus_data['energy_netto']
        if energy_after_krankenhaus <= 0:
            self.krankenhaus_enough_energy = False
            self.stromspeicher += self.krankenhaus_data['energy_production']
            self.krankenhaus_data['energy_usage'] = 0
            self.krankenhaus_data['energy_netto'] = self.krankenhaus_data['energy_production']
        else:
            self.stromspeicher = self.stromspeicher + self.krankenhaus_data['energy_netto']

        self.payload['krankenhaus'] = self.krankenhaus_data
        self.payload['general']['energy_production'] += self.krankenhaus_data['energy_production']
        self.payload['general']['energy_usage'] += self.krankenhaus_data['energy_usage']
        self.payload['general']['energy_netto'] += self.krankenhaus_data['energy_netto']

        energy_after_wohnblock = self.stromspeicher - self.wohnblock_data['energy_netto']
        if energy_after_wohnblock < 0 or self.blockWohnblock:
            self.wohnblock_enough_energy = False
            self.stromspeicher += self.wohnblock_data['energy_production']
            self.wohnblock_data['energy_usage'] = 0
            self.wohnblock_data['energy_netto'] = self.wohnblock_data['energy_production']
        else:
            self.stromspeicher = self.stromspeicher + self.wohnblock_data['energy_netto']

        self.payload['wohnblock'] = self.wohnblock_data
        self.payload['general']['energy_production'] += self.wohnblock_data['energy_production']
        self.payload['general']['energy_usage'] += self.wohnblock_data['energy_usage']
        self.payload['general']['energy_netto'] += self.wohnblock_data['energy_netto']

    def useGasEnergy(self):
        self.payload['GasEnergy'] = {}
        if self.benutzeGas:
            gas = self.gasKraftwerk.use_gas()
            self.stromspeicher += gas['energy']
            self.payload['GasEnergy'] = gas

    def day_loop(self):
        while True:
            print('Krankenhaus:', self.waiting_krankenhaus)
            print('Wohnblock:', self.waiting_wohnblock)
            while self.waiting_wohnblock or self.waiting_krankenhaus:
                time.sleep(0.01)
                data, adr = self.socket.recvfrom(4096)
                data = data.decode('utf-8')
                data = json.loads(data)

                if self.waiting_wohnblock and data['sender'] == 'Wohnblock':
                    self.waiting_wohnblock = False
                    self.wohnblock_data = data
                elif self.waiting_krankenhaus and data['sender'] == 'Krankenhaus':
                    self.waiting_krankenhaus = False
                    self.krankenhaus_data = data

            self.waiting_wohnblock = True
            self.waiting_krankenhaus = True
            self.wohnblock_enough_energy = True
            self.krankenhaus_enough_energy = True

            self.collect_sensor_data()

            print('Es ist', self.uhrzeit, 'Uhr.')

            solarPowerInfo = self.helper.calculateSolarEnergy(self.uhrzeit.hour)
            energy = self.calc_power()
            self.energy_production_average = (self.energy_production_average + (
                        energy['coal_energy'] + (solarPowerInfo['Effizienz'] * energy['solar_energy']))) / self.loop_counter
            self.energy_usage_average = (self.energy_usage_average + self.usage) / self.loop_counter
            self.energy_netto_average = (self.energy_netto_average + ((
                        energy['coal_energy'] + (solarPowerInfo['Effizienz'] * energy['solar_energy'])) - self.usage)) / self.loop_counter
            self.general_energy_netto_average = (self.general_energy_netto_average + (self.energy_netto_average + self.krankenhaus_data['energy_netto'] + self.wohnblock_data['energy_netto'])) / self.loop_counter

            self.setUpPayload(solarPowerInfo, energy)
            self.stromspeicher += self.payload['central']['energy_netto']

            self.useGridEnergy()

            self.stromspeicherProzent = self.helper.calculateBatteryPercentage(self.stromspeichermax, self.stromspeicher)

            if self.stromspeicherProzent < 10:
                self.benutzeGas = True
            elif self.benutzeGas and self.stromspeicherProzent >= 100:
                self.benutzeGas = False

            self.useGasEnergy()

            if self.stromspeicherProzent >= 100:
                self.gasKraftwerk.convertEnergyToGas(self.stromspeichermax - self.stromspeicher)
                self.stromspeicher = self.stromspeichermax
                self.stromspeicherProzent = 100

            if self.stromspeicherProzent < 30:
                self.blockWohnblock = True
            else:
                self.blockWohnblock = False

            self.payload['general']['stromspeicher_prozent'] = self.stromspeicherProzent
            self.payload['general']['stromspeicher'] = self.stromspeicher


            self.socket.sendto(bytes(json.dumps({
                'enough_energy': self.wohnblock_enough_energy
            }), 'utf-8'), self.wohnblock_adr)

            self.socket.sendto(bytes(json.dumps({
                'enough_energy': self.krankenhaus_enough_energy
            }), 'utf-8'), self.krankenhaus_adr)

            if self.LOCAL_TEST:
                print('Not using LEDs')
            else:
                self.setBatteryLEDStatus()

            self.sendDataToServer()
            if self.LOCAL_TEST:
                print('Not saving Data')
            else:
                self.saveRawSensorData(self.wohnblock_data, self.krankenhaus_data)
                self.saveData(self.payload)

            print(self.payload)
            print('Speicher ist: ', self.stromspeicherProzent, '%\n')

            if self.stromspeicher <= 0: #Batteriestand kann nicht negativ sein, sollte nie auftreten
                exit()

            self.uhrzeit = self.uhrzeit + datetime.timedelta(hours=1)
            self.loop_counter += 1
            time.sleep(1)

    def listen_for_data(self):
        while True:
            time.sleep(0.01)
            data, adr = self.socket.recvfrom(4096)
            data = data.decode('utf-8')
            data = json.loads(data)

            if self.waiting_wohnblock and data['sender'] == 'Wohnblock':
                self.waiting_wohnblock = False
                self.wohnblock_data = data
            elif self.waiting_krankenhaus and data['sender'] == 'Krankenhaus':
                self.waiting_krankenhaus = False
                self.krankenhaus_data = data

    def calc_power(self):
        if self.LOCAL_TEST:
            lightsensor_value = self.lightsensor['reading']
            potentiometer_value = self.potentiometer['position']
        else:
            lightsensor_value = self.lightsensor.reading
            potentiometer_value = self.potentiometer.position

        poweruse = 1.0  # Multiplikator
        solar_energy = 0
        coal_energy = 0
        energy_sum = 0

        solar_cells_default = 450
        solar_energy = (poweruse * (lightsensor_value / solar_cells_default)) * self.kiloWattPeakSolar
        energy_sum += solar_energy

        potentiometer_default = 450
        if not self.blockCoal:
            coal_energy = (poweruse * (potentiometer_value / potentiometer_default)) * self.kiloWattPeak
            energy_sum += coal_energy

        return {
            'sum': energy_sum,
            'solar_energy': solar_energy,
            'coal_energy': coal_energy
        }

    def collect_sensor_data(self) -> None:
        if self.LOCAL_TEST:
            self.temp_raw_data = {
                'lightsensor': self.lightsensor['reading'],
                'led_red': self.led_red['is_lit'],
                'led_yellow': self.led_yellow['is_lit'],
                'led_green': self.led_green['is_lit'],
                'potentiometer': self.potentiometer['position'],
                'buzzer': self.buzzer['value'],
                'button': self.button['is_pressed'],
                'button_led': self.button_led['is_lit']
            }
        else:
            self.temp_raw_data = {
                'lightsensor': self.lightsensor.reading,
                'led_red': self.led_red.is_lit,
                'led_yellow': self.led_yellow.is_lit,
                'led_green': self.led_green.is_lit,
                'potentiometer': self.potentiometer.position,
                'buzzer': self.buzzer.value,
                'button': self.button.is_pressed,
                'button_led': self.button_led.is_lit
            }

    def saveRawSensorData(self, wohnblock: dict, krankenhaus: dict) -> None:
        central = self.temp_raw_data

        if central is not None:
            query = 'insert into central_raw_data (time, lightsensor, led_red, led_yellow, led_green, potentiometer, buzzer, button, button_led) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
            values = (self.uhrzeit, central['lightsensor'], central['led_red'], central['led_yellow'], central['led_green'], central['potentiometer'], central['buzzer'], central['button'], central['button_led'])
            self.db.execute(query, values)

        if wohnblock is not None:
            wohnblock = wohnblock.get('raw_data')
            query = 'insert into wohnblock_raw_data (time, led_red, led_green, lightsensor, potentiometer, button, button_led) VALUES(%s, %s, %s, %s, %s, %s, %s)'
            values = (self.uhrzeit, wohnblock['led_red'], wohnblock['led_green'], wohnblock['lightsensor'], wohnblock['potentiometer'], wohnblock['button'], wohnblock['button_led'])
            self.db.execute(query, values)

        if krankenhaus is not None:
            krankenhaus = krankenhaus.get('raw_data')
            query = 'insert into krankenhaus_raw_data (time, lightsensor, potentiometer, button, button_led) VALUES(%s, %s, %s, %s, %s)'
            values = (self.uhrzeit, krankenhaus['lightsensor'], krankenhaus['potentiometer'], krankenhaus['button'], krankenhaus['button_led'])
            self.db.execute(query, values)

        self.database.commit()

    def saveData(self, payload: dict):
        query = 'insert into general_data (time, stromspeicher, stromspeicher_prozent, energy_usage, energy_production, energy_netto, energy_netto_average) VALUES(%s, %s, %s, %s, %s, %s, %s)'
        values = (self.uhrzeit,
                  payload['general']['stromspeicher'],
                  payload['general']['stromspeicher_prozent'],
                  payload['general']['energy_usage'],
                  payload['general']['energy_production'],
                  payload['general']['energy_netto'],
                  payload['general']['energy_netto_average']
        )
        self.db.execute(query, values)


        query = 'insert into central_data (time, coal_production, energy_netto, energy_netto_average,' \
                'energy_production, energy_production_average, energy_usage, energy_usage_average, solar_production, weather)' \
                'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        values = (self.uhrzeit,
                  payload['central']['coal_production'],
                  payload['central']['energy_netto'],
                  payload['central']['energy_netto_average'],
                  payload['central']['energy_production'],
                  payload['central']['energy_production_average'],
                  payload['central']['energy_usage'],
                  payload['central']['energy_usage_average'],
                  payload['central']['solar_production'],
                  payload['central']['weather']
        )
        self.db.execute(query, values)


        query = 'insert into wohnblock_data (time, energy_netto, energy_netto_average, energy_production,' \
                'energy_production_average, energy_usage, energy_usage_average, weather)' \
                'VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
        values = (
            self.uhrzeit,
            payload['wohnblock']['energy_netto'],
            payload['wohnblock']['energy_netto_average'],
            payload['wohnblock']['energy_production'],
            payload['wohnblock']['energy_production_average'],
            payload['wohnblock']['energy_usage'],
            payload['wohnblock']['energy_usage_average'],
            payload['wohnblock']['weather']
        )
        self.db.execute(query, values)


        query = 'insert krankenhaus_data (time, energy_netto, energy_netto_average, energy_production,' \
                'energy_production_average, energy_usage, energy_usage_average, weather)' \
                'VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
        values = (
            self.uhrzeit,
            payload['krankenhaus']['energy_netto'],
            payload['krankenhaus']['energy_netto_average'],
            payload['krankenhaus']['energy_production'],
            payload['krankenhaus']['energy_production_average'],
            payload['krankenhaus']['energy_usage'],
            payload['krankenhaus']['energy_usage_average'],
            payload['krankenhaus']['weather']
        )
        self.db.execute(query, values)

    def setBatteryLEDStatus(self):
        self.led_red.off()
        self.led_yellow.off()
        self.led_green.off()

        if self.stromspeicherProzent >= 80:
            self.led_green.on()
            self.buzzer.off()
        elif self.stromspeicherProzent < 80 and self.stromspeicherProzent >= 30:
            self.led_yellow.on()
            self.buzzer.off()
        else:
            self.led_red.on()
            self.buzzer.on()

    def emergencyBuzzer(self):
        buzzer_on = False
        while True:
            time.sleep(0.01)
            if not self.LOCAL_TEST:
                if self.stromspeicherProzent < 20:
                    self.buzzer.on()
                    buzzer_on = True
                else:
                    self.buzzer.off()
                    buzzer_on = False

            if buzzer_on:
                time.sleep(1)
            else:
                time.sleep(1)

    def toggleCoalUsage(self):
        self.blockCoal = not self.blockCoal




CentralPy()