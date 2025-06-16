import copy

#def place_by_sumo(antenna, car_material_id, lane_boundary_dict, cars_with_antenna=None):
def placement_rx(antenna,positions,obj_height):
    antenna = copy.deepcopy(antenna)
    antenna.clear()
    
    x_center,y_center,z_center = positions
    deltaz = obj_height/2 + 0.1
    
    antenna.add_vertice((x_center, y_center, z_center - deltaz))

    return antenna