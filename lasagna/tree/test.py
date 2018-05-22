from lasagna.tree.tree import Tree

# Generate an example if run from the command line
if __name__ == '__main__':

    (_ROOT, _DEPTH, _WIDTH) = list(range(3))

    print("\n\n   --------- Tree of life --------- \n")
    treeOfLife = Tree()

    treeOfLife.add_node("Life")  # root node
    treeOfLife.add_node("Archaebacteria", "Life")
    treeOfLife.add_node("Eukaryotes", "Life")
    treeOfLife.add_node("Protista", "Eukaryotes")
    treeOfLife.add_node("Plants", "Eukaryotes")
    treeOfLife.add_node("Fungi", "Eukaryotes")
    treeOfLife.add_node("Algae", "Plants")
    treeOfLife.add_node("Mosses", "Plants")
    treeOfLife.add_node("Ferns", "Plants")
    treeOfLife.add_node("Animals", "Eukaryotes")
    treeOfLife.add_node("Sponges", "Animals")
    treeOfLife.add_node("Flatworms", "Animals")
    treeOfLife.add_node("Arthropods", "Animals")
    treeOfLife.add_node("Insects", "Arthropods")
    treeOfLife.add_node("Crustaceans", "Arthropods")
    treeOfLife.add_node("Vertebrates", "Animals")
    treeOfLife.add_node("Fish", "Vertebrates")
    treeOfLife.add_node("Amphibians", "Vertebrates")
    treeOfLife.add_node("Reptiles", "Vertebrates")
    treeOfLife.add_node("Mammals", "Vertebrates")

    # Add some data to the vertebrates
    treeOfLife["Vertebrates"].data = 'they have backbones'
    treeOfLife["Fish"].data = 'they swim'
    treeOfLife["Amphibians"].data = 'they croak'
    treeOfLife["Reptiles"].data = 'they stick to walls'
    treeOfLife["Mammals"].data = 'they have udders'

    print("List of nodes:")
    print(list(treeOfLife.nodes.keys()))
    print("")

    print("Children of node 'Vertebrates'")
    print(treeOfLife.nodes['Vertebrates'].children)
    print("")

    print(treeOfLife.display('Life'))

    print("\n***** Depth-first *****")
    for nodeID in treeOfLife.traverse("Life"):
        print(nodeID)

    print("\n***** Width-first *****")
    for nodeID in treeOfLife.traverse("Life", mode=_WIDTH):
        print(nodeID)

    print("\n***** Width-first of all data in vertebrates *****")
    for nodeID in treeOfLife.traverse("Vertebrates", mode=_WIDTH):
        print("%s - %s" % (nodeID, treeOfLife[nodeID].data))

    print("\nLeaves:")
    print(treeOfLife.findLeaves('Life'))

    print("\nBranches:")
    print(treeOfLife.findBranches('Life'))

    print("\nPath to root from Fish:")
    print(treeOfLife.pathToRoot('Fish'))

    # - - - - - - -
    print("\n\n   --------- Tree of Fibonacci numbers --------- \n")
    treeOfN = Tree()

    treeOfN.add_node(1)  # root node
    treeOfN.add_node(2, 1)
    treeOfN.add_node(3, 2)
    treeOfN.add_node(5, 3)
    treeOfN.add_node(8, 5)
    treeOfN.add_node(13, 8)
    treeOfN.add_node(21, 13)

    treeOfN.display(1)