# A simple molecular structure editor
import sys 

from PyQt5 import QtWidgets,QtGui
from canvas.controller import CanvasController
from canvas.mode_button import Mode, ModeButton
from canvas.model import CanvasModel
from canvas.view import CanvasView


class ChemApp(QtWidgets.QMainWindow):

    def __init__(self,qapp):
        self.qapp = qapp
        super().__init__()

        self.canvas = CanvasController(chem_app=self,view=CanvasView(),model=CanvasModel(),)

        w_vert = QtWidgets.QWidget()
        l_vert = QtWidgets.QVBoxLayout()
        w_vert.setLayout(l_vert)

        w_hori = QtWidgets.QWidget()
        l_hori = QtWidgets.QHBoxLayout()
        w_hori.setLayout(l_hori)

        l_hori.addWidget(self.canvas)

        palette = QtWidgets.QVBoxLayout()
        self.add_palette_buttons(palette)
        palette.addStretch()
        l_hori.addLayout(palette)

        l_vert.addWidget(w_hori)

        self.label_messages = QtWidgets.QTextEdit("")
        self.label_messages.setReadOnly(True)
        self.label_messages.setMaximumHeight(60)
        l_vert.addWidget(self.label_messages)
        self.setCentralWidget(w_vert)

        self._createMenuBar()

    def keyPressEvent(self, evt: QtGui.QKeyEvent) -> None:
        # Controller will handle them!
        self.canvas.keyPressEvent(evt)

    def keyReleaseEvent(self, evt: QtGui.QKeyEvent) -> None:
        # Controller will handle them!
        self.canvas.keyReleaseEvent(evt)

    def _createMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QtWidgets.QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        # Creating menus using a title
        editMenu = menuBar.addMenu("&Edit")
        helpMenu = menuBar.addMenu("&Help")

    def display_message(self,msg:str):
        self.label_messages.setText(msg)


    def add_palette_buttons(self, layout):
        for mode_name in Mode:
            b = ModeButton(mode_name,self)
            #b.pressed.connect(lambda c=c: self.canvas.set_pen_color(c))
            layout.addWidget(b)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = ChemApp(qapp=app)
    window.show()
    app.exec()





