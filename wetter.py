

import time
import random

# Wetterwerte für jede Uhrzeit
wetter = 0
Wetterwert = ["Sonne", "Regen", "Nieselregen", "Schnee", "Nebel", "Sturm", "Sonnensturm", "Sonnenfinsternis"]
wettervar = 0
uhrzeit = 0
effizienz = 0
simulation = True

while (simulation):
    for uhrzeit in range(24):
        time.sleep(2)
        wettervar = random.choices(Wetterwert, weights=(200, 70, 50, 30, 25, 25, 2, 1))[0] #[0] wählt erstes Element aus der Liste, sonst krieg ich ne Liste ausgegeben
        if wettervar == "Sonne" :
            effizienz = random.randint(80,100);
            if uhrzeit <= 6 or uhrzeit >= 20 :
                wettervar = "Mond";
                effizienz = (effizienz * 0.2);
        elif wettervar == "Nebel" :
            effizienz = random.randint(30,50);
            if uhrzeit <= 6 or uhrzeit >= 20 :
                effizienz = (effizienz * 0.2);
        elif wettervar == "Regen" : 
            effizienz = random.randint(30,80);
            if uhrzeit <= 6 or uhrzeit >= 20 :
                effizienz = (effizienz * 0.2);
        elif wettervar == "Nieselregen" :
            effizienz = random.randint(30,70);
            if uhrzeit <= 6 or uhrzeit >= 20 :
                effizienz = (effizienz * 0.2);
        elif wettervar == "Schnee" :
            effizienz = random.randint(10,30);
            if uhrzeit <= 6 or uhrzeit >= 20 :
                effizienz = (effizienz * 0.2);
        elif wettervar == "Sturm" : 
            effizienz = random.randint(20,50);
            if uhrzeit <= 6 or uhrzeit >= 20 :
                effizienz = (effizienz * 0.2);
        elif wettervar == "Sonnensturm" :
            effizienz = random.randint(50,100);
            if uhrzeit <= 6 or uhrzeit >= 20 :
                effizienz = (effizienz * 0.2);
        elif wettervar == "Sonnenfinsternis" :
            effizienz = random.randint(1,5);
            if uhrzeit <= 6 or uhrzeit >= 20 :
                effizienz = (effizienz * 0.2);
        else : 
            effizienz = 0;
        print(wettervar)
        print("Uhrzeit ist : % s Uhr. " % (uhrzeit))
        print("Effizienz ist % s %%." % int(effizienz))
        print("\n")

#print("Das Wetterphänomen, welches dies auslöste, ist % s." % (random.choice(weathertype)))	#Wetterphänomen, ist ein Gimmick