from abc import abstractclassmethod
import math
from pathlib import Path 
import numpy as np

from PyQt5.QtCore import pyqtRemoveInputHook

from config_dlg import AtomConfigurationDialog

def debug_trace():
  '''Set a tracepoint in the Python debugger that works with Qt'''

  # Or for Qt5
  #from PyQt5.QtCore import pyqtRemoveInputHook

  from pdb import set_trace
  pyqtRemoveInputHook()
  set_trace()

def rot_2d(vec,angle):
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    x,y = vec[0],vec[1]
    return np.array([
        x*cos_angle - y*sin_angle,
        x*sin_angle + y*cos_angle,
    ])


def resolve_asset(asset_name:str,):
    here = Path(__file__).parent
    asset_dir = here.parent / "assets"
    assert asset_dir.exists()

    return {
        "icon__atom": asset_dir / "icons" / "atom.png",
        "icon__bond": asset_dir / "icons" / "bond.png",
    }[asset_name]


class Rect:

    """
    
    >>> r = Rect.from_coords(-2,-2,2,2)
    >>> r.contains([0,0])
    True
    >>> r.contains([1,1])
    True
    >>> r.contains([-1,-2])
    True
    >>> r.contains([-2,-2])
    True
    >>> r.contains([-2,-3])
    False

    """
    def __init__(self,points:np.ndarray) -> None:
        if isinstance(points,list) or isinstance(points,tuple):
            points = np.array(points)
        points = points.reshape((2,2))
        self.points = points

    def contains(self, point:np.ndarray) -> bool:
        if isinstance(point,list) or isinstance(point,tuple):
            point = np.array(point)
        a,b = self.points[0],self.points[1]
        return (point >= a).all() and (point <= b).all() or (point >= b).all() and (point <= a).all()


    @staticmethod
    def from_coords(x1,y1,x2,y2) -> "Rect":
        points = np.array([[x1,y1],[x2,y2]])
        return Rect(points)



def eucl_dist(v:np.ndarray,w:np.ndarray)->float:
    return float(np.linalg.norm(v-w))

class DocItem:
    def __init__(self) -> None:
        self._is_hovered = False
        self.translation = np.array([0,0])

    def within_rectangle(self,rect:Rect) -> bool:
        """
        Returns True if this doc item lies within
        the specified rectangle and False otherwise.
        """
        raise NotImplementedError()

    def show_configuration_dialog(self):
        """
        Shows a configuration dialog for this doc item.
        For example, an atom might expose the current
        atom symbol, charge, num implicit/explicit hydrogens
        et cetera.
        """
        raise NotImplementedError()

    def set_hovered(self,is_hovered:bool) -> None:
        self._is_hovered = is_hovered

    def is_hovered(self)->bool:
        return self._is_hovered

    def translate(self, dx:float, dy:float):
        self.translation = np.array([dx,dy])

    def commit_translate(self):
        raise NotImplementedError()



        


class Atom(DocItem):

    def __init__(self,symbol:str,pos:np.ndarray,) -> None:
        super().__init__()
        self.symbol = symbol
        self.pos = pos

    def x(self):
        return int(self.pos[0] + self.translation[0])

    def y(self):
        return int(self.pos[1] + self.translation[1])

    def within_rectangle(self, rect: Rect) -> bool:
        return rect.contains(self.pos)

    def show_configuration_dialog(self):
        AtomConfigurationDialog(self).show_dialog()

    def commit_translate(self):
        self.pos += self.translation
        self.translation = np.array([0.0,0.0])



class Bond(DocItem):

    def __init__(self, fst:Atom, snd:Atom, order:float) -> None:
        super().__init__()
        self.fst = fst
        self.snd = snd
        self.order = order

    def within_rectangle(self, rect: Rect) -> bool:
        return self.fst.within_rectangle(rect) and self.snd.within_rectangle(rect)

    def center_pos(self) -> np.ndarray:
        return (self.fst.pos + self.snd.pos) / 2

    def translate(self, dx: float, dy: float):
        pass 

    def commit_translate(self):
        pass

class Angle:

    """
    
    >>> a = np.array([-1,0])
    >>> b = np.array([0,0])
    >>> c = np.array([0,1])
    >>> Angle.enclosed_angle_vec(a,b,c)
    90.0
    """

    def __init__(self, a:Atom, b:Atom, c:Atom,) -> None:
        self.a,self.b,self.c = a,b,c

    def enclosed_angle(self):
        pa,pb,pc = self.a.pos,self.b.pos,self.c.pos
        return self.enclosed_angle_vec(pa,pb,pc)


    @staticmethod
    def enclosed_angle_vec(pa:np.ndarray, pb:np.ndarray, pc:np.ndarray):
        eta = 0.00001
        try:
            ab = pa-pb
            cb = pc-pb
            nom = ( np.linalg.norm(ab) * np.linalg.norm(cb))
            if nom < eta:
                nom = eta

            cos_w = np.dot(ab,cb) / nom
            cos_w = max(min(1,cos_w),-1)
            return math.degrees(math.acos(cos_w))
        except:
            import pdb; pdb.set_trace()
        
        


class Mol:
    def __init__(self, atoms=None,bonds=None,) -> None:
        if atoms is None:
            atoms = []
        if bonds is None:
            bonds = []
        self.atoms:list[Atom] = atoms
        self.bonds:list[Bond] = bonds


    def neighboring_atoms(self, atm:Atom) -> list[Atom]:
        neighs = []
        for bond in self.bonds:
            if bond.fst == atm:
                neighs.append(bond.snd)
            if bond.snd == atm:
                neighs.append(bond.fst)
        return neighs

    def is_explicit_atom(self, atm:Atom) -> bool:
        ns = self.neighboring_atoms(atm)
        if len(ns) and atm.symbol == 'C':
            # TODO: for now regarding every carbon
            # TODO: atom with neighbors as implicit
            # TODO: finer logic!
            return False

        # TODO: handle other possible implicit cases
        return True
    

    @staticmethod
    def merge_molecules(mol_a,mol_b):
        # TODO: apply deepcopy here for safety
        return Mol(atoms=mol_a.atoms+mol_b.atoms,bonds=mol_a.bonds+mol_b.bonds)
