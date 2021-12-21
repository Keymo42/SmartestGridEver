import time
import pitop

lightsensor = pitop.LightSensor('A0')
poti = pitop.Potentiometer('A1')
while True:
    time.sleep(0.1)
    print('Lightsensor: ', lightsensor.reading)
    print('Poti: ', poti.position)