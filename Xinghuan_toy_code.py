NODES = 10
affi_thre = 0.5 # If the weight of node j on node i is less than affi_thre, then it means node j will not influence node i's opinion so much. Then, node i will be less tolerant to the opinion difference between them. Vice versa.
infl_num = int(NODES * 0.1)
infl_conn_num = list(range(int(NODES * 0.5), NODES)) # The number of the nodes that an influential node can influence is randomly drawn from this list 
no_infl_conn_num = list(range(1, int(NODES * 0.2))) # The number of the nodes that a non-influential node can influence is randomly drawn from this list 
ROBUST = 50 # This robust is the same meaning with Taro's robustness

import networkx as nx
import random as rd
import numpy as np 
import matplotlib.pyplot as plt
import operator 

network = nx.DiGraph()

infl_list = rd.sample(range(NODES), infl_num) # We randomly generate a influence nodes list and the length of this list equals infl_num. 

for i in range(NODES):
    nodes_list = list(range(NODES))
    nodes_list.remove(i)
    if i in infl_list: 
        con_num = rd.choice(infl_conn_num) # The influential node randomly chooses the number of nodes it can influence 
        connect_list = rd.sample(nodes_list, con_num) # Based on the connection number it has, the influential node randomly chooses the nodes from the nodes list to build edge 
        network.add_node(i, opinion=rd.uniform(-1,1), non_aff_confi=0.3, # aff_confidence = affinity_confidence. I will explain it later 
                         aff_confi=0.6, con_num=con_num,
                         connect_list=connect_list, influential=True)
    else: 
        con_num = rd.choice(no_infl_conn_num) # The same as above 
        connect_list = rd.sample(nodes_list, con_num)
        network.add_node(i, opinion=rd.uniform(-1,1), non_aff_confi=0.3, 
                         aff_confi=0.6, con_num=con_num,
                         connect_list=connect_list, influential=False)           

def create_network(): 
    for i in network.nodes(): 
        connect_list = network.nodes[i]['connect_list']
        if connect_list != []: # It is possible that the connect list is empty 
            for j in range(len(connect_list)):
                network.add_edge(i, connect_list[j], weight=0) # If node j is in the connect list of node i, then node i will build edge with node j
    for i in network.nodes():
        pre_list = list(network.predecessors(i))
        if any(pre_list): # For each node j which could influence node i, the sum of the weight of node j on node i is 1. 
            pre_num = len(pre_list)
            weight_list = (np.random.dirichlet(np.ones(pre_num), size=1).tolist())[0]
            for j in range(pre_num): 
                    network.edges[pre_list[j], i]['weight'] = weight_list[j]

                                  
def update_opinion(): 
    for i in network.nodes(): 
        if any(network.predecessors(i)): 
            for j in network.predecessors(i): 
            	# Given that node i is influential node and the weight of node j on node i is less than affi_thre (it means node j is not very important for i), then if the opinion difference 
            	# between node j and node i is less than the non_aff_confi, with probability less than 50%, the node i could update the opinion from the opinion of node j. Vice versa for other situations
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
    for i in network.nodes(): 
        if any(network.predecessors(i)):
            i_pre = []
            i_pre[:] = network.predecessors(i)
            for j in i_pre: 
            	# For node j which could influence node i, if their opinion difference is bigger than 2, with probability less than 50%, node i will decrease the weight that node j on itself 0.05. 
                if abs(network.nodes[i]['opinion']-network.nodes[j]['opinion']) > 2 and rd.uniform(0, 1) < 0.05:  
                    network[j][i]['weight'] = network[j][i]['weight'] - 0.05
                    if network[j][i]['weight'] <= 0:
                        network.remove_edge(j, i)
                        network.nodes[j]['connect_list'].remove(i)
                    pre_list = i_pre
                    if len(pre_list) != 1: # If the weight is removed from node j which could influence node i, then we randomly pick another node which could influence node i and add 0.05 to the weight of that node
                        if j in pre_list: 
                            pre_list.remove(j)
                        opi_diff = {}
                        for k in pre_list: 
                            opi_diff.update({k: abs(network.nodes[i]['opinion']-network.nodes[k]['opinion'])})
                        add_weight = min(opi_diff.items(), key=operator.itemgetter(1))[0]
                        network[add_weight][i]['weight'] = network[add_weight][i]['weight'] + 0.05



create_network()     
for i in range(3): 
     update_opinion()
     print(network.nodes(data='opinion'))
    update_network()            
            
        
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


