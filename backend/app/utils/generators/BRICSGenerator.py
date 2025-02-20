from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.BRICS import BRICSDecompose, BRICSBuild
import random

class BRICSGenerator():
  def __init__(self, random_seed = 99, verbose=False):
    self.input_types = ["smiles", "psmiles"]
    self.random_seed = random_seed
    self.verbose = verbose

  def _BRICS_decompose(self, smiles_list: list):
    break_repo = []
    if self.verbose:
      print(f"[+] Incoming molecules ...")
    #   display(Draw.MolsToGridImage([Chem.MolFromSmiles(b) for b in smiles_list], molsPerRow=5, subImgSize=(200, 200)))
      print(f"[+] Decomposing the molecules ...")
    for smiles in smiles_list:
      mol = Chem.MolFromSmiles(smiles)
      dec = list(BRICSDecompose(mol))
      break_repo.extend(dec)
    if self.verbose:
      print(f"[+] Decomposed the molecules ...")
    #   display(Draw.MolsToGridImage([Chem.MolFromSmiles(b) for b in break_repo], molsPerRow=5, subImgSize=(200, 200)))
    return break_repo


  def _BRICS_build(self, decomposed_list: list):
    mol_list = [Chem.MolFromSmiles(dec) for dec in decomposed_list]
    if self.verbose:
      print(f"[+] Building the molecules ...")
    build = list(BRICSBuild(mol_list))
    random.seed(self.random_seed)
    if self.verbose:
      print(f"[+] Built the molecules ...")
    #   display(Draw.MolsToGridImage(build, molsPerRow=5, subImgSize=(400, 400)))
    return [Chem.MolToSmiles(mol) for mol in build]

  def replace_wildcards_with_vatoms(self, psmiles_list: list):
    mod_list = []
    for psmiles in psmiles_list:
      if psmiles.count("*") < 2:
        raise ValueError(f"The number of wildcards should be atleast 2, which is not the case for input {psmiles}")
      if psmiles.count("*") == psmiles.count("[*]"):
        mod_list.append(psmiles.replace("[*]", "[At]"))
      else:
        mod_list.append(psmiles.replace("*", "[At]"))
    return mod_list

  def replace_vatoms_with_wildcards(self, psmiles_list: list):
    mod_list = []
    for psmiles in psmiles_list:
      if psmiles.count("[At]") < 2:
        raise ValueError(f"The number of vritual atoms should be atleast 2, which is not the case for input {psmiles}")
      mod_list.append(psmiles.replace("[At]", "[*]"))
    return mod_list

  def filter_candidates(self, gen_mol_list: list):
    filtered_mols = list(filter(lambda mol: mol.count("[At]") >= 2, gen_mol_list))
    if self.verbose:
      print(f"[+] Filtering the molecules ...")
    #   display(Draw.MolsToGridImage([Chem.MolFromSmiles(b) for b in filtered_mols], molsPerRow=5, subImgSize=(200, 200)))
    return filtered_mols

  def generate(self, smiles_list: list, is_polymer: bool = False):
    if is_polymer:
        smiles_list = self.replace_wildcards_with_vatoms(smiles_list)
    decomposed_list = self._BRICS_decompose(smiles_list)
    built_atoms_w_vatoms = self._BRICS_build(decomposed_list)
    if is_polymer:
        filtered_mols= self.filter_candidates(built_atoms_w_vatoms)
    else :
        filtered_mols = built_atoms_w_vatoms
    if self.verbose:
      print(f"[+] total {len(filtered_mols)} are created in the process !")
    if is_polymer:
        filtered_mols = self.replace_vatoms_with_wildcards(filtered_mols)
    return filtered_mols, len(filtered_mols)
        

  def stream_generate(self, smiles_list: list, is_polymer: bool = False):
    try:
      if is_polymer:
          smiles_list = self.replace_wildcards_with_vatoms(smiles_list)
      decomposed_list = self._BRICS_decompose(smiles_list)
      print("decomposed_list", decomposed_list)
      yield {
          "type": "signal",
          "step" : "decomposition",
          "data": len(decomposed_list)
      }
      built_atoms_w_vatoms = self._BRICS_build(decomposed_list)
      yield {
          "type": "signal",
          "step" : "composition",
          "data": len(built_atoms_w_vatoms)
      }
      print("composed_list", built_atoms_w_vatoms)
      if is_polymer:
          filtered_mols= self.filter_candidates(built_atoms_w_vatoms)
      if self.verbose:
        print(f"[+] total {len(filtered_mols)} are created in the process !")
      if is_polymer:
          filtered_mols = self.replace_vatoms_with_wildcards(filtered_mols)
      else:
          filtered_mols = built_atoms_w_vatoms

      yield {
          "type": "completed",
          "step" : "completed",
          "data": [filtered_mols, len(filtered_mols)]
        }
    except Exception as e:
      yield {
          "type": "error",
          "step": "error",
          "data": str(e)
      }
 