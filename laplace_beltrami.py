from import_OBJ import importOBJ
import numpy as np
from scipy.sparse import csr_matrix
from vector_angle import angle_between
from mpmath import *
import math
from scipy.sparse.linalg import eigsh

'''this function takes a path to an obj-mesh with the maximum number of point_limit points,
and calculates n_evals eigenvalues of the Laplace Beltrami operator of the mesh'''


def laplace_beltrami_eigenvalues(mesh, n_evals=(1, 50), point_limit=100000):

    # import OBJ file
    layer_name, ismanifold, points, edges, faces, efaces, fvertices = importOBJ(mesh)

    # number of points = dimension of eigenvalue problem
    n = len(points)

    # point limit
    if n > point_limit:
        print ("mesh has ", n, " points")
        return 9, []

    # check if mesh is manifold and return empty array if not
    if not ismanifold:
        print ("mesh is not a manifold")
        return 1, []

    # initialize matrices
    # since both matrices have the same entries filled, one initializer for row and col for both will do
    row = []
    col = []
    dataA = []
    dataM = []

    # iterate over every edge of the mesh:
    ecount = 0  # need this to retrieve adjacent faces to this edge from the eface list
    for e in edges:

        # get the incident vertice to the edge
        i = e[0]
        j = e[1]

        # append i and j because of symetry
        row.append(i)
        row.append(j)
        col.append(j)
        col.append(i)

        # initialize cotangent and area for this edge
        cotangent = 0
        area = 0

        # find adjacent faces to this edge
        for face in efaces[ecount]:

            # get all vertices in (this adjacend) face (to the current edge)
            for v in fvertices[face]:
                #print (v)
                if v != i and v!= j:
                    corner = v

            # other two edges of this face as vectors
            ci = np.array(points[i]) - np.array(points[corner])
            cj = np.array(points[j]) - np.array(points[corner])

            # angle/contangent between the vectors
            angle = angle_between(ci, cj)
            if angle == 0.0:
                print ('an angle of the mesh is zero')
                return 2, []
            cotangent += cot(angle)

            # area of the triangle
            a = np.linalg.norm(np.array(points[i]) - np.array(points[corner]))
            b = np.linalg.norm(np.array(points[j]) - np.array(points[corner]))
            c = np.linalg.norm(np.array(points[i]) - np.array(points[j]))

            area += 0.25 * math.sqrt((a + b + c) * (-a + b + c) * (a - b + c) * (a + b - c))

        # poopulate A and M matrices, two times for symetry
        dataA.append(0.5*cotangent)
        dataA.append(0.5*cotangent)

        dataM.append(area/12)
        dataM.append(area/12)

        # need this to retrieve adjacent faces to this edge from the eface list
        ecount += 1

    ### loop end here, construct Matrices

    # cast dataA matrix to proper dtype because cotangent calculation returns 'mpf' type
    dataA = np.array(dataA, dtype=float)

    # construct priliminary matrices
    A = csr_matrix((dataA, (row, col)), shape=(n, n), dtype=float).toarray()
    M = csr_matrix((dataM, (row, col)), shape=(n, n), dtype=float).toarray()

    # take the rowsums
    sumA = np.sum(A,1)
    sumA = np.diag(sumA)
    sumM = np.sum(M,1)
    sumM = np.diag(sumM)

    A = -A + sumA
    M = M + sumM

    # solve GEV problem
    evals, evecs = eigsh(A, n_evals[1], M, sigma=0.0, which='LM')

    #print (np.sort(evals_small))
    #print (evecs_small)


    return 0, evals[n_evals[0]:], evecs[:,n_evals[0]:], np.array(points), A, M



