import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
from itertools import chain, combinations
from copy import copy, deepcopy


# modified from itertools documentation
def powerset(iterable):
    "powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))

def exclude_subsets(iter_of_sets):
    """ 
    This function takes an interable of sets and returns a new list with all
    sets that are a subset of any other eliminated 
    """
    keep_sets = []
    for si in iter_of_sets:
        any_subset = False
        for sj in iter_of_sets:
            if si != sj and set(si).issubset(sj):
                any_subset = True
                break
        if not any_subset:
            keep_sets.append(si)

    return keep_sets

def contains_subsets(iter_of_sets):
    """
    Checks whether a collection of sets contains any sets which are subsets of
    another set in the collection
    """
    for si in iter_of_sets:
        for sj in iter_of_sets:
            if si != sj and set(sj).issubset(si):
                return True
    
    return False

def PID_sets(k):
    """ This function returns a list of the sets in the redundancy lattice """
    double_powerset = list(powerset(powerset(range(1, k+1))))
    keep_sets = []
    for subset in double_powerset:
        if not contains_subsets(subset):
            keep_sets.append(subset)
    return keep_sets

def partial_order(alpha, beta):
    """ Check whether alpha preceeds beta on the redundancy lattice. This is the
    partial ordering we apply to the set calculated by PID sets """
    # for every element in beta there must be an element in alpha that is a 
    # subset of it. 
    for b, elem_b in enumerate(beta):
        has_subset = False
        for a, elem_a in enumerate(alpha):
            if set(elem_a).issubset(elem_b):
                has_subset = True

        # if we didn't find a subset for any b in beta we're done
        if has_subset == False:
            return False

    # if we dont find a violation than it must be true
    return True


def redundancy_lattice(pid_sets):
    """ construct the redundancy lattice using the partial ordering defined
    above """
    # this gets all of the paths but it doesn't get us the edges that we
    # actually want. The problem is, for example our relationship is satisfied
    # for beta = {1, 2, 3} and alpha = {{1}, {2}, {3}}. What we want are
    # actually the longest paths through our graph. thats why negative weight
    #
    # this approach is more or less copied from ryan james lattice package
    # https://github.com/dit/lattices/blob/master/lattices/lattice.py
    D_temp = nx.DiGraph()
    for atom_a, atom_b in combinations(pid_sets, 2):
        if partial_order(atom_a, atom_b):
            D_temp.add_edge(atom_a, atom_b, weight=-1)
        elif partial_order(atom_b, atom_a):
            D_temp.add_edge(atom_b, atom_a, weight=-1)

    
    # We want the edges that make up the longest paths
    lengths = nx.algorithms.all_pairs_bellman_ford_path_length(D_temp)

    # new graph with only the edges we care about
    lattice = nx.DiGraph()
    lattice.add_nodes_from(D_temp.nodes())

    # now we can select the paths we want
    for p, path in lengths:
        for w, weight in path.items():
            if weight == -1:
                lattice.add_edge(p, w)
    return lattice

def pretty_labels_map(atom_labels):
    """
    transforms all of these crazy tuples into the notation used in williams and
    beer I_min PID
    """
    rename_map = {}
    for label in atom_labels:
        new_label = str(label)

        # eliminate commas and spaces
        new_label = new_label.replace(',', '')
        new_label = new_label.replace(' ', '')

        # replace braces
        new_label = new_label.replace('(', '{')
        new_label = new_label.replace(')', '}')

        # put them in a map
        rename_map[label] = new_label[1:-1]
    
    return rename_map

def get_y_positions(n_inputs, vertical_height, pad):
    """
    Calculate the y position for nodes on the horizontal redundancy lattice
    """
    num_atoms = {2: 4,
                 3: 18,
                 4: 166}
    four_nodes = np.linspace(pad, vertical_height - pad, 4)
    three_nodes = four_nodes[:3]

    # this is for 3 inputs this code will have to be changed for more
    y_pos = np.zeros(num_atoms[n_inputs]) + (vertical_height / 3)
    y_pos[1:4] = three_nodes
    y_pos[4:7] = three_nodes
    y_pos[7:11] = four_nodes
    y_pos[11:14] = three_nodes
    y_pos[14:17] = three_nodes

    return y_pos



