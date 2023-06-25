#ifndef IF_H
#define IF_H

extern int fwert;
extern int swert; 
extern int leistung_now;
typedef unsigned short uint16_t;
typedef short int16_t;
typedef unsigned short uint8_t;
extern uint16_t abstandvorne;
extern uint16_t abstandlinks;
extern uint16_t abstandrechts;
__declspec(dllexport) void fahr(int f);
 __declspec(dllexport) int getfwert();
 __declspec(dllexport) void servo(int s);
 __declspec(dllexport) int getservo();
 __declspec(dllexport) void getfahr(float leistung);
 __declspec(dllexport) void getabstandvorne(uint16_t anlagwort);
 __declspec(dllexport) void getabstandrechts(uint16_t anlagwort,uint8_t cosAlpha);
 __declspec(dllexport) void getabstandlinks(uint16_t anlagwort, uint8_t cosAlpha);
 __declspec(dllexport) void regelungtechnik();
 __declspec(dllexport) int getFahr();
#endif