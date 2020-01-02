#include "MyBusyBar.h"

MyBusyBar::MyBusyBar(QString title) {
    progressBar = new QProgressBar(this);
    progressBar->setRange(0,0);

    mainLayout = new QGridLayout;
    mainLayout->addWidget(progressBar);
    mainLayout->setSizeConstraint(QLayout::SetMinimumSize);

    setWindowTitle(title);
    setLayout(mainLayout);
    setWindowFlags(Qt::FramelessWindowHint);
    setWindowFlags(Qt::WindowTitleHint);
}
