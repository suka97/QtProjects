# pyinstaller.exe .\giseapi.py --onefile --icon=logo.ico --log-level=DEBUG --add-data "mainwindow.ui;." --add-data "logo.jpg;." --noconsole 


from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import sys, webbrowser, apis, time
from os import listdir
from os.path import isfile, join, splitext, basename, exists
from shutil import copyfile


# pyinstaller path
try:
    sys_path = sys._MEIPASS
except:
    sys_path = '.'


# Worker for long taks
class Worker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal()
    progress = pyqtSignal(int, str)
    params = {}
    progress_index = 0
    running = False

    def isRunning(self):
        return self.running

    def cancelar(self):
        self.running = False

    # carpetas, access_token, desc, precio, unidades, categoria, altura, ancho, prof
    def setParams(self, parametros):
        self.params = parametros

    def run(self):
        self.running = True
        self.progress_index = 0
        for carpeta in self.params['carpetas']:
            nombre_carpeta = basename(carpeta)
            self.progress.emit(self.progress_index, "####### "+nombre_carpeta+" #######")
            imagenes = [f for f in listdir(carpeta) if isfile(join(carpeta, f))]
            for imagen in imagenes:
                articulo = splitext(imagen)[0]
                self.progress.emit(self.progress_index, imagen)
                upload_error = True
                while upload_error and self.running:
                    tmp_file = sys_path+'/temp'+splitext(imagen)[1]
                    try:
                        copyfile(join(carpeta,imagen), tmp_file)
                        ninja_resp = apis.upload_ninja( tmp_file )
                        ml_id = apis.publicar(self.params['access_token'], nombre_carpeta, articulo, ninja_resp, 
                            self.params['tituloPrepend'],
                            self.params['desc'], self.params['precio'], self.params['unidades'], self.params['categoria'],
                            self.params['altura'], self.params['ancho'], self.params['prof']
                            )
                        self.progress.emit(self.progress_index, '-> '+ml_id)
                        upload_error = False
                    except:
                        self.progress.emit(self.progress_index, 'ERROR SUBIDA... REINTENTANDO')
                        time.sleep(2)
                        pass
                self.progress_index += 1
                if not self.running: return
        self.progress.emit(self.progress_index, '')
        self.finished.emit()


class Ui(QtWidgets.QMainWindow):
    accessToken = ''
    running = False
    cancelado = False

    def __init__(self):
        # ui init
        super(Ui, self).__init__()
        uic.loadUi(sys_path+'\mainwindow.ui', self)
        self.setWindowTitle('GiseAPI')
        self.setWindowIcon(QIcon(sys_path+'\logo.jpg'))
        # buttons connect
        self.token_btn.clicked.connect(self.onClick_token_btn)
        self.carpeta_btn.clicked.connect(self.onClick_carpeta_btn)
        self.verificar_btn.clicked.connect(self.onClick_verificar_btn)
        self.publicar_btn.clicked.connect(self.onClick_publicar_btn)
        self.show()        

    def initWorkerThread(self):
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.reportProgress)
        self.worker.error.connect(self.onPublicar_error)
        self.thread.finished.connect(self.onPublicar_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.running = True

    def onClick_token_btn(self):
        webbrowser.get().open('http://auth.mercadolibre.com.ar/authorization?response_type=code&client_id=5949631012072735&redirect_uri=https://ingia.com.ar/testAPI/giseAPI/')

    def onClick_carpeta_btn(self):
        self.carpeta_text.setText(QtWidgets.QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta"))

    def onClick_verificar_btn(self):
        self.accessToken = apis.ml_getAccessToken(self.token_text.text())
        if self.accessToken.startswith('APP_USR'):
            self.log_text.append('ML TOKEN: ' + self.accessToken)
            self.publicar_btn.setEnabled(True)
            self.verificar_btn.setEnabled(False)
            self.token_btn.setEnabled(False)
            self.token_text.setEnabled(False)
        else:
            self.log_text.append('TOKEN INVALIDO')

    def onClick_publicar_btn(self):
        if not self.running :
            self.publicar()
        else :
            self.worker.cancelar()
            self.thread.exit()
            self.running = False
            self.publicar_btn.setText('Publicar')
            self.config_groupBox.setEnabled(True)
            self.progressBar.setEnabled(False)
            self.cancelado = True

    def onPublicar_finished(self):
        self.running = False
        self.thread.exit()
        self.publicar_btn.setText('Publicar')
        self.config_groupBox.setEnabled(True)
        self.progressBar.setEnabled(False)
        if not self.cancelado:
            self.cancelado = False
            msg = QtWidgets.QMessageBox()
            msg.information(self,'Productos Subidos', 'Ya están todos bombón😘')

    def onPublicar_error(self):
        msg = QtWidgets.QMessageBox()
        msg.critical(self,'Error', 'Error de subida')
        self.worker.cancelar()
        self.publicar_btn.setText('Publicar')
        self.config_groupBox.setEnabled(True)
        self.progressBar.setEnabled(False)
        self.running = False

    def reportProgress(self, n, log_text):
        self.progressBar.setValue(n)
        self.log_text.append(log_text)


    def publicar(self):
        rootPath = self.carpeta_text.text()
        msg = QtWidgets.QMessageBox()
        if not exists(rootPath):
            msg.critical(self,'Carpeta Invalida', 'Carpeta "'+rootPath+'" invalida')
            return
        carpetas = [join(rootPath,f) for f in listdir(rootPath) if not isfile(join(rootPath, f))]
        # cuento productos
        cantProductos = 0
        for carpeta in carpetas:
            imagenes = [f for f in listdir(carpeta) if isfile(join(carpeta, f))]
            for imagen in imagenes: 
                nombre = self.tituloPrepend_text.text() + ' ' + basename(carpeta) + ' ' + splitext(imagen)[0]
                if len(nombre) > 60:
                    msg.critical(self,'Nombre muy largo', 'Se te fue la mano con el nombre bombón 😢\n\n' + nombre)
                    return
                cantProductos += 1
        # pregunto confirmacion
        respuesta = msg.question(self,'Confirmación', '¿Estas segura de subir '+str(cantProductos)+' productos?', msg.Yes | msg.No)
        if respuesta == msg.Yes:
            self.progressBar.setMaximum(cantProductos)
            self.progressBar.setEnabled(True)
            self.config_groupBox.setEnabled(False)
            self.publicar_btn.setText('Cancelar')
            self.worker = Worker()
            self.worker.setParams({
                'access_token' : self.accessToken,
                'carpetas' : carpetas,
                'tituloPrepend' : self.tituloPrepend_text.text(),
                'desc' : self.desc_text.toPlainText(),
                'precio' : self.precio_text.text(),
                'unidades' : self.unidades_text.text(),
                'categoria' : self.categoria_text.text(),
                'altura' : self.altura_text.text(),
                'ancho' : self.ancho_text.text(),
                'prof' : self.prof_text.text()
            })
            self.initWorkerThread()



app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
