# -*- encoding: utf-8 -*-
from osgeo import ogr


class Node1():
    ROOT = 0
    BRANCH = 1
    LEAF = 2
    layer = None
    threshold = 5
    min_level = 4

    def __init__(self, parent, rect):
        self.parent = parent
        self.children = [None, None, None, None]
        if parent == None:
            self.depth = 0
        else:
            self.depth = parent.depth + 1
        self.rect = rect
        x0, y0, x1, y1 = rect
        if self.parent == None:
            self.type = Node1.ROOT
        else:
            self.type = Node1.BRANCH
    
    #_____预划分
    def init_subdivide(self):
        
            
        if self.type == Node1.LEAF:
            return
        if self.depth >= Node1.min_level:
            self.type = Node1.LEAF
            return
        x0,y0,x1,y1 = self.rect
        semi_width = (x1 - x0)/2
        semi_height = (y1 - y0) / 2
        rects = []
        rects.append( (x0, y0, x0 + semi_width, y0 + semi_height) )
        rects.append( (x0, y0 + semi_height, x0 + semi_width, y1) )
        rects.append( (x0 + semi_width, y0 + semi_height, x1, y1) )
        rects.append( (x0 + semi_width, y0, x1, y0 + semi_height) )
        for n in range(len(rects)):            
            self.children[n] = self.getinstance(rects[n])
            self.children[n].init_subdivide() # << recursion            


    #____划分
    def subdivide(self):
        if self.type == Node1.LEAF:
            return
        x0,y0,x1,y1 = self.rect
        semi_width = (x1 - x0)/2
        semi_height = (y1 - y0) / 2
        rects = []
        rects.append( (x0, y0, x0 + semi_width, y0 + semi_height) )
        rects.append( (x0, y0 + semi_height, x0 + semi_width, y1) )
        rects.append( (x0 + semi_width, y0 + semi_height, x1, y1) )
        rects.append( (x0 + semi_width, y0, x1, y0 + semi_height) )
        for n in range(len(rects)):
            span = self.spans_feature(rects[n])
            if span:
                self.children[n] = self.getinstance(rects[n])
                self.children[n].subdivide() # << recursion
            else:
                node = self.getinstance(rects[n])
                node.type = Node1.LEAF
                self.children[n] = node
    
    def is_point_within_rect(self, point, rect):
        x = float(point.GetX())
        y = float(point.GetY())
        if x > rect[0] and y > rect[1] and x < rect[2] and y < rect[3]:
            return True
        else:
            return False
    def point_count_within_rect(self, rect):
        Node1.layer.ResetReading()
        cnt = 0
        for fea in Node1.layer:
            geom = fea.GetGeometryRef()
            if self.is_point_within_rect(geom, self.rect):
                cnt += 1
        return cnt

    
    #________判断一个几何体是否落在矩形内

    def is_point_within(self, geom):    
        return geom.Within(self.create_polygon_from_2_points(*self.rect))

    #__________从矩形创建多边形

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

    #——————————计算落在矩形内的点数目
    def point_within_polygon(self, rect):
        envelope_polygon = self.create_polygon_from_2_points(*rect)
        Node1.layer.ResetReading()
        cnt = 0
        for fea in Node1.layer:
            geom = fea.GetGeometryRef()
            if geom.Within(envelope_polygon):
                cnt += 1
        return cnt

    def spans_feature(self, rect):
        if self.point_count_within_rect(self.rect) <= Node1.threshold:
            return False
        else:
            return True

    def getinstance(self,rect):
        return Node1(self,rect)            
    



class QuadTree1:
    maxdepth = 0 # the "depth" of the tree
    allnodes = []
    leaves = []
    def __init__(self, rootnode, layer, threshold, min_level):
        Node1.layer = layer
        Node1.threshold = threshold
        Node1.min_level = min_level
        self.rootnode = rootnode
        rootnode.init_subdivide()
        self.traverse(rootnode)
        for node in QuadTree1.leaves:
            if node.spans_feature(node.rect):
                node.type = Node1.BRANCH
                node.subdivide()
        self.traverse(rootnode)

    def traverse(self, node):
        QuadTree1.allnodes.append(node)
        if node.type == Node1.LEAF:
            QuadTree1.leaves.append(node)
            if node.depth > QuadTree1.maxdepth:
                QuadTree1.maxdepth = node.depth
        for child in node.children:
            if child != None:
                self.traverse(child) # << recursion

    def return_path(self, geom):
        self.path = ''

        def inner(node):
            
            for i in range(len(node.children)):
                child = node.children[i]
                if child != None and child.is_point_within_rect(geom, child.rect):
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