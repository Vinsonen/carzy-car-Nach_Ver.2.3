#include"IF.h"
#include"mf.h"
int fwert; 
int swert; 
float leistung_now; 
uint16_t abstandvorne;
uint16_t abstandlinks;
uint16_t abstandrechts;

__declspec(dllexport) void fahr(int f) {
	fwert = f;
}
__declspec(dllexport) int getfwert() {
	return fwert;
}
__declspec(dllexport) void getfahr(float leistung) {
	leistung_now = leistung;
}
__declspec(dllexport) void servo(int s) {
	swert = s;
}
__declspec(dllexport) int getservo() {
	return swert;
}
__declspec(dllexport) void getabstandvorne(uint16_t anlagwort) {
	abstandvorne = linearisierungVorne(anlagwort);
} 
__declspec(dllexport) void getabstandrechts(uint16_t anlagwort, uint8_t cosAlpha) {
	abstandrechts = linearisierungRechts(anlagwort, cosAlpha);
}
__declspec(dllexport) void getabstandlinks(uint16_t anlagwort, uint8_t cosAlpha) {
	abstandlinks = linearisierungLinks(abstandlinks, cosAlpha);
}
__declspec(dllexport) void regelungtechnik() {
	fahren1();
}
__declspec(dllexport) int getFahr() {
	return leistung_now;
}