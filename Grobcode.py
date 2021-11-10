# Python3 Script zur Erstellung von diversen Dingen
# Wettersimulation benötigt Randomwert
# Randomwert impliziert, wie viel % Effizienzminderung die Zellen haben
import random
import time

# zufällige Nummer zwischen 0 und 100 für Prozente; Wetter für naja Gimmick lawl
weather = random.randint(0, 100)
weathertype = ['Einfach zu hice', 'Blizzard', 'Sonnensturm', 'Hagel', 'Schneeregen', 'Sonne', 'Milde Brise', 'Steife Brise', 'Hitze',  'Starkregenereignis']
#print("Wetterbedingte Effizienzverminderung ist bei %  s" % (weather))

# erstmal Uhrzeit festlegen 10/10
uhrzeit = 0
Messung = 1
effizienz = 0
stundwert = 0
stromspeichermax = 36000
stromspeicher = 0
kilowattpeak = 12
verbrauchhaus = 6
verbrauchklinik = 6
atomkraftwerk = 0
atommuell = 0

#def effizienz():
#	return uhrzeit(

# outdated
#while Messung == 1:
#	if uhrzeit < 2:
#		uhrzeit = uhrzeit +1
#		print(uhrzeit)
#		time.sleep(1)
#	elif uhrzeit > 2:
#		uhrzeit = 0
#		print(uhrzeit)
#		time.sleep(1)




#for i = 0 to 24
while Messung == 1:
	for uhrzeit in range(24):
#		weather = random.randint(0, 100)
#		print("Wetterbedingte Effizienzverminderung ist bei % s Prozent." % (weather))
		time.sleep(1)
		if uhrzeit >= 5 and uhrzeit <= 13 and effizienz <= 100:
			effizienz = effizienz + random.randint(3,20)
			if effizienz >= 100:
				effizienz = 100
		elif uhrzeit >= 13 and uhrzeit != 5 and effizienz != 0 and effizienz >= 0:
			effizienz = effizienz - random.randint(5,20)
			if effizienz <= 0:
				effizienz = 0
		stromspeicher = stromspeicher + (kilowattpeak * (effizienz * 0.01))
		stromspeicher_formatiert = "{:.2f}".format(stromspeicher)
		print("Uhrzeit ist : % s Uhr. " % (uhrzeit))
		print("Die Effizienz der Produktion betrug gerade % s Prozent." % (effizienz))
		print("Das Wetterphänomen, welches dies auslöste, ist % s." % (random.choice(weathertype)))
		print("Stromspeicherstand : % s KWH.\n" % (stromspeicher_formatiert))
#		if (weather + effizienz <= 100) and (weather+ effizienz >= 0):
#			stundwert = weather + effizienz
#Atomkraftwerk
		if stromspeicher <= 0:
			atomkraftwerk = 1
		while atomkraftwerk == 1:
			print("Der Stromspeicher ist leer - Atomkraftwerk wird hochgefahren!!")
			stromspeicher = stromspeicher + 1000
			print("1000KW Atomstrom in den Speicher geballert!")
			atommuell = atommuell + 0.1
			print("Es ist % s Tonnen Atommuell angefallen." % (atommuell))
			if stromspeicher >= stromspeichermax:
				atomkraftwerk = 0
