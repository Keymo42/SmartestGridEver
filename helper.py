from typing import List
import random


class Helper:
    def __init__(self) -> None:
        self.hours_since_weather_change = 0
        self.last_efficiency = 0
        self.last_weather = ''
        pass

    def calculateBatteryPercentage(self, max: int, current: int) -> int:
         return int((current / max) * 100)

    def calculateSolarEnergy(self, uhrzeit: int) -> dict:
        if self.hours_since_weather_change < 3:
            self.hours_since_weather_change += 1
            return {
                'Wetter': self.last_weather,
                'Effizienz': self.last_efficiency
            }

        self.hours_since_weather_change = 0
        Wetterwert = ["Sonne", "Regen", "Nieselregen", "Schnee", "Nebel", "Sturm", "Sonnensturm",
                           "Sonnenfinsternis"]
        wettervar = random.choices(Wetterwert, weights=(200, 70, 50, 30, 25, 25, 2, 1))[0]  # [0] w# ählt erstes Element aus der Liste, sonst krieg ich ne Liste ausgegeben
        effizienz = 1
        if wettervar == "Sonne":
            if uhrzeit <= 6 or uhrzeit >= 20:
                wettervar = "Mond"
                effizienz = (effizienz * 0.3)
            else:
                effizienz = 1.5
        elif wettervar == "Nebel":
            if uhrzeit <= 6 or uhrzeit >= 20:
                effizienz = (effizienz * 0.3)
            else:
                effizienz = 0.6
        elif wettervar == "Regen":
            if uhrzeit <= 6 or uhrzeit >= 20:
                effizienz = (effizienz * 0.3)
            else:
                effizienz = 0.5
        elif wettervar == "Nieselregen":
            if uhrzeit <= 6 or uhrzeit >= 20:
                effizienz = (effizienz * 0.3)
            else:
                effizienz = 0.6
        elif wettervar == "Schnee":
            if uhrzeit <= 6 or uhrzeit >= 20:
                effizienz = (effizienz * 0.3)
            else:
                effizienz = 0.4
        elif wettervar == "Sturm":
            if uhrzeit <= 6 or uhrzeit >= 20:
                effizienz = (effizienz * 0.3)
            else:
                effizienz = 0.4
        elif wettervar == "Sonnensturm":
            if uhrzeit <= 6 or uhrzeit >= 20:
                effizienz = (effizienz * 0.3)
            else:
                effizienz = 2
        elif wettervar == "Sonnenfinsternis":
            effizienz = 0
        else:
            effizienz = 0

        self.last_efficiency = effizienz
        self.last_weather = wettervar
        self.hours_since_weather_change += 1

        return {
            'Wetter': wettervar,
            'Effizienz': effizienz
        }

    def useEnergy(self, sensor_values: list) -> dict:
        sum = 0
        for value in sensor_values:
            sum += value.get('energy')
        return sum

