# pyinstaller.exe .\gisebackup.py --onefile --icon=logo.ico --log-level=DEBUG --add-data "mainwindow.ui;." --add-data "logo.png;." --noconsole 


from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import sys, webbrowser, apis, time, json, requests, mimetypes
from os import listdir, mkdir, path

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
        
        self.progress.emit(self.progress_index, 'Contando Productos...')
        error = True
        while error and self.running:
            try:
                rta = apis.ml_getProducts(self.params['access_token'])
                self.progress.emit(len(rta), 'Encontrados '+str(len(rta))+' Productos')
                error = False
            except:
                self.progress.emit(self.progress_index, 'ERROR... REINTENTANDO')
                time.sleep(2)
                pass
        
        if ( self.running ):
            self.progress.emit(self.progress_index, 'Guardando Productos...')
            max_results = len(rta)
            for i in range(self.progress_index, max_results):
                if not self.running: break
                self.progress.emit(self.progress_index, str(i+1)+'/'+str(max_results)+'    '+rta[i])
                error = True
                max_intentos = 3
                while error and self.running:
                    try:
                         #json
                        det = apis.ml_getProductDetail(self.params['access_token'], rta[i])
                        folder = self.params['save_folder']+'/'+det['title']
                        if not path.exists(folder): mkdir(folder)
                        file = open(folder+'/datos.json', 'w')
                        file.write(json.dumps(det))
                        file.close()
                        #imagenes
                        for im_index in range(len(det['imagenes'])):
                            url = det['imagenes'][im_index]
                            response = requests.get(url)
                            content_type = response.headers['content-type']
                            ext = mimetypes.guess_extension(content_type)
                            file = open(folder+'/'+str(im_index)+ext, "wb")
                            file.write(response.content)
                            file.close()
                        self.progress_index += 1
                        error = False
                    except:
                        self.progress.emit(self.progress_index, 'ERROR... REINTENTANDO')
                        time.sleep(2)
                        if max_intentos == 0: 
                            self.progress.emit(self.progress_index, 'SALTEANDO '+rta[i]+'...')
                            error = False
                        else: max_intentos -= 1
                        pass

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
        self.setWindowTitle('GiseBackup')
        self.setWindowIcon(QIcon(sys_path+'\logo.png'))
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
            self.publicar_btn.setText('Descargar')
            self.config_groupBox.setEnabled(True)
            self.progressBar.setEnabled(False)
            self.cancelado = True

    def onPublicar_finished(self):
        self.running = False
        self.thread.exit()
        self.publicar_btn.setText('Descargar')
        self.config_groupBox.setEnabled(True)
        self.progressBar.setEnabled(False)
        if not self.cancelado:
            self.cancelado = False
            msg = QtWidgets.QMessageBox()
            msg.information(self,'Backup Realizado', 'Ya están todos bombón😘')

    def onPublicar_error(self):
        msg = QtWidgets.QMessageBox()
        msg.critical(self,'Error', 'Error de subida')
        self.worker.cancelar()
        self.publicar_btn.setText('Descargar')
        self.config_groupBox.setEnabled(True)
        self.progressBar.setEnabled(False)
        self.running = False

    def reportProgress(self, n, log_text):
        if n > self.progressBar.maximum() : self.progressBar.setMaximum(n)
        self.progressBar.setValue(n)
        self.log_text.append(log_text)

    scroll_id = ''
    def publicar(self):
        if not path.exists(self.carpeta_text.text()):
            msg = QtWidgets.QMessageBox()
            msg.critical(self,'Carpeta Invalida', 'Carpeta "'+self.carpeta_text.text()+'" invalida')
            return
        if len(listdir(self.carpeta_text.text()) ) > 0:
            msg = QtWidgets.QMessageBox()
            msg.critical(self,'Carpeta Invalida', 'La carpeta "'+self.carpeta_text.text()+'" no esta vacia')
            return
        self.progressBar.setMaximum(1)
        self.progressBar.setEnabled(True)
        self.config_groupBox.setEnabled(False)
        self.publicar_btn.setText('Cancelar')
        self.worker = Worker()
        self.worker.setParams({
            'access_token' : self.accessToken, #self.token_text.text()
            'save_folder' : self.carpeta_text.text()
        })
        self.initWorkerThread()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
