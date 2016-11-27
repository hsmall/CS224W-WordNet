#!/usr/bin/python

import snap
from snap import *
import pylab as pl
import numpy as np
import random, collections

# Directed null model

Dir = TNGraph.New()
AlreadyEdge = set()
step1 = 0
step2 = 0
step3 = 0
step4 = 0

# Creating super nodes
for i in range(60926):
    Dir.AddNode(i)

# Creating edges between super nodes
for i in range(104748):
    a = random.randint(0,60925)
    b = a
    while (b == a):
        b = random.randint(0,60925)
    while (a,b) in AlreadyEdge:
        a = random.randint(0,60925)
        b = a
        while (b == a):
            b = random.randint(0,60925)
    Dir.AddEdge(a,b)
    AlreadyEdge.add((a,b))
    step1 += 1

# Creating regular nodes
for i in range(60926, 107943):
    Dir.AddNode(i)

# Creating edges between super nodes and regular nodes
DistDict = {1: 44105, 2: 10863, 3: 3491, 4: 1348, 5: 598, 6: 271, 7: 108, 8: 61, 9: 36, 10: 8, 11: 11, 12: 10, 13: 6, 14: 2, 15: 3, 16: 1, 17: 1, 18: 1, 20: 2}
synsets = collections.defaultdict(list)
supernodes = range(60926)
for key, value in DistDict.iteritems():
    for i in range(value):
        super = random.choice(supernodes)
        supernodes.remove(super)
        for j in range(key):
            reg = random.randint(60926, 107942)
            Dir.AddEdge(super, reg)
            Dir.AddEdge(reg, super)
            synsets[super].append(reg)
            step3 += 1

# Creating edges between regular nodes in the same synset
for super in synsets:
    subnodes = synsets[super]
    for wordA in subnodes:
        for wordB in subnodes:
            if wordA == wordB: continue
            if random.random() < 0.5:
                Dir.AddEdge(wordB, wordA)
            else:
                Dir.AddEdge(wordA, wordB)
            step4 += 1

# Creating edges between regular nodes across synsets
for i in range(149039):
    print i
    supernodeA, supernodeB = random.sample(synsets.keys(), 2)
    regnodeA = random.choice(synsets[supernodeA])
    regnodeB = random.choice(synsets[supernodeB])
    Dir.AddEdge(regnodeA, regnodeB)
    step2 += 1

print Dir.GetNodes()
print Dir.GetEdges()

CfVec = snap.TFltPrV()
Cf = snap.GetClustCf(Dir, CfVec, -1)
print "Avg Clustering Coefficient: %f" % (Cf)

node_degrees = [node.GetOutDeg() for node in Dir.Nodes()]
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

#DegToCntV = snap.TIntPrV()
#snap.GetDegCnt(Dir, DegToCntV)
#totalDegree = 0
#totalNodes = 0
#maxDeg = 0
#minDeg = 1000000
#print DegToCntV
#for item in DegToCntV:
#    print item.GetVal2(), item.GetVal1()
#    totalDegree += item.GetVal1() * item.GetVal2()
#    totalNodes += item.GetVal2()
#    if item.GetVal1() > maxDeg:
#        maxDeg = item.GetVal1()
#    if item.GetVal1() < minDeg:
#        minDeg = item.GetVal1()
#print totalDegree, totalNodes
#Ad = totalDegree / float(totalNodes)

#print step1, step2, step3, step4
