from lasagna.tree.tree import Tree

# Generate an example if run from the command line
if __name__ == '__main__':

    _ROOT, _DEPTH, _WIDTH = list(range(3))

    print("\n\n   --------- Tree of life --------- \n")
    tree_of_life = Tree()

    tree_of_life.add_node("Life")  # root node
    tree_of_life.add_node("Archaebacteria", "Life")
    tree_of_life.add_node("Eukaryotes", "Life")
    tree_of_life.add_node("Protista", "Eukaryotes")
    tree_of_life.add_node("Plants", "Eukaryotes")
    tree_of_life.add_node("Fungi", "Eukaryotes")
    tree_of_life.add_node("Algae", "Plants")
    tree_of_life.add_node("Mosses", "Plants")
    tree_of_life.add_node("Ferns", "Plants")
    tree_of_life.add_node("Animals", "Eukaryotes")
    tree_of_life.add_node("Sponges", "Animals")
    tree_of_life.add_node("Flatworms", "Animals")
    tree_of_life.add_node("Arthropods", "Animals")
    tree_of_life.add_node("Insects", "Arthropods")
    tree_of_life.add_node("Crustaceans", "Arthropods")
    tree_of_life.add_node("Vertebrates", "Animals")
    tree_of_life.add_node("Fish", "Vertebrates")
    tree_of_life.add_node("Amphibians", "Vertebrates")
    tree_of_life.add_node("Reptiles", "Vertebrates")
    tree_of_life.add_node("Mammals", "Vertebrates")

    # Add some data to the vertebrates
    tree_of_life["Vertebrates"].data = 'they have backbones'
    tree_of_life["Fish"].data = 'they swim'
    tree_of_life["Amphibians"].data = 'they croak'
    tree_of_life["Reptiles"].data = 'they stick to walls'
    tree_of_life["Mammals"].data = 'they have udders'

    print("List of nodes:")
    print(list(tree_of_life.nodes.keys()))
    print("")

    print("Children of node 'Vertebrates'")
    print(tree_of_life.nodes['Vertebrates'].children)
    print("")

    print(tree_of_life.display('Life'))

    print("\n***** Depth-first *****")
    for node_id in tree_of_life.traverse("Life"):
        print(node_id)

    print("\n***** Width-first *****")
    for node_id in tree_of_life.traverse("Life", mode=_WIDTH):
        print(node_id)

    print("\n***** Width-first of all data in vertebrates *****")
    for node_id in tree_of_life.traverse("Vertebrates", mode=_WIDTH):
        print("%s - %s" % (node_id, tree_of_life[node_id].data))

    print("\nLeaves:")
    print(tree_of_life.find_leaves('Life'))

    print("\nBranches:")
    print(tree_of_life.find_branches('Life'))

    print("\nPath to root from Fish:")
    print(tree_of_life.path_to_root('Fish'))

    # - - - - - - -
    print("\n\n   --------- Tree of Fibonacci numbers --------- \n")
    tree_of_n = Tree()

    tree_of_n.add_node(1)  # root node
    tree_of_n.add_node(2, 1)
    tree_of_n.add_node(3, 2)
    tree_of_n.add_node(5, 3)
    tree_of_n.add_node(8, 5)
    tree_of_n.add_node(13, 8)
    tree_of_n.add_node(21, 13)

    tree_of_n.display(1)
