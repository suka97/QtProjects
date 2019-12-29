#ifndef DIALOG_H
#define DIALOG_H

#include <QDialog>
#include <QQueue>
#include <QDoubleSpinBox>
#include <QList>

#include "DefinitionsClass.h"
#include "MySerialComunication.h"

QT_BEGIN_NAMESPACE
class QComboBox;
class QDialogButtonBox;
class QGridLayout;
class QGroupBox;
class QLabel;
class QPushButton;
QT_END_NAMESPACE

class Dialog : public QDialog, public DefinitionsClass
{
    Q_OBJECT

private slots:
    void sendParameters();
    void connectPort();
    void updateAvailablePorts();

private:
    void createParametersGroupBox();
    void createSendButtonBox();
    void createComunicationGroupBox();
    void setConnection(bool state);
    void adjustSpinBoxValues();
    void readValuesFromDevice();
    QByteArray uint32ToByteArray(uint32_t n);
    uint32_t getMultiplesCurrentIndex(QDoubleSpinBox *spinBox);
    void checkResponseResult(MySerialComunication::readResult_t result);
    void waitingForResponse(bool state);

    bool _isConnected = false;
    bool _waitingResponse = false;

    QGridLayout *mainLayout;
    MySerialComunication *serialPort;

    QGroupBox *parametersGroupBox;
    QGridLayout *parametersLayout;
    QList <QComboBox *> parametersComboBox;
    QList <QDoubleSpinBox *> parametersDoubleSpinBox;
    QList <QLabel *> parametersLabel;
    QPushButton *checkButton;

    QDialogButtonBox *sendButtonBox;
    QPushButton *sendButton, *readButton;

    QGroupBox *comunicationGroupBox;
    QGridLayout *comunicationLayout;
    QPushButton *connectButton, *refreshPortsButton;
    QComboBox *portsComboBox;

public:
    Dialog(QWidget *parent = nullptr);
    ~Dialog();
};
#endif // DIALOG_H
