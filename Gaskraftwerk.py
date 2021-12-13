class Gaskraftwerk:
    def __init__(self) -> None:
        self.gasVorrat = 1000 #kg
        self.gasPeak = 25 #kW/h
        self.gasUsage = 25 #kg
        
    def use_gas(self) -> dict:
        bought_gas = 0
        if self.gasVorrat < 25:
            bought_gas += 25
            self.gasVorrat += 25
        
        self.gasVorrat -= 25
        return {
            'energy': 25 * 25,
            'bought_gas': bought_gas
        }
