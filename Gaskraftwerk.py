class Gaskraftwerk:
    def __init__(self) -> None:
        self.gasVorrat = 1000 #kWh
        self.spent_money = 0

        #kWh = 1€
        
    def use_gas(self, needed_energy) -> dict:
        self.gasVorrat = self.gasVorrat - needed_energy
        if self.gasVorrat > 0:
            self.spent_money = self.spent_money + (-1 * self.gasVorrat)
        return {
            'energy': needed_energy,
            'money_spent': self.spent_money
        }

    def convertEnergyToGas(self, excess_energy: float) -> None:
        self.gasVorrat += excess_energy * 0.7