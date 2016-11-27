#!/usr/bin/python

import snap
from snap import *
import pylab as pl
import numpy as np
import random, collections

# Undirected null model

Undir = TUNGraph.New()
AlreadyEdge = set()
step1 = 0
step2 = 0
step3 = 0
step4 = 0

# Creating super nodes
for i in range(117659):
    Undir.AddNode(i)

# Creating edges between super nodes
for i in range(142674):
    a = random.randint(0,117658)
    b = a
    while (b == a):
        b = random.randint(0,117658)
    while (a,b) in AlreadyEdge or (b,a) in AlreadyEdge:
        a = random.randint(0,117658)
        b = a
        while (b == a):
            b = random.randint(0,117658)
    Undir.AddEdge(a,b)
    AlreadyEdge.add((a,b))
    AlreadyEdge.add((b,a))
    step1 += 1

# Creating regular nodes
for i in range(117659, 266888):
    Undir.AddNode(i)


# Creating edges between super nodes and regular nodes
DistDict = {1: 63848, 2: 33914, 3: 11678, 4: 4668, 5: 1853, 6: 846, 7: 384, 8: 199, 9: 109, 10: 41, 11: 38, 12: 30, 13: 20, 14: 6, 15: 8, 16: 4, 17: 1, 18: 3, 19: 2, 21: 2, 23: 1, 24: 1, 25: 1, 27: 1, 28: 1}

synsets = collections.defaultdict(list)
supernodes = range(117659)
for key, value in DistDict.iteritems():
    for i in range(value):
        super = random.choice(supernodes)
        supernodes.remove(super)
        for j in range(key):
            reg = random.randint(117659, 266887)
            while (super, reg) in AlreadyEdge:
                reg = random.randint(117659, 266887)
            Undir.AddEdge(super, reg)
            synsets[super].append(reg)
            step3 += 1

# Creating edges between regular nodes in the same synset
for super in synsets:
    subnodes = synsets[super]
    for wordA in subnodes:
        for wordB in subnodes:
            if wordA == wordB: continue
            if (wordB,wordA) not in AlreadyEdge:
                Undir.AddEdge(wordA, wordB)
                step4 += 1

# Creating edges between regular nodes across synsets
for i in range(46122):
    supernodeA, supernodeB = random.sample(synsets.keys(), 2)
    regnodeA = random.choice(synsets[supernodeA])
    regnodeB = random.choice(synsets[supernodeB])
    while (regnodeA, regnodeB) in AlreadyEdge or (regnodeB, regnodeA) in AlreadyEdge:
        regnodeB = random.choice(synsets[supernodeB])
    Undir.AddEdge(regnodeA, regnodeB)
    step2 += 1

print Undir.GetNodes()
print Undir.GetEdges()

CfVec = snap.TFltPrV()
Cf = snap.GetClustCf(Undir, CfVec, -1)
print "Avg Clustering Coefficient: %f" % (Cf)

node_degrees = [node.GetOutDeg() for node in Undir.Nodes()]
min_degree = min(node_degrees)
max_degree = max(node_degrees)

degree_distr = [0] * (max_degree + 1)
for degree in node_degrees:
    degree_distr[degree] += 1

def normalize(vector):
    total = float(sum(vector))
    return [elem / total for elem in vector]

print normalize(degree_distr), min_degree, max_degree

degree_distr = normalize(degree_distr)

average_degree = sum([i * degree_distr[i] for i in range(len(degree_distr))])

print "Avg Degree %f" % (average_degree)
print "Max %f" % (min_degree)
print "Min %f" % (max_degree)

#Debugging
#DegToCntV = snap.TIntPrV()
#snap.GetDegCnt(Undir, DegToCntV)
#totalDegree = 0
#totalNodes = 0
#maxDeg = 0
#minDeg = 1000000
#print DegToCntV
#for item in DegToCntV:
#    totalDegree += item.GetVal1() * item.GetVal2()
#    totalNodes += item.GetVal2()
#    if item.GetVal1() > maxDeg:
#        maxDeg = item.GetVal1()
#    if item.GetVal1() < minDeg:
#        minDeg = item.GetVal1()
#Ad = totalDegree / float(totalNodes)
#print "Avg Degree %f" % (Ad)
#print "Max %f" % (maxDeg)
#print "Min %f" % (minDeg)

#print step1, step2, step3, step4
