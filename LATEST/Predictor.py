import torch
import torch.nn as nn

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

class StringClassifier(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, output_dim, pad_idx, dropout=0.3):
        super(StringClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=pad_idx)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, texts, lengths):
        # texts: [batch, seq_len]
        embedded = self.embedding(texts)  # [batch, seq_len, embedding_dim]
        # Pack the sequences (requires lengths to be sorted in descending order).
        packed_emb = nn.utils.rnn.pack_padded_sequence(embedded, lengths, batch_first=True, enforce_sorted=True)
        packed_output, (hidden, cell) = self.lstm(packed_emb)
        last_hidden = hidden[-1]  # [batch, hidden_dim]
        dropped = self.dropout(last_hidden)
        logits = self.fc(dropped)  # [batch, output_dim]
        return logits

class Predictor:
    def __init__(self, model_checkpoint_path: str):
        """
        Loads the checkpoint from model_checkpoint_path.
        Expects that checkpoint is a dictionary with:
          - model_state_dict: state dict of the trained model.
          - vocab: a dict mapping characters to indices.
          - label_map: a mapping of {column_name: label_index}.
          - Hyperparameters: embedding_dim, hidden_dim, output_dim, vocab_size, pad_idx, dropout.
        """
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load(model_checkpoint_path, map_location=self.device)
        
        self.vocab = checkpoint['vocab']
        self.label_map = checkpoint['label_map']
        embedding_dim = checkpoint['embedding_dim']
        hidden_dim = checkpoint['hidden_dim']
        output_dim = checkpoint['output_dim']
        vocab_size = checkpoint['vocab_size']
        pad_idx = checkpoint['pad_idx']
        dropout = checkpoint['dropout']
        
        self.model = StringClassifier(vocab_size, embedding_dim, hidden_dim, output_dim, pad_idx, dropout)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model = self.model.to(self.device)
        self.model.eval()
        print("Model loaded successfully on", self.device)

    def predict(self, text: str) -> dict:
        """
        Accepts a string and returns a dictionary containing probabilities for each class label.
        Example return:
            {'firstName': 0.60, 'lastName': 0.39, 'Email': 0.00004, 'birthdates': 0.00011, 'normalWords': 0.00012}
        """
        self.model.eval()
        indices = [self.vocab.get(ch, self.vocab["<UNK>"]) for ch in text]
        input_tensor = torch.tensor(indices, dtype=torch.long).unsqueeze(0).to(self.device)  # [1, seq_len]
        lengths = [len(indices)]
        with torch.no_grad():
            logits = self.model(input_tensor, lengths)
            probabilities = torch.softmax(logits, dim=1)
        prob = probabilities.cpu().numpy()[0]
        # Inverse mapping for labels.
        inv_label_map = {v: k for k, v in self.label_map.items()}
        return {inv_label_map[i]: float(prob[i]) for i in range(len(prob))}