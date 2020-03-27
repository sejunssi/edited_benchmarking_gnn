import time
import pickle
import numpy as np
import itertools
from scipy.spatial.distance import pdist, squareform

import dgl
import torch
from torch.utils.data import Dataset


class TSP(Dataset):
    def __init__(self, data_dir, split="train", num_neighbors=25, max_samples=10000):    
        self.data_dir = data_dir
        self.split = split
        self.filename = f'{data_dir}/tsp50-500_{split}.txt'
        self.max_samples = max_samples
        self.num_neighbors = num_neighbors
        self.is_test = split.lower() in ['test', 'val']
        
        self.graph_lists = []
        self.edge_labels = []
        self._prepare()
        self.n_samples = len(self.edge_labels)
    
    def _prepare(self):
        print('preparing all graphs for the %s set...' % self.split.upper())
        
        file_data = open(self.filename, "r").readlines()[:self.max_samples]
        
        for graph_idx, line in enumerate(file_data):
            line = line.split(" ")  # Split into list
            num_nodes = int(line.index('output')//2)
            
            # Convert node coordinates to required format
            nodes_coord = []
            for idx in range(0, 2 * num_nodes, 2):
                nodes_coord.append([float(line[idx]), float(line[idx + 1])])

            # Compute distance matrix
            W_val = squareform(pdist(nodes_coord, metric='euclidean'))
            # Determine k-nearest neighbors for each node
            knns = np.argpartition(W_val, kth=self.num_neighbors, axis=-1)[:, self.num_neighbors::-1]

            # Convert tour nodes to required format
            # Don't add final connection for tour/cycle
            tour_nodes = [int(node) - 1 for node in line[line.index('output') + 1:-1]][:-1]

            # Compute an edge adjacency matrix representation of tour
            edges_target = np.zeros((num_nodes, num_nodes))
            for idx in range(len(tour_nodes) - 1):
                i = tour_nodes[idx]
                j = tour_nodes[idx + 1]
                edges_target[i][j] = 1
                edges_target[j][i] = 1
            # Add final connection of tour in edge target
            edges_target[j][tour_nodes[0]] = 1
            edges_target[tour_nodes[0]][j] = 1
            
            # Construct the DGL graph
            g = dgl.DGLGraph()
            g.add_nodes(num_nodes)
            g.ndata['feat'] = torch.Tensor(nodes_coord)
            
            edge_feats = []  # edge features i.e. euclidean distances between nodes
            edge_labels = []  # edges_targets as a list
            # Important!: order of edge_labels must be the same as the order of edges in DGLGraph g
            # We ensure this by adding them together
            for idx in range(num_nodes):
                for n_idx in knns[idx]:
                    if n_idx != idx:  # No self-connection
                        g.add_edge(idx, n_idx)
                        edge_feats.append(W_val[idx][n_idx])
                        edge_labels.append(int(edges_target[idx][n_idx]))
            # dgl.transform.remove_self_loop(g)
            
            # Sanity check
            assert len(edge_feats) == g.number_of_edges() == len(edge_labels)
            
            # Add edge features
            g.edata['feat'] = torch.Tensor(edge_feats).unsqueeze(-1)
            
            # # Uncomment to add dummy edge features instead (for Residual Gated ConvNet)
            # edge_feat_dim = g.ndata['feat'].shape[1] # dim same as node feature dim
            # g.edata['feat'] = torch.ones(g.number_of_edges(), edge_feat_dim)
            
            self.graph_lists.append(g)
            self.edge_labels.append(edge_labels)

    def __len__(self):
        """Return the number of graphs in the dataset."""
        return self.n_samples

    def __getitem__(self, idx):
        """
            Get the idx^th sample.
            Parameters
            ---------
            idx : int
                The sample index.
            Returns
            -------
            (dgl.DGLGraph, list)
                DGLGraph with node feature stored in `feat` field
                And a list of labels for each edge in the DGLGraph.
        """
        return self.graph_lists[idx], self.edge_labels[idx]


class TSPDatasetDGL(Dataset):
    def __init__(self, name):
        self.name = name
        self.train = TSP(data_dir='./data/TSP', split='train', num_neighbors=25, max_samples=10000) 
        self.val = TSP(data_dir='./data/TSP', split='val', num_neighbors=25, max_samples=1000)
        self.test = TSP(data_dir='./data/TSP', split='test', num_neighbors=25, max_samples=1000)
        

class TSPDataset(Dataset):
    def __init__(self, name):
        start = time.time()
        print("[I] Loading dataset %s..." % (name))
        self.name = name
        data_dir = 'data/TSP/'
        with open(data_dir+name+'.pkl',"rb") as f:
            f = pickle.load(f)
            self.train = f[0]
            self.test = f[1]
            self.val = f[2]
        print('train, test, val sizes :',len(self.train),len(self.test),len(self.val))
        print("[I] Finished loading.")
        print("[I] Data load time: {:.4f}s".format(time.time()-start))
    
    # form a mini batch from a given list of samples = [(graph, label) pairs]
    def collate(self, samples):
        # The input samples is a list of pairs (graph, label).
        graphs, labels = map(list, zip(*samples))
        # Edge classification labels need to be flattened to 1D lists
        labels = torch.LongTensor(np.array(list(itertools.chain(*labels))))
        tab_sizes_n = [ graphs[i].number_of_nodes() for i in range(len(graphs))]
        tab_snorm_n = [ torch.FloatTensor(size,1).fill_(1./float(size)) for size in tab_sizes_n ]
        snorm_n = torch.cat(tab_snorm_n).sqrt()  
        tab_sizes_e = [ graphs[i].number_of_edges() for i in range(len(graphs))]
        tab_snorm_e = [ torch.FloatTensor(size,1).fill_(1./float(size)) for size in tab_sizes_e ]
        snorm_e = torch.cat(tab_snorm_e).sqrt()
        batched_graph = dgl.batch(graphs)

        return batched_graph, labels, snorm_n, snorm_e
    
    
    def _add_self_loops(self):
        """
           No self-loop support since TSP edge classification dataset. 
        """
        raise NotImplementedError
        
        