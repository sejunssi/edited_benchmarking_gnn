import torch
import torch.nn as nn
import torch.nn.functional as F

import dgl

import numpy as np

"""
    GMM: Gaussian Mixture Model Convolution layer
    Geometric Deep Learning on Graphs and Manifolds using Mixture Model CNNs (Federico Monti et al., CVPR 2017)
    https://arxiv.org/pdf/1611.08402.pdf
"""

from layers.gmm_layer import GMMLayer
from layers.mlp_readout_layer import MLPReadout

class MoNet(nn.Module):
    def __init__(self, net_params):
        super().__init__()
        
        in_dim = net_params['in_dim']
        hidden_dim = net_params['hidden_dim']
        out_dim = net_params['out_dim']
        kernel = net_params['kernel']                       # for MoNet
        dim = net_params['pseudo_dim_MoNet']                # for MoNet
        n_classes = net_params['n_classes']
        dropout = net_params['dropout']
        n_layers = net_params['L']
        self.readout = net_params['readout']                      
        graph_norm = net_params['graph_norm']      
        batch_norm = net_params['batch_norm']
        residual = net_params['residual']  
        self.device = net_params['device']
        self.n_classes = n_classes
        
        aggr_type = "sum"                                    # default for MoNet
        
        self.embedding_h = nn.Embedding(in_dim, hidden_dim)
        
        self.layers = nn.ModuleList()
        self.pseudo_proj = nn.ModuleList()

        # Hidden layer
        for _ in range(n_layers-1):
            self.layers.append(GMMLayer(hidden_dim, hidden_dim, dim, kernel, aggr_type,
                                        dropout, graph_norm, batch_norm, residual))
            self.pseudo_proj.append(nn.Sequential(nn.Linear(2, dim), nn.Tanh()))
            
        # Output layer
        self.layers.append(GMMLayer(hidden_dim, out_dim, dim, kernel, aggr_type,
                                    dropout, graph_norm, batch_norm, residual))
        self.pseudo_proj.append(nn.Sequential(nn.Linear(2, dim), nn.Tanh()))
        
        self.MLP_layer = MLPReadout(out_dim, n_classes)

    def forward(self, g, h, e, snorm_n, snorm_e):
        h = self.embedding_h(h)
        
        # computing the 'pseudo' named tensor which depends on node degrees
        us, vs = g.edges()
        # to avoid zero division in case in_degree is 0, we add constant '1' in all node degrees denoting self-loop
        pseudo = [ [1/np.sqrt(g.in_degree(us[i])+1), 1/np.sqrt(g.in_degree(vs[i])+1)] for i in range(g.number_of_edges()) ]
        pseudo = torch.Tensor(pseudo).to(self.device)
        
        for i in range(len(self.layers)):
            h = self.layers[i](g, h, self.pseudo_proj[i](pseudo), snorm_n)

        return self.MLP_layer(h)
        
    def loss(self, pred, label):

        # calculating label weights for weighted loss computation
        V = label.size(0)
        label_count = torch.bincount(label)
        label_count = label_count[label_count.nonzero()].squeeze()
        cluster_sizes = torch.zeros(self.n_classes).long().to(self.device)
        cluster_sizes[torch.unique(label)] = label_count
        weight = (V - cluster_sizes).float() / V
        weight *= (cluster_sizes>0).float()
        
        # weighted cross-entropy for unbalanced classes
        criterion = nn.CrossEntropyLoss(weight=weight)
        loss = criterion(pred, label)

        return loss