# -*- encoding: utf-8 -*-
from osgeo import ogr








# quadtree.py
# Implements a Node and QuadTree class that can be used as 
# base classes for more sophisticated implementations.
# Malcolm Kesson Dec 19 2012
class Node():
    ROOT = 0
    BRANCH = 1
    LEAF = 2
    minsize = 1   # Set by QuadTree
    layer = None
    threshold = 5
    #_______________________________________________________
    # In the case of a root node "parent" will be None. The
    # "rect" lists the minx,minz,maxx,maxz of the rectangle
    # represented by the node.
    def __init__(self, parent, rect):
        self.parent = parent
        self.children = [None,None,None,None]
        if parent == None:
            self.depth = 0
        else:
            self.depth = parent.depth + 1
        self.rect = rect
        x0,z0,x1,z1 = rect
        if self.parent == None:
            self.type = Node.ROOT
        # elif self.point_within_polygon(rect) < Node.threshold:
        #     self.type = Node.LEAF
        else:
            self.type = Node.BRANCH



    #_________________________

    def is_point_within(self, geom):
        return geom.Within(self.create_polygon_from_2_points(*self.rect))

    #_________________________

    def create_polygon_from_2_points(self, minx, miny, maxx, maxy):
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(minx, miny)
        ring.AddPoint(minx, maxy)
        ring.AddPoint(maxx, maxy)
        ring.AddPoint(maxx, miny)
        ring.AddPoint(minx, miny)
        

        # Create polygon
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)

        return poly


    def point_within_polygon(self, rect):
        envelope_polygon = self.create_polygon_from_2_points(*rect)
        Node.layer.ResetReading()
        cnt = 0
        for fea in Node.layer:
            geom = fea.GetGeometryRef()
            if geom.Within(envelope_polygon):
                cnt += 1
        return cnt
    #__________________________        
    def getinstance(self,rect):
        return Node(self,rect)            
    



    
    #_______________________________________________________
    # Recursively subdivides a rectangle. Division occurs 
    # ONLY if the rectangle spans a "feature of interest".
    def subdivide(self):
        if self.type == Node.LEAF:
            return
        x0,z0,x1,z1 = self.rect
        semi_width = (x1 - x0)/2
        semi_height = (z1 - z0) / 2
        rects = []
        rects.append( (x0, z0, x0 + semi_width, z0 + semi_height) )
        rects.append( (x0, z0 + semi_height, x0 + semi_width, z1) )
        rects.append( (x0 + semi_width, z0 + semi_height, x1, z1) )
        rects.append( (x0 + semi_width, z0, x1, z0 + semi_height) )
        for n in range(len(rects)):
            span = self.spans_feature(rects[n])
            if span == True:
                self.children[n] = self.getinstance(rects[n])
                self.children[n].subdivide() # << recursion
            else:
                node = self.getinstance(rects[n])
                node.type = Node.LEAF
                self.children[n] = node
    #_______________________________________________________
    # A utility proc that returns True if the coordinates of
    # a point are within the bounding box of the node.
    def contains(self, x, z):
        x0,z0,x1,z1 = self.rect
        if x >= x0 and x <= x1 and z >= z0 and z <= z1:
            return True
        return False
    #_______________________________________________________
    # Sub-classes must override these two methods.
    def getinstance(self,rect):
        return Node(self,rect)            
    def spans_feature(self, rect):
        if self.point_within_polygon(rect) <= Node.threshold:
            return False
        else:
            return True
  
#===========================================================            
class QuadTree():
    maxdepth = 1 # the "depth" of the tree
    leaves = []
    allnodes = []
    #_______________________________________________________
    def __init__(self, rootnode, layer, threshold):
        Node.layer = layer
        Node.threshold = threshold
        self.rootnode = rootnode
        rootnode.subdivide() # constructs the network of nodes
        #self.prune(rootnode)
        self.traverse(rootnode)
    #_______________________________________________________
    # Sets children of 'node' to None if they do not have any
    # LEAF nodes.        
    def prune(self, node):
        if node.type == Node.LEAF:
            return 1
        leafcount = 0
        removals = []
        for child in node.children:
            if child != None:
                leafcount += self.prune(child)
                if leafcount == 0:
                    removals.append(child)
        for item in removals:
            n = node.children.index(item)
            node.children[n] = None        
        return leafcount
    #_______________________________________________________
    # Appends all nodes to a "generic" list, but only LEAF 
    # nodes are appended to the list of leaves.
    def traverse(self, node):
        QuadTree.allnodes.append(node)
        if node.type == Node.LEAF:
            QuadTree.leaves.append(node)
            if node.depth > QuadTree.maxdepth:
                QuadTree.maxdepth = node.depth
        for child in node.children:
            if child != None:
                self.traverse(child) # << recursion

    def return_path(self, geom):
        self.path = ''

        def inner(node):
            
            for i in range(len(node.children)):
                child = node.children[i]
                if child != None and child.is_point_within(geom):
                    self.path += str(i)
                    inner(child)
                    return
        inner(self.rootnode)
        return self.path
    #____________________ return node's path
    def return_node_path(self, tree_node):

        self.path = ''
        
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint((tree_node.rect[0] + tree_node.rect[2]) / 2, (tree_node.rect[1] + tree_node.rect[3]) / 2)

        def inner(node):
            
            for i in range(len(node.children)):
                child = node.children[i]
                if child != None and child.is_point_within(point):
                    self.path += str(i)
                    inner(child)
                    return
        inner(self.rootnode)
        return self.path



