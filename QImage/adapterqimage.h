#ifndef ADAPTERQIMAGE_H
#define ADAPTERQIMAGE_H

#include <QImage>
#include <QtCore/QtMath>

const int CANT_MUESTRAS = 360;
const int CANT_LEDS = 24;

class AdapterQImage : public QImage
{
public:
    AdapterQImage(const QImage &im_original);
    QByteArray getColorsOf(unsigned int muestra, unsigned int led);

protected:
    QColor color[CANT_MUESTRAS][CANT_LEDS];
};

#endif // ADAPTERQIMAGE_H
