import sys
import time
from operator import itemgetter
from igraph import *


# Colors class for pretty print
class bcolors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    ENDC = '\033[0m'


# Function that add a vertex on a dict
def add_vertex_dico(vertex_dict, u, index_dict):
    try:
        vertex_dict[u]
    except:
        vertex_dict[u] = index_dict
        index_dict += 1
    return index_dict

# Function that create and return a graph from a given path file
def graph_from_file(path):
    g = Graph()

    print("\t-> reading given file")
    with open(path) as fp:

        # Parse the first line (number of nodes)
        line = fp.readline()
        number_nodes = int(line)
        g.add_vertices(number_nodes)

        # Ignoring following lines (degrees)
        """
        count = 0
        for line in fp:   
            count += 1
            if count == number_nodes:
                break
        """

        # Parse the following lines (edges)
        index_dict = 0
        vertex_dict = {}
        edges_list = []
        for line in fp:
            line_split = line.split("\t")
            u = int(line_split[0])
            v = int(line_split[1])
            index_dict = add_vertex_dico(vertex_dict, u, index_dict)
            index_dict = add_vertex_dico(vertex_dict, v, index_dict)
            tuple_uv = (vertex_dict[u], vertex_dict[v])
            edges_list.append(tuple_uv)
        
        print("\t-> filling graph with vertex/edges")
        g.add_edges(edges_list)

    return g

# Function that return true if an element is in a list of list, false otherwise
def is_elm_in_listlist(elm, lists):
    for sub in lists:
        for elm_sub in sub:
            if elm == elm_sub:
                return True
    return False

# Function that remove the visited vertex from the to_visit list
def update_to_visit(to_visit, sub_component):
    if len(to_visit) == len(sub_component):
        return []
    else:
        return [item for item in to_visit if item not in sub_component]

# Function that return the largest component of a given graph
def graph_isolation_component(g):
    component_list = []

    to_visit = list(range(g.vcount()))
    while len(to_visit) > 0:
        sub_component = g.subcomponent(to_visit[0], mode='ALL')
        component_list.append(sub_component)
        #print("sub component founded: {}".format(sub_component))
        to_visit = update_to_visit(to_visit, sub_component)
        #print("vertices to visit: {}".format(to_visit))        

    print("\t-> getting the largest component")
    max_sub = max(component_list, key=len)
    #print(component_list)
    return g.subgraph(max_sub)

# Function that calculate the distance between root and last leaf of a bfs tree
def distance(bfs_tree, root_bfs, last_node):
    dist = 0
    dad = last_node
    while True:
        dist += 1
        dad = bfs_tree[dad]

        # If gone up to the root
        if dad == root_bfs:
            break
    
    return dist

# Function that return the path between root and last leaf of a bfs tree
def bfs_path(bfs_tree, root_bfs, last_node):
    path = []
    dad = last_node
    while True:
        path.append(dad)
        dad = bfs_tree[dad]

        # If gone up to the root
        if dad == root_bfs:
            path.append(dad)            
            break
    
    return path

# Function that do a multiple sweep on given graph g
def multiple_sweep(g):
    eccentricity_list = []  # Ecc of vertices, ie: [(u, ecc(u)), (v, ecc(v))]

    # Doing 3 BFS
    root_bfs = 0
    for nb_turn in range(3):
        bfs_res = g.bfs(root_bfs)

        last_node = bfs_res[0][-1]
        ecc = distance(bfs_res[2], root_bfs, last_node)
        eccentricity_list.append((root_bfs, ecc))

        # Set the next BFS root
        if nb_turn < 2:
            root_bfs = last_node

    return eccentricity_list, bfs_res, root_bfs

# Function that do the middle tactic
def middle_tactic(g, bfs, root):
    last_vertex = bfs[0][-1]
    path = bfs_path(bfs[2], root, last_vertex)
    
    path_len = len(path)
    middle_vertex = []
    middle_vertex.append(path[int(path_len / 2)])

    # If path is odd, get the second middle
    if path_len % 2 == 0:
        middle_vertex.append(path[int(path_len / 2 - 1)])
    
    # Calculate eccentricity of the middle(s)
    eccentricity_middle = []
    for i in range(len(middle_vertex)):
        bfs_res = g.bfs(middle_vertex[i])
        last_node = bfs_res[0][-1]
        ecc = distance(bfs_res[2], middle_vertex[i], last_node)
        eccentricity_middle.append((middle_vertex[i], ecc))

    return eccentricity_middle

# Function that calculate the diameter of given graph g
def diameter_calculation(g):
    # Doing multiple sweep
    print("\t-> doing multiple sweep")
    eccentricity_list, last_bfs_tree, last_root = multiple_sweep(g)

    # Doing the middle tactic
    print("\t-> doing the middle tactic")
    eccentricity_middle = middle_tactic(g, last_bfs_tree, last_root)

    # Getting bound
    print("\t-> getting lower and upper bound")    
    eccentricity_list += eccentricity_middle
    lower_bound = max(eccentricity_list, key=itemgetter(1))[1]
    upper_bound = 2 * min(eccentricity_list, key=itemgetter(1))[1]

    # Getting diameter
    diam_approximation = int((lower_bound + upper_bound) / 2)

    # Getting radius
    radius_approximation = min(eccentricity_list, key=itemgetter(1))[1]

    # Getting center vertex
    center_vertex = min(eccentricity_list, key=itemgetter(1))[0]

    # Pretty print
    print(bcolors.GREEN + "\nResults" + bcolors.ENDC)
    print("\tAn enclosure of the diameter: " + bcolors.BLUE + "{}".format(lower_bound), end='')
    print(bcolors.ENDC + " <= diameter(G) <= " + bcolors.BLUE + "{}".format(upper_bound) + bcolors.ENDC)
    print("\tAn approximation of the diameter: " + bcolors.BLUE + "{}".format(diam_approximation) + bcolors.ENDC)
    print("\tAn approximation of the radius: " + bcolors.BLUE + "{}".format(radius_approximation) + bcolors.ENDC)
    print("\tVertex from the center is: " + bcolors.BLUE + "{}".format(center_vertex) + bcolors.ENDC)


def main():
    print("\n========================")
    print("  Giant Graph Calculus")
    print("========================")

    g = Graph()
    path = sys.argv[1]

    # Reading file
    print(bcolors.GREEN + "\nReading file and filling graph" + bcolors.ENDC)
    g = graph_from_file(path)
    
    # Isolation of the largest component
    print(bcolors.GREEN + "\nIsolation of the largest component" + bcolors.ENDC)
    g = graph_isolation_component(g)

    # Calculate diameter
    print(bcolors.GREEN + "\nCalculate diameter" + bcolors.ENDC)
    start = time.time()
    diameter_calculation(g)
    end = time.time() - start
    print("\tTime to calculates diam has taken: " + bcolors.BLUE + "{}".format(round(end, 3)) + bcolors.ENDC + " secondes")


if __name__ == "__main__":
  main()
