import myParser

def findNodeOrder(objs):
    # separate in links and nodes
    nodes, links, _, _ = myParser.createGraph(objs)
    # build Graph
    # each node remembers its connections
    remaining_nodes = [True] * len(nodes)
    remaining_links = [True] * len(links)
    orderedNodes = []
    graphHasLeaves = 1
    while graphHasLeaves:
        curr_order = []
        graphHasLeaves = 0
        updateList = []
        for iNode, node in enumerate(nodes):
            bla = 1
            if remaining_nodes[iNode]:
                if isLeaf(node, links, remaining_links):
                    graphHasLeaves = 1  
                    # put node in list for order i
                    curr_order.append(node)
                    linkIDs = []
                    for iLink, link in enumerate(links):
                        if link[0] == node or link[1] == node:
                            linkIDs.append(iLink)
                    updateList.append((iNode, linkIDs)) 
        # remove node and references to it in list of links at end of current iteration
        for update in updateList:
            remaining_nodes[update[0]] = False
            for iLink in update[1]:
                remaining_links[iLink] = False

        orderedNodes.append(curr_order)
    # last element is empty list by definition
    del orderedNodes[-1]
    orderedNodes.append([node for iNode, node in enumerate(nodes) if remaining_nodes[iNode]])

    print("nodes", nodes)
    print("links", links)
    print("remaining nodes", remaining_nodes)
    print("remaining links", remaining_links)
    print("orderedNodes", orderedNodes)
    return orderedNodes

def isLeaf(node, links, remaining_links):
    connections = 0
    for iLink, link in enumerate(links):
        if remaining_links[iLink]:
            if node == link[0] or node == link[1]:
                connections += 1
    return connections < 2


## testing
# glmFile = '/Users/jacquesdechalendar/benson/glm-plotter/example/test.glm'
glmFile = '/Users/jacquesdechalendar/benson/glm-plotter/example/IEEE123.glm'
objs, _, _ = myParser.readGLM(glmFile)
findNodeOrder(objs)