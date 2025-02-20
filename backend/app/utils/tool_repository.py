#################################
from pypdb import get_info
import requests
from rdkit import Chem
from rdkit.Chem import Draw 
from rdkit.Chem import Descriptors
from io import BytesIO
import base64

#################################
# UTILS FUNCTIONS

def extract_simplified_pdb_data(pdb_data: dict) -> dict:
    """
    Extracts significant scientific properties from a complex PDB data dictionary.
    
    Parameters:
    pdb_data (dict): The complex PDB data dictionary.

    Returns:
    dict: A simplified dictionary containing significant scientific properties.
    """
    simplified_data = {}

    # Extract pdb_id
    simplified_data['Pdb_Id'] = pdb_data.get('rcsb_id') or pdb_data.get('entry', {}).get('id')

    # Extract title
    simplified_data['Title'] = pdb_data.get('struct', {}).get('title')

    # Extract authors as a comma-separated string
    authors_list = [author['name'] for author in pdb_data.get('audit_author', [])]
    simplified_data['Authors'] = ', '.join(authors_list) if authors_list else None

    # Extract citation details
    citation = pdb_data.get('citation', [])
    if citation:
        # Find the primary citation
        primary_citation = next((c for c in citation if c.get('id') == 'primary'), citation[0])
        simplified_data['Journal'] = primary_citation.get('rcsb_journal_abbrev') or primary_citation.get('journal_abbrev')
        simplified_data['Year'] = primary_citation.get('year')
        simplified_data['Volume'] = primary_citation.get('journal_volume')
        # Handle page numbers
        page_first = primary_citation.get('page_first')
        page_last = primary_citation.get('page_last')
        if page_first and page_last:
            pages = f"{page_first}-{page_last}"
        elif page_first:
            pages = page_first
        else:
            pages = None
        simplified_data['Pages'] = pages
        simplified_data['Doi'] = primary_citation.get('pdbx_database_id_doi')
        simplified_data['Pubmed_Id'] = primary_citation.get('pdbx_database_id_pub_med')
    else:
        simplified_data['Journal'] = None
        simplified_data['Year'] = None
        simplified_data['Volume'] = None
        simplified_data['Pages'] = None
        simplified_data['Doi'] = None
        simplified_data['Pubmed_Id'] = None

    # Extract experiment method
    exptl = pdb_data.get('exptl', [])
    if exptl:
        simplified_data['Experiment_Method'] = exptl[0].get('method')
    else:
        simplified_data['Experiment_Method'] = None

    # Extract molecular weight
    simplified_data['Molecular_Weight_(kDa)'] = pdb_data.get('rcsb_entry_info', {}).get('molecular_weight')

    # Extract deposited model count
    simplified_data['Deposited_Model_Count'] = pdb_data.get('rcsb_entry_info', {}).get('deposited_model_count')

    # # Extract keywords as a comma-separated string
    # keywords_list = []
    # keywords = pdb_data.get('struct_keywords', {}).get('pdbx_keywords', '')
    # additional_keywords = pdb_data.get('struct_keywords', {}).get('text', '')
    # if keywords:
    #     keywords_list.extend([kw.strip() for kw in keywords.split(',') if kw.strip()])
    # if additional_keywords:
    #     keywords_list.extend([kw.strip() for kw in additional_keywords.split(',') if kw.strip()])
    # simplified_data['keywords'] = ', '.join(keywords_list) if keywords_list else None

    # Extract polymer entity count
    simplified_data['Polymer_entity_count'] = pdb_data.get('rcsb_entry_info', {}).get('polymer_entity_count')

    # Extract polymer monomer count
    simplified_data['Polymer_monomer_count'] = pdb_data.get('rcsb_entry_info', {}).get('deposited_polymer_monomer_count')

    # Extract structural features
    simplified_data['Structural_Features'] = pdb_data.get('struct_keywords', {}).get('text')

    # Extract release date
    release_date = pdb_data.get('rcsb_accession_info', {}).get('initial_release_date', '')
    if 'T' in release_date:
        simplified_data['Release_Date'] = release_date.split('T')[0]
    else:
        simplified_data['Release_Date'] = release_date

    # Extract resolution if available (for X-ray structures)
    # For NMR structures, resolution is not applicable
    resolution = pdb_data.get('rcsb_entry_info', {}).get('resolution_combined', [None])
    if resolution and resolution[0] is not None:
        simplified_data['Resolution'] = resolution[0]
    else:
        simplified_data['Resolution'] = None

    return simplified_data
        
