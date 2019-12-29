#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    QGraphicsPixmapItem *image = new QGraphicsPixmapItem( QPixmap(":/MisArchivos/images.jpg") );
    int imageWidth = image->pixmap().width();
    int imageHeight = image->pixmap().height();

    image->setOffset(- imageWidth / 2, -imageHeight / 2);
    image->setPos(0, 0);

    QGraphicsScene *graphicsScene = new QGraphicsScene();
    graphicsScene->setSceneRect(-imageWidth / 2, -imageHeight / 2, imageWidth, imageHeight);

    ui->graphicsView->setScene(graphicsScene);
    ui->graphicsView->scene()->addItem(image);
}

MainWindow::~MainWindow()
{
    delete ui;
}
