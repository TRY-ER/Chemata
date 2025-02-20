tools = [
    {
        "name": "Molecule Explorer",
        "map": "molecule_explorer",
        "description": """The molecule explorer tool takes SMILES string of the molecule and provides interface for 
                     showcasing the 2D image of the chemical representation of the molecule and an information panel
                     for showcasing other properties. The information panel shows details as Molecular Formula,
                     Molecular Weight, Heavy Atoms Count, H Bond Doner Count, H Bond Acceptor Count, Rotatale Bonds Count,
                     Topological Polar Surface Area (TPSA), and Number of rings
                     """,
        "input_types": [str],
        "input_parameters": ["smiles"],
        "input_descriptions": ["SMILES string of the molecule"],
        "output_types": [dict],
        "callable": None
    },
    {
        "name": "Protein Explorer",
        "map": "protein_explorer",
        "description" : """The protein explorer tool takes the Protein Data Bank ID (PDB ID) to show it's details and 3D structure
                      in two panels. The 3D structure is rotatable and scalable for exploration purposes. The information panel 
                      shows it's several details consisting Pdb Id, Title,Authors,Journal, Year, Volume, Pages, DOI, Pubmed Id,
                     Experiment Method, Molecular Weight (kDa), Deposited Model Count, Polymer entity count, Polymer monomer count,
                     Structural Features, Release Date, Resolution.
                        """,
        "input_types": [str],
        "input_parameters": ["pdb_id"],
        "input_descriptions": ["PDB ID of the protein"],
        "output_types": [dict],
        "callable": None
    },
    {
        "name": "Polymer Explorer",
        "map": "polymer_explorer",
        "description": """
                        The polymer explorer tool takes PSMILES of the polymer and gives visual representation in a sidepanel,
                      as well as shows it's relevant details in the information panel containing details of molecular formula
                      of the PSMILES, Monomer Molcular Weight, Number of rings in the Monomer, and the corresponding open bond
                      indexes to indicate wher the potential bonds can be formed to connect with the next monomer.
                    """,
        "input_types": [str],
        "input_parameters": ["psmiles"],
        "input_descriptions": ["PSMILES of the polymer"],
        "output_types": [dict],
        "callable": None
    },
    {
        "name": "SMILES Similarity Search",
        "map": "smiles_similarity_search",
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
        "output_types": [dict],
        "callable": None
    },
    {
        "name": "Polymer Similarity Search",
        "map": "polymer_similarity_search",
        "description": """
                      This tool uses PSMILES string to retrieve similar polymers from the polymer space.
                      This tool takes the PSMILES string with a the number of candidates to retrieve and does
                      the operation and returns a section that shows the image of the polymers with it's PSMILES and 
                      the similarity distance from the query PSMILES.
                    """,
        "input_types": [str, int],
        "input_parameters": ["psmiles", "num_candidates"],
        "input_descriptions": ["PSMILES string of the polymer", "Number of candidates to retrieve"],
        "output_types": [dict],
        "callable": None
    },
    {
        "name": "Protein Similarity Search",
        "map": "protein_similarity_search",
        "description": """
                      This tool uses PDB ID string to retrieve similar proteins from the PDB space.
                      This tool takes the PDB ID string with a the number of candidates to retrieve and does
                      the operation and returns a JSON containing list of PDB Ids and corresponding similarity score. 
                    """,
        "input_types": [str, int],
        "input_parameters": ["pdb_id", "num_candidates"],
        "input_descriptions": ["PDB ID of the protein", "Number of candidates to retrieve"],
        "output_types": [dict],
        "callable": None
    },
    {
        "name": "BRICS SMILES Generation",
        "map": "brics_smiles_generation",
        "description": """
                       This tool uses SMILES string to generate molecules using BRICS algorithm. The algorithm generates hypothetical molecules based on the given input.
                       The input is a list of SMILES string and the output is a list of molecules generated based on the input. 
                       """,
        "input_types": [str],
        "input_parameters": ["smiles_list"],
        "input_descriptions": ["List of SMILES strings"],
        "output_types": [dict],
        "callable": None
    },
    {
        "name": "BRICS PSMILES Generation",
        "map": "brics_psmiles_generation",
        "description": """
                      Generate molecules using the BRICS algorithm. The BRICS algorithm is a rule-based algorithm that generates molecules based on the given input.
                     The input is a list of PSMILES strings. The output will be a set of molecules that are generated based on the input.
                     It returns list of generated candidates from BRICS algorithm.
                    """,
        "input_types": [str],
        "input_parameters": ["psmiles_list"],
        "input_descriptions": ["List of PSMILES strings"],
        "output_types": [dict],
        "callable": None
    },
    {
        "name": "LSTM PSMILES Generation",
        "map": "lstm_psmiles_generation",
        "description": """
                     Generate molecules using the LSTM algorithm. The LSTM algorithm is a deep learning algorithm that generates molecules for required iterations
                     to get the desired number of candidates. The input is a list of PSMILES strings. It might return errors sometimes, if the input is not in the correct format.
                     The output will be a set of molecules that are generated based on the input.
                      """,
        "input_types": [int],
        "input_parameters": ["num_candidates"],
        "input_descriptions": ["Number of candidates to generate"],
        "output_types": [dict],
        "callable": None
    },
    {
        "name": "LSTM WDG Generation",
        "map": "lstm_wdg_generation",
        "description": """
                     Generate molecules using the LSTM algorithm. The LSTM algorithm is a deep learning algorithm that generates molecules for required iterations
                     to get the desired number of candidates. The input is a list of weighted directed graph strings. It might return errors sometimes, if the input is not in the correct format. 
                     The output will be a set of molecules that are generated based on the input.
                      """,
        "input_types": [int],
        "input_parameters": ["num_candidates"],
        "input_descriptions": ["Number of candidates to generate"],
        "output_types": [dict],
        "callable": None
    }
]