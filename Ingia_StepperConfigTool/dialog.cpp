#include "dialog.h"
#include <QtWidgets>

Dialog::Dialog(QWidget *parent)
    : QDialog(parent)
{

    createComunicationGroupBox();
    createParametersGroupBox();
    createSendButtonBox();

    updateAvailablePorts();
    serialPort = new MySerialComunication(this);
    connect(serialPort, &MySerialComunication::readResult, this, &Dialog::checkResponseResult);

    mainLayout = new QGridLayout;
    mainLayout->addWidget(comunicationGroupBox, 0, 0);
    mainLayout->addWidget(parametersGroupBox, 1, 0);
    mainLayout->addWidget(sendButtonBox, 2, 0);

    setLayout(mainLayout);
    mainLayout->setSizeConstraint(QLayout::SetMinimumSize);
    setWindowTitle(tr("Ingia Stepper Config Tool"));
}

Dialog::~Dialog()
{
}


void Dialog::createParametersGroupBox() {
    parametersGroupBox = new QGroupBox(tr("Parametros"));
    parametersLayout = new QGridLayout;

    for ( uint16_t i=0 ; powerStep01_parameters[i].name!="END_PARAMETER" ; i++ ) {
        parametersLabel.append ( new QLabel( powerStep01_parameters[i].name ) );
        parametersLayout->addWidget(parametersLabel.at(i), i, 0);

        switch ( powerStep01_parameters[i].inputType ) {
            case DISCRETE: {
                parametersComboBox.append ( new QComboBox );
                QStringList opcList = powerStep01_parameters[i].opc.split("|");
                for ( uint16_t j=0 ; j<opcList.length() ; j++ ) {
                    parametersComboBox.last()->addItem( opcList.at(j) );
                }
                parametersLayout->addWidget(parametersComboBox.last(), i, 1);
                break;
            }

            case MULTIPLES: {
                QStringList limits = powerStep01_parameters[i].opc.split("-");
                parametersDoubleSpinBox.append ( new QDoubleSpinBox );
                parametersDoubleSpinBox.last()->setDecimals(2);
                parametersDoubleSpinBox.last()->setRange( limits.at(0).toDouble(), limits.at(1).toDouble() );
                parametersDoubleSpinBox.last()->setSuffix( " "+limits.at(2) );
                parametersLayout->addWidget(parametersDoubleSpinBox.last(), i, 1);
                break;
            }
            case NUMBER: {
                break;
            }
        }
    }

    checkButton = new QPushButton("Check");
    parametersLayout->addWidget(checkButton);
    connect(checkButton, &QPushButton::clicked, this, &Dialog::adjustSpinBoxValues);

    //parametersLayout->setColumnStretch(2, 1);
    parametersGroupBox->setLayout(parametersLayout);
    parametersGroupBox->setDisabled(true);
}

void Dialog::createSendButtonBox() {
    sendButtonBox = new QDialogButtonBox;

    sendButton = sendButtonBox->addButton(tr("Enviar"), QDialogButtonBox::ActionRole);
    connect(sendButton, &QPushButton::clicked, this, &Dialog::sendParameters);

    readButton = sendButtonBox->addButton(tr("Leer"), QDialogButtonBox::ActionRole);
    connect(readButton, &QPushButton::clicked, this, &Dialog::readValuesFromDevice);

    sendButtonBox->setDisabled(true);
}

void Dialog::createComunicationGroupBox() {
    comunicationGroupBox = new QGroupBox(tr("Comunicacion"));
    comunicationLayout = new QGridLayout;

    connectButton = new QPushButton("Conectar");
    connect(connectButton, &QPushButton::clicked, this, &Dialog::connectPort);
    connect(connectButton, &QPushButton::clicked, this, &Dialog::updateAvailablePorts);
    comunicationLayout->addWidget(connectButton, 1, 1);

    refreshPortsButton = new QPushButton("Refresh");
    connect(refreshPortsButton, &QPushButton::clicked, this, &Dialog::updateAvailablePorts);
    comunicationLayout->addWidget(refreshPortsButton, 0, 0);

    portsComboBox = new QComboBox;
    comunicationLayout->addWidget(portsComboBox, 1, 0);

    comunicationGroupBox->setLayout(comunicationLayout);
}

void Dialog::updateAvailablePorts() {
    // ------------- bloque copy paste ----------------
    portsComboBox->clear();
    static const char blankString[] = QT_TRANSLATE_NOOP("SettingsDialog", "N/A");
    const auto infos = QSerialPortInfo::availablePorts();
    for (const QSerialPortInfo &info : infos) {
        QStringList list;
        QString description = info.description();
        QString manufacturer = info.manufacturer();
        QString serialNumber = info.serialNumber();
        list << info.portName()
             << (!description.isEmpty() ? description : blankString)
             << (!manufacturer.isEmpty() ? manufacturer : blankString)
             << (!serialNumber.isEmpty() ? serialNumber : blankString)
             << info.systemLocation()
             << (info.vendorIdentifier() ? QString::number(info.vendorIdentifier(), 16) : blankString)
             << (info.productIdentifier() ? QString::number(info.productIdentifier(), 16) : blankString);

        portsComboBox->addItem(list.first(), list);
    }
    // ------------------------------------------------
}

