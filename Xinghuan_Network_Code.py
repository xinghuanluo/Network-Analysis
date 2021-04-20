
import networkx as nx
import matplotlib.pyplot as plt
import random as rd
import matplotlib.pyplot as plt
import pandas as pd 

NODES = 500
INFL = 50
lambda_1 = 0.6 
lambda_2 = 0.3
same_opinion_thre = 0.3
ROBUST = 20 

network = nx.DiGraph()

new_opinion_list = []
for i in range(NODES): 
    network.add_node(i, opinion=rd.uniform(-1, 1), 
                     influential=False, 
                     same_opinion_list=[], 
                     diff_opinion_list=[])
    new_empty = []
    new_opinion_list.append(new_empty)

influ_list = []
for i in rd.sample(network.nodes(), int((INFL))): 
    influ_list.append(i)

for i in influ_list[0:25]: 
    network.nodes[i]['influential'] = True  
    network.nodes[i]['opinion'] = 0.9
    
for i in influ_list[25:]: 
    network.nodes[i]['influential'] = True  
    network.nodes[i]['opinion'] = -0.9

def network_graph(): 
    node_color = []
    node_size = []
    for i in network.nodes(): 
        if network.nodes[i]['influential'] == True: 
            node_color.append('red')
            node_size.append(100)
        elif network.nodes[i]['influential'] == False: 
            node_color.append('blue')
            node_size.append(30)
    nx.draw(network, node_color=node_color, node_size=node_size)
    plt.show()

def create_network(): 
    for i in network.nodes(): 
        for j in network.nodes(): 
            if i != j: 
                if network.nodes[i]['influential'] == True \
                    and abs(network.nodes[i]['opinion'] - network.nodes[j]['opinion']) < lambda_1 \
                    and rd.uniform(0, 1) < 0.95: 
                        network.add_edge(i, j)
                        
                elif network.nodes[i]['influential'] == False \
                    and abs(network.nodes[i]['opinion'] - network.nodes[j]['opinion']) < lambda_2 \
                    and rd.uniform(0, 1) < 0.05: 
                        network.add_edge(i, j)

def get_same_diff_opinion(): 
    for i in network.nodes(): 
        network.nodes[i]['same_opinion_list'] = []
        network.nodes[i]["diff_opinion_list"] = []
        for j in network.nodes(): 
            if i != j: 
                if abs(network.nodes[i]['opinion']-network.nodes[j]['opinion']) <= same_opinion_thre:
                   network.nodes[i]['same_opinion_list'].append(j)
        if list(network.predecessors(i)): 
            for n in network.predecessors(i):
                if abs(network.nodes[i]['opinion']-network.nodes[n]['opinion']) > same_opinion_thre:
                    network.nodes[i]["diff_opinion_list"].append(n)

def update_edges(): 
    for i in network.nodes(): 
        if network.nodes[i]["diff_opinion_list"]:
            j = rd.choice(network.nodes[i]["diff_opinion_list"])
            if network.nodes[j]['influential'] == True and rd.uniform(0, 1) < 1:
                network.remove_edge(j, i)
            elif network.nodes[j]['influential'] == False: 
                network.remove_edge(j, i)
            for k in network.nodes[i]['same_opinion_list']: 
                if (k, i) not in network.edges(): 
                    if network.nodes[k]['influential'] == True and rd.uniform(0, 1) < 0.5:
                        network.add_edge(k, i)
                        break 
                    elif network.nodes[k]['influential'] == False and rd.uniform(0, 1) < 0.2:
                        network.add_edge(k, i)
                        break 

def update_opinion(): 
    opinion_temp = []
    for i in network.nodes():
        if network.nodes[i]['influential'] == True:
            normfac = network.in_degree(i) + ROBUST
            opinion_temp.append(network.nodes[i]['opinion']*ROBUST/normfac)
            for j in network.predecessors(i):
                if abs(network.nodes[i]['opinion'] - network.nodes[j]['opinion']) < lambda_2: 
                    opinion_temp[i] = opinion_temp[i] + network.nodes[j]['opinion']/normfac
        elif network.nodes[i]['influential'] == False:
            normfac = network.in_degree(i) + 1
            opinion_temp.append(network.nodes[i]['opinion']/normfac)
            for j in network.predecessors(i):
                if abs(network.nodes[i]['opinion'] - network.nodes[j]['opinion']) < lambda_1: 
                    opinion_temp[i] = opinion_temp[i] + network.nodes[j]['opinion']/normfac           

    for i in network.nodes():
        network.nodes[i]['opinion'] = opinion_temp[i]
        new_opinion_list[i].append(network.nodes[i]['opinion'])



create_network()
update_opinion()
for j in range(100): 
    get_same_diff_opinion()
    update_edges()
    update_opinion()
network_graph()

opinion_df = pd.DataFrame(new_opinion_list).T
opinion_df.plot(legend=False)
plt.show()

opinion_df.var(axis="columns").plot(legend=False)
plt.show()

influ_opinion_list = [new_opinion_list[i] for i in influ_list]
influ_opinion_df = pd.DataFrame(influ_opinion_list).T
influ_opinion_df.plot(legend=False)
plt.show()


