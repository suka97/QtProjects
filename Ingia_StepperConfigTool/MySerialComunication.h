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
        _SUCCESS_, _ERROR_RESPONSE_, _ERROR_TIMEOUT_, _RESPONSE_TO_CHECK_
    } readResult_t;

public:
    MySerialComunication(QObject *parent = nullptr);
    void sendExpecting(QByteArray sendByteArray, QByteArray expectByteArray = "");
    void setTimeout(int timeout) { _timeout = timeout; }
    QList<QByteArray> lastResponseInParameters(uint8_t bytesPerParameter, QByteArray initString = nullptr, QByteArray endString = nullptr);
    QByteArray lastResponse() { return _lastResponse; };

signals:
    void readResult(readResult_t result);

protected:
    QByteArray _stringWeExpect, _lastResponse;
    QBasicTimer _timer;
    int _timeout = 2000;

    void timerEvent(QTimerEvent *event) override;
    void readyRead_Handler();

};

#endif // MYSERIALCOMUNICATION_H
