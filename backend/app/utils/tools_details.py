from .tool_repository import (
    get_smiles_details,
    get_protein_details,
    get_polymer_details,
    get_similar_smiles,
    get_similar_psmiles,
    get_similar_proteins,
    brics_generate_smiles,
    brics_generate_polymer,
    lstm_generate_psmiles,
    lstm_generate_wdg
)

tool_mapper = [
    {
        "name": "Molecule Explorer",
        "map": "get_smiles_details",
        "description": """The molecule explorer tool takes SMILES string of the molecule and provides 
                     details in json with the 2D image of the chemical representation of the molecule and informations
                     it's properties. The information panel shows different chemical details as Molecular Formula,
                     Molecular Weight, Heavy Atoms Count, H Bond Doner Count, H Bond Acceptor Count, Rotatale Bonds Count,
                     Topological Polar Surface Area (TPSA), and Number of rings.
                     """,
        "input_types": [str],
        "input_parameters": ["smiles"],
        "input_descriptions": ["SMILES string of the molecule"],
        "default_inputs": [None],
        "output_types": [dict],
        "callable": get_smiles_details 
    },
    {
        "name": "Protein Explorer",
        "map": "get_protein_details",
        "description" : """The protein explorer tool takes the Protein Data Bank ID (PDB ID) and returns it's several details consisting Pdb Id, Title,Authors,Journal, Year, Volume, Pages, DOI, Pubmed Id,
                     Experiment Method, Molecular Weight (kDa), Deposited Model Count, Polymer entity count, Polymer monomer count,
                     Structural Features, Release Date, Resolution.
                        """,
        "input_types": [str],
        "input_parameters": ["pdb_id"],
        "input_descriptions": ["PDB ID of the protein"],
        "default_inputs": [None],
        "output_types": [dict],
        "callable": get_protein_details 
    },
    {
        "name": "Polymer Explorer",
        "map": "get_polymer_details",
        "description": """
                        The polymer explorer tool takes PSMILES of the polymer and returns it's 2D image along with relevant details as molecular formula
                      of the PSMILES, Monomer Molcular Weight, Number of rings in the Monomer, and the corresponding open bond
                      indexes to indicate wher the potential bonds can be formed to connect with the next monomer.
                    """,
        "input_types": [str],
        "input_parameters": ["psmiles"],
        "input_descriptions": ["PSMILES of the polymer"],
        "default_inputs": [None],
        "output_types": [dict],
        "callable": get_polymer_details 
    },
    {
        "name": "SMILES Similarity Search",
        "map": "get_similar_smiles",
        "description": """
                      This tool uses SMILES string to retrieve similar molecules from the chemical space.
                      This tool takes the SMILES string with a the number of candidates to retrieve and does
                      the operation and returns a json that includes the image of the molecules (in base64 encoded strings) 
                      with it's SMILES and the similarity distance from the query SMILES. The results can be downloadable in 
                      a text as well as can be copied to the clipboard.
                    """,
        "input_types": [str, int],
        "input_parameters": ["smiles", "num_candidates"],
        "input_descriptions": ["SMILES string of the molecule", "Number of candidates to retrieve"],
        "default_inputs": [None, 5],
        "output_types": [dict],
        "callable": get_similar_smiles 
    },
    {
        "name": "Polymer Similarity Search",
        "map": "get_similar_psmiles",
        "description": """
                      This tool uses PSMILES string to retrieve similar polymers from the polymer space.
                      This tool takes the PSMILES string with a the number of candidates to retrieve and does
                      the operation and returns the json containing image of the polymers with it's PSMILES and 
                      the similarity distance from the queried PSMILES.
                    """,
        "input_types": [str, int],
        "input_parameters": ["psmiles", "num_candidates"],
        "input_descriptions": ["PSMILES string of the polymer", "Number of candidates to retrieve"],
        "default_inputs": [None, 5],
        "output_types": [dict],
        "callable": get_similar_psmiles 
    },
    {
        "name": "Protein Similarity Search",
        "map": "get_similar_proteins",
        "description": """
                      This tool uses PDB ID (Protein Databank ID) string to retrieve similar proteins from the PDB space.
                      This tool takes the PDB ID string with a the number of candidates to retrieve and does
                      the operation and returns a JSON containing list of PDB Ids and corresponding similarity score. 
                    """,
        "input_types": [str, int],
        "input_parameters": ["pdb_id", "num_candidates"],
        "input_descriptions": ["PDB ID of the protein", "Number of candidates to retrieve"],
        "default_inputs": [None, 5],
        "output_types": [dict],
        "callable": get_similar_proteins 
    },
    {
        "name": "BRICS SMILES Generation",
        "map": "brics_generate_smiles",
        "description": """
                       This tool uses SMILES string to generate molecules using BRICS algorithm. The algorithm generates hypothetical molecules based on the given input.
                       The input is a list of SMILES string and the output is a list of molecules generated based on the input. 
                       """,
        "input_types": [str],
        "input_parameters": ["smiles_list"],
        "input_descriptions": ["List of SMILES strings"],
        "default_inputs": [None],
        "output_types": [dict],
        "callable": brics_generate_smiles 
    },
    {
        "name": "BRICS PSMILES Generation",
        "map": "brics_generate_polymer",
        "description": """
                      This tool generates molecules using the BRICS algorithm. The BRICS algorithm is a rule-based algorithm that generates molecules based on the given input.
                      The input is a list of PSMILES strings. The output will be a set of molecules that are generated based on the input.
                      It returns list of generated candidates from BRICS algorithm.
                    """,
        "input_types": [str],
        "input_parameters": ["psmiles_list"],
        "input_descriptions": ["List of PSMILES strings"],
        "default_inputs": [None],
        "output_types": [dict],
        "callable": brics_generate_polymer 
    },
    {
        "name": "LSTM PSMILES Generation",
        "map": "lstm_generate_psmiles",
        "description": """
                     This tool generates molecules using the LSTM algorithm. The LSTM algorithm is a deep learning algorithm that generates molecules for required iterations
                     to get the desired number of candidates. The input is a list of PSMILES strings. It might return errors sometimes, if the input is not in the correct format.
                     The output will be a set of molecules that are generated based on the input.
                     """,
        "input_types": [int],
        "input_parameters": ["num_candidates"],
        "input_descriptions": ["Number of candidates to generate"],
        "default_inputs": [5],
        "output_types": [dict],
        "callable": lstm_generate_psmiles 
    },
    {
        "name": "LSTM WDG Generation",
        "map": "lstm_generate_wdg",
        "description": """
                     This tool generates molecules using the LSTM algorithm. The LSTM algorithm is a deep learning algorithm that generates molecules for required iterations
                     to get the desired number of candidates. The input is a list of weighted directed graph strings. It might return errors sometimes, if the input is not in the correct format. 
                     The output will be a set of molecules that are generated based on the input.
                      """,
        "input_types": [int],
        "input_parameters": ["num_candidates"],
        "input_descriptions": ["Number of candidates to generate"],
        "default_inputs": [5],
        "output_types": [dict],
        "callable": lstm_generate_wdg 
    }
]