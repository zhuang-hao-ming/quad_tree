
# -*- encoding: utf-8 -*-

from osgeo import ogr
from quad_tree import Node, QuadTree
from quad_tree1 import Node1, QuadTree1




#___ 检查一个字段是否存在
def check_if_field_exists(layer, field_name):
    from sets import Set

    layer_defn = layer.GetLayerDefn()
    field_name_set = Set([layer_defn.GetFieldDefn(i).GetName() for i in range(0, layer_defn.GetFieldCount())])     
    if field_name in field_name_set:
        return True
    else:
        return False




def main():

    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    data_set = driver.Open('./shp/HZ_Point/HZ_Point.shp', 1)

    # data_set = driver.Open('./shp/HZ_Point/HZ_Point_Add10.shp', 1)

    # data_set = driver.Open('./shp/point.shp', 1)
    # data_set = driver.Open('./shp/point1.shp', 1)
    layer = data_set.GetLayer()
    #layer1 = data_set1.GetLayer()
    point_envelope = layer.GetExtent()
    #point_envelope1 = layer1.GetExtent()
    

        
    
    
    
    

    envelope_rect = [point_envelope[0] - 1,point_envelope[2] - 1, point_envelope[1] + 1, point_envelope[3] + 1]
    #envelope_rect1 = [point_envelope1[0] - 1,point_envelope1[2] - 1, point_envelope1[1] + 1, point_envelope1[3] + 1]

    print envelope_rect
    #print envelope_rect1
    # import sys
    # sys.exit()



    # root_node = Node(None, envelope_rect)
    # tree = QuadTree(root_node, layer, 3000)

    root_node = Node1(None, envelope_rect)
    tree = QuadTree1(root_node, layer, 2500, 3)




    #___________________________绘图
    if True:
        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib.path as mpath
        import matplotlib.patches as mpatches
        all_nodes = tree.allnodes
        fig = plt.figure(figsize=(20, 20))
        ax = fig.add_subplot(111)
        xoff = (point_envelope[1] - point_envelope[0]) / 10
        yoff = (point_envelope[3] - point_envelope[2]) / 10
        ax.set_xlim(point_envelope[0] - xoff, point_envelope[1] + xoff)
        ax.set_ylim(point_envelope[2] - yoff, envelope_rect[3] + yoff)

        paths = []
        cet_x = []
        cet_y = []
        tree_paths = []
        for node in all_nodes:
            rect = node.rect
            cet_x.append((rect[2] + rect[0]) / 2)
            cet_y.append((rect[3] + rect[1]) / 2)
            tree_paths.append(tree.return_node_path(node))
            all_x = [rect[0], rect[0], rect[2], rect[2], rect[0]]
            all_y = [rect[1], rect[3], rect[3], rect[1], rect[1]]
            codes = [mpath.Path.MOVETO] + (len(all_x)-1)*[mpath.Path.LINETO]
            path = mpath.Path(np.column_stack((all_x,all_y)), codes)
            paths.append(path)
            
        for path in paths:
            patch = mpatches.PathPatch(path, facecolor='none', edgecolor='black')
            ax.add_patch(patch)
        for x,y,tree_path in zip(cet_x, cet_y, tree_paths):
            plt.text(x, y, tree_path, fontsize=10)
        

        ax.set_aspect(1.0)
        
        
        
        
        layer.ResetReading()
        all_x = []
        all_y = []
        for fea in layer:
            geo = fea.GetGeometryRef()
            x = geo.GetX()
            y = geo.GetY()
            all_x.append(x)
            all_y.append(y)

        plt.plot(all_x, all_y, marker='+', color='r', ls='')
        plt.show()
    #————————————————————————————————————————————————————————————————————————————————————————


    


    if not check_if_field_exists(layer, 'tree_path1'):
        field_name = ogr.FieldDefn("tree_path1", ogr.OFTString)
        field_name.SetWidth(24)
        layer.CreateField(field_name)
    layer.ResetReading()    
    for fea in layer:
        str = ''
        geom = fea.GetGeometryRef()
        path = tree.return_path(geom)        
        #print(path)
        fea.SetField("tree_path1", path)
        layer.SetFeature(fea)
        

    data_set = None
        








if __name__ == '__main__':
    main()