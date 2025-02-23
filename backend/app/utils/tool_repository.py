#################################
from pypdb import get_info
import requests
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import Descriptors
from io import BytesIO
import base64
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json
from dataclasses import dataclass
from typing import List, Dict, Any
from urllib.parse import urlencode
# from app.utils.generators.BRICSGenerator import BRICSGenerator
# from app.utils.generators.LSTMGenerator import RNNPolymerGenerator

from utils.generators.BRICSGenerator import BRICSGenerator
from utils.generators.LSTMGenerator import RNNPolymerGenerator

# from generators.BRICSGenerator import BRICSGenerator
# from generators.LSTMGenerator import RNNPolymerGenerator

##### Testing Setup ##############
CHROMADB_SMILES_DB_NAME = "smiles_data"
CHROMADB_PSMILES_DB_NAME = "psmiles_data"
CHROMADB_PERSISTENT_PATH = "../dist/chroma_store"
RCSB_URL = "https://search.rcsb.org/rcsbsearch/v2/query"

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
    simplified_data['Pdb_Id'] = pdb_data.get(
        'rcsb_id') or pdb_data.get('entry', {}).get('id')

    # Extract title
    simplified_data['Title'] = pdb_data.get('struct', {}).get('title')

    # Extract authors as a comma-separated string
    authors_list = [author['name']
                    for author in pdb_data.get('audit_author', [])]
    simplified_data['Authors'] = ', '.join(
        authors_list) if authors_list else None

    # Extract citation details
    citation = pdb_data.get('citation', [])
    if citation:
        # Find the primary citation
        primary_citation = next(
            (c for c in citation if c.get('id') == 'primary'), citation[0])
        simplified_data['Journal'] = primary_citation.get(
            'rcsb_journal_abbrev') or primary_citation.get('journal_abbrev')
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
        simplified_data['Pubmed_Id'] = primary_citation.get(
            'pdbx_database_id_pub_med')
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
    simplified_data['Molecular_Weight_(kDa)'] = pdb_data.get(
        'rcsb_entry_info', {}).get('molecular_weight')

    # Extract deposited model count
    simplified_data['Deposited_Model_Count'] = pdb_data.get(
        'rcsb_entry_info', {}).get('deposited_model_count')

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
    simplified_data['Polymer_entity_count'] = pdb_data.get(
        'rcsb_entry_info', {}).get('polymer_entity_count')

    # Extract polymer monomer count
    simplified_data['Polymer_monomer_count'] = pdb_data.get(
        'rcsb_entry_info', {}).get('deposited_polymer_monomer_count')

    # Extract structural features
    simplified_data['Structural_Features'] = pdb_data.get(
        'struct_keywords', {}).get('text')

    # Extract release date
    release_date = pdb_data.get('rcsb_accession_info', {}).get(
        'initial_release_date', '')
    if 'T' in release_date:
        simplified_data['Release_Date'] = release_date.split('T')[0]
    else:
        simplified_data['Release_Date'] = release_date

    # Extract resolution if available (for X-ray structures)
    # For NMR structures, resolution is not applicable
    resolution = pdb_data.get('rcsb_entry_info', {}).get(
        'resolution_combined', [None])
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
            raise HTTPException(
                status_code=400, detail="Failed to get image data")
        image_base64 = base64.b64encode(image_value).decode("utf-8")
        return image_base64


class ChromaSearcher():
    def __init__(self,
                 collection_name: str,
                 persist_directory: str):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name)
        self.model = SentenceTransformer('kuelumbus/polyBERT')

    def get_embedding(self, smiles: str):
        return self.model.encode(smiles).tolist()

    def query(self, query_val: str, top_k: int = 3):
        embedding = self.get_embedding(query_val)
        return self.collection.query(query_embeddings=[embedding],
                                     n_results=top_k)


