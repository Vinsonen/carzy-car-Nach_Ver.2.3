#include"IF.h"
#include"mf.h"
int16_t histerese = 0;
int8_t ereignisBremsen = 0;
 int8_t servoIgliedspeicher;
 int8_t servoDgliedolde;
 int8_t servoDgliedAbkling;
// <== Eigene Funktion und Bedingungen formulieren / schreiben
void fahren1(void) {
	double sensordst1 = 130;
	double Kp1 = 0.3;
	double sensordst2 = 100;
	double Kp2 = 5;
	double diff_abs = abstandlinks - abstandrechts;
	double minabstand = 40;



	//if ((sensordst2 < abstandrechts < sensordst1) || (sensordst2 < abstandlinks < sensordst1)){
	//	servo((diff_abs)*Kp2);
	//}
	if ((abstandrechts < sensordst1) && (abstandlinks < sensordst1)) {
		servo((diff_abs)*Kp1);
	}
	else if (abstandrechts >=130) {
		servo(-10);
	}
	else if (abstandlinks >= 130) {
		servo(10);
	}
	if (abstandvorne < 135) {
		if (abstandvorne > 10) {
			
				if (leistung_now <= 0) {
					leistung_now = 20;
					fahr(leistung_now);
				}
				else {
					if (leistung_now <= 30) {
						fahr(leistung_now + 3);
					}
					else fahr(leistung_now);
				}
		
			

		}

		else if ((abstandvorne < 10) || (abstandrechts < 10) || (abstandlinks < 10) || (abstandvorne < minabstand)
			|| (abstandrechts < minabstand) || (abstandlinks < minabstand)) {
			fahr(-20);
			servo(-(diff_abs) * 5);
		}
	}
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
	abstandvorne = 23962 / (analogwert + 20);
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
	abstandlinks = 23962/ (analogwert + 20);
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
	abstandrechts = 23962 / (analogwert + 20);
	// 
	return abstandrechts;// Ergebnis zur點kliefern
}
int8_t Pglied(int8_t e, int8_t K){
	int16_t zvar = 0;
	int8_t u = 0;
	
	zvar = (int16_t)e * K;
	u = zvar / 100;
	return u;
}

int8_t Iglied(int8_t e, int8_t K, int8_t eAkkumuliert, int8_t eMax){
	//I-Glied mit externen Speicher und Maximalwert
	int16_t zvar = 0;
	int8_t u = 0;
	
	zvar = (int16_t)e + eAkkumuliert;
	if(abs(zvar)>eMax){
		zvar = eMax;
	}	
	zvar = zvar * K;
	u = zvar / 100;
	return u;
}

int8_t Dglied(int8_t eold, int8_t e, int8_t K){
	//D-Glied mit einfacher Rückwärtsdifferation
	//Alle Werte in Prozent
	int16_t zvar = 0;
	int8_t  u = 0;
	
	zvar = (int16_t)e - eold;
	zvar = zvar/2;
	zvar = zvar * K;
	u = zvar / 100;
	return u;
}
