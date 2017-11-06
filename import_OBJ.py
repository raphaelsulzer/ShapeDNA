def importOBJ(path_to_file):

    ismanifold = True
    layer_name = 'layer1'

    # open file into list of lines
    f = open(path_to_file, 'r')
    lines = f.readlines()

    # initializes return lists
    points = []
    edges = []
    faces = []
    efaces = []     # tells which faces are incident to this edge
    fvertices = []  # tells which vertices are incident to this face

    # iterate over every line and extract points and faces
    facecount = 0
    for line in lines:

        # identification of line
        ident = line[0]

        # extract layer name
        if ident == 'g':        # get layer name
            layer_name = line.split()[1]

        # create point list
        elif ident == 'v':      # built point list
            line = line.split()
            p = [float(line[1]), float(line[2]), float(line[3])]
            points.append(p)

        # create facelist, edgelist, edgeface-list and facevertex-list
        elif ident == 'f':      # built edge and face list
            line = line.split()
            # (create) vertices of this face
            fv = [int(line[1])-1, int(line[2])-1, int(line[3])-1]
            # create fvertice list (of this face)
            fvertices.append(fv)

            # construct edge list. -1 (above) so that edge entries correspond to vertices idx
            # i.e. construct edges of this face (with vetrices)
            es = [ [fv[0], fv[1]], [fv[1], fv[2]], [fv[0], fv[2]] ]

            # initialize face list
            f = []

            # however, if one of the edges was already dealt with (by being incident to another face):
            # iterate over these 3 edges and check
            edgecount = 0
            for e in es:
                # could also be edge in different direction
                er = [e[1], e[0]]
                # if the edge is already in the edge list,
                # add the existing edge to the face
                # and add this face to the edge in the efaces list
                if e in edges:
                    f.append(edges.index(e))
                    # construct efaces list
                    efaces[edges.index(e)].append(facecount)
                    # check if this edge has more than two faces, i.e. (polygonal) mesh is not manifold
                    if len(efaces[edges.index(e)]) > 2:
                        ismanifold = False
                elif er in edges:
                    f.append(edges.index(er))
                    # construct efaces list
                    efaces[edges.index(er)].append(facecount)
                    # check if this edge has more than two faces, i.e. (polygonal) mesh is not manifold
                    if len(efaces[edges.index(er)]) > 2:
                        ismanifold = False
                # else add the new edge
                else:
                    #print (e)
                    edges.append(e)
                    f.append(len(edges)-1)
                    # construct efaces list
                    efaces.append([facecount])
                    # check if this edge has more than two faces, i.e. (polygonal) mesh is not manifold
                    if len(efaces[edges.index(e)]) > 2:
                        ismanifold = False
                    edgecount += 1



            facecount += 1


            faces.append(f)


    return layer_name, ismanifold, points, edges, faces, efaces, fvertices
