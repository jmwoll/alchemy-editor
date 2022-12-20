from pathlib import Path
import pandas as pd
from dataclasses import dataclass


@dataclass
class ChemElt:
    atomic_number:int
    element:str
    symbol:str
    period:int
    group:int
    valence:int


class PSE:
    """
    A utility class for accessing the periodic table.

    >>> pse = PSE()
    >>> pse.elements[0]
    ChemElt(atomic_number=1, element='Hydrogen', symbol='H', period=1, group=1.0, valence=1.0)

    """
    def __init__(self) -> None:
        self.elements:list[ChemElt] = []
        self.setup()

    def setup(self):
        here = Path(__file__).parent
        csv = here.parent / "assets" / "pse.csv"
        assert csv.exists()
        data = pd.read_csv(csv)
        self.elements = []
        for _,row in data.iterrows():
            elt = ChemElt(
                atomic_number=row["AtomicNumber"],
                element=row["Element"],
                symbol=row["Symbol"],
                period=row["Period"],
                group=row["Group"],
                valence=row["NumberofValence"],
            )
            if str(elt.group) == "nan":continue
            if str(elt.period) == "nan":continue
            self.elements.append(elt)


