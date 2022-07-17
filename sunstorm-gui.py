import cmd
import os
import sys

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
    from gui import Ui_MainWindow
    from applescript import tell
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

        dep = dependencies()
        #dep = None
        #QMessageBox.critical(self, "Error!", f"Dependency check stopped")
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

            path = os.path.abspath(os.getcwd())

            if not os.path.exists(f"{os.path.dirname(os.path.abspath(__file__))}/"):
                QMessageBox.critical(self, "Error!", "sunst0rm was not found in current path.")
                return

            command = f"{sys.executable} {path}/sunstorm.py {args}"

            QMessageBox.critical(self, "Warning!", "Connect your device already in DFU mode with sigchecks removed before proceeding")

            tell.app( 'Terminal', 'do script "' + command + '"') 


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

            command = f"{sys.executable} {os.path.abspath(os.getcwd())}sunstorm.py {args}"

            QMessageBox.critical(self, "Warning!", "After this script finishes, put your device into pwndfu with sigchecks removed again and run \"boot.sh\"")

            tell.app( 'Terminal', 'do script "' + command + '"') 
        

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
