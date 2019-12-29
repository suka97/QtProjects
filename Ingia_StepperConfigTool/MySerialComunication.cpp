#include "MySerialComunication.h"

MySerialComunication::MySerialComunication(QObject *parent) : QSerialPort(parent)
{

}

void MySerialComunication::sendExpecting(QByteArray sendByteArray, QByteArray expectByteArray) {
    write(sendByteArray);

    // limpio el buffer de lectura
    if ( bytesAvailable() > 0 )
        readAll();

    _stringWeExpect = expectByteArray;
    QObject::connect(this, &QSerialPort::readyRead, this, &MySerialComunication::readyRead_Handler);
    _timer.start(_timeout, this);
}

void MySerialComunication::readyRead_Handler() {
    if ( _stringWeExpect == readAll() )
        emit readResult(_SUCCESS_);
    else
        emit readResult(_ERROR_RESPONSE_);

    QObject::disconnect(this, &QSerialPort::readyRead, this, &MySerialComunication::readyRead_Handler);
    _timer.stop();
}

void MySerialComunication::timerEvent(QTimerEvent *event) {
    if ( event->timerId() == _timer.timerId() ) {
        emit readResult(_ERROR_TIMEOUT_);
        _timer.stop();
    }
}
