#include "mainwindow.h"
#include <QApplication>
#include <QLabel>
#include "adapterqimage.h"


int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

    /*
    QImage myImage;
    myImage.load(":R/Koala.jpg");    // devuelve false en error

    QImage myAdaptedImage = AdaptarQImage( myImage, CANT_LEDS );

    QLabel myLabel;
    myLabel.setPixmap( QPixmap::fromImage(myAdaptedImage) );

    myLabel.show();
    */

    MainWindow w;
    w.show();

    return a.exec();
}
