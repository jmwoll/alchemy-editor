
import enum
import math
from pathlib import Path
import random
import sys
from typing import TYPE_CHECKING 

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import numpy as np

from transf import Transf

if TYPE_CHECKING:
    from canvas.controller import CanvasController

from core import Atom,Bond,Angle,Mol, debug_trace,rot_2d


class ChemStyle:
    # TODO: this class is going to be where all the styling goes
    # TODO: in the long run. note that also e.g. bond spacing
    # TODO: should be considered part of the styling.
    # TODO: it would be really great if we could have several
    # TODO: different subclasses of ChemStyle, e.g. ACSChemStyle
    double_bond_spread = 3
    triple_bond_spread = 4

class CanvasView:

    def __init__(self) -> None:
        self.chem_style = ChemStyle()
        self.pen_color = QtGui.QColor("#000000")
        self.transf = Transf()

    def set_pen_color(self, c):
        self.pen_color = QtGui.QColor(c)


    def _draw_line(self,painter,a,b):
        ax,ay = float(a[0]),float(a[1])
        bx,by = float(b[0]),float(b[1])
        ax,ay = self.transf.forward(ax,ay)
        bx,by = self.transf.forward(bx,by)
        painter.drawLine(QtCore.QLineF(ax,ay,bx,by))

    def _draw_bond(self, bond:Bond, painter):
        eta = 0.0001
        atm1, atm2 = bond.fst, bond.snd
        v_1 = np.array([atm1.x(), atm1.y()])
        v_2 = np.array([atm2.x(), atm2.y()])
        v_12 = v_2 - v_1
        v_orth = rot_2d(v_12,math.radians(90))
        norm_vo = np.linalg.norm(v_orth)
        if norm_vo < eta:
            norm_vo = eta

        v_orth = v_orth / norm_vo

        if bond.order == 1:
            self._draw_line(painter,v_1,v_2)

        if bond.order == 2:
            dbs = self.chem_style.double_bond_spread
            self._draw_line(painter,v_1+dbs*v_orth,v_2+dbs*v_orth)
            self._draw_line(painter,v_1-dbs*v_orth,v_2-dbs*v_orth)

        if bond.order == 3:
            tbs = self.chem_style.triple_bond_spread
            self._draw_line(painter,v_1+tbs*v_orth,v_2+tbs*v_orth)
            self._draw_line(painter,v_1-tbs*v_orth,v_2-tbs*v_orth)
            self._draw_line(painter,v_1,v_2)

    



    def paintEvent(self,
            ev: QtGui.QPaintEvent,
            controller: "CanvasController",
            ) -> None:
        self.transf = controller.transf
        painter = QtGui.QPainter(controller)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        brush = QtGui.QBrush()
        pen = QtGui.QPen()
        pen.setWidth(2)
        pen.setColor(QtGui.QColor("black"))
        painter.setPen(pen)

        brush.setColor(QtGui.QColor("white"))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        rect = QtCore.QRect(0,0,painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)

        zoomf = self.transf.zoom_factor()
        f = painter.font()
        f.setPointSizeF(f.pointSizeF() * zoomf)
        painter.setFont(f)
        fm = QtGui.QFontMetrics(f)
        for mol in controller.model.mols:
            for bond in mol.bonds:
                if bond in controller.model.selection:
                    pen.setColor(QtGui.QColor("blue"))
                elif bond.is_hovered():
                    pen.setColor(QtGui.QColor("red"))
                else:
                    pen.setColor(QtGui.QColor("black"))
                painter.setPen(pen)
                self._draw_bond(bond,painter)

            for atm in mol.atoms:
                ax,ay = self.transf.forward(atm.x(),atm.y())
                if mol.is_explicit_atom(atm):
                    # We want to draw the atom symbol:
                    # at position of atom (ax,ay):
                    text = atm.symbol
                    # Furthermore, we need to vertically and horizontally
                    # center the atom symbol. To achieve this, we get
                    # the bounding rect of the text using font metrics:
                    text_rect = QtCore.QRectF(fm.tightBoundingRect(text))
                    text_width = text_rect.width()
                    text_height = text_rect.height()
                    text_rect.translate(ax-text_width/2,ay+text_height/2)

                    # If bonds are drawn from an explicit atom, then
                    # the bonds would draw over the atom label leading to
                    # lines clashing with each other. To avoid this effect,
                    # we paint a white rectangle behind the symbol that will
                    # remove any possible bonds.
                    # This also includes some small amount of padding to
                    # visually separate the atom symbols from the bond lines:
                    atom_pad = 0.5
                    text_back_rect = QtCore.QRectF(text_rect)
                    text_back_rect.setWidth(text_back_rect.width() * (1 + 2*atom_pad))
                    text_back_rect.setHeight(text_back_rect.height() * (1 + 2*atom_pad))
                    text_back_rect.translate(-text_back_rect.width() * atom_pad/2, -text_back_rect.height() * atom_pad/2)
                    brush.setColor(QtGui.QColor("white"))
                    painter.fillRect(text_back_rect,brush)

                    if atm in controller.model.selection:
                        pen.setColor(QtGui.QColor("blue"))
                    elif atm.is_hovered():
                        pen.setColor(QtGui.QColor("red"))
                    else:
                        pen.setColor(QtGui.QColor("black"))
                    painter.setPen(pen)
                    painter.drawText(
                        text_rect,
                        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                        atm.symbol)

                else: # implicit atom
                    if atm.is_hovered():
                        # The user hovered over an implicit atom.
                        # We will display a little circle to notify
                        # the user that we registered the hovering
                        # over this atom:
                        r = QtCore.QRectF(ax-3,ay-3,6,6)
                        hov_col = QtGui.QColor(255,0,0)
                        brush.setColor(hov_col)
                        painter.setBrush(brush)
                        pen.setColor(hov_col)
                        painter.setPen(pen)
                        painter.drawEllipse(r,)
            
        pen.setWidth(2)
        pen.setColor(QtGui.QColor("red"))
        active_bond = controller.model.active_bond
        if active_bond:
            painter.setPen(pen)
            self._draw_bond(active_bond,painter)

        if controller.model.selection_rectangle:
            pen = QtGui.QPen()
            pen.setWidth(2)
            pen.setColor(QtGui.QColor("black"))
            pen.setStyle(Qt.PenStyle.DotLine)
            painter.setPen(pen)
            x1,y1,x2,y2 = controller.model.selection_rectangle.points.reshape(-1)
            x1,y1 = controller.transf.forward(x1,y1)
            x2,y2 = controller.transf.forward(x2,y2)
            qr:QtCore.QRectF = QtCore.QRectF(float(x1),float(y1),float(x2-x1),float(y2-y1))
            painter.drawRect(qr)#x1,y1,x2-x1,y2-y1)

        painter.end()