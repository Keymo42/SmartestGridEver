import time
import threading
import socket
import json
import datetime
import sys

from helper import Helper


class Krankenhaus:
    def __init__(self) -> None:
        self.LOCAL_TEST = False
        if '--test' in sys.argv:
            self.LOCAL_TEST = True

        if self.LOCAL_TEST:
            print('Not importing pitop')
        else:
            import pitop

        self.define_variables()

        self.found_server = False
        while self.found_server is False:
            self.get_server_ip()

        sensor_thread = threading.Thread(target=self.listen_for_message)
        sensor_thread.daemon = True
        sensor_thread.start()

        dayloop_thread = threading.Thread(target=self.day_loop)
        dayloop_thread.daemon = True
        dayloop_thread.start()

        while True:
            time.sleep(1)

    def define_variables(self):
        self.helper = Helper()
        self.uhrzeit = datetime.datetime(2069, 1, 1)
        self.kiloWattPeakSolar = 10  # kW/h
        self.powerUsage = 2000 # kW/h
        # Define Sensors and Actors
        self.temp_raw_data = {}
        self.waiting = False

        self.counter = 1
        self.energy_production_average = 0
        self.energy_usage_average = 0
        self.energy_netto_average = 0

        self.setUpSensors()

        self.LOCAL_SERVER = ('0.0.0.0', 8084)
        self.CENTRAL_SERVER = (None, 8082)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.LOCAL_SERVER)

    def setUpSensors(self):
        if self.LOCAL_TEST:
            self.lightsensor = {
                'reading': 550
            }

            self.potentiometer = {
                'position': 550
            }

            self.button = {
                'is_pressed': True
            }
        else:
            self.lightsensor = pitop.LightSensor('A0')
            self.potentiometer = pitop.Potentiometer('A1')
            self.button = pitop.Button('D4')

    def day_loop(self) -> None:
        while True:
            print(self.waiting)
            if self.waiting:
                time.sleep(0.01)
                continue
            self.waiting = True

            self.solarPowerInfo = self.helper.calculateSolarEnergy(self.uhrzeit.hour)
            power_needed = self.pre_calc_needed_power()
            self.collect_sensor_data()

            self.energy_production_average = (self.energy_production_average * (self.counter - 1) + (self.solarPowerInfo['Effizienz'] * self.kiloWattPeakSolar)) / self.counter
            self.energy_usage_average = (self.energy_usage_average * (self.counter - 1) + power_needed['poweruse_kwatt']) / self.counter
            self.energy_netto_average = (self.energy_netto_average * (self.counter - 1) + ((self.solarPowerInfo['Effizienz'] * self.kiloWattPeakSolar) - power_needed['poweruse_kwatt'])) / self.counter

            payload = {
                'sender': 'Krankenhaus',
                'weather': self.solarPowerInfo['Wetter'],
                'energy_production': self.solarPowerInfo['Effizienz'] * self.kiloWattPeakSolar,
                'energy_usage': power_needed['poweruse_kwatt'],
                'energy_netto': (self.solarPowerInfo['Effizienz'] * self.kiloWattPeakSolar) - power_needed['poweruse_kwatt'],
                'energy_production_average': self.energy_production_average,
                'energy_usage_average': self.energy_usage_average,
                'energy_netto_average': self.energy_netto_average,
                'raw_data': self.temp_raw_data
            }

            self.socket_out.sendto(bytes(json.dumps(payload), 'utf-8'), self.CENTRAL_SERVER)
            self.uhrzeit = self.uhrzeit + datetime.timedelta(hours=1)
            self.counter += 1
            time.sleep(1)

    def listen_for_message(self):
        while True:
            self.socket.recvfrom(4096)
            self.waiting = False
            time.sleep(0.1)

    def collect_sensor_data(self) -> None:
        if self.LOCAL_TEST:
            self.temp_raw_data = {
                'lightsensor': self.lightsensor['reading'],
                'potentiometer': self.potentiometer['position'],
                'button': self.button['is_pressed']
            }
        else:
            self.temp_raw_data = {
                'lightsensor': self.lightsensor.reading,
                'potentiometer': self.potentiometer.position,
                'button': self.button.is_pressed
            }

    def pre_calc_needed_power(self) -> dict:
        if self.LOCAL_TEST:
            lightsensor_value = self.lightsensor['reading']
            potentiometer_value = self.potentiometer['position']
        else:
            lightsensor_value = self.lightsensor.reading
            potentiometer_value = self.potentiometer.position
        poweruse = 1.0  # Multiplikator

        solar_cells_default = 450
        poweruse = poweruse * (lightsensor_value / solar_cells_default)

        poweruse_kwatt = poweruse * self.powerUsage

        potentiometer_default = 450
        poweruse_kwatt = poweruse_kwatt * (potentiometer_value / potentiometer_default)

        return {
            'poweruse_kwatt': poweruse_kwatt,
            'solarcells_efficiency': (lightsensor_value / solar_cells_default),
            'potentiometer_efficiency': (potentiometer_value / potentiometer_default)
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

Krankenhaus()