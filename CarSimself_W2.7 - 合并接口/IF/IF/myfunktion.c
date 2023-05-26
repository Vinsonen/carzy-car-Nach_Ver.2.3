#include"IF.h"
#include"mf.h"
void fahren1(void) {
	if (abstandrechts < 100 || abstandlinks < 100) {
		if (abstandrechts < abstandlinks) {
			servo(-10);
		}
		else if (abstandrechts > abstandlinks) {
			servo(10);
		}
	}	
	fahr(30);
}
uint16_t linearisierungVorne(uint16_t analogwert) {
	//TJ Linearisierung der Sensorwerte in cm
	  //Variabel erzeugen und initialisieren 
	  //Variabel erzeugen und initialisieren 
	if (analogwert < 100) {
		analogwert = 100;
	}

	if (analogwert > 900) {
		analogwert = 900;
	}
	abstandvorne = 23692 / (analogwert - 20);
	// 
	return abstandvorne;// Ergebnis zur點kliefern
}
uint16_t  linearisierungLinks(uint16_t analogwert, uint8_t cosAlpha) {
	//TJ Linearisierung der Sensorwerte in cm
	  //Variabel erzeugen und initialisieren 
	  //Variabel erzeugen und initialisieren 
	if (analogwert < 100) {
		analogwert = 100;
	}

	if (analogwert > 900) {
		analogwert = 900;
	}
	abstandlinks = 23692 / (analogwert - 20)*cosAlpha/100;
	// 
	return abstandlinks;// Ergebnis zur點kliefern
}
uint16_t  linearisierungRechts(uint16_t analogwert, uint8_t cosAlpha) {
	//TJ Linearisierung der Sensorwerte in cm
	  //Variabel erzeugen und initialisieren 
	  //Variabel erzeugen und initialisieren 
	if (analogwert < 100) {
		analogwert = 100;
	}

	if (analogwert > 900) {
		analogwert = 900;
	}
	abstandrechts = 23692 / (analogwert - 20)*cosAlpha/100;
	// 
	return abstandrechts;// Ergebnis zur點kliefern
}
