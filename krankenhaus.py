import time
import threading
import socket
import json
import datetime
import sys
import random
import pitop

from helper import Helper


class Krankenhaus:
    def __init__(self) -> None:
        self.LOCAL_TEST = False
        if '--test' in sys.argv:
            self.LOCAL_TEST = True

        if self.LOCAL_TEST:
            print('Not importing pitop')

        self.define_variables()

        self.helper = Helper()

        dayloop_thread = threading.Thread(target=self.day_loop)
        dayloop_thread.daemon = True
        dayloop_thread.start()

        while True:
            time.sleep(0.01)

    def define_variables(self):
        self.uhrzeit = datetime.datetime(2069, 1, 1)
        self.kiloWattPeakSolar = 45.66  # kWh
        # self.powerUsage = 13.7 # kWh
        self.usage_actual = 0
        self.powerUsage = 26  # kWh
        # Define Sensors and Actors
        self.temp_raw_data = {}
        self.waiting = False
        self.off_grid = False

        self.loop_counter = 1
        self.energy_production_average = 0
        self.energy_usage_average = 0
        self.energy_netto_average = 0

        self.setUpSensors()

        self.CENTRAL_SERVER = ('172.16.221.2', 8082)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.CENTRAL_SERVER)

        data_thread = threading.Thread(target=self.listen_for_data)
        data_thread.daemon = True
        data_thread.start()

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

            self.button_led = {
                'is_lit': True
            }
        else:
            self.lightsensor = pitop.LightSensor('A0')      # Acts as a solar panel
            self.potentiometer = pitop.Potentiometer('A1')  # Acts as a multiplier for Energy Usage
            self.button = pitop.Button('D0')                # Takes it off the grid (Energy Usage is 0)
            self.button_led = pitop.LED('D1')            # Lights up when Button is active

            self.button.when_pressed = self.toggleGrid

    def setUpPayload(self, solarPowerInfo: dict, energy_usage: float, energy: float) -> dict:
        payload = {
            'sender': 'Krankenhaus',
            'weather': solarPowerInfo['Wetter'],
            'energy_production': solarPowerInfo['Effizienz'] * energy,
            'energy_usage': energy_usage,
            'energy_netto': (solarPowerInfo['Effizienz'] * energy) - energy_usage,
            'energy_production_average': self.energy_production_average,
            'energy_usage_average': self.energy_usage_average,
            'energy_netto_average': self.energy_netto_average,
            'raw_data': self.temp_raw_data
        }
        return payload

    def day_loop(self) -> None:
        while True:
            # print('Waiting: ', self.waiting)
            while self.waiting:
                continue
            self.waiting = True

            usage_multiplier = random.randint(5, 11)
            usage_multiplier = usage_multiplier / 10
            self.usage_actual = self.powerUsage * usage_multiplier

            self.collect_sensor_data()

            solarPowerInfo = self.helper.calculateSolarEnergy(self.uhrzeit.hour)
            power_needed = self.pre_calc_needed_power()
            energy = self.calc_power()

            self.energy_production_average = (self.energy_production_average + (solarPowerInfo['Effizienz'] * energy)) / self.loop_counter
            self.energy_usage_average = (self.energy_usage_average + power_needed['poweruse_kwatt']) / self.loop_counter
            self.energy_netto_average = (self.energy_netto_average + ((solarPowerInfo['Effizienz'] * energy) - power_needed['poweruse_kwatt'])) / self.loop_counter

            payload = self.setUpPayload(solarPowerInfo, power_needed['poweruse_kwatt'], energy)
            # print(payload)
            self.socket.send(bytes(json.dumps(payload), 'utf-8'))
            self.uhrzeit = self.uhrzeit + datetime.timedelta(hours=1)
            self.loop_counter += 1

    def listen_for_data(self):
        while True:
            time.sleep(0.01)
            data = self.socket.recv(1024)
            data = json.loads(data.decode('utf-8'))

            if self.waiting and data is not None:
                self.waiting = False

    def collect_sensor_data(self) -> None:
        if self.LOCAL_TEST:
            self.temp_raw_data = {
                'lightsensor': self.lightsensor['reading'],
                'potentiometer': self.potentiometer['position'],
                'button': self.button['is_pressed'],
                'button_led': self.button_led['is_lit']
            }
        else:
            self.temp_raw_data = {
                'lightsensor': self.lightsensor.reading,
                'potentiometer': self.potentiometer.position,
                'button': self.button.is_pressed,
                'button_led': self.button_led.is_lit
            }

    def pre_calc_needed_power(self) -> dict:
        if self.off_grid:
            return {
                'poweruse_kwatt': 0,
                'potentiometer_efficiency': 0
            }
        if self.LOCAL_TEST:
            potentiometer_value = self.potentiometer['position']
        else:
            potentiometer_value = self.potentiometer.position
        poweruse = 1.0  # Multiplikator

        potentiometer_default = 450
        poweruse = poweruse * (potentiometer_value / potentiometer_default)

        poweruse_kwatt = poweruse * self.usage_actual

        return {
            'poweruse_kwatt': poweruse_kwatt,
            'potentiometer_efficiency': (potentiometer_value / potentiometer_default)
        }

    def calc_power(self):
        if self.off_grid:
            return 0

        if self.LOCAL_TEST:
            lightsensor_value = self.lightsensor['reading']
        else:
            lightsensor_value = self.lightsensor.reading

        poweruse = 1

        solar_cells_default = 50
        solar_energy = (poweruse * (lightsensor_value / solar_cells_default)) * self.kiloWattPeakSolar

        return solar_energy

    def toggleGrid(self):
        self.off_grid = not self.off_grid

        self.button_led.off()
        if self.off_grid:
            self.button_led.on()


Krankenhaus()