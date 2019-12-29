#ifndef MYSERIALCOMUNICATION_H
#define MYSERIALCOMUNICATION_H

#include <QBasicTimer>
#include <QtSerialPort/QSerialPort>
#include <QtSerialPort/QSerialPortInfo>
#include <QDialog>
#include <QTimerEvent>

class MySerialComunication : public QSerialPort
{
    Q_OBJECT

public:
    typedef enum {
        _SUCCESS_, _ERROR_RESPONSE_, _ERROR_TIMEOUT_
    } readResult_t;

public:
    MySerialComunication(QObject *parent = nullptr);
    void sendExpecting(QByteArray sendByteArray, QByteArray expectByteArray);
    void setTimeout(int timeout) { _timeout = timeout; }

signals:
    void readResult(readResult_t result);

protected:
    QByteArray _stringWeExpect;
    QBasicTimer _timer;
    int _timeout = 2000;

    void timerEvent(QTimerEvent *event) override;
    void readyRead_Handler();

};

#endif // MYSERIALCOMUNICATION_H
