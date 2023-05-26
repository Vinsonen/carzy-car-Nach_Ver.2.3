#ifndef MF_H
#define MF_H
typedef unsigned short uint16_t;
typedef short int16_t;
typedef unsigned short uint8_t;
void fahren1(void); 
uint16_t  linearisierungRechts(uint16_t analogwert, uint8_t cosAlpha);
uint16_t  linearisierungLinks(uint16_t analogwert, uint8_t cosAlpha);
uint16_t linearisierungVorne(uint16_t analogwert);
#endif