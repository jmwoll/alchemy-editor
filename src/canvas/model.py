
import enum
import math
from pathlib import Path
import random
import sys
from typing import TYPE_CHECKING, Optional 

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
import numpy as np

if TYPE_CHECKING:
    from app import ChemApp

from core import Atom,Bond,Angle, DocItem,Mol, Rect, debug_trace, eucl_dist,rot_2d


class CanvasModel:

    BOND_LENGTH = 30

    def __init__(self) -> None:
        self.mols:list[Mol] = [] 
        self.active_bond = None
        self.selection_rectangle = None
        self.selection = []
        self.delta_coords = 5
        self.current_atom_symbol = 'C'
        self.current_bond_order = 1
        self.bond_constraint_slack = 20

    def document_items(self) -> list[DocItem]:
        for mol in self.mols:
            for atm in mol.atoms:
                yield atm
            for bnd in mol.bonds:
                yield bnd

    
    def doc_item_near_pos(self, p_mouse:np.array, ) -> Optional[DocItem]:
        hit = None
        delta_max = 10
        best_dist = 10000000
        for mol in self.mols:

            for atm in mol.atoms:
                dist = eucl_dist(atm.pos,p_mouse)
                if dist < delta_max and dist < best_dist:
                    hit = atm
                    best_dist = dist

            for bnd in mol.bonds:
                dist = eucl_dist(bnd.center_pos(),p_mouse)
                if dist < delta_max and dist < best_dist:
                    hit = bnd
                    best_dist = dist
        return hit


    def find_mol_and_atom_at_point(self, xp, yp, delta_max=100,):
        atm_found, mol_found = None, None
        min_delta = 100000
        for mol in self.mols:
            for atm in mol.atoms:
                x,y = atm.x(),atm.y()
                dx,dy = (x-xp),(y-yp)
                delta = dx**2 + dy**2
                if delta < delta_max and delta < min_delta:
                    min_delta = delta
                    atm_found = atm
                    mol_found = mol
        return mol_found,atm_found

    def acceptable_angle(self,ang:Angle):
        ang = abs(round(ang.enclosed_angle()))
        return ang in [30*i for i in range(12+1)]

    
    def preview_new_bond(self, x1, y1, x2, y2, commit_action,):
        mol_from,atm_from = self.find_mol_and_atom_at_point(x1,y1)
        mol_to,atm_to = self.find_mol_and_atom_at_point(x2,y2)

        absolute_angle_constraints = False
        if not atm_from:

            atm_from = Atom(self.current_atom_symbol,np.array([x1,y1]))
            mol_from = Mol(atoms=[atm_from,])

            # There is no starting point for this bond.
            # Therefore this is a "starting bond".
            # This will happen when the user starts a completely
            # new molecule, so often just after starting the program
            # when beginning to draw.
            # The important thing to note in that case is:
            # normally we will operate with relative angle constraints.
            # But only in this case, the user obviously wants to start
            # out with a nice absolute orientation of his initial
            # bond line:
            absolute_angle_constraints = True 

        if not atm_to:
            x12, y12 = x2-x1, y2-y1

            user_angle = round(math.degrees(math.atan2(x12,y12)))

            b = atm_from
            b_neighs = mol_from.neighboring_atoms(atm_from)

            stop_outer_loop = False
            for angle_candidate_amount in list(range(0,self.bond_constraint_slack+1)):
                for angle_dir in [1,-1]:
                    angle_candidate = angle_dir * angle_candidate_amount
                    probe = np.array([0.,1.]) 
                    probe = rot_2d(probe,-(math.radians(angle_candidate) + math.radians(user_angle)))
                    probe *= self.BOND_LENGTH
                
                    c = Atom(self.current_atom_symbol,atm_from.pos + probe)

                    if angle_candidate_amount == 0:
                        atm_to = c

                    if absolute_angle_constraints:
                        overall_angle = abs(round(math.degrees(math.atan2(probe[0],probe[1]))))
                        if overall_angle in [30*i for i in range(12+1)]:
                            atm_to = c
                            stop_outer_loop = True 
                            break
                    else:
                        relevant_angles = [Angle(a,b,c) for a in b_neighs]


                        if all(self.acceptable_angle(rel_angle) for rel_angle in relevant_angles):
                            atm_to = c
                            stop_outer_loop = True
                            break

                if stop_outer_loop: 
                    break

            # Because atm_to did not exist before, we know
            # that we have to create a new molecule with
            # only this new atom where the user points at.
            mol_to = Mol(atoms=[atm_to,])

        active_bond = Bond(fst=atm_from,snd=atm_to,order=self.current_bond_order,)
        if commit_action:
            if mol_from == mol_to:
                mol_from.bonds.append(active_bond)
                self.active_bond = None
            else:
                mol_merged = Mol.merge_molecules(mol_from,mol_to)
                mol_merged.bonds.append(active_bond)
                self.mols = [mol for mol in self.mols if mol not in [mol_from,mol_to,]]
                self.mols.append(mol_merged)
                self.active_bond = None
        else:
            # we are still in preview mode
            self.active_bond = active_bond

    
    def translate(self, dx:float, dy:float,):

        for itm in self.selection:
            itm:DocItem
            itm.translate(dx,dy)

    def commit_translate(self):
        for itm in self.selection:
            itm:DocItem
            itm.commit_translate()


    def preview_rect_select(self,
            x1:float, y1:float,
            x2:float, y2:float,
            add_to_selection:bool,
            commit_action:bool,):

        if not add_to_selection:
            self.selection = []
        selection_rectangle = Rect([x1,y1,x2,y2])
        self.selection_rectangle = selection_rectangle

        if commit_action:
            for itm in self.document_items():
                if itm.within_rectangle(selection_rectangle) and itm not in self.selection:
                    self.selection.append(itm)
            self.selection_rectangle = None
