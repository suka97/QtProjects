#ifndef MYBUSYBAR_H
#define MYBUSYBAR_H

#include <QDialog>
#include <QProgressBar>
#include <QGridLayout>

class MyBusyBar : public QDialog
{
public:
    MyBusyBar(QString title = "Trabajando...");

private:
    QProgressBar *progressBar;
    QGridLayout *mainLayout;
};

#endif // MYBUSYBAR_H
