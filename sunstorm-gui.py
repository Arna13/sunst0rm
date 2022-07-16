import os
import sys
import io
import subprocess
import threading

try:
    from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QFileDialog, QMessageBox
    from PyQt5 import QtCore
    from PyQt5.QtCore import QObject, QThread, pyqtSignal
    from gui import Ui_MainWindow
    from restore_gui import Ui_RestoreDialog
    from boot_gui import Ui_BootDialog

except ImportError:
    if input("Requirements not satisfied, please install the pip requirements.\nTry and install automatically? (y/n) ") == "y":
        try:
            os.system("pip3 install -r requirements.txt")
        except Exception:
            print("Error automatically installing requirements, please install them manually.")
            quit()
        
        print("Please restart sunst0rm")
    

class QtGui(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #dep = dependencies()
        dep = None
        QMessageBox.critical(self, "Error!", f"Dependency check stopped")
        if dep != None:
            QMessageBox.critical(self, "Error!", f"{dep} not found, please install it.")
            quit()

    def StartButton_clicked(self):
        ipsw = self.ui.IPSWLineEdit.text()
        blob = self.ui.BlobLineEdit.text()
        boardconfig = self.ui.BoardConfigLineEdit.text().lower()
        
        if self.ui.RestoreMode.isChecked():
            if ipsw == "":
                QMessageBox.critical(self, "Error!", "No IPSW file specified")
                return
            elif blob == "":
                QMessageBox.critical(self, "Error!", "No blob file specified")
                return
            elif boardconfig == "":
                QMessageBox.critical(self, "Error!", "No BoardConfig specified.")
                return


            file_exists = os.path.exists(ipsw)
            if not file_exists:
                QMessageBox.critical(self, "Error!", "The specified IPSW file does not exist.")
                return
            if not ipsw.endswith(".ipsw"):
                QMessageBox.warning(self, "Warning!", "Your IPSW file is not a file ending in .ipsw\nThis can cause errors in the execution and it is recommended to choose a file ending in .ipsw")


            file_exists = os.path.exists(blob)
            if not file_exists:
                QMessageBox.critical(self, "Error!", "The specified blob file does not exist.")
                return

            args = f"-i {ipsw} -t {blob} -r -d {boardconfig}"

            if self.ui.KPPCheckBox.isChecked():
                args += " --kpp"
            if self.ui.LegacyCheckBox.isChecked():
                args += " --legacy"
            if self.ui.SkipBasebandCheckBox.isChecked():
                args += " --skip-baseband"

            print(f"Starting sunst0rm: {sys.executable} sunstorm.py {args}")

            file_exists = os.path.exists("./sunstorm_command.sh")
            if file_exists:
                os.remove("./sunstorm_command.sh")
            with open("sunstorm_command.sh", "x") as f:
                f.write(f"{sys.executable} sunstorm.py {args}")
                f.close()

            dlg = RestoreDialog(self)
            dlg.exec()

            os.remove("./sunstorm_command.sh")


        elif self.ui.BootMode.isChecked():
            identifier = self.ui.IdentifierLineEdit.text()

            if ipsw == "":
                QMessageBox.critical(self, "Error!", "No IPSW file specified")
                return
            elif blob == "":
                QMessageBox.critical(self, "Error!", "No blob file specified")
                return
            elif boardconfig == "":
                QMessageBox.critical(self, "Error!", "No BoardConfig specified.")
                return
            elif identifier == "":
                QMessageBox.critical(self, "Error!", "No Identifer specified.")
                return


            file_exists = os.path.exists(ipsw)
            if not file_exists:
                QMessageBox.critical(self, "Error!", "The specified IPSW file does not exist.")
                return
            if not ipsw.endswith(".ipsw"):
                QMessageBox.warning(self, "Warning!", "Your IPSW file is not a file ending in .ipsw\nThis can cause errors in the execution and it is recommended to choose a file ending in .ipsw")


            file_exists = os.path.exists(blob)
            if not file_exists:
                QMessageBox.critical(self, "Error!", "The specified blob file does not exist.")
                return

            args = f"-i {ipsw} -t {blob} -b -d {boardconfig} -id {identifier}"

            if self.ui.KPPCheckBox.isChecked():
                args += " --kpp"
            if self.ui.LegacyCheckBox.isChecked():
                args += " --legacy"

            print(f"Starting sunst0rm: {sys.executable} sunstorm.py {args}")

            file_exists = os.path.exists("./sunstorm_boot.sh")
            if file_exists:
                os.remove("./sunstorm_boot.sh")
            with open("sunstorm_boot.sh", "x") as f:
                f.write(f"{sys.executable} sunstorm.py {args}")
                f.write(f"sh boot.sh")
                f.close()

            dlg = BootDialog(self)
            dlg.exec()

            os.remove("./sunstorm_boot.sh")
        

    def IPSWPath_clicked(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","IPSW Files (*.ipsw);;All Files (*)", options=options)
        if fileName:
            self.ui.IPSWLineEdit.setText(fileName)

    def BlobPath_clicked(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","SHSH2 Files (*.shsh2);;All Files (*)", options=options)
        if fileName:
            self.ui.BlobLineEdit.setText(fileName)
            
class RestoreDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.restoreui = Ui_RestoreDialog()
        self.restoreui.setupUi(self)

        with open("sunstorm_command.sh", "r") as f:
                cmd = f.read()
                f.close()
        self.restoreui.RestoreTextEdit.append(f"Restoring now with: {cmd}\n")

        global proc
        proc = subprocess.Popen(['sh ','./sunstorm_command.sh'],stdout=subprocess.PIPE)

        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            print(line)

        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

        self.restoreui.CancelButton.setEnabled(False)

        self.thread.finished.connect(
            lambda: print("AAAAAAAAAAAAAAAA")
        )

    def CancelButton_clicked(self):
        self.restoreui.CancelButton.setEnabled(False)
        proc.terminate()
        print("Subprocess stopped!")
        RestoreDialog.reject(self)

class BootDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bootui = Ui_BootDialog()
        self.bootui.setupUi(self)

        with open("sunstorm_boot.sh", "r") as f:
                cmd = f.read()
                f.close()
        self.bootui.BootTextEdit.append(f"Booting now with: {cmd}\n")

        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardOutput.connect(self.stdoutReady)
        self.process.readyReadStandardError.connect(self.stderrReady)

        self.process.start("sh", ["sunstorm_boot.sh"])

    def CancelButton_clicked(self):
            self.bootui.CancelButton.setEnabled(False)
            self.process.kill()
            print("Killed process")
            BootDialog.reject(self)

    def append(self, text):
        self.bootui.BootTextEdit.append(text)

    def stdoutReady(self):
        text = str(self.process.readAllStandardOutput(), 'utf-8')
        self.append(text)

    def stderrReady(self):
        text = str(self.process.readAllStandardError(), 'utf-8')
        self.append(text)


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        global proc
        fnsh = False
        print("thread running")
        while not fnsh:
            try:
                poll = proc.poll()
            except:
                pass
            if poll is not None:
                fnsh = True
                self.finished.emit()
                

def main_gui():
    app = QApplication(sys.argv)

    win = QtGui()
    win.show()

    sys.exit(app.exec())

def dependencies():
    if not os.path.exists('/usr/local/bin/futurerestore'):
        return "futurerestore"
    if not os.path.exists('/usr/local/bin/img4tool'):
        return "img4tool"
    if not os.path.exists('/usr/local/bin/img4'):
        return "img4"
    if not os.path.exists('/usr/local/bin/Kernel64Patcher'):
        return "Kernel64Patcher"
    if not os.path.exists('/usr/local/bin/iBoot64Patcher'):
        return "iBoot64Patcher"
    if not os.path.exists('/usr/local/bin/ldid'):
        return "ldid"
    if not os.path.exists('/usr/local/bin/asr64_patcher'):
        return "asr64_patcher"
    if not os.path.exists('/usr/local/bin/restored_external64_patcher'):
        return "restored_external64_patcher"
    
if __name__ == '__main__':
    #print("sunst0rm")
    #print("Made by mineek")
    #print("Some code by m1n1exploit")
    main_gui()