def format_smiles_search_results(results):
    formatted_results = []
    # try:
    print("result recieved >>", results)
    smiles_key_str = "smiles" if "smiles" in results["metadatas"][0][0] else "SMILES"
    for metadata, distance in zip(results["metadatas"][0], results["distances"][0]):
        mol = Chem.MolFromSmiles(metadata.get(smiles_key_str))
        img = Draw.MolToImage(mol, size=(100, 100))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        image_data = base64.b64encode(buffer.read()).decode("utf-8")
        formatted_results.append({
            "identifier": metadata.get(smiles_key_str),
            "score": distance,
            "image": image_data
        })
    return {"status": "success", "results": formatted_results}


def get_smiles_search(collection_name, payload):
    searcher = ChromaSearcher(
        collection_name=collection_name, persist_directory=CHROMADB_PERSISTENT_PATH)
    results = searcher.query(payload["data"], top_k=payload["k"])
    return format_smiles_search_results(results)


@dataclass
class RCSBQuery:
    entry_id: str
    assembly_id: str = "1"
    rows: int = 25
    start: int = 0


class RCSBSearcher:
    def __init__(self):
        self.base_url = RCSB_URL

    def build_query(self, query: RCSBQuery) -> Dict[str, Any]:
        return {
            "query": {
                "type": "terminal",
                "service": "structure",
                "parameters": {
                    "operator": "strict_shape_match",
                    "target_search_space": "assembly",
                    "value": {
                        "entry_id": query.entry_id,
                        "assembly_id": query.assembly_id
                    }
                }
            },
            "return_type": "entry",
            "request_options": {
                "paginate": {
                    "start": query.start,
                    "rows": query.rows
                },
                "results_content_type": ["experimental"],
                "sort": [{"sort_by": "score", "direction": "desc"}],
                "scoring_strategy": "combined"
            }
        }

    def search(self, query: RCSBQuery) -> Dict[str, Any]:
        query_dict = self.build_query(query)
        params = {"json": json.dumps(query_dict)}
        url = f"{self.base_url}?{urlencode(params)}"

        response = requests.get(url)
        response.raise_for_status()
        return response.json()

#################################
# MAIN TOOLS


def get_smiles_details(smiles: str) -> dict:
    """
    Get details about a molecule from its SMILES string

    The molecule explorer tool takes SMILES string of the molecule and provides 
    details in json with the 2D image of the chemical representation of the molecule and informations
    it's properties. The information panel shows different chemical details as Molecular Formula,
    Molecular Weight, Heavy Atoms Count, H Bond Doner Count, H Bond Acceptor Count, Rotatale Bonds Count,
    Topological Polar Surface Area (TPSA), and Number of rings.

    :param smiles: SMILES string
    :return: dict containing details about the molecule
    """
    try:
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
    except Exception as e:
        return {"error": str(e)}


def get_protein_details(pdb_id: str) -> dict:
    """
    Get details about a protein from its PDB ID

    The protein explorer tool takes the Protein Data Bank ID (PDB ID) and returns it's several details consisting Pdb Id, Title,Authors,Journal, Year, Volume, Pages, DOI, Pubmed Id,
    Experiment Method, Molecular Weight (kDa), Deposited Model Count, Polymer entity count, Polymer monomer count,
    Structural Features, Release Date, Resolution. 
    Always look if the pdbid is valid or not. 
    
    :param pdb_id: PDB ID
    :return: dict containing details about the protein
    """
    try:
        pdb_info = get_pdb_info(pdb_id)
        pdb_image = get_pdb_image(pdb_id)
        return {"type": "protein", "info": pdb_info, "image": pdb_image}
    except Exception as e:
        return {"error": str(e)}


def get_polymer_details(psmiles: str) -> dict:
    """
    Get details about a polymer from its PSMILES string

    The polymer explorer tool takes PSMILES of the polymer and returns it's 2D image along with relevant details as molecular formula
    of the PSMILES, Monomer Molcular Weight, Number of rings in the Monomer, and the corresponding open bond
    indexes to indicate wher the potential bonds can be formed to connect with the next monomer.

    :param psmiles: PSMILES string
    :return: dict containing details about the polymer
    """
    try:
        mol = Chem.MolFromSmiles(psmiles)

        # get indexes of [*] content in the PSMILES string
        wildcard_indices = [atom.GetIdx()
                            for atom in mol.GetAtoms() if atom.GetSymbol() == '*']
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
    except Exception as e:
        return {"error": str(e)}
    


