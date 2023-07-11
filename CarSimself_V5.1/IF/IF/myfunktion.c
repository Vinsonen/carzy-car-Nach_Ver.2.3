#include"IF.h"
#include"mf.h"
int16_t histerese = 0;
int8_t ereignisBremsen = 0;
int8_t servoIgliedspeicher;
int8_t servoDgliedolde;
int8_t servoDgliedAbkling;
// <== Eigene Funktion und Bedingungen formulieren / schreiben
void fahren1(void) {
	//abstandlinks
	//abstandrechts
	//abstandvorne
	//void servo(int16_t swert ){}														//2
	//	// setzt den Lenkeinschalt von -10 bis +10
	//void fahr(int16_t fwert ){}														//2
	//	// setzt der Geschindigkeit von -100 bis +100
	//int8_t getFahr(){}																	//2
	//	//z.B. getFahr(); liefert die aktuelle Geschindigkeit
	//int8_t getServo(){}																	//2
	//	//z.B. getServo(); liefert den aktuellen Lenkeinschlag 

		//Regelparameter
	int8_t minAbstand = 30; //Hysterese für den Minimalen Abstand beim Rückwärtsfahren
	int8_t KPservo = 100; //Servo P-Glied Regelkonstante in Prozent
	int8_t KIservo = 0; //Servo I-Glied Regelkonstante in Prozent
	int8_t Iservomax = 100; //Servo I-Glied Maximalwert des Speichers in Prozent
	int8_t KDservo = 0; //Servo D-Glied Regelkonstante in Prozent
	int8_t KDservoAbkling = 0; //Servo D-Glied Abklingkonstante in Prozent	
	int8_t KPfahr = 50; //Geschindigkeit P-Glied Regelkonstante in Prozent
	//int8_t KPfahrlenk = 50; //Geschindigkeit P-Glied Regelkonstante für den Lenkeinfluss in Prozent
	int8_t fahrmin = 18; //Minimale Fahrtenregleransteuerung in Prozent

	int16_t zentrierung = 0;
	int8_t zente = 0; //Zentrierungsfehler in Prozent
	int8_t ve = 0; //Regeldifferenz für die Geschwindigkeit in Prozent
	int8_t uservo = 0; //Stellgröße Servo in Prozent
	int8_t ufahr = 0; //Stellgröße Servo in Prozent
	int8_t k1 = 1.1;
	int8_t k2 = 1.1;
	int8_t k3 = 1.1;
	int8_t kp1 = 1;
	int8_t kp2 = 2;
	uint16_t sollwert1 = abstandvorne * k1;
	uint16_t sollwert2 = abstandvorne * k2;
	uint16_t sollwert3 = abstandvorne * k3;
	uint16_t sollwert4 = 0;

	if (abstandvorne > 100) {
		if (getFahr() < 80) {
			fahr(getFahr() + (sollwert1 - abstandvorne) * kp1 + 18);
			if ((getFahr() + (sollwert1 - abstandvorne) * kp1 + 18) > 80)
				fahr(80);
		}

	}
	else if (50 < abstandvorne < 100) {
		if (getFahr() > 18) {
			fahr((getFahr() - (sollwert2 - abstandvorne) * kp1));
			if ((getFahr() - (sollwert2 - abstandvorne) * kp1) < 18)
				fahr(18);
		}
	}

	else if (abstandvorne < 50 || (abstandvorne < 80 && getFahr() < -18)) {
		fahr((-1) * (sollwert3 - abstandvorne) * kp1 - 18);
	}

	if (abstandlinks <= 130 || abstandrechts <= 130) {
		servo((-1)*((abstandlinks - abstandrechts) - sollwert4) * kp2);
	}
}



	uint16_t linearisierungVorne(uint16_t analogwert) {
		//TJ Linearisierung der Sensorwerte in cm
		  //Variabel erzeugen und initialisieren 
		  //Variabel erzeugen und initialisieren 
		if (analogwert < 163) {
			analogwert = 163;
		}

		if (analogwert > 770) {
			analogwert = 770;
		}
		abstandvorne = 23962 / (analogwert + 20);
		// 
		return abstandvorne;// Ergebnis zur點kliefern
	}
	uint16_t  linearisierungLinks(uint16_t analogwert, uint8_t cosAlpha) {
		//TJ Linearisierung der Sensorwerte in cm
		  //Variabel erzeugen und initialisieren 
		  //Variabel erzeugen und initialisieren 
		if (analogwert < 163) {
			analogwert = 163;
		}

		if (analogwert > 770) {
			analogwert = 770;
		}
		abstandlinks = 23962 / (analogwert + 20);
		// 
		return abstandlinks;// Ergebnis zur點kliefern
	}
	uint16_t  linearisierungRechts(uint16_t analogwert, uint8_t cosAlpha) {
		//TJ Linearisierung der Sensorwerte in cm
		  //Variabel erzeugen und initialisieren 
		  //Variabel erzeugen und initialisieren 
		if (analogwert < 163) {
			analogwert = 163;
		}

		if (analogwert > 770) {
			analogwert = 770;
		}
		abstandrechts = 23962 / (analogwert + 20);
		// 
		return abstandrechts;// Ergebnis zur點kliefern
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
