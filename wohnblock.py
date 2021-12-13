import time
import threading
import socket
import json
import datetime
# import pitop

from random import randrange


class WohnBlock:
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
        self.uhrzeit = datetime.datetime(2069, 1, 1)
        self.effizienzen = [0, 0, 0, 0,
                            0, 0, 0, 0.3,
                            0.4, 0.5, 0.6, 0.7,
                            0.8, 0.7, 0.6, 0.5,
                            0.4, 0.3, 0.2, 0,
                            0, 0, 0, 0]  # Faktoren für Effizienzberechnung

        # Define Sensors and Actors
        self.temp_raw_data = {}
        self.waiting = False
        # self.led_red = pitop.LED('D0')
        # self.led_yellow = pitop.LED('D1')
        # self.led_green = pitop.LED('D2')
        # self.extra_poweruse_switch = pitop.Button('D3')
        # self.solar_cells = pitop.LightSensor('A1')
        # self.potentiometer = pitop.Potentiometer('A0')

        UDP_IP = "127.0.0.1"
        UDP_PORT = 8083
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((UDP_IP, UDP_PORT))

    def day_loop(self) -> None:
        while True:
            if self.waiting:
                time.sleep(.01)
                continue

            self.collect_sensor_data()
            data = self.pre_calc_needed_power()
            payload = {
                'sender': 'Wohnblock',
                'power_usage': data.get('poweruse_kwatt'),
                'solarcells_efficiency': data.get('solarcells_efficiency'),
                'potentiometer_efficiency': data.get('potentiometer_efficiency'),
                'raw_data': {
                    # 'led_red_on': self.led_red.is_lit,
                    # 'led_yellow_on': self.led_yellow.is_lit,
                    # 'led_green_on': self.led_green.is_lit,
                    'extra_power_switch_on': self.temp_raw_data['extra_poweruse_switch'],
                    'light_sensor': self.temp_raw_data['solar_cells'],
                    'potentiometer': self.temp_raw_data['potentiometer']
                }
            }
            self.waiting = True
            self.socket.sendto(bytes(json.dumps(payload), 'utf-8'), ("127.0.0.1", 8082))
            self.uhrzeit = self.uhrzeit + datetime.timedelta(hours=1)
            time.sleep(1)

    def listen_for_sensors(self):
        while True:
            data, adr = self.socket.recvfrom(4096)
            data = data.decode('utf-8')
            data = json.loads(data)
            print(data)
            self.waiting = False
            time.sleep(0.01)

    def collect_sensor_data(self) -> None:
        test = randrange(0, 2)
        print(test)
        if test == 0:
            self.temp_raw_data['extra_poweruse_switch'] = False
        else:
            self.temp_raw_data['extra_poweruse_switch'] = True
        self.temp_raw_data['solar_cells'] = randrange(0, 999, 1)
        self.temp_raw_data['potentiometer'] = randrange(0, 999, 1)

    def pre_calc_needed_power(self) -> dict:
        poweruse = 1.0
        kw_per_h = 25

        solar_cells_default = 555
        poweruse = poweruse * (self.temp_raw_data['solar_cells'] / solar_cells_default)
        print((self.temp_raw_data['solar_cells'] / solar_cells_default))

        if self.temp_raw_data['extra_poweruse_switch']:
            poweruse = poweruse * 1.5

        potentiometer_default = 450
        poweruse = poweruse * (self.temp_raw_data['potentiometer'] / potentiometer_default)
        print((self.temp_raw_data['potentiometer'] / potentiometer_default))

        poweruse_kwatt = poweruse * kw_per_h

        return {
            'poweruse_kwatt': poweruse_kwatt,
            'solarcells_efficiency': (self.temp_raw_data['solar_cells'] / solar_cells_default),
            'potentiometer_efficiency': (self.temp_raw_data['potentiometer'] / potentiometer_default)
        }

WohnBlock()