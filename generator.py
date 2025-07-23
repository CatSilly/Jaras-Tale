# generator.py

import random
import math
import builtins

def rects_overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)

def generate_portals(map_id):
    mw = builtins.MAP_WIDTH
    mh = builtins.MAP_HEIGHT

    if map_id == 0:
        return [
            {"x": mw - 60, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 1},
            {"x": 10, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 5}
        ]
    elif map_id == 1:
        return [
            {"x": 50, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 0},
            {"x": mw - 100, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 2},
            {"x": mw // 2 - 25, "y": mh - 60, "width": 50, "height": 50, "target": 13}
        ]
    elif map_id == 2:
        return [
            {"x": 50, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 1},
            {"x": mw - 100, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 3}
        ]
    elif map_id == 3:
        return [
            {"x": 50, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 2},
            {"x": mw - 100, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 4}
        ]
    elif map_id == 4:
        return [
            {"x": 50, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 3}
        ]
    elif map_id == 5:
        return [
            {"x": mw - 60, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 0},
            {"x": 10, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 7}
        ]
    elif map_id == 7:
        return [
            {"x": mw - 60, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 5},
            {"x": 10, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 8},
            {"x": mw // 2 - 25, "y": mh - 60, "width": 50, "height": 50, "target": 9}
        ]
    elif map_id == 8:
        return [
            {"x": mw - 60, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 7}
        ]
    elif map_id == 9:
        return [
            {"x": mw // 2 - 25, "y": 10, "width": 50, "height": 50, "target": 7}
        ]
    elif map_id == 10:
        return [
            {"x": mw // 2 - 25, "y": mh - 60, "width": 50, "height": 50, "target": 11}
        ]
    elif map_id == 11:
        return [
            {"x": mw // 2 - 25, "y": 10, "width": 50, "height": 50, "target": 10},
            {"x": mw - 60, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 12}
        ]
    elif map_id == 12:
        return [
            {"x": 10, "y": mh // 2 - 50, "width": 50, "height": 100, "target": 11}
        ]
    elif map_id == 13:
        return [
            {"x": mw // 2 - 25, "y": 10, "width": 50, "height": 50, "target": 1},
            {"x": mw // 2 - 25, "y": mh // 2 - 150, "width": 50, "height": 100, "target": -999}
        ]

    return []
    
def generate_roads(houses, mw, mh, map_id=None):
    roads = []

    main_road = {
        "x": 0,
        "y": mh // 2 - 75,
        "width": mw,
        "height": 120,
        "type": "main"
    }
    roads.append(main_road)

    if map_id == 7:
        branch_road = {
            "x": mw // 2 - 25,
            "y": main_road["y"] + main_road["height"],
            "width": 50,
            "height": mh - (main_road["y"] + main_road["height"]),
            "type": "branch"
        }
        roads.append(branch_road)

    for house in houses:
        h_center_x = house["x"] + house["width"]//2
        h_center_y = house["y"] + house["height"]//2

        if h_center_y < main_road["y"]:
            road = {
                "x": h_center_x - 25,
                "y": h_center_y,
                "width": 50,
                "height": main_road["y"] - h_center_y,
                "type": "side"
            }
        else:
            road = {
                "x": h_center_x - 25,
                "y": main_road["y"] + main_road["height"],
                "width": 50,
                "height": h_center_y - (main_road["y"] + main_road["height"]),
                "type": "side"
            }
        roads.append(road)

    return roads

def generate_houses(mw, mh, roads=[]):
    houses = []
    spacing = 400
    max_attempts = 100
    house_count = 10

    for _ in range(house_count):
        attempt = 0
        while attempt < max_attempts:
            width  = random.randint(150, 300)
            height = random.randint(120, 200)
            x = random.randint(100, mw - width - 100)
            y = random.randint(100, mh - height - 100)

            overlap = any(
                math.hypot(h["x"] - x, h["y"] - y) < spacing
                for h in houses
            )
            if not overlap:
                for r in roads:
                    if rects_overlap(x, y, width, height,
                                     r["x"] - 40, r["y"] - 40, r["width"] + 500, r["height"] + 500):
                        overlap = True
                        break

            if not overlap:
                houses.append({
                    "x": x, "y": y,
                    "width": width, "height": height,
                    "body_color": (238, 232, 170),
                    "roof_color": (178, 34, 34),
                    "door_color": (101, 67, 33),
                    "window_color": (173, 216, 230)
                })
                break
            attempt += 1

    return houses

def generate_trees(mw, mh, count, houses=[], monsters=[], roads=[]):
    trees = []
    grid_size = 500
    cols, rows = mw // grid_size, mh // grid_size
    per_cell = max(1, count // (cols * rows))

    def is_valid(x, y, tw, th):
        for h in houses:
            if rects_overlap(x, y - th, tw, th, h["x"], h["y"], h["width"], h["height"]):
                return False
        for m in monsters:
            if math.hypot(m["x"] - x, m["y"] - y) < m["radius"] + max(tw, th):
                return False
        for r in roads:
            if rects_overlap(x, y - th, tw, th, r["x"], r["y"], r["width"], r["height"]):
                return False
        return True

    for i in range(cols):
        for j in range(rows):
            for _ in range(per_cell):
                tw = random.randint(10, 20)
                th = random.randint(30, 50)
                x = random.randint(i * grid_size + tw, (i + 1) * grid_size - tw)
                y = random.randint(j * grid_size + th, (j + 1) * grid_size - th)
                if is_valid(x, y, tw, th):
                    trees.append({
                        "x": x, "y": y,
                        "trunk_width": tw,
                        "trunk_height": th,
                        "canopy_radius": random.randint(30, 50)
                    })

    while len(trees) < count:
        tw = random.randint(10, 20)
        th = random.randint(30, 50)
        x = random.randint(tw, mw - tw)
        y = random.randint(th, mh - th)
        if is_valid(x, y, tw, th):
            trees.append({
                "x": x, "y": y,
                "trunk_width": tw,
                "trunk_height": th,
                "canopy_radius": random.randint(30, 50)
            })

    return trees

def generate_pine_trees(mw, mh, count, houses=[], monsters=[], roads=[], upper_half=False):
    trees = []
    grid_size = 500
    cols, rows = mw // grid_size, mh // grid_size
    per_cell = max(1, count // (cols * rows))

    def is_valid(x, y, tw, th):
        for h in houses:
            if rects_overlap(x, y - th, tw, th, h["x"], h["y"], h["width"], h["height"]):
                return False
        for m in monsters:
            if math.hypot(m["x"] - x, m["y"] - y) < m["radius"] + max(tw, th):
                return False
        for r in roads:
            if rects_overlap(x, y - th, tw, th, r["x"] - 40, r["y"] - 40, r["width"] + 80, r["height"] + 80):
                return False
        return True

    for i in range(cols):
        for j in range(rows):
            for _ in range(per_cell):
                tw = random.randint(10, 20)
                th = random.randint(30, 50)
                x = random.randint(i * grid_size + tw, (i + 1) * grid_size - tw)
                y_start = j * grid_size + th
                y_end = (j + 1) * grid_size - th
                if upper_half:
                    y_end = min(y_end, mh // 2)
                if y_end <= y_start:
                    continue
                y = random.randint(y_start, y_end)
                if is_valid(x, y, tw, th):
                    trees.append({
                        "x": x, "y": y,
                        "trunk_width": tw,
                        "trunk_height": th,
                        "canopy_radius": random.randint(30, 50)
                    })

    while len(trees) < count:
        tw = random.randint(10, 20)
        th = random.randint(30, 50)
        x = random.randint(tw, mw - tw)
        y_min = th
        y_max = mh // 2 if upper_half else mh - th
        if y_max <= y_min:
            continue
        y = random.randint(y_min, y_max)
        if is_valid(x, y, tw, th):
            trees.append({
                "x": x, "y": y,
                "trunk_width": tw,
                "trunk_height": th,
                "canopy_radius": random.randint(30, 50)
            })

    return trees

def generate_acacia_trees(mw, mh, count, houses=[], monsters=[], roads=[], bottom_half=False, lake_polygon=None):
    trees = []
    grid_size = 500
    cols, rows = mw // grid_size, mh // grid_size
    per_cell = max(1, count // (cols * rows))

    def point_in_polygon(x, y, polygon):
        inside = False
        n = len(polygon)
        for i in range(n):
            j = (i - 1) % n
            xi, yi = polygon[i]
            xj, yj = polygon[j]
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 0.00001) + xi):
                inside = not inside
        return inside

    def is_valid(x, y, tw, th):
        for h in houses:
            if rects_overlap(x, y - th, tw, th, h["x"], h["y"], h["width"], h["height"]):
                return False
        for m in monsters:
            if math.hypot(m["x"] - x, m["y"] - y) < m["radius"] + max(tw, th):
                return False
        for r in roads:
            if rects_overlap(x, y - th, tw, th, r["x"] - 40, r["y"] - 40, r["width"] + 80, r["height"] + 80):
                return False
        if lake_polygon and point_in_polygon(x, y, lake_polygon):
            return False
        return True

    for i in range(cols):
        for j in range(rows):
            for _ in range(per_cell):
                tw = random.randint(8, 12)
                th = random.randint(42, 56)
                x = random.randint(i * grid_size + tw, (i + 1) * grid_size - tw)
                y_start = j * grid_size + th
                y_end = (j + 1) * grid_size - th
                if bottom_half:
                    y_start = max(y_start, mh // 2)
                if y_end <= y_start:
                    continue
                y = random.randint(y_start, y_end)
                if is_valid(x, y, tw, th):
                    trees.append({
                        "x": x, "y": y,
                        "trunk_width": tw,
                        "trunk_height": th,
                        "canopy_width": random.randint(36, 46),
                        "canopy_height": random.randint(18, 22),
                        "tree": "acacia"
                    })

    while len(trees) < count:
        tw = random.randint(8, 12)
        th = random.randint(42, 56)
        x = random.randint(tw, mw - tw)
        y_min = mh // 2 if bottom_half else th
        y_max = mh - th
        if y_max <= y_min:
            continue
        y = random.randint(y_min, y_max)
        if is_valid(x, y, tw, th):
            trees.append({
                "x": x, "y": y,
                "trunk_width": tw,
                "trunk_height": th,
                "canopy_width": random.randint(36, 46),
                "canopy_height": random.randint(18, 22),
                "tree": "acacia"
            })

    return trees
    
import random

def generate_grass(mw, mh, count):
    return [{"x": random.randint(0, mw), "y": random.randint(0, mh), "radius": random.randint(2, 5)} for _ in range(count)]

def generate_dry_grass(mw, mh, count, houses=[], monsters=[], roads=[], bottom_half=False):
    grasses = []
    for _ in range(count):
        x = random.randint(0, mw)
        y = random.randint(mh // 2 if bottom_half else 0, mh)
        if all(not rects_overlap(x, y, 6, 6, h["x"], h["y"], h["width"], h["height"]) for h in houses):
            grasses.append({"x": x, "y": y})
    return grasses