def get_pdb_info(pdb_id: str) -> dict:
    """
    Return basic RDKit descriptors from a SMILES string.
    """
    info = get_info(pdb_id)
    extract = extract_simplified_pdb_data(info)
    return extract 

def get_pdb_image(pdb_id: str):
    url = f"https://cdn.rcsb.org/images/structures/{pdb_id.lower()}_assembly-1.jpeg"
    # get the image using url and return the image data as base64 encoding

    image_value = None 
    response = requests.get(url)
    if response.status_code == 200:
        image_value = response.content
        if image_value is None:
            raise HTTPException(status_code=400, detail="Failed to get image data")
        image_base64 = base64.b64encode(image_value).decode("utf-8")
        return image_base64

#################################
# MAIN TOOLS

def get_smiles_details(smiles: str) -> dict:
    """
    Get details about a molecule from its SMILES string
    :param smiles: SMILES string
    :return: dict containing details about the molecule
    """ 
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return {"error": "Invalid SMILES"}

    # Basic properties about the molecule:
    # MolecularFormula  - chemical formula for the molecule
    # MolecularWeight   - approximate weight in daltons
    # NumHeavyAtoms     - count of non-hydrogen atoms
    # NumHBD            - hydrogen bond donor count
    # NumHBA            - hydrogen bond acceptor count
    # NumRotatableBonds - number of freely rotating bonds
    # TPSA              - topological polar surface area
    # NumRings          - number of ring structures
    info = {
        "Molecular Formula": Chem.rdMolDescriptors.CalcMolFormula(mol),
        "Molecular Weight": round(float(Descriptors.MolWt(mol)), 3),
        "Heavy Atoms Count": Descriptors.HeavyAtomCount(mol),
        "H Bond Donor Count": Descriptors.NumHDonors(mol),
        "H Bond Acceptor Count": Descriptors.NumHAcceptors(mol),
        "Rotatable Bonds Count": Descriptors.NumRotatableBonds(mol),
        "TPSA": Descriptors.TPSA(mol),
        "Number of Rings": Descriptors.RingCount(mol),
    }
    if not mol:
        return None
    img = Draw.MolToImage(mol, size=(600, 600))
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    image = base64.b64encode(buffer.read()).decode("utf-8")
    return {"type": "smiles", "info": info, "image": image}


def get_protein_details(pdb_id: str) -> dict:
    """
    Get details about a protein from its PDB ID
    :param pdb_id: PDB ID
    :return: dict containing details about the protein
    """
    pdb_info = get_pdb_info(pdb_id)
    pdb_image = get_pdb_image(pdb_id)
    return {"type": "protein", "info": pdb_info, "image": pdb_image}


def get_polymer_details(psmiles: str) -> dict:
    """
    Get details about a polymer from its PSMILES string
    :param psmiles: PSMILES string
    :return: dict containing details about the polymer
    """

    mol = Chem.MolFromSmiles(psmiles)

    # get indexes of [*] content in the PSMILES string
    wildcard_indices = [atom.GetIdx() for atom in mol.GetAtoms() if atom.GetSymbol() == '*']
    wildcard_indices = ",".join([str(index) for index in wildcard_indices])

    info = {
        "Molecular Formula": Chem.rdMolDescriptors.CalcMolFormula(mol),
        "Monomer Molecular Weight": round(float(Descriptors.MolWt(mol)), 3),
        "Number of Rings in Monomer": Descriptors.RingCount(mol),
        "Open Bond Indexes": wildcard_indices
    }

    img = Draw.MolToImage(mol, size=(600, 600))
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    image = base64.b64encode(buffer.read()).decode("utf-8")
    return {"type": "psmiles", "info": info, "image": image}


if __name__ == "__main__":
    # Test the functions
    smiles = "CCO"
    pdb_id = "1BNA"
    psmiles = "[*]CC[*]"

    print("smiles details >>", get_smiles_details(smiles))
    print("protein details >>", get_protein_details(pdb_id))
    print("polymer details >>", get_polymer_details(psmiles)) 