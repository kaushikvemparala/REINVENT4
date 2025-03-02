"""Compute the PMI score in RDKit"""

from dataclasses import dataclass
from typing import List

import numpy as np
from rdkit.Chem import AllChem as Chem

from ..component_results import ComponentResults
from ..add_tag import add_tag
from reinvent_plugins.mol_cache import molcache


@add_tag("__parameters")
@dataclass
class Parameters:
    property: List[str]


@add_tag("__component")
class PMI:
    """Compute the PMI index to characterize the dimensionality of a molecule

    See https://doi.org/10.4155%2Ffmc-2016-0095
    """

    def __init__(self, params: Parameters):
        self.properties = params.property

        if not "npr1" in self.properties and not "npr2" in self.properties:
            raise RuntimeError("Need npr1 and or npr2")

    @molcache
    def __call__(self, mols: List[Chem.Mol]) -> np.array:
        scores1 = []
        scores2 = []

        for mol in mols:
            try:
                mol3d = Chem.AddHs(mol)
                Chem.EmbedMolecule(mol3d)

                npr1 = Chem.CalcNPR1(mol3d)
                npr2 = Chem.CalcNPR2(mol3d)
            except ValueError:
                npr1 = np.nan
                npr2 = np.nan

            scores1.append(npr1)
            scores2.append(npr2)

        scores = []

        if "npr1" in self.properties:
            scores.append(np.array(scores1, dtype=float))

        if "npr2" in self.properties:
            scores.append(np.array(scores2, dtype=float))

        return ComponentResults(scores)
