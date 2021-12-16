from typing import List
import random


class Helper:
    def __init__(self) -> None:
        pass

    def calculateBatteryPercentage(max: int, current: int) -> int:
         return int((current / max) * 100)

    def calculateSolarEnergy(uhrzeit: int) -> dict:
        Wetterwert = ["Sonne", "Regen", "Nieselregen", "Schnee", "Nebel", "Sturm", "Sonnensturm",
                           "Sonnenfinsternis"]
        wettervar = random.choices(Wetterwert, weights=(200, 70, 50, 30, 25, 25, 2, 1))[0]  # [0] w# ählt erstes Element aus der Liste, sonst krieg ich ne Liste ausgegeben
        effizienz = random.randint(80, 100)
        if wettervar == "Sonne":
            effizienz = random.randint(80, 100)
            if uhrzeit <= 6 or uhrzeit >= 20:
                wettervar = "Mond"
                effizienz = (effizienz * 0.2)
        elif wettervar == "Nebel":
            effizienz = random.randint(30, 50)
            if uhrzeit <= 6 or uhrzeit >= 20:
                effizienz = (effizienz * 0.2)
        elif wettervar == "Regen":
            effizienz = random.randint(30, 80)
            if uhrzeit <= 6 or uhrzeit >= 20:
                effizienz = (effizienz * 0.2)
        elif wettervar == "Nieselregen":
            effizienz = random.randint(30, 70)
            if uhrzeit <= 6 or uhrzeit >= 20:
                effizienz = (effizienz * 0.2)
        elif wettervar == "Schnee":
            effizienz = random.randint(10, 30)
            if uhrzeit <= 6 or uhrzeit >= 20:
                effizienz = (effizienz * 0.2)
        elif wettervar == "Sturm":
            effizienz = random.randint(20, 50)
            if uhrzeit <= 6 or uhrzeit >= 20:
                effizienz = (effizienz * 0.2)
        elif wettervar == "Sonnensturm":
            effizienz = random.randint(50, 100)
            if uhrzeit <= 6 or uhrzeit >= 20:
                effizienz = (effizienz * 0.2)
        elif wettervar == "Sonnenfinsternis":
            effizienz = random.randint(1, 5)
            if uhrzeit <= 6 or uhrzeit >= 20:
                effizienz = (effizienz * 0.2)
        else:
            effizienz = 0


        return {
            'Wetter': wettervar,
            'Effizienz': effizienz
        }

    def calculateKohleEnergy(self):
        print('FUCK')

    def useEnergy(self, sensor_values: list) -> dict:
        sum = 0
        for value in sensor_values:
            sum += value.get('energy')
        return sum

