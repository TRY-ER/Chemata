from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.BRICS import BRICSDecompose
from rdkit.Chem.BRICS import BRICSBuild
from torch import nn
from transformers import BertTokenizer
from .validators import PolyWDGStringValidator, PSMILESValidator
import torch
import re
import json

def convert_smarts_to_psmiles(smarts_str: str) -> str:
    """Convert a SMARTS string with [*:N] pattern to pSMILES with [N*]"""
    try:
        pattern = r'\[\*:(\d+)\]'
        if not re.search(pattern, smarts_str):
            return None
        return re.sub(pattern, r'[\1*]', smarts_str)
    except:
        return None

class LSTMPolymerModel(nn.Module):

    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers=1):
        super(LSTMPolymerModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.rnn = nn.LSTM(embedding_dim,
                           hidden_dim,
                           num_layers,
                           batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        embedded = self.embedding(x)
        output, _ = self.rnn(embedded)
        output = self.fc(output)
        return output


class RNNPolymerGenerator:

    def __init__(self,
                 embedding_dim=128,
                 hidden_dim=256,
                 num_layers=2,
                 tokenizer=None,
                 input_type: str = "psmiles"):
        self.tokenizer = BertTokenizer.from_pretrained(
            'bert-base-cased') if tokenizer is None else tokenizer
        self.embedding_dim = 128
        self.hidden_dim = 256
        self.num_layers = 2
        self.model = None
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.input_type = input_type

    def load_model_from_ckpt(self, ckpt_path, device="cpu"):
        self.model = LSTMPolymerModel(self.tokenizer.vocab_size,
                                      self.embedding_dim, self.hidden_dim,
                                      self.num_layers)
        self.model.load_state_dict(torch.load(ckpt_path))
        self.model = self.model.to(self.device)

    def generate_polymer(self, max_len=600, temperature=1.0):
        generated_sequence = [self.tokenizer.cls_token_id]
        for _ in range(max_len):
            input_tensor = torch.tensor(generated_sequence).unsqueeze(0)
            # print("input tensor >>", input_tensor)
            # print("input tensor shape >>", input_tensor.shape)
            input_tensor = input_tensor.to(self.device)
            output = self.model(input_tensor)
            logits = output[:, -1, :] / temperature
            prbos = torch.softmax(logits, dim=-1)

            predicted_tokens = torch.multinomial(prbos, num_samples=1).item()
            # print("output reshaped >>", output.reshape(-1, tokenizer.vocab_size))
            # print("output last token >>", torch.argmax(output[:, -1, :]).item())
            # print("output last token item >>", torch.argmax(output[:, -1, :]).item())
            generated_sequence.append(predicted_tokens)
            if predicted_tokens == self.tokenizer.sep_token_id:
                break
        generated_sequence = self.tokenizer.decode(generated_sequence,
                                                   skip_special_tokens=True)
        generated_sequence = generated_sequence.replace(" ", "")
        return generated_sequence

    def generate(self, number_of_seq=100, max_len=600):
        self.model.eval()
        results = []
        count = 0
        while count < number_of_seq:
            generated_sequence = self.generate_polymer(max_len)
            if self.input_type == "psmiles":
                if PSMILESValidator().validate(generated_sequence):
                    results.append(generated_sequence)
                    count += 1 
                else:
                    print('failed for generation >>', generated_sequence)
            elif self.input_type == "wdg":
                gen_str = convert_smarts_to_psmiles(generated_sequence)
                if PolyWDGStringValidator().validate(gen_str):
                    results.append(gen_str)
                    count += 1
                else:
                    print('failed for generation >>', gen_str)
            else:
                raise ValueError("Invalid input type")
        return results

    def stream_generate(self, number_of_seq=100, max_len=600):
        self.model.eval()
        results = []
        count = 0 
        while count < number_of_seq:
            generated_sequence = self.generate_polymer(max_len)
            if self.input_type == "psmiles":
                if PSMILESValidator().validate(generated_sequence):
                    results.append(generated_sequence)
                    yield json.dumps({"type": "generated", "data": generated_sequence})
                    count += 1
            elif self.input_type == "wdg":
                gen_str = convert_smarts_to_psmiles(generated_sequence)
                print("gen_str >>", gen_str)
                if PolyWDGStringValidator().validate(gen_str):
                    results.append(gen_str)
                    yield json.dumps({"type": "generated", "data": gen_str})
                    count += 1
        yield json.dumps({"type": "completed", "data": results})
