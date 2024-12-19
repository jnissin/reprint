import azure.ai.formrecognizer as fr


def bounding_regions_intersect(br_1: fr.BoundingRegion, br_2: fr.BoundingRegion) -> bool:
    r1 = br_1.polygon
    r2 = br_2.polygon
    
    r1_min_x = min(r1[::2])
    r1_max_x = max(r1[::2])
    r1_min_y = min(r1[1::2])
    r1_max_y = max(r1[1::2])
    
    r2_min_x = min(r2[::2])
    r2_max_x = max(r2[::2])
    r2_min_y = min(r2[1::2])
    r2_max_y = max(r2[1::2])
    
    return not (r1_max_y < r2_min_y or r2_max_y < r1_min_y or
               r1_min_x > r2_max_x or r2_min_x > r1_max_x)