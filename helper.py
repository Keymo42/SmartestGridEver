from typing import List
import random


class Helper:
    def __init__(self) -> None:
        pass

    def calculateBatteryPercentage(max: int, current: int) -> int:
         return int((current / max) * 100)

    def calculateEnergy(self, kiloWattPeak: int, efficiency: float) -> float:
        return kiloWattPeak * efficiency

    def getWeatherVariance() -> float:
        temp = random.randint(7, 15)
        temp = temp / 10
        return temp


    def useEnergy(sensor_values: List) -> float:
        sum = 0
        for value in sensor_values:
            sum += value.get('energy')
        return sum