void Dialog::adjustSpinBoxValues() {
    uint16_t multiplesIndex = 0;
    for ( uint16_t i=0 ; powerStep01_parameters[i].name!="END_PARAMETER" ; i++ ) {
        if ( powerStep01_parameters[i].inputType == MULTIPLES ) {
            double div = parametersDoubleSpinBox.at(multiplesIndex)->value() / parametersDoubleSpinBox.at(multiplesIndex)->minimum();
            parametersDoubleSpinBox.at(multiplesIndex)->setValue( parametersDoubleSpinBox.at(multiplesIndex)->minimum() * std::round(div) );

            multiplesIndex++;
        }
    }
}

QByteArray Dialog::uint32ToByteArray(uint32_t n) {
    QByteArray byteArray;
    for ( uint8_t i=0 ; i<4 ; i++ ) {
        byteArray.append( ((uint8_t *)&n)[i] );
    }
    return byteArray;
}

uint32_t Dialog::getMultiplesCurrentIndex(QDoubleSpinBox *spinBox) {
    double div = (spinBox->value() / spinBox->minimum()) - 1;   // -1 porque arranca de 0
    return ( (uint32_t)(std::round(div)) );
}

void Dialog::checkResponseResult(MySerialComunication::readResult_t result) {
    if ( _waitingResponse ) {
        switch (result) {
            case MySerialComunication::_SUCCESS_: {
                QMessageBox::information(this, tr("OK"), "Parametros cargados exitosamente");
                break;
            }
            case MySerialComunication::_ERROR_TIMEOUT_: {
                QMessageBox::critical(this, tr("Error"), "Timeout");
                break;
            }
            case MySerialComunication::_ERROR_RESPONSE_: {
                QMessageBox::critical(this, tr("Error"), "Fallo en respuesta");
                break;
            }
        }
        waitingForResponse(false);
    }
}

// la trama empieza con '@@' y termina con '##', con 4 bytes para cada parametro
void Dialog::sendParameters() {
    QByteArray byteArray;
    byteArray.append("@@");

    uint16_t multiplesIndex = 0, discretesIndex = 0;
    for ( uint16_t i=0 ; powerStep01_parameters[i].name!="END_PARAMETER" ; i++ ) {
        switch (powerStep01_parameters[i].inputType) {
            case DISCRETE: {
                uint32_t val = parametersComboBox.at(discretesIndex)->currentIndex();
                byteArray.append( uint32ToByteArray(val) );
                discretesIndex++;
                break;
            }
            case MULTIPLES: {
                byteArray.append( uint32ToByteArray(getMultiplesCurrentIndex(parametersDoubleSpinBox.at(multiplesIndex))) );
                multiplesIndex++;
                break;
            }
            case NUMBER: {
                break;
            }
        }
    }
    byteArray.append("##");
    serialPort->sendExpecting(byteArray, byteArray);
    waitingForResponse(true);
}

// la trama empieza con '@@' y termina con '##', con 4 bytes para cada parametro
void Dialog::readValuesFromDevice() {
    QByteArray byteArray;
    byteArray.append("@@");
}

void Dialog::waitingForResponse(bool state) {
    parametersGroupBox->setEnabled(!state);
    sendButtonBox->setEnabled(!state);
    _waitingResponse = state;
}

void Dialog::connectPort() {
    if ( _isConnected == false ) {
        serialPort->setPortName( portsComboBox->currentText() );
        serialPort->setBaudRate(QSerialPort::Baud9600);
        serialPort->setDataBits(QSerialPort::Data8);
        serialPort->setParity(QSerialPort::Parity::NoParity);
        serialPort->setStopBits(QSerialPort::StopBits::OneStop);
        serialPort->setFlowControl(QSerialPort::FlowControl::NoFlowControl);

        if ( serialPort->open(QIODevice::ReadWrite) ) {
            setConnection(true);
        } else {
            QMessageBox::critical(this, tr("Error"), serialPort->errorString());
        }
    }
    else {
        setConnection(false);
        if (serialPort->isOpen())
            serialPort->close();
    }
}

void Dialog::setConnection(bool state) {
    _isConnected = state;

    parametersGroupBox->setDisabled(!state);
    sendButtonBox->setDisabled(!state);
    refreshPortsButton->setDisabled(state);
    portsComboBox->setDisabled(state);
    if ( state == true ) {
        connectButton->setText("Desconectar");
    }
    else {
        connectButton->setText("Conectar");
    }
}
