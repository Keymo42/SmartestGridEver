import time
import threading
import socket
import json
import datetime
#import pitop
from helper import Helper


class WohnBlock:
    def __init__(self) -> None:
        self.define_variables()

        self.found_server = False
        while self.found_server is False:
            self.get_server_ip()

        sensor_thread = threading.Thread(target=self.listen_for_sensors)
        sensor_thread.daemon = True
        sensor_thread.start()

        dayloop_thread = threading.Thread(target=self.day_loop)
        dayloop_thread.daemon = True
        dayloop_thread.start()

        while True:
            time.sleep(1)

    def define_variables(self):
        self.uhrzeit = datetime.datetime(2069, 1, 1)
        self.kiloWattPeakSolar = 50  # kW/h
        self.powerUsage = 50  # kW/h

        # Define Sensors and Actors
        self.temp_raw_data = {}
        self.waiting = False

        # self.led_red = pitop.LED('D0')
        self.led_red = {
            'is_lit': False
        }
        # self.led_green = pitop.LED('D2')
        self.led_green = {
            'is_lit': True
        }
        # self.lighsensor = pitop.Lightsensor('A0')
        self.lightsensor = {
            'reading': 550
        }
        # self.potentiometer = pitop.Potentiometer('A1')
        self.potentiometer = {
            'position': 550
        }
        # self.button = pitop.Button('D4')
        self.button = {
            'is_pressed': True
        }


        self.LOCAL_SERVER = ('0.0.0.0', 8083)
        self.CENTRAL_SERVER = (None, 8082)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.LOCAL_SERVER)

    def day_loop(self) -> None:
        while True:
            if self.waiting:
                time.sleep(.01)
                continue

            self.solarPowerInfo = Helper.calculateSolarEnergy(self.uhrzeit.hour)
            power_needed = self.pre_calc_needed_power()

            self.collect_sensor_data()

            payload = {
                'sender': 'Wohnblock',
                'weather': self.solarPowerInfo['Wetter'],
                'energy_production': self.solarPowerInfo['Effizienz'] * self.kiloWattPeakSolar,
                'energy_usage': power_needed['poweruse_kwatt'],
                'energy_netto': (self.solarPowerInfo['Effizienz'] * self.kiloWattPeakSolar) - power_needed['poweruse_kwatt'],
                'raw_data': self.temp_raw_data
            }

            self.waiting = True
            self.socket_out.sendto(bytes(json.dumps(payload), 'utf-8'), self.CENTRAL_SERVER)
            self.uhrzeit = self.uhrzeit + datetime.timedelta(hours=1)
            time.sleep(1)

    def listen_for_sensors(self):
        while True:
            self.socket.recvfrom(4096)
            self.waiting = False
            time.sleep(0.01)

    def collect_sensor_data(self) -> None:
        self.temp_raw_data = {
            'led_red': self.led_red['is_lit'],
            'led_green': self.led_green['is_lit'],
            'lightsensor': self.lightsensor['reading'],
            'potentiometer': self.potentiometer['position'],
            'button': self.button['is_pressed']
        }

    def pre_calc_needed_power(self) -> dict:
        poweruse_rate = 1.0 #Multiplikator

        potentiometer_default = 450
        poweruse_rate *= (self.potentiometer['position'] / potentiometer_default)

        if self.button['is_pressed']:
            poweruse_rate = 0

        poweruse_kwatt = self.powerUsage * poweruse_rate

        return {
            'poweruse_kwatt': poweruse_kwatt,
            'potentiometer_efficiency': (self.potentiometer['position'] / potentiometer_default)
        }

    def get_server_ip(self):
        time.sleep(0.1)
        data, adr = self.socket.recvfrom(4096)
        data = json.loads(data.decode('utf-8'))
        print(data)
        if data.get('sender') == 'Server':
            self.CENTRAL_SERVER = adr
            print(self.CENTRAL_SERVER)
            self.found_server = True

WohnBlock()