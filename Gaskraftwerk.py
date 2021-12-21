class Gaskraftwerk:
    def __init__(self) -> None:
        self.gasVorrat = 1000 #kWh
        self.kWhCost = 1
        self.spent_money = 0
        self.average_production = 0
        self.counter = 1

        #kWh = 1€
        
    def use_gas(self, needed_energy) -> dict:
        self.gasVorrat = self.gasVorrat - needed_energy
        if self.gasVorrat < 0:
            self.spent_money += (self.kWhCost * needed_energy)

        return {
            'energy': needed_energy,
            'money_spent': self.spent_money,
            'speicher': self.gasVorrat,
            'average_production': self.average_production,
            'production': 0
        }

    def convertEnergyToGas(self, excess_energy: float):
        self.average_production = (self.average_production + (excess_energy * 0.7)) / self.counter
        self.gasVorrat += excess_energy * 0.7
        return {
            'energy': 0,
            'money_spent': self.spent_money,
            'speicher': self.gasVorrat,
            'average_production': self.average_production,
            'production': (excess_energy * 0.7)
        }

    def getData(self):
        return {
            'energy': 0,
            'money_spent': self.spent_money,
            'speicher': self.gasVorrat,
            'average_production': self.average_production,
            'production': 0
        }
