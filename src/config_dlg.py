from PyQt5 import QtWidgets 
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core import Atom


class AtomConfigurationDialog(QtWidgets.QDialog):

    def __init__(self, atm:"Atom",) -> None:
        super().__init__()
        self.atm = atm
        self.setWindowTitle("HELLO!")

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel("Something happened, is that OK?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def show_dialog(self,):
        self.exec()