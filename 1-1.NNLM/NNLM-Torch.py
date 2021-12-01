# -*- coding: utf-8 -*-
"""“NNLM-Torch.ipynb”的副本

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-agQZoIOxaE68_SMaNGy35pz8ccWefps
"""

# code by Tae Hwan Jung @graykode, modify by wmathor
import torch
import torch.nn as nn
import torch.optim as optimizer
import torch.utils.data as Data

dtype = torch.FloatTensor

sentences = ['i like cat', 'i love coffee', 'i hate milk']
sentences_list = " ".join(sentences).split() # ['i', 'like', 'cat', 'i', 'love'. 'coffee',...]
vocab = list(set(sentences_list))
word2idx = {w:i for i, w in enumerate(vocab)}
idx2word = {i:w for i, w in enumerate(vocab)}

V = len(vocab)

def make_data(sentences):
  input_data = []
  target_data = []
  for sen in sentences:
    sen = sen.split() # ['i', 'like', 'cat']
    input_tmp = [word2idx[w] for w in sen[:-1]]
    target_tmp = word2idx[sen[-1]]

    input_data.append(input_tmp)
    target_data.append(target_tmp)
  return input_data, target_data

input_data, target_data = make_data(sentences)
input_data, target_data = torch.LongTensor(input_data), torch.LongTensor(target_data)
dataset = Data.TensorDataset(input_data, target_data)
loader = Data.DataLoader(dataset, 2, True)

# parameters
m = 2
n_step = 2
n_hidden = 10

class NNLM(nn.Module):
  def __init__(self):
    super(NNLM, self).__init__()
    self.C = nn.Embedding(V, m)
    self.H = nn.Parameter(torch.randn(n_step * m, n_hidden).type(dtype))
    self.d = nn.Parameter(torch.randn(n_hidden).type(dtype))
    self.b = nn.Parameter(torch.randn(V).type(dtype))
    self.W = nn.Parameter(torch.randn(n_step * m, V).type(dtype))
    self.U = nn.Parameter(torch.randn(n_hidden, V).type(dtype))

  def forward(self, X):
    '''
    X : [batch_size, n_step]
    '''
    X = self.C(X) # [batch_size, n_step, m]
    X = X.view(-1, n_step * m) # [batch_szie, n_step * m]
    hidden_out = torch.tanh(self.d + torch.mm(X, self.H)) # [batch_size, n_hidden]
    output = self.b + torch.mm(X, self.W) + torch.mm(hidden_out, self.U)
    return output
model = NNLM()
optim = optimizer.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()

for epoch in range(5000):
  for batch_x, batch_y in loader:
    pred = model(batch_x)
    loss = criterion(pred, batch_y)

    if (epoch + 1) % 1000 == 0:
      print(epoch + 1, loss.item())
    optim.zero_grad()
    loss.backward()
    optim.step()

# Pred
pred = model(input_data).max(1, keepdim=True)[1]
print([idx2word[idx.item()] for idx in pred.squeeze()])

