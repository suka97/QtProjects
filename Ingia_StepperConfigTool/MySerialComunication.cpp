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
    _timer.stop();
    _lastResponse = readAll();
    if ( _stringWeExpect != "" ) {
        if ( _stringWeExpect == _lastResponse )
            emit readResult(_SUCCESS_);
        else
            emit readResult(_ERROR_RESPONSE_);
    }
    else
        emit readResult(_RESPONSE_TO_CHECK_);

    QObject::disconnect(this, &QSerialPort::readyRead, this, &MySerialComunication::readyRead_Handler);
}

void MySerialComunication::timerEvent(QTimerEvent *event) {
    QObject::disconnect(this, &QSerialPort::readyRead, this, &MySerialComunication::readyRead_Handler);
    if ( event->timerId() == _timer.timerId() ) {
        emit readResult(_ERROR_TIMEOUT_);
        _timer.stop();
    }
}

// devuelve un array vacio en caso de error
QList<QByteArray> MySerialComunication::lastResponseInParameters(uint8_t bytesPerParameter, QByteArray initString, QByteArray endString) {
    QByteArray stringReceived = _lastResponse;
    QList<QByteArray> result;


    if ( initString != nullptr ) {
        if ( !stringReceived.startsWith(initString) )
            return result;
        else
            stringReceived.remove(0, initString.size());
    }
    if ( endString != nullptr ) {
        if ( !stringReceived.endsWith(endString) )
            return result;
        else
            stringReceived.chop(endString.size());
    }

    // si no devolvio la cantidad de bytes que deberia
    if ( (stringReceived.size() % bytesPerParameter) != 0 )
        return result;

    for( int i=0 ; i<stringReceived.size() ; i+=bytesPerParameter ) {
        QByteArray element;
        for ( uint8_t j=0 ; j<bytesPerParameter ; j++ ) {
            element.append( stringReceived.at(i+j) );
        }
        result.append(element);
    }
    return result;
}