def pid_plot(pid_series, n_inputs):
    """ 
    Takes a set of values from a partial information decomposition and
    returns a plot to aid in quick comparisons between decompositions.
    """
    # calculate lattice
    D = redundancy_lattice(PID_sets(3))

    # Get the values we need for sorting
    D_top = list(nx.topological_sort(D))[0]
    from_top = nx.single_source_shortest_path_length(D, source=D_top)
    D_sorted = sorted(list(D.nodes()), key=lambda x: from_top[x])


    # sort lattice, relabel
    label_map = pretty_labels_map(D.nodes())
    fancy = nx.relabel_nodes(D, label_map)
    fancy_sorted = [label_map[n] for n in D_sorted]
    # drop the rule column
    pid_series = pid_series.drop('rule', axis=1)

    # unpack keys and labels from dictionary into lists
    atoms = [k for k in pid_series.columns]
    values = [pid_series[atom].values[0] for atom in atoms]

    fig, ax = plt.subplots(nrows=2, sharex=True, gridspec_kw={'height_ratios': [2.5, 1]})

    # get the dimensions of the axes for the lattice
    bbox = ax[1].get_window_extent()
    print(bbox)
    # calculate positions for nodes
    nhpad = 50
    nvpad = 20
    node_x = np.linspace(nhpad, bbox.width - nhpad, len(D.nodes()))
    node_y = get_y_positions(n_inputs, bbox.height, nvpad)
    pos_dict = {lab:(x, y) for lab, x, y in zip(fancy_sorted, node_x, node_y)}

    # draw network
    ax[1].vlines(node_x, ymin=min(node_y), ymax=max(node_y), color='lightgrey', 
                 linestyle='dotted', alpha=0.8)
    nx.draw_networkx(fancy, ax=ax[1], node_size=5, pos=pos_dict, font_size=10,
                     arrows=False, alpha=0.6, with_labels=False,
                     edge_color='grey', node_color='grey')
    nx.draw_networkx_labels(fancy, ax=ax[1], pos=pos_dict,
                            verticalalignment='center', font_size=8)
    ax[1].spines['top'].set_visible(False)
    ax[1].spines['bottom'].set_visible(False)
    ax[1].spines['left'].set_visible(False)
    ax[1].spines['right'].set_visible(False)



    # actual bar plot
    # we're going to shade regions on the barplot
    halfway = np.diff(node_x)[0] / 2
    first_point = node_x[0] - halfway
    mid_points = np.hstack((first_point, node_x + halfway))
    pal = sns.color_palette('RdBu', 7)
    al = 0.2
    # fill sections from redundancy to synergy
    ax[0].fill_between(mid_points[:2], 0, 1.1, color=pal[0], edgecolor=pal[0], alpha=al)
    ax[0].fill_between(mid_points[1:5], 0, 1.1, color=pal[1], edgecolor=pal[1], alpha=al)
    ax[0].fill_between(mid_points[4:8], 0, 1.1, color=pal[2], edgecolor=pal[2], alpha=al)
    ax[0].fill_between(mid_points[7:12], 0, 1.1, color=pal[3], edgecolor=pal[3], alpha=al)
    ax[0].fill_between(mid_points[11:15], 0, 1.1, color=pal[4], edgecolor=pal[4], alpha=al)
    ax[0].fill_between(mid_points[14:18], 0, 1.1, color=pal[5], edgecolor=pal[5], alpha=al)
    ax[0].fill_between(mid_points[17:], 0, 1.1, color=pal[6], edgecolor=pal[6], alpha=al)




    ax[0].bar(node_x, values, width=(node_x[2] - node_x[1]) * 0.8)
    ax[0].set_xticklabels(atoms, rotation=90)
    ax[0].set_xticks([])
    ax[0].set_ylabel('Partial Information (bits)')
    ax[0].spines['top'].set_visible(False)
    ax[0].spines['right'].set_visible(False)
    fig.tight_layout(h_pad=0)

    return ax