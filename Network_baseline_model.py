NODES = 10
affi_thre = 0.5 
infl_num = int(NODES * 0.1)
infl_conn_num = list(range(int(NODES * 0.5), NODES)) 
no_infl_conn_num = list(range(1, int(NODES * 0.2))) 
ROBUST = 50 

import networkx as nx
import random as rd
import numpy as np 
import matplotlib.pyplot as plt
import operator 

network = nx.DiGraph()

# We randomly generate a influence nodes list and the length of this list equals infl_num. 
infl_list = rd.sample(range(NODES), infl_num) 

for i in range(NODES):
    """
    The influential node randomly chooses the number of nodes it can influence. 
    Based on the connection number it has, the influential node randomly chooses the nodes from the nodes list to build edge 
    """
    nodes_list = list(range(NODES))
    nodes_list.remove(i)
    if i in infl_list: 
        con_num = rd.choice(infl_conn_num) 
        connect_list = rd.sample(nodes_list, con_num) 
        network.add_node(i, opinion=rd.uniform(-1,1), non_aff_confi=0.3, 
                         aff_confi=0.6, con_num=con_num,
                         connect_list=connect_list, influential=True)
    else: 
        con_num = rd.choice(no_infl_conn_num) 
        connect_list = rd.sample(nodes_list, con_num)
        network.add_node(i, opinion=rd.uniform(-1,1), non_aff_confi=0.3, 
                         aff_confi=0.6, con_num=con_num,
                         connect_list=connect_list, influential=False)           

def create_network(): 
    """
    This function create the network. It will also assign weights to the node which could affect other nodes. 
    """
    for i in network.nodes(): 
        connect_list = network.nodes[i]['connect_list']
        if connect_list != []: 
            for j in range(len(connect_list)):
                network.add_edge(i, connect_list[j], weight=0) 
    for i in network.nodes():
        pre_list = list(network.predecessors(i))
        if any(pre_list): 
            pre_num = len(pre_list)
            weight_list = (np.random.dirichlet(np.ones(pre_num), size=1).tolist())[0]
            for j in range(pre_num): 
                    network.edges[pre_list[j], i]['weight'] = weight_list[j]

                                  
def update_opinion():
    """
    This function updates the opinion. Influential nodes will are less likely to change their opinion. 
    Non-influential nodes are more likely to be influenced by other people. 
    """
    for i in network.nodes(): 
        if any(network.predecessors(i)): 
            for j in network.predecessors(i): 
                if network.nodes[i]['influential'] == True and rd.uniform(0, 1) < 0.5: 
                    if abs(network.nodes[i]['opinion']-network.nodes[j]['opinion']) < network.nodes[i]['non_aff_confi'] \
                    and network.edges[j, i]['weight'] < affi_thre:
                        network.nodes[i]['opinion'] = network.nodes[i]['opinion'] + network.nodes[j]['opinion'] * (network[j][i]['weight'] / ROBUST)
                    
                    elif abs(network.nodes[i]['opinion']-network.nodes[j]['opinion']) < network.nodes[i]['aff_confi'] \
                    and network[j][i]['weight'] > affi_thre:
                        network.nodes[i]['opinion'] = network.nodes[i]['opinion'] + network.nodes[j]['opinion'] * (network[j][i]['weight'] / ROBUST )
                        
                elif network.nodes[i]['influential'] == False and rd.uniform(0, 1) < 0.5: 
                    if abs(network.nodes[i]['opinion']-network.nodes[j]['opinion']) < network.nodes[i]['non_aff_confi'] \
                    and network.edges[j, i]['weight'] < affi_thre:
                        network.nodes[i]['opinion'] = network.nodes[i]['opinion'] + network.nodes[j]['opinion'] * network[j][i]['weight'] 
                    
                    elif abs(network.nodes[i]['opinion']-network.nodes[j]['opinion']) < network.nodes[i]['aff_confi'] \
                    and network[j][i]['weight'] > affi_thre:
                        network.nodes[i]['opinion'] = network.nodes[i]['opinion'] + network.nodes[j]['opinion'] * network[j][i]['weight']
                    
def update_network(): 
    """
    This function update the opinion of whole network. It will remove the nodes with 0 weight on other nodes. 
    """
    for i in network.nodes(): 
        if any(network.predecessors(i)):
            i_pre = []
            i_pre[:] = network.predecessors(i)
            for j in i_pre: 
                if abs(network.nodes[i]['opinion']-network.nodes[j]['opinion']) > 2 and rd.uniform(0, 1) < 0.05:  
                    network[j][i]['weight'] = network[j][i]['weight'] - 0.05
                    if network[j][i]['weight'] <= 0:
                        network.remove_edge(j, i)
                        network.nodes[j]['connect_list'].remove(i)
                    pre_list = i_pre
                    if len(pre_list) != 1: 
                        if j in pre_list: 
                            pre_list.remove(j)
                        opi_diff = {}
                        for k in pre_list: 
                            opi_diff.update({k: abs(network.nodes[i]['opinion']-network.nodes[k]['opinion'])})
                        add_weight = min(opi_diff.items(), key=operator.itemgetter(1))[0]
                        network[add_weight][i]['weight'] = network[add_weight][i]['weight'] + 0.05


# The network will be updated by 1000 times. 
create_network()     
for i in range(1000): 
     update_opinion()
     print(network.nodes(data='opinion'))
     update_network()            
            
# Plotting the network graph.    
node_color = []
node_size = []
edge_color = []
for i in network.nodes(): 
    if len(network.nodes[i]['connect_list']) > (NODES * 1/8): 
        node_color.append('red')
        node_size.append(100)
    else: 
        node_color.append('blue')
        node_size.append(50)
for i in network.nodes(): 
    if any(network.predecessors(i)):
        for j in network.predecessors(i): 
            if network[j][i]['weight'] > 0.5: 
                edge_color.append('red')
            else: 
                edge_color.append('blue')
            
nx.draw(network, node_color=node_color, node_size=node_size, edge_color=edge_color)
plt.show()