def get_similar_smiles(smiles: str) -> dict:
    """
    Get similar molecules from the chemical space using SMILES string

    The polymer explorer tool takes PSMILES of the polymer and returns it's 2D image along with relevant details as molecular formula
    of the PSMILES, Monomer Molcular Weight, Number of rings in the Monomer, and the corresponding open bond
    indexes to indicate wher the potential bonds can be formed to connect with the next monomer.

    :param smiles: SMILES string
    :return: dict containing details about the similar molecules
    """
    # collection_name = CHROMADB_SMILES_DB_NAME
    collection_name = CHROMADB_SMILES_DB_NAME
    payload = {
        "data": smiles,
        "k": 5 
    }
    return get_smiles_search(collection_name, payload)


def get_similar_psmiles(psmiles: str) -> dict:
    """
    Get similar polymers from the chemical space using PMILES string
    
    This tool uses PSMILES string to retrieve similar polymers from the polymer space.
    This tool takes the PSMILES string with a the number of candidates to retrieve and does
    the operation and returns the json containing image of the polymers with it's PSMILES and 
    the similarity distance from the queried PSMILES.

    :param psmiles: PSMILES string
    :return: dict containing details about the similar molecules
    """
    # collection_name = CHROMADB_PSMILES_DB_NAME
    collection_name = CHROMADB_PSMILES_DB_NAME
    payload = {
        "data": psmiles,
        "k": 5 
    }
    return get_smiles_search(collection_name, payload)

def get_similar_proteins(pdb_id: str) -> dict:
    """
    Get similar proteins from the chemical space using PDB ID

    This tool uses PDB ID (Protein Databank ID) string to retrieve similar proteins from the PDB space.
    This tool takes the PDB ID string with a the number of candidates to retrieve and does
    the operation and returns a JSON containing list of PDB Ids and corresponding similarity score. 

    :param pdb_id: PDB ID
    :return: dict containing details about the similar proteins with their images
    """
    query = RCSBQuery(entry_id=pdb_id, rows=5)
    searcher = RCSBSearcher()
    results = searcher.search(query)
    returnable = []
    for r in results["result_set"]:
        image_data = get_pdb_image(r["identifier"])
        returnable.append({
            "identifier": r["identifier"],
            "score": r["score"],
            "image": image_data
        })
    return returnable


def brics_generate_smiles(smiles_list: list[str]) -> list:
    """
    Generate new molecules using BRICS decomposition and reconstruction for molecules using SMILES

    This tool uses SMILES string to generate molecules using BRICS algorithm. The algorithm generates hypothetical molecules based on the given input.
    The input is a list of SMILES string and the output is a list of molecules generated based on the input. 

    :param smiles_list: List of SMILES strings
    :return: List of generated SMILES strings
    """
    generator = BRICSGenerator()
    return generator.generate(smiles_list)


def brics_generate_polymer(psmiles_list: list[str]) -> list:
    """
    Generate new polymers using BRICS decomposition and reconstruction for polymer material using PSMILES

    This tool generates molecules using the BRICS algorithm. The BRICS algorithm is a rule-based algorithm that generates molecules based on the given input.
    The input is a list of PSMILES strings. The output will be a set of molecules that are generated based on the input.
    It returns list of generated candidates from BRICS algorithm.

    :param psmiles_list: List of PSMILES strings
    :return: List of generated PSMILES strings
    """
    generator = BRICSGenerator()
    return generator.generate(psmiles_list, is_polymer=True)


