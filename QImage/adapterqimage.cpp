#include "adapterqimage.h"


AdapterQImage::AdapterQImage(const QImage &im_original) : QImage (im_original.width(), im_original.height(), im_original.format())
{
    // cant de pixeles de la imagen original
    int pixHeight = height();
    int pixWidth = width();

    // centro de la imagen y "radio" de la imagen a transformar
    QPoint centro(pixWidth/2, pixHeight/2);
    int radio = pixWidth/2;
    if ( pixHeight < pixWidth )
        radio = pixHeight/2;

    const int DELTA_PIX = 3;    // lo que me fijo fuera de mi pixel para aproximar el color
    const int interval = radio / CANT_LEDS;     // distancia en pixeles entre cada led

    qreal angulo = 0;
    for ( int muestra=0 ; muestra<CANT_MUESTRAS ; muestra++ )
    {
        for ( int led=0 ; led<CANT_LEDS ; led++ )
        {
            int aprox_pixX = centro.x() + qRound( static_cast<double>(interval * led) * qCos(qDegreesToRadians(angulo)) );
            int aprox_pixY = centro.y() + qRound( static_cast<double>(interval * led) * qSin(qDegreesToRadians(angulo)) );


            double r_Promedio = 0;
            double g_Promedio = 0;
            double b_Promedio = 0;
            double a_Promedio = 0;

            // la segunda pasada voy seteando los colores
            for ( int j=0 ; j<2 ; j++ )
            {
                // aproximo el color
                for ( int x=aprox_pixX-DELTA_PIX ; x<=(aprox_pixX+DELTA_PIX) ; x++ ) {
                    for ( int y=aprox_pixY-DELTA_PIX ; y<=(aprox_pixY+DELTA_PIX) ; y++ ) {
                        if ( j==0 ) {
                            QColor current_pixColor = im_original.pixelColor(x, y);
                            r_Promedio += static_cast<double>(current_pixColor.red()) / static_cast<double>(255);
                            g_Promedio += static_cast<double>(current_pixColor.green()) / static_cast<double>(255);
                            b_Promedio += static_cast<double>(current_pixColor.blue()) / static_cast<double>(255);
                            a_Promedio += static_cast<double>(current_pixColor.alpha()) / static_cast<double>(255);
                        }
                        else {
                            setPixelColor( x, y, QColor( static_cast<int>(r_Promedio), static_cast<int>(g_Promedio), static_cast<int>(b_Promedio), static_cast<int>(a_Promedio)) );             
                        }
                    }
                }
                if ( j== 0) {   // pregunto para no reescribir dos veces lo mismo
                    int volumenDelta = (2*DELTA_PIX +1) * (2*DELTA_PIX +1);

                    // obtengo el promedio, y lo paso a absoulto (x255)
                    r_Promedio = r_Promedio / static_cast<double>( volumenDelta );
                    g_Promedio = g_Promedio / static_cast<double>( volumenDelta );
                    b_Promedio = b_Promedio / static_cast<double>( volumenDelta );
                    a_Promedio = a_Promedio / static_cast<double>( volumenDelta );
                    // -----
                    r_Promedio = r_Promedio * static_cast<double>(255);
                    g_Promedio = g_Promedio * static_cast<double>(255);
                    b_Promedio = b_Promedio * static_cast<double>(255);
                    a_Promedio = a_Promedio * static_cast<double>(255);
                    // -----
                    r_Promedio = std::round(r_Promedio);
                    g_Promedio = std::round(g_Promedio);
                    b_Promedio = std::round(b_Promedio);
                    a_Promedio = std::round(a_Promedio);
                }
            }
            // lo guardo en el array
            color[muestra][led].setRgba( qRgba(qRound(r_Promedio),qRound(g_Promedio),qRound(b_Promedio),qRound(a_Promedio)) );
        }

        // aumento el algulo un delta grados (en este caso 1º)
        angulo += static_cast<qreal>(360) / static_cast<qreal>(CANT_MUESTRAS);
    }
}


QByteArray AdapterQImage::getColorsOf(unsigned int muestra, unsigned int led)
{
    QByteArray salida;

    if ( (muestra>CANT_MUESTRAS) || (led>CANT_LEDS) )
        return  salida;

    salida.append( static_cast<char>(color[muestra][led].red()) );
    salida.append( static_cast<char>(color[muestra][led].green()) );
    salida.append( static_cast<char>(color[muestra][led].blue()) );
    return salida;
}


