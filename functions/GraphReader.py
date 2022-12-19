#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import rdkit
from rdkit import Chem
import networkx as nx

import numpy as np


# In[ ]:


def qm9_edges(g):
    remove_edges = []
    e={}    
    for n1, n2, d in g.edges(data=True):
        e_t = []
        # Raw distance function
        if d['b_type'] is None:
            remove_edges += [(n1, n2)]
        else:
            #e_t.append(d['distance'])
            e_t += [int(d['b_type'] == x) for x in [rdkit.Chem.rdchem.BondType.SINGLE, rdkit.Chem.rdchem.BondType.DOUBLE,
                                                    rdkit.Chem.rdchem.BondType.TRIPLE, rdkit.Chem.rdchem.BondType.AROMATIC]]
        if e_t:
            e[(n1, n2)] = e_t
    for edg in remove_edges:
        g.remove_edge(*edg)    
    
    return nx.to_numpy_matrix(g), e
    


# In[ ]:


def qm9_nodes(g, hydrogen=False):
    h = []
    for n, d in g.nodes(data=True): 
        h_t = []
        # Atom type (One-hot H, C, N, O F)
        h_t += [int(d['a_type'] == x) for x in ['H', 'C', 'N', 'O', 'F']]
        # Atomic number
        h_t.append(d['a_num'])
        # Acceptor
        h_t.append(d['acceptor'])
        # Donor
        h_t.append(d['donor'])
        # Aromatic
        h_t.append(int(d['aromatic']))
        # If number hydrogen is used as a
        if hydrogen:
            h_t.append(d['num_h'])
        h.append(h_t)
    return h


# In[ ]:


class Qm9():
#class Qm9(data.Dataset):
    # Constructor
    def __init__(self, idx, vertex_transform=qm9_nodes, edge_transform=qm9_edges,
                 target_transform=None, e_representation='raw_distance'):
        self.idx = idx
        self.vertex_transform = vertex_transform
        self.edge_transform = edge_transform
        self.target_transform = target_transform
        self.e_representation = e_representation

    def __getitem__(self,index):
        
        g, target = xyz_graph_reader(self.idx[index])
        if self.vertex_transform is not None:
            h = self.vertex_transform(g)

        if self.edge_transform is not None:
            g, e = self.edge_transform(g)

        if self.target_transform is not None:
            target = self.target_transform(target)

        #g：adjacent matrix
        #h：node properties（list of list）
        #e：diction，key:edge，value:properties
        return (g, h, e), target

    def __len__(self):
        return len(self.idx)

    def set_target_transform(self, target_transform):
        self.target_transform = target_transform


# In[ ]:


def get_values(obj, start, end):
    vals = []
    for i in range(start, end):
        vals.append(obj[i][1])
    return vals
def get_graph_stats(graph_obj_handle):
    inputs = len(graph_obj_handle)
    res = get_values(graph_obj_handle, 0, inputs) 
    param = np.array(res)
    
    stat_dict = {}
    
    stat_dict['target_mean'] = np.mean(param, axis=0)
    stat_dict['target_std'] = np.std(param, axis=0)

    return stat_dict


# In[ ]:




