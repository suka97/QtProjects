#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    m_serial = (new QSerialPort(this));
    updateCOMChannels();
    checkInputs();
}

MainWindow::~MainWindow()
{
    delete myImage;
    delete ui;
}

void MainWindow::open()
{
    const QString fileName =
        QFileDialog::getOpenFileName(this, tr("Open File"),
                                     QDir::currentPath());
    if (!fileName.isEmpty()) {
        openImage(fileName);
    }
}

bool MainWindow::openImage(const QString &fileName)
{
    QImage loadedImage;
    if (!loadedImage.load(fileName)) {
        return false;
    }


    myImage = new AdapterQImage(loadedImage);
    ui->image_Label->setPixmap( QPixmap::fromImage(*myImage) );

    return true;
}

void MainWindow::updateCOMChannels()
{
    static const char blankString[] = QT_TRANSLATE_NOOP("SettingsDialog", "N/A");
    ui->comChannels_ComboBox->clear();

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

        ui->comChannels_ComboBox->addItem(list.first(), list);
    }

}

void MainWindow::checkInputs()
{
    if ( (ui->comChannels_ComboBox->count() > 0) ) {
        ui->connect_Btn->setEnabled(true);
    }
    else {
        ui->connect_Btn->setEnabled(false);
    }

    if ( m_serial->isOpen() && (myImage != nullptr) ) {
        ui->sendImage_Btn->setEnabled(true);
    } else {
        ui->sendImage_Btn->setEnabled(false);
    }

    if ( m_serial->isOpen() ) {
        ui->connect_Btn->setEnabled(false);
        ui->disconnect_Btn->setEnabled(true);
    }
    else {
        ui->connect_Btn->setEnabled(true);
        ui->disconnect_Btn->setEnabled(false);
    }
}

bool MainWindow::openSerialPort(QString portName)
{
    m_serial->setPortName(portName);
    m_serial->setBaudRate(QSerialPort::Baud9600);
    m_serial->setDataBits(QSerialPort::Data8);
    m_serial->setParity(QSerialPort::Parity::NoParity);
    m_serial->setStopBits(QSerialPort::StopBits::OneStop);
    m_serial->setFlowControl(QSerialPort::FlowControl::NoFlowControl);

    if ( m_serial->open(QIODevice::ReadWrite) ) {
        return true;
    } else {
        QMessageBox::critical(this, tr("Error"), m_serial->errorString());
        return false;
    }
}

void MainWindow::closeSerialPort()
{
    if (m_serial->isOpen())
        m_serial->close();
}

void MainWindow::readyRead_Handler()
{
    static bool responseOK = true;
    static int index = 0;

    QByteArray input = m_serial->readAll();
    for ( int i=0 ; i<input.length() ; i++ )
    {
        char c = input.at(i);
        if ( c != stringWeExpect.at(index) ) {
            responseOK = false;
            break;
        }
        index++;
    }

    if (!responseOK) {
        // error
        index = 0;  responseOK = true;  // reinicio los static
        disconnect(m_serial, &QSerialPort::readyRead, this, &MainWindow::readyRead_Handler);
        QMessageBox::critical(this, tr("Error"), "Fallo en respuesta");
        sendTrama(true);
    }
    if ( (index == stringWeExpect.length()) && (responseOK) ) {
        // recibi todo OK
        index = 0;
        disconnect(m_serial, &QSerialPort::readyRead, this, &MainWindow::readyRead_Handler);
        sendTrama();
    }
}

void MainWindow::checkResponse(QByteArray string) {
    // limpio el buffer de lectura
    if ( m_serial->bytesAvailable() > 0 )
        m_serial->readAll();

    stringWeExpect = string;
    connect(m_serial, &QSerialPort::readyRead, this, &MainWindow::readyRead_Handler);
}

void MainWindow::sendTrama(bool resetFlag)
{
    static unsigned int muestra = 0;
    if ( muestra == 0 ) {
        // creo y muestro el progreso del envio
        progressBar = new QProgressBar;
        progressBar->setRange(0, CANT_MUESTRAS);
        progressBar->show();
    }
    if ( ((muestra+1) == CANT_MUESTRAS) || resetFlag ) {
        if (!resetFlag) {
            // aviso que se envio todo OK
            QMessageBox::critical(this, tr("Success"), "Se envio la imagen correctamente");
        }
        muestra = 0;
        progressBar->hide();
        delete progressBar;
        return;
    }

    progressBar->setValue(static_cast<int>(muestra));     // actualizo el progreso de la barra
    m_serial->write("@");   // inicio de trama
    for ( unsigned int j=0 ; j<CANT_LEDS ; j++ ) {
        QByteArray byteArray = myImage->getColorsOf(muestra, j);
        m_serial->write(byteArray);
    }
    // espero recibir una trama del tipo: |‘@’|24G|‘#’|
    QByteArray stringWeExpect = "@"; stringWeExpect.append(myImage->getColorsOf(muestra, CANT_LEDS-1).at(1)); stringWeExpect.append("#");
    checkResponse(stringWeExpect);

    muestra++;
}

void MainWindow::on_loadImage_Btn_clicked()
{
    open();
    checkInputs();
}

void MainWindow::on_updateChannels_Btn_clicked()
{
    updateCOMChannels();
    checkInputs();
}

void MainWindow::on_sendImage_Btn_clicked()
{
    sendTrama();
}

void MainWindow::on_connect_Btn_clicked()
{
    openSerialPort(ui->comChannels_ComboBox->currentText());
    checkInputs();
}

void MainWindow::on_disconnect_Btn_clicked()
{
    closeSerialPort();
    checkInputs();
}