def lstm_generate_psmiles(num_generations: int) -> list:
    """
    Generate new polymers using LSTM model for polymer material using PSMILES

    This tool generates molecules using the LSTM algorithm. The LSTM algorithm is a deep learning algorithm that generates molecules for required iterations
    to get the desired number of candidates. The input is a list of PSMILES strings. It might return errors sometimes, if the input is not in the correct format.
    The output will be a set of molecules that are generated based on the input.

    :param num_generations: Number of polymer sequences to generate (default 10)
    :return: List of generated PSMILES strings
    """
    generator = RNNPolymerGenerator(input_type="psmiles")
    generator.load_model_from_ckpt(
        "./generators/model_path/PSMILES_LSTM_1M_5_epochs.pth")
    candidates = generator.generate(number_of_seq=num_generations)
    return candidates


def lstm_generate_wdg(num_generations: int) -> list:
    """
    Generate new polymers using LSTM model for polymer material using Weighted Directed Graph

    This tool generates molecules using the LSTM algorithm. The LSTM algorithm is a deep learning algorithm that generates molecules for required iterations
    to get the desired number of candidates. The input is a list of weighted directed graph strings. It might return errors sometimes, if the input is not in the correct format. 
    The output will be a set of molecules that are generated based on the input.


    if exact number of generations is not provided consider it 10

    :param num_generations: Number of polymer sequences to generate (defaule 10)
    :return: List of generated PSMILES strings
    """
    generator = RNNPolymerGenerator(input_type="wdg")
    generator.load_model_from_ckpt(
        "./generators/model_path/WDGraph_LSTM_42K_50_epochs.pth")
    candidates = generator.generate(number_of_seq=num_generations)
    return candidates


master_tools = [get_smiles_details, get_protein_details,
                get_polymer_details, get_similar_smiles, 
                get_similar_psmiles, get_similar_proteins,
                brics_generate_smiles, brics_generate_polymer,
                lstm_generate_psmiles, lstm_generate_wdg]

if __name__ == "__main__":
    # Test the functions
    smiles = "CC(=O)"
    pdb_id = "1BNA"
    psmiles = "[*]CC[*]"

    # print("smiles details >>", get_smiles_details(smiles))
    # print("protein details >>", get_protein_details(pdb_id))
    # print("polymer details >>", get_polymer_details(psmiles))

    # ret_smiles = get_similar_smiles(smiles, 5)
    # print("recieved smiles >>", ret_smiles)

    # ret_psmiles = get_similar_psmiles(psmiles, 5)
    # print("recieved psmiles >>", ret_psmiles)

    # ret_proteins = get_similar_proteins(pdb_id, 5)
    # print("recieved proteins >>", ret_proteins)

    # smiles_list = [ "CC(=O)OC1=CC=CC=C1C(=O)O",
    #     "CC(=O)NC1=CC=C(O)C=C1",
    #     "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    #     "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
    #     "C(C1C(C(C(C(O1)O)O)O)O)O"]

    # print("generated smiles >>", brics_generate_smiles(smiles_list))

    # psmiles_list = [
    #     "O=C([*])CCCCOC(=O)C(CC1OC([*])C(O)C(O)C1O)N[*]",
    #     "O=C([*])CCCCOC(=O)C(Cc1c[nH]cn1)N[*]",
    #     "O=C([*])CCCCOC(=O)C(CC1OC([*])C(O)C(O)C1CO)N[*]",
    #     "O=C([*])CCCCOC(=O)C(CC1OC([*])C(O)C(O)C1C[*])N[*]",
    #     "O=C([*])CCCCOC(=O)C(CC1OC([*])C(O)C(O)C1NCO[*])N[*]",
    #     "O=C([*])CCCCOC(=O)C(CC1OC([*])C(O)C(O)C1c1c[nH]cn1)N[*]",
    #     "O=C([*])CCCCOC(=O)C(CC1OC([*])C(O)C(O)C1O[*])N[*]",
    # ]

    # print("generated psmiles >>", brics_generate_polymer(psmiles_list))

    # print('lstm generation for 10 num >>', lstm_generate_psmiles(10))
    # print('lstm generation for 10 num >>', lstm_generate_wdg(10))
