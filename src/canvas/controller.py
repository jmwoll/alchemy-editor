import enum
import math
from pathlib import Path
import random
import sys
from typing import TYPE_CHECKING 

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import numpy as np
from canvas.drag_n_drop import DragNDrop
from canvas.mode_button import Mode
from canvas.model import CanvasModel
from canvas.pse_widget import PSEDialog, PSEWidget
from canvas.view import CanvasView
from transf import Transf
from ui_utils import keyevent_to_keys

if TYPE_CHECKING:
    from app import ChemApp

from core import Atom,Bond,Angle,Mol,rot_2d


class CanvasController(QtWidgets.QLabel):


    def __init__(self, chem_app, view, model):
        super().__init__()

        self.setMouseTracking(True)

        self.view:CanvasView = view
        self.model:CanvasModel = model

        self.current_mode = None
        self.activate_bonds_mode()

        self.drag_n_drop = DragNDrop()
        self.chem_app = chem_app

        self.transf = Transf()
        self.keys_pressed = set()


    def activate_bonds_mode(self):
        self.current_mode = Mode.SINGLE_BOND


    def _unhover_all(self):
        for item in self.model.document_items():
            item.set_hovered(False)

    def mouseDoubleClickEvent(self, evt: QtGui.QMouseEvent) -> None:
        if self.current_mode == Mode.ATOM:
            # The user double clicked in atom mode. Therefore,
            # we interpret this as the user wanting to add an
            # atom at the current position.
            # Per definition, this atom won't be connected to
            # anything else (we are not in bond mode). Hence,
            # the atom will be placed in its own molecule.
            pos = np.array(self.transf.backward(evt.x(),evt.y()))
            atm = Atom(self.model.current_atom_symbol, pos)
            mol = Mol(atoms=[atm],bonds=[])
            self.model.mols.append(mol)
            self.update()

        return super().mouseDoubleClickEvent(evt)

    
    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.buttons():
            if ev.buttons() & QtCore.Qt.LeftButton:
                dnd = self.drag_n_drop

                x,y = ev.pos().x(),ev.pos().y()
                x,y = self.transf.backward(x,y)
                if dnd.at_start():
                    dnd.start_x = x
                    dnd.start_y = y
                else:
                    dnd.end_x = x
                    dnd.end_y = y

                    if self.current_mode.is_bond_mode():
                        self.model.preview_new_bond(dnd.start_x,dnd.start_y,dnd.end_x,dnd.end_y,commit_action=False,)

                    elif self.current_mode == Mode.ATOM:
                        pass # TODO

                    elif self.current_mode == Mode.RECT_SELECT:
                        add_to_selection = 'Shift' in self.keys_pressed
                        self.model.preview_rect_select(dnd.start_x,dnd.start_y,dnd.end_x,dnd.end_y,add_to_selection=add_to_selection,commit_action=False,)
                    else:
                        assert False, f"Cannot handle mode {self.current_mode}"

            self.update()

        else: # no buttons pressed
            # As there where no buttons pressed, the user is just 
            # hovering over the canvas with his mouse. We should
            # therefore check wheter any document items are nearby
            # to the current mouse position and highlight them
            # if appropriate.
            self._unhover_all()
            pos = np.array(self.transf.backward(ev.x(),ev.y()))
            item = self.model.doc_item_near_pos(pos)

            if item:
                item.set_hovered(True)
        
        self.update()

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.buttons() & QtCore.Qt.RightButton:
            # The user right clicked on the canvas.
            # This means that the user is interested
            # in inspecting / changing the attributes
            # of an object on the canvas.
            # Therefore, the first thing that we have
            # to do is identify which object the user
            # clicked on:                
            pos = np.array(self.transf.backward(ev.x(),ev.y()))
            item = self.model.doc_item_near_pos(pos)
            if item:
                item.show_configuration_dialog()

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        dnd = self.drag_n_drop

        if dnd.ready_to_commit():

            if self.current_mode.is_bond_mode():
                self.model.preview_new_bond(dnd.start_x,dnd.start_y,dnd.end_x,dnd.end_y,commit_action=True,)
                self.active_bond = None
            elif self.current_mode == Mode.ATOM:
                pass # TODO
            elif self.current_mode == Mode.RECT_SELECT:
                add_to_selection = 'Shift' in self.keys_pressed
                self.model.preview_rect_select(dnd.start_x,dnd.start_y,dnd.end_x,dnd.end_y,add_to_selection=add_to_selection,commit_action=True,)
            else:
                assert False, f"Cannot handle mode {self.current_mode}"

            dnd.clear()

        self.update()

    
    def wheelEvent(self,event:QtGui.QWheelEvent,):
        delta = event.angleDelta().y()
        if delta > 0:
            self.transf.zoom_in()
        if delta < 0:
            self.transf.zoom_out()

        self.update()

    def paintEvent(self,
            ev: QtGui.QPaintEvent,
            ) -> None:
        self.view.paintEvent(ev=ev,controller=self,)

    def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
        self.keys_pressed = self.keys_pressed.union(keyevent_to_keys(ev))
        print(">>",self.keys_pressed)
        do_refresh = False
        if ev.key() == Qt.Key.Key_Left:
            do_refresh = True

        if ev.key() == Qt.Key.Key_Escape:
            self.model.selection = []
            do_refresh = True

        if do_refresh:
            self.update()

        return super().keyPressEvent(ev)

    def keyReleaseEvent(self, ev: QtGui.QKeyEvent) -> None:
        self.keys_pressed.difference_update(keyevent_to_keys(ev))
        print("<<R",self.keys_pressed)
        do_refresh = False
        return super().keyPressEvent(ev)




