import enum
import math
from pathlib import Path
import random
import sys
from typing import TYPE_CHECKING 

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import numpy as np
from canvas.model import CanvasModel
from canvas.pse_widget import PSEDialog, PSEWidget
from canvas.view import CanvasView
from transf import Transf
from ui_utils import keyevent_to_keys

if TYPE_CHECKING:
    from app import ChemApp

from core import Atom,Bond,Angle,Mol,rot_2d
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

class Mode(enum.Enum):
    ATOM = "atom"
    SINGLE_BOND = "single_bond"
    DOUBLE_BOND = "double_bond"
    TRIPLE_BOND = "triple_bond"
    RECT_SELECT = "rect_select"
    TRANSLATE = "translate"


    def is_bond_mode(self) -> bool:
        return self in [Mode.SINGLE_BOND,Mode.DOUBLE_BOND,Mode.TRIPLE_BOND]

    def to_bond_order(self) -> int:
        assert self.is_bond_mode(), "attempted to convert non-bond mode to bond order!"
        return {Mode.SINGLE_BOND: 1, Mode.DOUBLE_BOND: 2, Mode.TRIPLE_BOND: 3,}[self]


class ModeButton(QtWidgets.QPushButton):
    def __init__(self,mode:Mode,app:"ChemApp"):
        super().__init__()
        self.w = 24
        self.h = 24
        self.setFixedSize(QtCore.QSize(self.w,self.h))
        self.mode = mode
        self.app = app
        
        self.clicked.connect(self._update_app_mode)


    def _update_app_mode(self):
        assert hasattr(self.app.canvas, "current_mode")
        self.app.canvas.current_mode = self.mode
        if self.mode.is_bond_mode():
            self.app.canvas.model.current_bond_order = self.mode.to_bond_order()

        if self.mode == Mode.ATOM:
            pse = PSEDialog(self.app.canvas.model.current_atom_symbol,parent=self)
            pse.exec()
            self.app.canvas.model.current_atom_symbol = pse.current_atom_symbol
        
        self.app.update()


    def paintEvent(self, evt: QtGui.QPaintEvent) -> None:
        # TODO: refactor as "proper OOP design"
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        brush = QtGui.QBrush()
        pen = QtGui.QPen()
        pen.setWidth(2)
        pen.setColor(QtGui.QColor("black"))
        painter.setPen(pen)

        bg_color = "yellow" if self.app.canvas.current_mode == self.mode else "white"
        brush.setColor(QtGui.QColor(bg_color))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        rect = QtCore.QRect(0,0,painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)

        painter.setPen(pen)
        painter.drawRect(rect)

        w = round(self.width())
        h = round(self.height())

        pad = 2
        if self.mode == Mode.ATOM:
            painter.drawText(
                w//2-10,h//2-10,20,20,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                self.app.canvas.model.current_atom_symbol,
                )

        elif self.mode == Mode.SINGLE_BOND:
            painter.drawLine(pad,pad,w-pad,h-pad) 

        elif self.mode == Mode.DOUBLE_BOND:
            painter.drawLine(pad-4,pad,w-pad-4,h-pad) 
            painter.drawLine(pad+4,pad,w-pad+4,h-pad)

        elif self.mode == Mode.TRIPLE_BOND:
            painter.drawLine(pad-5,pad,w-pad-5,h-pad) 
            painter.drawLine(pad,pad,w-pad,h-pad) 
            painter.drawLine(pad+5,pad,w-pad+5,h-pad)

        elif self.mode == Mode.RECT_SELECT:
            pen.setStyle(Qt.PenStyle.DotLine)
            painter.setPen(pen)
            pad = 4
            painter.drawRect(pad,pad,w-pad*2,h-pad*2)

        elif self.mode == Mode.TRANSLATE:
            pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawLine(QtCore.QLineF(pad,h/2,w-pad,h/2))
            painter.drawLine(QtCore.QLineF(w/2,pad,w/2,h-pad))
            d = 3
            # arrow tips horizontal
            painter.drawLine(QtCore.QLineF(pad,h/2,pad+d,h/2+d))
            painter.drawLine(QtCore.QLineF(pad,h/2,pad+d,h/2-d))
            painter.drawLine(QtCore.QLineF(w-pad,h/2,w-pad-d,h/2-d))
            painter.drawLine(QtCore.QLineF(w-pad,h/2,w-pad-d,h/2+d))

            # arrow tips vertical
            painter.drawLine(QtCore.QLineF(w/2,pad,w/2+d,pad+d,))
            painter.drawLine(QtCore.QLineF(w/2,pad,w/2-d,pad+d,))
            painter.drawLine(QtCore.QLineF(w/2,h-pad,w/2-d,h-pad-d,))
            painter.drawLine(QtCore.QLineF(w/2,h-pad,w/2+d,h-pad-d,))
        
        else:
            assert False, f"Unknown mode {self.mode}"
        
        painter.end()

    