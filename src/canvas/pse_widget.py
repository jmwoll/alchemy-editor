from PyQt5 import QtGui,QtCore,Qt,QtWidgets

from core import debug_trace
from pse import PSE, ChemElt


class PSEWidget(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.w = 400
        self.h = 300
        self.setFixedSize(QtCore.QSize(self.w,self.h))


    def paintEvent(self, evt: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        brush = QtGui.QBrush()
        pen = QtGui.QPen()
        pen.setWidth(2)
        pen.setColor(QtGui.QColor("black"))
        painter.setPen(pen)

        bg_color = "green" 
        brush.setColor(QtGui.QColor(bg_color))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        rect = QtCore.QRect(0,0,painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)
        
        painter.end()


class PSECloseElt(QtWidgets.QLabel):
    # Button that closes the PSE view
    clicked=QtCore.pyqtSignal()

    def __init__(self,parent):
        super().__init__(parent=parent,text='X')
        self.setStyleSheet("QWidget { background-color : red; color: white; }")
        self.setAlignment(QtCore.Qt.AlignCenter)


    def mousePressEvent(self, ev):
        self.clicked.emit()

class PSElt(QtWidgets.QLabel):
    # Button that represents a chemical element
    clicked=QtCore.pyqtSignal()

    def __init__(self,x,y,w,h,parent,chem_elt:ChemElt):
        self.chem_elt = chem_elt
        super().__init__(parent=parent,text=chem_elt.symbol)
        self.css_active = "QWidget { background-color : red; border: 2.5px solid black;}"
        self.css_unactive = "QWidget { background-color : green; border: 0.5px solid black;}"
        self.css_hover = "QWidget { background-color : rgb(200,200,255); border: 2.5px solid black;}"
        if self.is_active_elt():
            self.setStyleSheet(self.css_active)
        else:
            self.setStyleSheet(self.css_unactive)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setGeometry(x,y,w,h)

    def is_active_elt(self) -> bool:
        parent = self._get_dlg()
        return parent.current_atom_symbol == self.chem_elt.symbol

    def _get_dlg(self)->"PSEDialog":
        parent = self.parent()
        assert isinstance(parent,PSEDialog)
        return parent

    def mousePressEvent(self, ev):
        self.clicked.emit()
        parent = self._get_dlg()
        parent.current_atom_symbol = self.chem_elt.symbol
        parent.accept()

    def enterEvent(self, evt: QtCore.QEvent) -> None:
        if not self.is_active_elt():
            self.setStyleSheet(self.css_hover)# TODO: handle selected case!
        return super().enterEvent(evt)

    def leaveEvent(self, evt: QtCore.QEvent) -> None:
        parent = self._get_dlg()
        if not self.is_active_elt():
            self.setStyleSheet(self.css_unactive) # TODO: handle selected case!
        return super().enterEvent(evt)


class PSEDialog(QtWidgets.QDialog):


    def __init__(self, current_atom_symbol, parent=None):
        self.pse = PSE()
        self.current_atom_symbol = current_atom_symbol
        self.my_w = 600
        self.my_h = 300
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.close_label = PSECloseElt(parent=self)

        pad_x = 20
        pad_y = 20
        self.close_label.setGeometry(self.my_w-pad_x,0,pad_x,pad_y)

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)


        self.pse_tab = QtWidgets.QFrame(self)
        self.pse_tab.setGeometry(pad_x,pad_y,self.my_w-pad_x*2,self.my_h-pad_y*2)
        self.ps_elts = []

        n_periods = max([e.period for e in self.pse.elements])
        n_groups = max([e.group for e in self.pse.elements])
        w_pad =(self.my_w - pad_x*2)
        h_pad =(self.my_h - pad_x*2)
        for chem_elt in self.pse.elements:
            w =  w_pad / n_groups 
            h =  h_pad / n_periods
            x = pad_x + (chem_elt.group-1) * w_pad / n_groups
            y = pad_y + (chem_elt.period-1) * h_pad / n_periods
            w,h,x,y = int(w),int(h),int(x),int(y)
            ps_elt = PSElt(x,y,w,h,parent=self,chem_elt=chem_elt)
            self.ps_elts.append(ps_elt)
        self._update_geom()
        self.close_label.clicked.connect(self.accept)

        self.setMouseTracking(True)
        



    def leaveEvent(self, evt: QtCore.QEvent) -> None:
        self.accept()
        return super().leaveEvent(evt)

    def _update_geom(self):
        par_rect:QtCore.QRect = self.parent().geometry()
        par_rect.moveTopLeft(self.parent().parent().mapToGlobal(par_rect.topLeft()));
        self.setGeometry(par_rect.x()-self.my_w,par_rect.y(),self.my_w,self.my_h)