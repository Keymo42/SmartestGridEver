class Gaskraftwerk:
    def __init__(self) -> None:
        self.gasVorrat = 1000 #kg
        self.gasPeak = 25 #kW/h / kg
        self.gasUsage = 25 #kg / kw/h
        self.gasCost = 1 # € / kg
        self.spent_money = 0
        self.gasUsed = 0
        
    def use_gas(self) -> dict:
        bought_gas = 0
        if self.gasVorrat < self.gasUsage:
            bought_gas += self.gasUsage
            self.gasVorrat += self.gasUsage
        
        self.gasVorrat -= self.gasUsage
        self.gasUsed += self.gasUsage
        self.spent_money += self.gasUsage * self.gasCost
        return {
            'energy': self.gasUsage * self.gasPeak,
            'bought_gas': bought_gas,
            'used_gas': self.gasUsed,
            'money_spent': self.spent_money
        }

    def convertEnergyToGas(self, excess_energy: float) -> None:
        self.gasVorrat = excess_energy / self.gasPeak