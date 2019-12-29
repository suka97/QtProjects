#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QFileDialog>
#include <QLabel>
#include <QtSerialPort/QSerialPort>
#include <QtSerialPort/QSerialPortInfo>
#include <QMessageBox>
#include <QProgressBar>
#include "adapterqimage.h"

const int MILLIS_TIMEOUT = 10000;

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

protected:
    Ui::MainWindow *ui;
    void open();
    bool openImage(const QString &);
    void updateCOMChannels();
    void checkInputs();
    bool openSerialPort(QString);
    void closeSerialPort();
    void checkResponse(QByteArray);
    void readyRead_Handler();
    void sendTrama(bool resetFlag = false);
    AdapterQImage * myImage = nullptr;
    QSerialPort *m_serial = nullptr;
    QByteArray stringWeExpect;
    QProgressBar *progressBar;

private slots:
    void on_loadImage_Btn_clicked();
    void on_updateChannels_Btn_clicked();
    void on_sendImage_Btn_clicked();
    void on_connect_Btn_clicked();
    void on_disconnect_Btn_clicked();
};

#endif // MAINWINDOW_H
