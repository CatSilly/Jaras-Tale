import pygame, math, random, time, os, json
os.makedirs("saves", exist_ok=True)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (50, 200, 50)
GRAY  = (100, 100, 100)
BLACK = (0, 0, 0)
pygame.init()
from data import *
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
MAP_WIDTH, MAP_HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Multi-Map Game (Slum Style)")
base_path = os.path.dirname(__file__)
music_path = os.path.join(base_path, "assets", "audio", "backgroundmusic.mp3")
pygame.mixer.music.load(music_path)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
player_attack_sound = pygame.mixer.Sound(os.path.join(base_path, "assets", "audio", "attack.wav"))
BACKGROUND_COLOR = (60, 120, 60)
ROAD_COLOR = (139, 69, 19)

from generator import generate_roads, generate_houses, generate_trees, generate_pine_trees, generate_acacia_trees, generate_grass, generate_dry_grass, generate_portals
  
from mydraw import draw_player, draw_skill_button, draw_skill2_button, draw_skill3_button, draw_roads, draw_portal, draw_house, draw_blackhole, draw_rope_portal, draw_dry_grass, draw_portal_dungeon, draw_guardian, draw_knight_shield, draw_heart_defense, draw_tree, draw_acacia_tree, draw_player, draw_player2, draw_player3, draw_pine_tree, show_menu, draw_stat_popup

from skill import shoot_arrow, update_and_draw_projectiles, shoot_skill_arrow, update_and_draw_skill_arrows, use_knight_skill, use_archer_skill, use_knight_skill2, is_shield_active, use_archer_skill2, use_knight_skill3, update_skill3, draw_skill3_effect, use_wizard_skill1, use_wizard_skill2, use_wizard_skill3, update_and_draw_magic_bolts, wizard_skill2_explosions, update_and_draw_lightning_ring
    
def spawn_monster_generic(mw, mh, params, lake_polygon=None):
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

    while True:
        x = random.randint(100, mw - 100)
        y = random.randint(100, mh - 100)

        if lake_polygon and point_in_polygon(x, y, lake_polygon):
            continue
        return {
            "x": x,
            "y": y,
            "radius": params["radius"],
            "speed": params["speed"],
            "vision": params["vision"],
            "attack_range": params["attack_range"],
            "attack_damage": params["attack_damage"],
            "attack_cooldown": 0,
            "attack_max_cooldown": params["attack_max_cooldown"],
            "health": params["health"],
            "max_health": params["health"],
            "exp": params["exp"],
            "type": params["type"],
            "level": params["level"],
            "name": params["name"],
        }

def spawn_monsters(mw, mh, count, seed, monster_type):
    random.seed(seed)
    base_stats = {
        "monsters1": {
            "radius": 15, "speed": 6, "vision": 300, "attack_range": 75,
            "attack_damage": 10, "attack_max_cooldown": 40, "health": 70,
            "exp": 10, "level": 1, "name": "Tím"
        },
        "monsters2": {
            "radius": 18, "speed": 6, "vision": 350, "attack_range": 75,
            "attack_damage": 12, "attack_max_cooldown": 40, "health": 110,
            "exp": 12, "level": 2, "name": "Cam"
        },
        "monsters3": {
            "radius": 20, "speed": 6, "vision": 400, "attack_range": 80,
            "attack_damage": 12, "attack_max_cooldown": 35, "health": 125,
            "exp": 15, "level": 3, "name": "Đỏ"
        },
        "monsters4": {
            "radius": 22, "speed": 6, "vision": 300, "attack_range": 80,
            "attack_damage": 3, "attack_max_cooldown": 10, "health": 200,
            "exp": 18, "level": 4, "name": "Vàng"
        },
        "monsters5": {
            "radius": 12, "speed": 6, "vision": 300, "attack_range": 80,
            "attack_damage": 5, "attack_max_cooldown": 20, "health": 20,
            "exp": 3, "level": 5, "name": "Xám"
        },
        "monsters6": {
            "radius": 50, "speed": 8, "vision": 800, "attack_range": 150,
            "attack_damage": 10, "attack_max_cooldown": 30, "health": 500,
            "exp": 200, "level": 10, "name": "Trùm: Lam Phát Sáng"
        },
        "monsters7": {
            "radius": 18, "speed": 5, "vision": 5000, "attack_range": 60,
            "attack_damage": 10, "attack_max_cooldown": 20, "health": 80,
            "exp": 0, "level": 4, "name": "Xanh Lá"
        },
        "monsters8": {
            "radius": 20, "speed": 5, "vision": 5000, "attack_range": 80,
            "attack_damage": 12, "attack_max_cooldown": 20, "health": 90,
            "exp": 0, "level": 4, "name": "Hồng"
        },
        "monsters9": {
            "radius": 22, "speed": 6, "vision": 5000, "attack_range": 100,
            "attack_damage": 15, "attack_max_cooldown": 20, "health": 100,
            "exp": 0, "level": 4, "name": "Cam Đậm"
        },
        "monsters10": {
            "radius": 22, "speed": 2, "vision": 5000, "attack_range": 100,
            "attack_damage": 10, "attack_max_cooldown": 50, "health": 100,
            "exp": 0, "level": 5, "name": "Tím Đậm"
        },
    }[monster_type]
    base_stats["type"] = monster_type
    return [spawn_monster_generic(mw, mh, base_stats) for _ in range(count)]
  
def check_level_monster(player_lv, monster_lv, base_exp):
    try:
        if int(player_lv) > int(monster_lv):
            return int(base_exp * 0.2)
        return base_exp
    except:
        return base_exp
     
MAP_SCALE = 2
MAP_WIDTH = SCREEN_WIDTH * MAP_SCALE
MAP_HEIGHT = SCREEN_HEIGHT * MAP_SCALE
import builtins
builtins.MAP_WIDTH = MAP_WIDTH
builtins.MAP_HEIGHT = MAP_HEIGHT
   
# --- Maps ---
houses1 = generate_houses(MAP_WIDTH, MAP_HEIGHT)

def generate_blackhole(mw, mh):
    width = 100
    height = 100
    x = random.randint(10, mw - width - 10)
    y = random.randint(10, mh - height - 10)
    return {"x": x, "y": y, "width": width, "height": height, "target": 6}

# Khởi tạo trước dữ liệu dùng chung
temp_roads = generate_roads([], MAP_WIDTH, MAP_HEIGHT)
houses1 = generate_houses(MAP_WIDTH, MAP_HEIGHT, temp_roads)
roads1 = generate_roads(houses1, MAP_WIDTH, MAP_HEIGHT, map_id=7)

NPC_COUNT = 5
npc_map_data = {}

import random

class NPC:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dir = random.choice([-1, 1])
        self.speed = random.uniform(2.2, 3.8)
        self.left_bound = x - random.randint(40, 80)
        self.right_bound = x + random.randint(40, 80)
        self.pause_counter = 0

        self.dialog_list = [
            "Chào bạn!", "Trời đẹp thật.", "Đừng đi quá xa!",
            "Cẩn thận quái vật!", "Tôi đói rồi...", "Bạn thấy gì chưa?",
            "Hôm nay thế nào?", "Có nghe tin gì mới?", "Giữ an toàn nhé!",
            "Đi cùng tôi đi!", "Nghỉ ngơi một chút thôi.", "Bạn khỏe chứ?",
            "Cố lên nào!", "Tôi đang chờ bạn.", "Đừng vội vàng!",
            "Điều này quan trọng đấy.", "Đừng quên nhiệm vụ!", "Bạn làm tốt lắm!",
            "Hãy cẩn thận trên đường.", "Chúc bạn may mắn!"
        ]
        self.current_dialog = None
        self.dialog_timer = 0

    def update(self):
        if self.pause_counter > 0:
            self.pause_counter -= 1
        else:
            self.x += self.dir * self.speed
            if self.x < self.left_bound:
                self.x = self.left_bound
                self.dir = 1
                self.pause_counter = random.randint(30, 80)
            elif self.x > self.right_bound:
                self.x = self.right_bound
                self.dir = -1
                self.pause_counter = random.randint(30, 80)
            elif random.random() < 0.002:
                self.pause_counter = random.randint(20, 60)

        if self.dialog_timer > 0:
            self.dialog_timer -= 1
        else:
            self.current_dialog = None
            if random.random() < 0.001:
                self.current_dialog = random.choice(self.dialog_list)
                self.dialog_timer = random.randint(180, 240)

    def draw(self, camera_x, camera_y):
        draw_player(self.x, self.y, player_radius, camera_x, camera_y)
        if self.current_dialog:
            draw_npc_dialog(self, camera_x, camera_y)

npc_font = pygame.font.SysFont("arial", 22)

def draw_npc_dialog(npc, camera_x, camera_y):
    text = npc.current_dialog
    txt_surface = npc_font.render(text, True, (255, 255, 255))
    w, h = txt_surface.get_size()
    bx = int(npc.x - camera_x - w // 2)
    by = int(npc.y - camera_y - player_radius - 50)
    padding = 10
    bg_rect = pygame.Rect(bx - padding, by - padding, w + 2 * padding, h + 2 * padding)
    pygame.draw.rect(screen, (0, 0, 0), bg_rect, border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2, border_radius=8)
    screen.blit(txt_surface, (bx, by))

def generate_npcs_for_map(map_id, map_data):
    npc_list = []
    for i in range(NPC_COUNT):
        base_x = map_data["width"] * (i + 1) / (NPC_COUNT + 1)
        base_y = map_data["height"] // 2
        spawn_x = base_x + random.randint(-40, 40)
        spawn_y = base_y + random.randint(-80, 80)
        npc_list.append(NPC(spawn_x, spawn_y))
    npc_map_data[map_id] = npc_list

def update_npcs():
    map_id = current_map["id"]
    if map_id not in npc_map_data:
        return
    for npc in npc_map_data[map_id]:
        npc.update()

def draw_npcs(camera_x, camera_y):
    map_id = current_map["id"]
    if map_id not in npc_map_data:
        return
    for npc in npc_map_data[map_id]:
        npc.draw(camera_x, camera_y)

def draw_ship(x, y, camera_x, camera_y):
    sx = x - camera_x
    sy = y - camera_y
    hull = [
        (sx, sy + 30),
        (sx + 20, sy + 50),
        (sx + 100, sy + 50),
        (sx + 120, sy + 30),
        (sx + 60, sy + 35),
    ]
    pygame.draw.polygon(screen, (139, 69, 19), hull)
    mast_x = sx + 60
    pygame.draw.line(screen, (101, 67, 33), (mast_x, sy + 35), (mast_x, sy - 10), 3)
    sail = [
        (mast_x, sy - 10),
        (mast_x, sy + 10),
        (mast_x + 40, sy),
        (mast_x + 40, sy - 10),
    ]
    pygame.draw.polygon(screen, (255, 255, 255), sail)

HALF_HEIGHT = MAP_HEIGHT // 2

def make_transition_zones(order):
    zones = []
    y = 0
    for i in range(2):
        y += MAP_HEIGHT * order[i][1] // 100
        zones.append({
            "x": 0, "y": y - 20, "width": MAP_WIDTH, "height": 40,
            "start_color": order[i][0],
            "end_color": order[i + 1][0]
        })
    return zones

def make_background_zones(order):
    return [
        {"x": 0, "y": 0, "width": MAP_WIDTH, "height": MAP_HEIGHT * order[0][1] // 100, "color": order[0][0]},
        {"x": 0, "y": MAP_HEIGHT * order[0][1] // 100, "width": MAP_WIDTH, "height": MAP_HEIGHT * order[1][1] // 100, "color": order[1][0]},
        {"x": 0, "y": MAP_HEIGHT * (order[0][1] + order[1][1]) // 100, "width": MAP_WIDTH, "height": MAP_HEIGHT * order[2][1] // 100, "color": order[2][0]}
    ]

zones_9 = [((35, 80, 35), 50), ((210, 190, 140), 25), ((80, 150, 200), 25)]

zones_10 = [((80, 150, 200), 25), ((210, 190, 140), 25), ((255, 204, 102), 50)]

background_zones_map9 = make_background_zones(zones_9)
transition_zones_map9 = make_transition_zones(zones_9)

background_zones_map10 = make_background_zones(zones_10)
transition_zones_map10 = make_transition_zones(zones_10)

def draw_transition_zones(zones):
    for zone in zones:
        steps = zone["height"]
        for i in range(steps):
            ratio = i / steps
            r = int(zone["start_color"][0] * (1 - ratio) + zone["end_color"][0] * ratio)
            g = int(zone["start_color"][1] * (1 - ratio) + zone["end_color"][1] * ratio)
            b = int(zone["start_color"][2] * (1 - ratio) + zone["end_color"][2] * ratio)
            y = zone["y"] + i - camera_y
            pygame.draw.rect(screen, (r, g, b), (zone["x"] - camera_x, y, zone["width"], 1))

def generate_lake_polygon(map_width, map_height):
    cx, cy = map_width // 2, map_height // 2
    radius = 360
    points = []
    for i in range(12):
        angle = math.radians(i * 30)
        r_offset = radius + ((i * 41) % 60 - 30)
        x = cx + int(math.cos(angle) * r_offset)
        y = cy + int(math.sin(angle) * r_offset)
        points.append((x, y))
    return points

def draw_lake_polygon(polygon, camera_x, camera_y, screen):
    pts = [(x - camera_x, y - camera_y) for x, y in polygon]
    pygame.draw.polygon(screen, (50, 120, 200), pts)
    pygame.draw.lines(screen, (30, 80, 150), True, pts, 2)
    
def is_in_lake(mon_x, mon_y, mon_height, polygon):
    feet_y = mon_y + mon_height * 0.2
    return point_in_polygon(mon_x, feet_y, polygon)

dungeon_active = False
dungeon_start_time = 0
dungeon_duration_ms = 5 * 60 * 1000
spawn_timer = 0

def enter_dungeon():
    global dungeon_active, dungeon_start_time, spawn_timer, boss_spawned, current_map
    dungeon_active    = True
    dungeon_start_time= pygame.time.get_ticks()
    spawn_timer       = dungeon_start_time
    boss_spawned      = False
    current_map       = maps[99]
    current_map["monsters"].clear()

def exit_dungeon():
    global current_map, dungeon_active, spawn_timer
    dungeon_active = False
    current_map = maps[1]
    spawn_timer = pygame.time.get_ticks()

def show_dungeon_stage_menu():
    font = pygame.font.SysFont("Segoe UI", 48, bold=True)
    small_font = pygame.font.SysFont("Segoe UI", 26)
    desc_font = pygame.font.SysFont("Segoe UI", 22)
    clock = pygame.time.Clock()

    stage_buttons = []
    button_w, button_h = 240, 120
    spacing = 60
    start_x = SCREEN_WIDTH // 2 - (button_w * 3 + spacing * 2) // 2
    y = SCREEN_HEIGHT // 2 - button_h // 2

    for i in range(3):
        rect = pygame.Rect(start_x + i * (button_w + spacing), y, button_w, button_h)
        stage_buttons.append((i + 1, rect))

    stage_labels = ["Dễ", "Trung bình", "Khó"]

    t = 0
    running_menu = True
    while running_menu:
        t += 1
        screen.fill((10, 10, 20))

        # Vẽ sọc nền động
        for i in range(0, SCREEN_HEIGHT, 30):
            wave = int(math.sin(t * 0.03 + i * 0.1) * 10)
            pygame.draw.line(screen, (30 + wave, 30 + wave, 60), (0, i), (SCREEN_WIDTH, i), 2)

        # Tiêu đề sáng nhấp nháy
        title_glow = 180 + int(math.sin(t * 0.05) * 75)
        title = font.render("CHỌN CẤP ĐỘ DUNGEON", True, (title_glow, title_glow, 255))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5)))

        fade = 100 + int(math.sin(t * 0.05) * 50)

        for index, (stage, rect) in enumerate(stage_buttons):
            if stage == 1:
                color = (100, 180, 100)
                border_color = (fade, 255, fade)
            else:
                color = (50 + index * 20, 50 + index * 20, 50 + index * 20)
                border_color = (100, 100, 100)

            # Hiệu ứng nổi khi rê chuột
            mx, my = pygame.mouse.get_pos()
            hover = rect.collidepoint(mx, my)
            if hover:
                pygame.draw.rect(screen, (min(color[0]+30,255), min(color[1]+30,255), min(color[2]+30,255)), rect.inflate(6, 6), border_radius=24)

            pygame.draw.rect(screen, color, rect, border_radius=20)
            pygame.draw.rect(screen, border_color, rect, 3, border_radius=20)

            label = font.render(f"Cấp {stage}", True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=rect.center))

            sub_label = small_font.render(stage_labels[index], True, (200, 200, 200))
            screen.blit(sub_label, sub_label.get_rect(midtop=(rect.centerx, rect.bottom + 10)))

            if stage != 1:
                pulse = 150 + int(math.sin(t * 0.1) * 50)
                locked = desc_font.render("Chưa mở", True, (pulse, pulse, pulse))
                screen.blit(locked, locked.get_rect(midtop=(rect.centerx, rect.bottom + 40)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for stage, rect in stage_buttons:
                    if rect.collidepoint(mx, my):
                        if stage == 1:
                            enter_dungeon()
                        running_menu = False

        pygame.display.flip()
        clock.tick(60)

def create_base_map(id, background_color=(60, 120, 60), monsters=None, portals=None, extras=None):
    return {
        "id": id,
        "width": MAP_WIDTH,
        "height": MAP_HEIGHT,
        "links": {},
        "monsters": monsters or [],
        "respawn_queue": [],
        "portals": portals if portals is not None else generate_portals(id),
        "background_color": background_color,
        **(extras or {})
    }

def create_forest_map(id, monster_count, seed, monster_type, tree_count):
    return create_base_map(
        id,
        background_color=(60, 120, 60),
        monsters=spawn_monsters(MAP_WIDTH, MAP_HEIGHT, monster_count, seed, monster_type),
        extras={
            "trees": generate_trees(MAP_WIDTH, MAP_HEIGHT, tree_count, houses1, [], roads1),
            "grass": generate_grass(MAP_WIDTH, MAP_HEIGHT, 150)
        }
    )

def create_pine_map(id, monster_count, seed, monster_type, pine_count, grass_amount=300, extras=None):
    if extras is None:
        extras = {}

    return create_base_map(
        id,
        background_color=(35, 80, 35),
        monsters=spawn_monsters(MAP_WIDTH, MAP_HEIGHT, monster_count, seed, monster_type),
        extras={
            "pine_trees": generate_pine_trees(MAP_WIDTH, MAP_HEIGHT, pine_count, houses1, [], roads1),
            "grass": generate_grass(MAP_WIDTH, MAP_HEIGHT, grass_amount),
            **extras  # thêm extras tùy chọn vào map
        }
    )

# Tạo từng map
map0 = create_forest_map(0, 8, 301, "monsters2", 30)

map1 = create_base_map(1, extras={
    "houses": houses1,
    "trees": generate_trees(MAP_WIDTH, MAP_HEIGHT, 30, houses1, [], roads1),
    "roads": roads1,
    "grass": generate_grass(MAP_WIDTH, MAP_HEIGHT, 300)
})

map2 = create_forest_map(2, 15, 101, "monsters1", 8)

map3 = create_forest_map(3, 17, 202, "monsters1", 12)

map4 = create_forest_map(4, 13, 202, "monsters3", 12)

map5 = create_pine_map(5, 8, 301, "monsters4", 50, 150, extras={
    "blackholes": [generate_blackhole(MAP_WIDTH, MAP_HEIGHT)]
})

map6 = create_base_map(6, background_color=(100, 100, 100), monsters=spawn_monsters(MAP_WIDTH, MAP_HEIGHT, 35, 101, "monsters5"), portals=[
    {"x": MAP_WIDTH // 2 - 25, "y": MAP_HEIGHT // 2 - 50, "width": 50, "height": 100, "target": 5}
])


roads7 = generate_roads(houses1, MAP_WIDTH, MAP_HEIGHT, map_id=7)
map7 = create_base_map(7, background_color=(35, 80, 35), extras={
    "houses": houses1,
    "pine_trees": generate_pine_trees(MAP_WIDTH, MAP_HEIGHT, 50, houses1, [], roads1),
    "roads": roads7,
    "grass": generate_grass(MAP_WIDTH, MAP_HEIGHT, 150)
})

map8 = create_pine_map(8, 1, 401, "monsters6", 50, 150)

map9 = create_base_map(9, background_color=(60, 120, 60), extras={
    "pine_trees": generate_pine_trees(MAP_WIDTH, MAP_HEIGHT, 30, upper_half=True),
    "background_zones": background_zones_map9,
    "transition_zones": transition_zones_map9,
    "ship_portal": {
        "x": MAP_WIDTH // 2 + 100,
        "y": (MAP_HEIGHT * 3) // 4 - 60,
        "width": 80,
        "height": 120,
        "target": 10
    },
    "grass": []
})

map10 = create_base_map(10, background_color=(255, 204, 102), extras={
    "acacia": generate_acacia_trees(MAP_WIDTH, MAP_HEIGHT, 30, bottom_half=True),
    "dry_grass": generate_dry_grass(MAP_WIDTH, MAP_HEIGHT, 300, bottom_half=True),
    "background_zones": background_zones_map10,
    "transition_zones": transition_zones_map10,
    "ship_portal": {
        "x": MAP_WIDTH // 2 + 100,
        "y": MAP_HEIGHT // 4 - 35,
        "width": 80,
        "height": 120,
        "target": 9
    },
    "grass": []
})

map11 = create_base_map(11, background_color=(255, 204, 102), monsters=spawn_monsters(MAP_WIDTH, MAP_HEIGHT, 8, 301, "monsters2"), extras={
    "acacia": generate_acacia_trees(MAP_WIDTH, MAP_HEIGHT, 30),
    "dry_grass": generate_dry_grass(MAP_WIDTH, MAP_HEIGHT, 300),
    "grass": []
})

lake_polygon_map12 = generate_lake_polygon(MAP_WIDTH, MAP_HEIGHT)
globals()["lake_polygon"] = lake_polygon_map12

map12 = create_base_map(12, background_color=(255, 204, 102), monsters=spawn_monsters(MAP_WIDTH, MAP_HEIGHT, 15, 301, "monsters2"), extras={
    "lake_polygon": lake_polygon_map12,
    "acacia": generate_acacia_trees(MAP_WIDTH, MAP_HEIGHT, 30, lake_polygon=lake_polygon_map12),
    "dry_grass": generate_dry_grass(MAP_WIDTH, MAP_HEIGHT, 300),
    "grass": []
})

map13 = create_base_map(13, extras={
    "trees": generate_trees(MAP_WIDTH, MAP_HEIGHT, 30, houses1, [], roads1),
    "grass": generate_grass(MAP_WIDTH, MAP_HEIGHT, 250)
})

map99 = create_base_map(99, background_color=(40, 40, 40), portals=[])

map100 = create_base_map(100, background_color=(60, 120, 60), portals=[])

# Tổng hợp vào maps
maps = {i: eval(f"map{i}") for i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 99, 13, 100]}

# Khởi tạo
current_map = map1
generate_npcs_for_map(1, map1)
generate_npcs_for_map(7, map7)

screen_shake_timer = 0
shake_offset_x = 0
shake_offset_y = 0

show_stat_popup = False
stat_title_font = pygame.font.SysFont("Segoe UI", 48, bold=True)
stat_label_font = pygame.font.SysFont("Segoe UI", 30)
stat_value_font = pygame.font.SysFont("Segoe UI", 36)

close_stat_btn = pygame.Rect(0, 0, 0, 0)
hp_plus_btn = pygame.Rect(0, 0, 0, 0)
dmg_plus_btn = pygame.Rect(0, 0, 0, 0)
WHITE  = (255, 255, 255)
PURPLE = (138,  43, 226)
YELLOW = (255, 255,   0) 
ORANGE = (255, 140,   0)
player_x, player_y = current_map["width"] // 2, current_map["height"] // 2
joystick_radius = int(SCREEN_WIDTH * 1.2 / 13)
joystick_x = int(joystick_radius * 1.2)
joystick_y = int(SCREEN_HEIGHT - joystick_radius * 1.2)
joystick_inner_radius = joystick_radius / 2.5
joystick_active = False
attack_button_center = (int(SCREEN_WIDTH * 0.85), int(SCREEN_HEIGHT * 0.78))
attack_button_radius = int(SCREEN_HEIGHT * 0.157)
skill_button_radius = int(SCREEN_HEIGHT * 0.093)

# Skill 1
skill_cooldown = 0
skill_max_cooldown = 120
skill_button_center = (
    int(SCREEN_WIDTH * 0.72),
    int(SCREEN_HEIGHT * 0.85)
)

# Skill 2
skill2_cooldown = 0
skill2_max_cooldown = 240
skill2_button_radius = skill_button_radius
skill2_button_center = (
    int(SCREEN_WIDTH * 0.735),
    int(SCREEN_HEIGHT * 0.635)
)

# Skill 3
skill3_cooldown = 0
skill3_max_cooldown = 240
skill3_button_radius = skill_button_radius
skill3_button_center = (
    int(SCREEN_WIDTH * 0.82),
    int(SCREEN_HEIGHT * 0.51)
)
monster_death_effects = []

def update_and_draw_monster_death_effects(camera_x, camera_y, screen):
    now = pygame.time.get_ticks()
    remaining = []
    for eff in monster_death_effects:
        elapsed = now - eff["start"]
        if elapsed > eff["duration"]:
            continue

        t = elapsed / eff["duration"]
        fade = max(0, 1 - t)
        alpha = int(fade * 255)
        radius = eff["radius"] + t * 30
        px = int(eff["x"] - camera_x)
        py = int(eff["y"] - camera_y)

        # --- Glow burst nhiều lớp ---
        for i in range(3):
            inner_r = radius * (0.6 + i * 0.2)
            glow_surface = pygame.Surface((inner_r*2, inner_r*2), pygame.SRCALPHA)
            color = (255, int(100 + 100 * t), 50)
            glow_alpha = int(fade * 100 * (1 - i * 0.3))
            pygame.draw.circle(glow_surface, (*color, glow_alpha), (int(inner_r), int(inner_r)), int(inner_r))
            screen.blit(glow_surface, (px - inner_r, py - inner_r))

        # --- Core chớp nháy ---
        pulse_r = int(radius * 0.4 + math.sin(t * 20) * 3)
        pygame.draw.circle(screen, (255, 200, 100, alpha), (px, py), pulse_r)

        # --- Particles bay ---
        if "particles" not in eff:
            eff["particles"] = [{
                "angle": random.uniform(0, 2 * math.pi),
                "speed": random.uniform(1, 3),
                "size": random.randint(2, 5),
                "offset": random.uniform(0, 5)
            } for _ in range(20)]

        for p in eff["particles"]:
            dist = p["speed"] * elapsed * 0.05 + p["offset"]
            x = px + math.cos(p["angle"]) * dist
            y = py + math.sin(p["angle"]) * dist
            size = p["size"]
            particle_color = (255, 180, 100, alpha)
            surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, particle_color, (size, size), size)
            screen.blit(surf, (x - size, y - size))

        remaining.append(eff)

    monster_death_effects[:] = remaining
    
def handle_monster_death(mon):
    global player_exp, player_potion

    if random.random() < 0.1:
        item_type = random.choice(list(ITEM_DEFS.keys()))
        inventory[item_type] += 1

    exp_gain = check_level_monster(player_level, mon.get("level", 1), mon["exp"])
    player_exp += exp_gain

    if random.randint(1, 100) <= 20:
        player_potion += 1

    check_level_up()
    if exp_gain > 0:
        reduced = exp_gain < mon["exp"]
        exp_popups.append(ExpPopup(f'+{exp_gain} EXP', reduced=reduced))

    # Hồi sinh (nếu không phải map 100)
    if current_map["id"] != 100:
        current_map["respawn_queue"].append({
            "respawn_time": pygame.time.get_ticks() + random.randint(10000, 15000),
            "type": mon["type"]
        })

    # Hiệu ứng chết
    monster_death_effects.append({
        "x": mon["x"],
        "y": mon["y"],
        "start": pygame.time.get_ticks(),
        "duration": 650,
        "radius": 20
    })

attack_effects = []

def add_attack_effect(x, y, start_r, max_r, color, life):
    attack_effects.append({"x": x, "y": y, "radius": start_r, "max_radius": max_r, "color": color, "life": life})
    
def update_attack_effects():
    for eff in attack_effects[:]:
        eff["radius"] += (eff["max_radius"] - eff["radius"]) * 0.2
        eff["life"] -= 1
        if eff["life"] <= 0:
            attack_effects.remove(eff)
            
def create_glow_surface(radius, color):
    glow_radius = radius + 6
    surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
    center = glow_radius
    draw = pygame.draw.circle
    rgba = (*color,)

    draw(surf, rgba + (64,), (center, center), radius + 6)
    draw(surf, rgba + (128,), (center, center), radius + 3)
    return surf

def draw_attack_effects(cx, cy):
    for eff in attack_effects:
        life_ratio = eff["life"] / 20
        if life_ratio <= 0:
            continue
        alpha = int(255 * life_ratio)
        if alpha < 10:
            continue

        px = int(eff["x"] - cx)
        py = int(eff["y"] - cy)

        if "glow_surface" not in eff:
            eff["glow_surface"] = create_glow_surface(eff["radius"], eff["color"])

        glow_surf = eff["glow_surface"].copy()
        glow_surf.set_alpha(alpha)
        center = glow_surf.get_width() // 2
        screen.blit(glow_surf, (px - center, py - center))
        
def is_colliding(x1, y1, r1, x2, y2, r2):
    return math.hypot(x2 - x1, y2 - y1) < (r1 + r2)
def circle_rect_collision(cx, cy, r, rx, ry, rw, rh):
    closest_x = max(rx, min(cx, rx + rw))
    closest_y = max(ry, min(cy, ry + rh))
    return math.hypot(cx - closest_x, cy - closest_y) < r
    
def update_respawn():
    ct = pygame.time.get_ticks()
    for m in maps.values():
        if m["id"] == 100:
            continue
        for ent in m["respawn_queue"][:]:
            if ct >= ent["respawn_time"]:
                monster = spawn_monsters(m["width"], m["height"], 1, random.randint(0, 999999), ent["type"])[0]
                m["monsters"].append(monster)
                m["respawn_queue"].remove(ent)
    
level_up_effects = []

def add_level_up_effect(x, y):
    level_up_effects.append({
        "x": x,
        "y": y,
        "start": pygame.time.get_ticks(),
        "duration": 1200,  # 1.2 giây
        "particles": [
            {
                "angle": random.uniform(0, 2 * math.pi),
                "speed": random.uniform(1.5, 3.5),
                "radius": 0,
                "size": random.randint(2, 5)
            } for _ in range(30)
        ]
    })
    
def check_level_up():
    global player_level, player_exp, exp_to_next, player_health, player_max_health
    global unspent_points
    while player_exp >= exp_to_next:
        player_exp -= exp_to_next
        player_level += 1
        player_health = player_max_health
        exp_to_next += 20
        unspent_points += 3   # cấp 3 điểm
        add_level_up_effect(player_x, player_y)
        
def update_and_draw_level_up_effects(camera_x, camera_y):
    now = pygame.time.get_ticks()
    remaining = []
    for eff in level_up_effects:
        elapsed = now - eff["start"]
        if elapsed > eff["duration"]:
            continue
        t = elapsed / eff["duration"]
        alpha = max(0, 255 * (1 - t))

        px = eff["x"] - camera_x
        py = eff["y"] - camera_y

        # --- Vẽ vòng tròn xoay ---
        for i in range(3):
            angle_offset = t * (3 + i) * math.pi
            radius = 30 + i * 10 + math.sin(t * 6 + i) * 5
            for j in range(6):
                angle = angle_offset + j * math.pi / 3
                x = px + math.cos(angle) * radius
                y = py + math.sin(angle) * radius
                pygame.draw.circle(screen, (255, 255 - i*50, 100 + i*50), (int(x), int(y)), 4)

        # --- Vẽ ánh sáng trung tâm ---
        glow_radius = int(15 + 10 * math.sin(t * 10))
        glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 255, 120, int(alpha)), (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (px - glow_radius, py - glow_radius))

        # --- Particles bay ---
        for p in eff["particles"]:
            angle = p["angle"]
            dist = p["speed"] * elapsed * 0.05
            x = px + math.cos(angle) * dist
            y = py + math.sin(angle) * dist
            pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), p["size"])

        remaining.append(eff)

    level_up_effects[:] = remaining
        
def transition_effect():
    fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade.fill((0, 0, 0))
    for alpha in range(0, 300, 10):
        fade.set_alpha(alpha)
        screen.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(30)
clock = pygame.time.Clock()

def fade_into_game():
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill((0, 0, 0))
    for alpha in range(255, -1, -10):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(30)

npc_interacted = False
show_npc_popup = False
dialog_font = pygame.font.SysFont("arial", 24)
npc_yes_btn = pygame.Rect(0, 0, 0, 0)
npc_no_btn = pygame.Rect(0, 0, 0, 0)
heart_hp = 500
heart_max_hp = 500
heart_pos = (MAP_WIDTH // 2, MAP_HEIGHT // 2)
defense_start_time = 0
defense_duration = 300000
defense_spawn_timer = 0
defense_active = False

npcs = [
    {
        "id": "guardian",  # duy nhất để xác định
        "name": "Hộ Vệ Già",
        "map_id": 4,
        "x": MAP_WIDTH // 2,
        "y": MAP_HEIGHT // 2,
        "dialog": [
            "Xin chào người thám hiểm trẻ.",
            "Hãy giúp tôi bảo vệ thứ này, tôi sẽ",
            "trả công cho bạn, theo tôi nếu muốn."
        ],
        "once": True
    },
    
    {
        "id": "old_man",
        "name": "Ông Già",
        "map_id": 1,
        "x": 600,
        "y": MAP_HEIGHT // 2+50,
        "dialog": [
            "Xin chào người mới.",
            "Đây là làng Hope nếu ngươi chưa biết."
        ],
        "once": False  # nói lại nhiều lần
    }
]

def draw_npc_popup():
    global show_npc_popup, npc_interacted
    global npc_yes_btn, npc_no_btn, npc_exit_btn

    if not show_npc_popup:
        return

    npc = show_npc_popup

    popup_w, popup_h = 510, 310
    popup = pygame.Rect((SCREEN_WIDTH - popup_w) // 2, (SCREEN_HEIGHT - popup_h) // 2, popup_w, popup_h)

    pygame.draw.rect(screen, (30, 30, 50), popup, border_radius=16)
    pygame.draw.rect(screen, (220, 220, 255), popup, 3, border_radius=16)

    lines = [npc.get("name", "NPC")] + npc.get("dialog", [])
    for i, line in enumerate(lines):
        color = (255, 215, 100) if i == 0 else WHITE
        txt = dialog_font.render(line, True, color)
        screen.blit(txt, (popup.x + 30, popup.y + 30 + i * 38))

    btn_w, btn_h = 120, 50
    spacing = 40
    btn_y = popup.bottom - btn_h - 30

    if npc.get("id") == "guardian":
        npc_yes_btn = pygame.Rect(popup.left + spacing, btn_y, btn_w, btn_h)
        npc_no_btn = pygame.Rect(popup.right - spacing - btn_w, btn_y, btn_w, btn_h)

        pygame.draw.rect(screen, (80, 180, 120), npc_yes_btn, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), npc_yes_btn, 2, border_radius=10)
        screen.blit(dialog_font.render("Có", True, WHITE), npc_yes_btn.move(35, 12))

        pygame.draw.rect(screen, (180, 80, 80), npc_no_btn, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), npc_no_btn, 2, border_radius=10)
        screen.blit(dialog_font.render("Không", True, WHITE), npc_no_btn.move(20, 12))
    else:
        npc_exit_btn = pygame.Rect(popup.centerx - btn_w // 2, btn_y, btn_w, btn_h)
        pygame.draw.rect(screen, (150, 150, 100), npc_exit_btn, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), npc_exit_btn, 2, border_radius=10)
        screen.blit(dialog_font.render("Thoát", True, WHITE), npc_exit_btn.move(30, 12))

    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        if npc.get("id") == "guardian":
            if npc_yes_btn.collidepoint((mx, my)):
                npc_interacted = True
                show_npc_popup = False
            elif npc_no_btn.collidepoint((mx, my)):
                show_npc_popup = False
        else:
            if npc_exit_btn.collidepoint((mx, my)):
                show_npc_popup = False
    
ITEM_DEFS = {
    "sword": {"name": "Kiếm", "bonus": {"damage": 5}},
    "helmet": {"name": "Mũ", "bonus": {"max_health": 5}},
    "armor": {"name": "Áo", "bonus": {"max_health": 5}},
    "pants": {"name": "Quần", "bonus": {"max_health": 5}},
}

def save_character(slot, data):
    import os
    if not os.path.exists("saves"):
        os.makedirs("saves")
    with open(f"saves/slot{slot}.json", "w") as f:
        json.dump(data, f)

def load_character(slot):
    try:
        with open(f"saves/slot{slot}.json", "r") as f:
            return json.load(f)
    except:
        return None
        
def save_current_character():
    if selected_slot:
        map_id = next((i for i, m in maps.items() if m == current_map), 1)
        data = {
            "name": f"Nhân vật {selected_slot}",
            "class": "Knight" if Knight else "Archer" if Archer else "Wizard",
            "level": player_level,
            "exp": player_exp,
            "exp_to_next": exp_to_next,
            "base_stats": {
                "max_hp": player_max_health,
                "damage": player_attack_damage
            },
            "unspent_points": unspent_points,
            "position": [player_x, player_y],
            "map_id": map_id,
            "inventory": inventory,
            "equipped": equipped,
        }
        save_character(selected_slot, data)
        
selecting = True
fade_out = False
fade_alpha = 0

player_attack_range = 0

def show_class_selection():
    global fade_out, selecting, fade_alpha
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 64, bold=True)
    title_font = pygame.font.SysFont("arial", 72, bold=True)

    # Nền gradient
    gradient_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for y in range(SCREEN_HEIGHT):
        c = 40 + int(60 * (y / SCREEN_HEIGHT))
        pygame.draw.line(gradient_bg, (0, c, min(255, c + 60)), (0, y), (SCREEN_WIDTH, y))

    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill((0, 0, 0))

    fade_alpha = 0
    fade_out = False
    selecting = True
    selected_class = None

    while selecting or fade_out:
        screen.blit(gradient_bg, (0, 0))

        title = title_font.render("CHỌN CLASS", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))

        knight_text = font.render("Knight", True, (255, 255, 255))
        wizard_text = font.render("Wizard", True, (255, 255, 255))
        archer_text = font.render("Archer", True, (255, 255, 255))

        knight_rect = knight_text.get_rect(center=(SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2))
        wizard_rect = wizard_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        archer_rect = archer_text.get_rect(center=(5 * SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2))

        knight_box = knight_rect.inflate(40, 30)
        wizard_box = wizard_rect.inflate(40, 30)
        archer_box = archer_rect.inflate(40, 30)

        shadow_offset = 6
        for box in [knight_box, wizard_box, archer_box]:
            pygame.draw.rect(screen, (0, 0, 0, 100), box.move(shadow_offset, shadow_offset), border_radius=15)

        pygame.draw.rect(screen, (0, 90, 200), knight_box, border_radius=15)
        pygame.draw.rect(screen, (100, 50, 180), wizard_box, border_radius=15)
        pygame.draw.rect(screen, (0, 160, 120), archer_box, border_radius=15)

        for box in [knight_box, wizard_box, archer_box]:
            pygame.draw.rect(screen, (255, 255, 255), box, 4, border_radius=15)

        screen.blit(knight_text, knight_rect)
        screen.blit(wizard_text, wizard_rect)
        screen.blit(archer_text, archer_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and selecting:
                mx, my = pygame.mouse.get_pos()
                if knight_box.collidepoint(mx, my):
                    selected_class = "Knight"
                    fade_out = True
                    selecting = False
                elif wizard_box.collidepoint(mx, my):
                    selected_class = "Wizard"
                    fade_out = True
                    selecting = False
                elif archer_box.collidepoint(mx, my):
                    selected_class = "Archer"
                    fade_out = True
                    selecting = False

        if fade_out:
            fade_alpha += 10
            if fade_alpha >= 255:
                fade_alpha = 255
                fade_out = False
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))

        pygame.display.flip()
        clock.tick(60)

    return selected_class
    
def character_menu():
    global player_x, player_y, player_level, player_exp, exp_to_next
    global player_attack_damage, player_health, player_max_health, player_attack_range
    global Knight, Archer, Wizard, equipped, inventory, current_map, selected_slot
    global unspent_points

    font = pygame.font.SysFont("Segoe UI", 32)
    title_font = pygame.font.SysFont("Segoe UI", 60, bold=True)
    subtitle_font = pygame.font.SysFont("Segoe UI", 24, italic=True)
    clock = pygame.time.Clock()

    def draw_character_thumbnail(surface, x, y, radius, data):
        pygame.draw.circle(surface, (200, 200, 200), (x, y), radius)
        pygame.draw.circle(surface, (255, 255, 255), (x, y), radius, 4)
        if data:
            if data["class"] == "Knight":
                draw_player(x, y, radius, 0, 0)
            elif data["class"] == "Archer":
                draw_player2(x, y, radius, 0, 0)
            elif data["class"] == "Wizard":
                draw_player3(x, y, radius, 0, 0)

    def confirm_delete():
        btn_font = pygame.font.SysFont("Segoe UI", 36)
        yes_btn = pygame.Rect(SCREEN_WIDTH//2 - 160, SCREEN_HEIGHT//2 + 60, 120, 60)
        no_btn  = pygame.Rect(SCREEN_WIDTH//2 + 40, SCREEN_HEIGHT//2 + 60, 120, 60)
        while True:
            screen.fill((30, 0, 0))
            msg1 = btn_font.render("XÁC NHẬN XÓA NHÂN VẬT?", True, (255,255,255))
            screen.blit(msg1, msg1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40)))
            pygame.draw.rect(screen, (200,0,0), yes_btn, border_radius=10)
            pygame.draw.rect(screen, (100,100,100), no_btn, border_radius=10)
            screen.blit(btn_font.render("XÓA", True, WHITE), (yes_btn.x + 25, yes_btn.y + 15))
            screen.blit(btn_font.render("HỦY", True, WHITE), (no_btn.x + 25, no_btn.y + 15))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_btn.collidepoint(event.pos): return True
                    if no_btn.collidepoint(event.pos):  return False
            pygame.display.flip()
            clock.tick(60)

    slots = [load_character(i) for i in range(1,4)]

    while True:
        screen.fill((20,20,40))
        for i in range(50):
            px = (pygame.time.get_ticks()//(10+i%5) + i*23) % SCREEN_WIDTH
            py = (i*37 + pygame.time.get_ticks()//(20+i%7)) % SCREEN_HEIGHT
            pygame.draw.circle(screen, (100+i%155,100+i%155,255), (px,py), 1)

        pygame.draw.rect(screen, (255,255,255), (80,40, SCREEN_WIDTH-160, SCREEN_HEIGHT-80), 4, border_radius=20)
        title = title_font.render("CHỌN NHÂN VẬT", True, WHITE)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2,80)))
        subtitle = subtitle_font.render("Chạm vào một ô để chọn hoặc tạo nhân vật", True, (180,180,220))
        screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH//2,130)))

        delete_buttons = []
        for i in range(3):
            top = 160 + i*160
            rect = pygame.Rect(SCREEN_WIDTH//2 - 300, top, 600, 120)
            pygame.draw.rect(screen, (50,50,80), rect, border_radius=15)
            pygame.draw.rect(screen, (255,255,255), rect, 3, border_radius=15)

            data = slots[i]
            circle_center = (rect.x + 70, rect.centery)
            draw_character_thumbnail(screen, *circle_center, 40, data)

            if data:
                text = f"{data['name']} - {data['class']} - Lv {data['level']}"
            else:
                text = "Tạo nhân vật mới"
            screen.blit(font.render(text, True, WHITE), (rect.x+130, rect.y+40))
            
            if data:
            	del_btn = pygame.Rect(rect.right + 20, rect.centery - 20, 60, 40)
            	pygame.draw.rect(screen, (180, 0, 0), del_btn, border_radius=8)
            	del_text = font.render("XÓA", True, WHITE)
            	screen.blit(del_text, del_text.get_rect(center=del_btn.center))
            	delete_buttons.append((i, del_btn))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = event.pos
                for i,btn in delete_buttons:
                    if btn.collidepoint((mx,my)):
                        if confirm_delete():
                            try:
                                os.remove(f"saves/slot{i+1}.json")
                                slots[i] = None
                            except: pass
                        break
                else:
                    for i in range(3):
                        rect = pygame.Rect(SCREEN_WIDTH//2-300, 160 + i*160,600,120)
                        if rect.collidepoint((mx,my)):
                            selected_slot = i+1
                            data = slots[i]
                            if data:
                                Knight = 1 if data["class"]=="Knight" else 0
                                Archer = 1 if data["class"]=="Archer" else 0
                                Wizard = 1 if data["class"]=="Wizard" else 0
                                if Knight:
                                	player_attack_range = 50
                                elif Archer:
                                	player_attack_range = 180
                                elif Wizard:
                                	player_attack_range = 150
                                player_level  = data["level"]
                                player_exp    = data["exp"]
                                exp_to_next   = data.get("exp_to_next", 100 + (player_level-1)*10)
                                player_max_health    = data["base_stats"]["max_hp"]
                                player_health        = player_max_health
                                player_attack_damage = data["base_stats"]["damage"]
                                unspent_points       = data.get("unspent_points",0)
                                player_x, player_y   = data["position"]
                                map_id               = data.get("map_id", 1)
                                current_map          = maps[map_id]
                                inventory            = data["inventory"]
                                equipped             = data["equipped"]
                                return
                            else:
                                selected_class = show_class_selection()
                                if not selected_class: continue
                                Knight = 1 if selected_class=="Knight" else 0
                                Archer = 1 if selected_class=="Archer" else 0
                                Wizard = 1 if selected_class=="Wizard" else 0
                                player_level  = 1
                                player_exp    = 0
                                exp_to_next   = 100
                                unspent_points = 0
                                player_attack_range = 50 if Knight else 180 if Archer else 150
                                player_attack_damage = 20 if Knight else 10
                                player_max_health = 100
                                player_health     = player_max_health
                                inventory = {k:0 for k in ITEM_DEFS}
                                equipped  = {k:False for k in ITEM_DEFS}
                                player_x = maps[1]["width"]//2
                                player_y = maps[1]["height"]//2
                                current_map = maps[1]
                                save_current_character()
                                return

        pygame.display.flip()
        clock.tick(60)

show_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, clock, WHITE, fade_into_game, character_menu)
last_combat_time = pygame.time.get_ticks()
running = True

last_ms_update_time = 0
displayed_ms = 0
joystick_offset_x = 0
joystick_offset_y = 0

class DamageText:
    def __init__(self, x, y, text, color=(255, 0, 0), duration=30):
        self.x = x
        self.y = y
        self.text = str(text)
        self.color = color
        self.duration = duration
        self.counter = 0

    def update(self):
        self.y -= 1
        self.counter += 1

    def draw(self, surface, font, camera_x, camera_y):
    	img = font.render(self.text, True, self.color)
    	surface.blit(img, (int(self.x - camera_x), int(self.y - camera_y)))

    def is_expired(self):
        return self.counter > self.duration
        
damage_texts = []

def restart_game():
    global current_map, player_attack_range, player_health, player_max_health
    global player_attack_cooldown, player_level, player_exp, exp_to_next
    global player_x, player_y

    transition_effect()
    current_map = map1

    if Knight:
        player_attack_range = 50
    elif Archer:
        player_attack_range = 180
    elif Wizard:
        player_attack_range = 150

    player_health = player_max_health = 100
    player_attack_cooldown = 0
    player_level, player_exp, exp_to_next = 1, 0, 100
    player_x = current_map["width"] // 2
    player_y = current_map["height"] // 2
    
player_potion = 0
player_heal = 30
potion_button = pygame.Rect(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100, 60, 60)
healing_effects = []
def update_and_draw_healing_effects(camera_x, camera_y, screen):
    now = pygame.time.get_ticks()
    remaining = []
    for eff in healing_effects:
        elapsed = now - eff["start"]
        if elapsed > eff["duration"]:
            continue

        t = elapsed / eff["duration"]
        alpha = max(0, int(255 * (1 - t)))
        rise = int(t * 30)
        float_offset = math.sin(t * 8) * 5  # dao động ngang nhẹ

        # Vị trí vẽ
        x = eff["x"] - camera_x + float_offset
        y = eff["y"] - camera_y - rise

        # --- Glow xung quanh text ---
        text = font.render(f"+{eff['value']}", True, (0, 255, 0))
        text.set_alpha(alpha)
        glow_surf = pygame.Surface((text.get_width()+20, text.get_height()+20), pygame.SRCALPHA)
        glow_rect = glow_surf.get_rect(center=(text.get_width()//2 + 10, text.get_height()//2 + 10))

        pygame.draw.circle(glow_surf, (0, 255, 0, int(alpha * 0.3)), glow_rect.center, text.get_width() // 2 + 5)
        screen.blit(glow_surf, (x - 10, y - 10))

        # --- Text chính ---
        screen.blit(text, (x, y))
        remaining.append(eff)

    healing_effects[:] = remaining
    
def healing():
    global player_potion, player_health, player_max_health
    if player_potion > 0 and player_health < player_max_health:
        old_health = player_health
        player_health += player_heal
        if player_health > player_max_health:
            player_health = player_max_health
        player_potion -= 1

        # Thêm hiệu ứng phục hồi
        healing_effects.append({
            "x": player_x,
            "y": player_y - 50,
            "value": player_health - old_health,
            "start": pygame.time.get_ticks(),
            "duration": 700
        })

fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
fade_surface.fill((0, 0, 0))
   
attack_sound_played = False
monster_attack_sound_played = False

def attack():
    global attack_sound_played

    pygame.draw.circle(screen, (255, 90, 90), attack_button_center, attack_button_radius)
    MAX_ATTACK_COOLDOWN = 20
    border_width = 8  # hoặc số bạn muốn

    pygame.draw.circle(screen, (0, 0, 0), attack_button_center, attack_button_radius + border_width)  # viền ngoài đen
    pygame.draw.circle(screen, (255, 90, 90), attack_button_center, attack_button_radius)

    if player_attack_cooldown > 0:
        if not attack_sound_played:
            player_attack_sound.play()
            attack_sound_played = True

        ratio = 1 - player_attack_cooldown / MAX_ATTACK_COOLDOWN
        start_angle = -math.pi / 2
        end_angle = start_angle + 2 * math.pi * ratio
        rect = pygame.Rect(0, 0, (attack_button_radius + border_width) * 2, (attack_button_radius + border_width) * 2)
        rect.center = attack_button_center
        pygame.draw.arc(screen, WHITE, rect, start_angle, end_angle, border_width)
    else:
        attack_sound_played = False
        pygame.draw.circle(screen, WHITE, attack_button_center, attack_button_radius + border_width, border_width)
        pygame.draw.circle(screen, WHITE, attack_button_center, attack_button_radius, 5)

    pygame.draw.circle(screen, (0, 0, 0, 100), attack_button_center, attack_button_radius - 15)
    
last_autosave_time = time.time()
AUTOSAVE_INTERVAL = 30
class ExpPopup:
    def __init__(self, text, duration=1.5, reduced=False):
        self.text = text
        self.start_time = time.time()
        self.duration = duration
        self.alpha = 255
        self.reduced = reduced  # True nếu là EXP bị giảm

    def is_expired(self):
        return time.time() - self.start_time > self.duration

    def get_surface(self, font):
        elapsed = time.time() - self.start_time
        fade_ratio = max(0, 1 - elapsed / self.duration)
        self.alpha = int(255 * fade_ratio)
        color = (255, 0, 0) if self.reduced else (255, 255, 0)  # đỏ nếu bị giảm EXP
        surface = font.render(self.text, True, color)
        surface.set_alpha(self.alpha)
        return surface
        
font = pygame.font.SysFont("Arial", 30)
font_info = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.04))
level_font = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.07))  # Cỡ chữ căn chỉnh với tỷ lệ màn hình
font = pygame.font.SysFont(None, 50)
exp_popups = []
exp_font = pygame.font.SysFont(None, 50)  # Bạn có thể chỉnh font size
player_max_cooldown = 20
ratio = 1 - player_attack_cooldown / player_max_cooldown
    
def joystick():
    pygame.draw.circle(screen, (180, 180, 180), inner_pos, int(joystick_inner_radius))
    pygame.draw.circle(screen, (0, 0, 0, 80), inner_pos, int(joystick_inner_radius) + 5)
    
def ms():
    global last_ms_update_time, displayed_ms

    if current_time - last_ms_update_time >= 1000:
        displayed_ms = clock.get_time()
        last_ms_update_time = current_time

    fps = int(clock.get_fps())

    if not hasattr(ms, "cached_fps") or ms.cached_fps != fps or ms.cached_ms != displayed_ms:
        ms.cached_fps = fps
        ms.cached_ms = displayed_ms
        ms.cached_text = font_info.render(f"{fps} FPS / {displayed_ms} ms", True, (255, 255, 255))
        ms.cached_rect = ms.cached_text.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)).inflate(12, 6)

    pygame.draw.rect(screen, (0, 0, 0), ms.cached_rect)
    pygame.draw.rect(screen, (255, 255, 255), ms.cached_rect, 1)
    screen.blit(ms.cached_text, (ms.cached_rect.x + 6, ms.cached_rect.y + 3))
    
show_settings_menu = False
show_minimap = False

SETTINGS_BTN_RECT = pygame.Rect(SCREEN_WIDTH - 70, 10, 60, 60)
GRAY = (200, 200, 200)

def draw_settings_button():
    pygame.draw.rect(screen, (50, 50, 50), SETTINGS_BTN_RECT, border_radius=12)
    
    cx, cy = SETTINGS_BTN_RECT.center
    pygame.draw.circle(screen, (200, 200, 200), (cx, cy), 6)
    pygame.draw.circle(screen, (200, 200, 200), (cx, cy - 12), 6)
    pygame.draw.circle(screen, (200, 200, 200), (cx, cy + 12), 6)
    
    return SETTINGS_BTN_RECT
settings = {
    "show_minimap": True
}
settings_font = pygame.font.SysFont('Arial', int(SCREEN_HEIGHT * 0.05))

SAFE_DISTANCE = 100

def draw_settings_menu():
    menu_width = int(SCREEN_WIDTH * 0.5)
    menu_height = int(SCREEN_HEIGHT * 0.6)
    menu_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - menu_width // 2,
        SCREEN_HEIGHT // 2 - menu_height // 2,
        menu_width,
        menu_height
    )
    pygame.draw.rect(screen, (70, 70, 70), menu_rect, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), menu_rect, 6, border_radius=10)

    labels = ["Thoát", "Chơi lại"]
    btn_rects = []

    for i, label in enumerate(labels):
        text = settings_font.render(label, True, (255, 255, 255))
        text_rect = text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - menu_height // 4 + i * int(SCREEN_HEIGHT * 0.1))
        )
        btn_rects.append(text_rect)
        pygame.draw.rect(screen, (100, 100, 100), text_rect.inflate(20, 20), border_radius=16)
        pygame.draw.rect(screen, (255, 255, 255), text_rect.inflate(20, 20), 3, border_radius=16)
        screen.blit(text, text_rect)

    # --- Âm lượng: < 0.5 > ---
    vol_y = SCREEN_HEIGHT // 2 + menu_height // 5
    vol_text = settings_font.render("Âm lượng", True, (255, 255, 255))
    vol_rect = vol_text.get_rect(center=(SCREEN_WIDTH // 2, vol_y - 80))
    screen.blit(vol_text, vol_rect)

    vol = round(pygame.mixer.music.get_volume(), 2)
    value_label = settings_font.render(f"<  {vol:.1f}  >", True, (255, 255, 255))
    value_rect = value_label.get_rect(center=(SCREEN_WIDTH // 2, vol_y))
    pygame.draw.rect(screen, (100, 100, 100), value_rect.inflate(20, 10), border_radius=12)
    pygame.draw.rect(screen, (255, 255, 255), value_rect.inflate(20, 10), 2, border_radius=12)
    screen.blit(value_label, value_rect)

    # Tạo 2 vùng click trái & phải
    vol_dec_rect = pygame.Rect(value_rect.left, value_rect.top, value_rect.width // 3, value_rect.height)
    vol_inc_rect = pygame.Rect(value_rect.right - value_rect.width // 3, value_rect.top, value_rect.width // 3, value_rect.height)

    return menu_rect, btn_rects, vol_dec_rect, vol_inc_rect
def handle_settings_input(event, menu_rect, btn_rects, vol_dec_rect, vol_inc_rect):
    global show_settings_menu

    if event.type == pygame.MOUSEBUTTONDOWN:
        mx, my = pygame.mouse.get_pos()

        if not menu_rect.collidepoint((mx, my)):
            show_settings_menu = False
        else:
            if btn_rects[0].collidepoint((mx, my)):
                save_current_character()
                pygame.quit()
                sys.exit()
            elif btn_rects[1].collidepoint((mx, my)):
                restart_game()
            elif vol_dec_rect.collidepoint((mx, my)):
                new_volume = max(0.0, pygame.mixer.music.get_volume() - 0.1)
                pygame.mixer.music.set_volume(new_volume)
            elif vol_inc_rect.collidepoint((mx, my)):
                new_volume = min(1.0, pygame.mixer.music.get_volume() + 0.1)
                pygame.mixer.music.set_volume(new_volume)
    
map_name = ""
map_change_time = 0
MAP_NAME_DURATION = 2  # giây
map_title_font = pygame.font.SysFont("Arial", 120)
skill1_max_cooldown = 120        
archer_speed_boost_until = 0

def use_archer_skill3():
    global skill3_cooldown, archer_speed_boost_until, player_attack_range
    archer_speed_boost_until = time.time() + 8
    player_max_cooldown = 10
    player_attack_range += 100
    skill3_cooldown = skill3_max_cooldown
    
skill3_cooldown = 0

inventory = {k: 0 for k in ITEM_DEFS}
equipped = {k: False for k in ITEM_DEFS}
explosions = []
def equip(item_type):
    global player_attack_damage, player_max_health, player_health

    if inventory[item_type] <= 0:
        return

    if equipped[item_type]:
        return

    for attr, val in ITEM_DEFS[item_type]["bonus"].items():
        if attr == "damage":
            player_attack_damage += val
        elif attr == "max_health":
            player_max_health += val
            player_health = min(player_health + val, player_max_health)

    equipped[item_type] = True

def unequip(item_type):
    global player_attack_damage, player_max_health, player_health

    if not equipped[item_type]:
        return
    for attr, val in ITEM_DEFS[item_type]["bonus"].items():
        if attr == "damage":
            player_attack_damage -= val
        elif attr == "max_health":
            player_max_health -= val
            player_health = min(player_health, player_max_health)

    equipped[item_type] = False
        
show_inventory = False

game_font = pygame.font.SysFont("arial", 28)
def draw_inventory():  
    inv_w, inv_h = 400, 300  
    inv_x = SCREEN_WIDTH // 2 - inv_w // 2  
    inv_y = SCREEN_HEIGHT // 2 - inv_h // 2  
    slot_size = 80  
    padding = 20  
    keys = list(ITEM_DEFS.keys())  
  
    # Nền inventory  
    pygame.draw.rect(screen, (40, 40, 40), (inv_x, inv_y, inv_w, inv_h), border_radius=12)  
  
    # Tiêu đề BALO  
    title_text = game_font.render("BALO", True, WHITE)  
    screen.blit(title_text, (inv_x + (inv_w - title_text.get_width()) // 2, inv_y - 40))  
  
    for idx, key in enumerate(keys):  
        row = idx // 2  
        col = idx % 2  
        sx = inv_x + padding + col * (slot_size + padding)  
        sy = inv_y + padding + row * (slot_size + padding)  
        slot_rect = pygame.Rect(sx, sy, slot_size, slot_size)  
  
        # Nền ô  
        pygame.draw.rect(screen, (90, 90, 90), slot_rect, border_radius=8)  
  
        # Số lượng item  
        count_text = game_font.render(str(inventory[key]), True, WHITE)  
        screen.blit(count_text, (sx + 6, sy + 6))  
  
        # Viền sáng nếu đang mặc  
        if equipped[key]:  
            pygame.draw.rect(screen, (0, 255, 0), slot_rect, 4, border_radius=8)  
  
        # Tên item bên dưới ô  
        name_text = game_font.render(ITEM_DEFS[key]["name"], True, WHITE)  
        screen.blit(name_text, (sx, sy + slot_size - 20))  
  
    # Gợi ý sử dụng  
    hint_text = game_font.render("Bấm vào để sử dụng", True, (180, 180, 180))  
    screen.blit(hint_text, (inv_x + (inv_w - hint_text.get_width()) // 2, inv_y + inv_h + 10))

level_font = pygame.font.SysFont(None, int(settings_font.get_height() * 0.85))

MONSTERS7_COLOR = (0, 255, 0)
MONSTERS8_COLOR = (255, 100, 100)
MONSTERS9_COLOR = (255, 165, 0)
MONSTERS10_COLOR = (128, 0, 128)

def get_monster_color(mon):
    monster_type = mon.get("type", "")
    ticks = pygame.time.get_ticks()

    if monster_type == "monsters6":
        glow = int(100 + 40 * math.sin(ticks / 300))
        return (glow, glow, 255)
    elif monster_type == "monsters7":
        return MONSTERS7_COLOR
    elif monster_type == "monsters8":
        return MONSTERS8_COLOR
    elif monster_type == "monsters9":
        return MONSTERS9_COLOR
    elif monster_type == "monsters10":
        return MONSTERS10_COLOR
    elif monster_type == "monsters5":
        return GRAY
    elif monster_type == "monsters4":
        return YELLOW
    elif monster_type == "monsters3":
        return RED
    elif monster_type == "monsters2":
        return ORANGE
    elif monster_type == "monsters1":
        return PURPLE
    else:
        return PURPLE
        
map_names = {
    0: "Đồng cỏ 1",
    1: "Làng Hope",
    2: "Đồng cỏ 2",
    3: "Đồng cỏ 3",
    4: "Đồng cỏ 4",
    5: "Rừng thông 1",
    6: "Hang động",
    7: "Làng Silver",
    8: "Rừng thông 2",
    9: "Bãi biển 1",
    10: "Bãi biển 2",
    11: "Trảng cỏ 1",
    12: "Trảng cỏ 2",
    13: "Di tích cổ",
    99: "Dungeon 1"
}

def draw_background_zones(map_data):
    for zone in map_data.get("background_zones", []):
        rect = pygame.Rect(zone["x"] - camera_x, zone["y"] - camera_y, zone["width"], zone["height"])
        pygame.draw.rect(screen, zone["color"], rect)

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
mouse_down = False
mouse_down = False

big_font          = pygame.font.SysFont("Arial", int(SCREEN_HEIGHT * 0.065), bold=True)
warning_font      = pygame.font.SysFont("Arial", int(SCREEN_WIDTH * 0.05), bold=True)
unable_exit_font  = pygame.font.SysFont("Arial", int(SCREEN_WIDTH * 0.04), bold=True)

boss_spawned = False
spawn_timer = 0
knight_shield_active = False
shield_active_until = 0
shield_duration = 0
thunder_ring_active = False
thunder_ring_start = 0
thunder_ring_duration = 5000
thunder_orbs = []
effects_list = []

def draw_background_zones(current_map, cx, cy):
    for zone in current_map.get("background_zones", []):
        x, y, w, h = zone["x"] - cx, zone["y"] - cy, zone["width"], zone["height"]

        # Bỏ qua nếu ngoài màn hình
        if x + w < 0 or x > SCREEN_WIDTH or y + h < 0 or y > SCREEN_HEIGHT:
            continue

        color = zone.get("color", BACKGROUND_COLOR)
        pygame.draw.rect(screen, color, (x, y, w, h))


def draw_background(current_map, cx, cy):
    if "background_zones" in current_map:
        screen.fill(current_map.get("background_color", BLACK))
        draw_background_zones(current_map, cx, cy)
    else:
        screen.fill(current_map.get("background_color", BLACK))

original_attack_range = 180

def update_monsters(current_map):
    global player_health, player_x, player_y, last_combat_time, monster_attack_sound_played, screen_shake_timer

    for mon in current_map.get("monsters", []):
        if (camera_x - 200 <= mon["x"] <= camera_x + SCREEN_WIDTH + 200 and
            camera_y - 200 <= mon["y"] <= camera_y + SCREEN_HEIGHT + 200):
            if mon["attack_cooldown"] > 0:
                mon["attack_cooldown"] -= 1

        d = math.hypot(mon["x"] - player_x, mon["y"] - player_y)

        if d <= mon["vision"]:
            dx, dy = player_x - mon["x"], player_y - mon["y"]
            if d:
                dx, dy = dx / d, dy / d

            mon["last_seen_player"] = pygame.time.get_ticks()

            # Swarm AI - né đồng đội
            avoid_x, avoid_y = 0, 0
            nearby_count = 0
            for other in current_map.get("monsters", []):
                if other is not mon:
                    dist = math.hypot(mon["x"] - other["x"], mon["y"] - other["y"])
                    if dist < mon["radius"] * 4:
                        ax = mon["x"] - other["x"]
                        ay = mon["y"] - other["y"]
                        if dist:
                            ax /= dist
                            ay /= dist
                        avoid_x += ax
                        avoid_y += ay
                        nearby_count += 1

            if nearby_count > 0:
                avoid_x /= nearby_count
                avoid_y /= nearby_count
                dx = dx + avoid_x * 0.7
                dy = dy + avoid_y * 0.7
                norm = math.hypot(dx, dy)
                if norm:
                    dx /= norm
                    dy /= norm

            # Né chướng ngại vật nâng cao
            def will_hit_obstacle(x, y):
                for house in current_map.get("houses", []):
                    if circle_rect_collision(x, y, mon["radius"], house["x"], house["y"], house["width"], house["height"]):
                        return True
                for tree in current_map.get("trees", []):
                    if circle_rect_collision(x, y, mon["radius"],
                                             tree["x"], tree["y"] - tree["trunk_height"],
                                             tree["trunk_width"], tree["trunk_height"]):
                        return True
                for pine in current_map.get("pine_trees", []):
                    if circle_rect_collision(x, y, mon["radius"],
                                             pine["x"], pine["y"] - pine["trunk_height"],
                                             pine["trunk_width"], pine["trunk_height"]):
                        return True
                return False

            base_angle = math.atan2(dy, dx)
            found = False
            for offset in [0, 30, -30, 60, -60, 90, -90]:
                ang = base_angle + math.radians(offset)
                test_dx = math.cos(ang)
                test_dy = math.sin(ang)
                test_x = mon["x"] + test_dx * mon["speed"]
                test_y = mon["y"] + test_dy * mon["speed"]
                if not will_hit_obstacle(test_x, test_y):
                    dx, dy = test_dx, test_dy
                    found = True
                    break
            if not found:
                dx, dy = 0, 0

        else:
            if "wander_dx" not in mon:
                mon["wander_dx"] = random.uniform(-1, 1)
                mon["wander_dy"] = random.uniform(-1, 1)
            if random.random() < 0.01:
                mon["wander_dx"] = random.uniform(-1, 1)
                mon["wander_dy"] = random.uniform(-1, 1)
            dx, dy = mon["wander_dx"], mon["wander_dy"]

        prop_x = mon["x"] + dx * mon["speed"]
        prop_y = mon["y"] + dy * mon["speed"]

        if not is_colliding(prop_x, prop_y, mon["radius"], player_x, player_y, player_radius):
            blocked = False

            for other in current_map.get("monsters", []):
                if other is not mon:
                    dist = math.hypot(prop_x - other["x"], prop_y - other["y"])
                    if dist < mon["radius"] + other["radius"]:
                        blocked = True
                        break

            if not blocked:
                if (0 + mon["radius"] <= prop_x <= MAP_WIDTH - mon["radius"] and
                    0 + mon["radius"] <= prop_y <= MAP_HEIGHT - mon["radius"]):
                    mon["x"], mon["y"] = prop_x, prop_y
                    mon["blocked_count"] = 0
            else:
                mon["blocked_count"] = mon.get("blocked_count", 0) + 1
                if mon["blocked_count"] > 10:
                    mon["wander_dx"] = random.uniform(-1, 1)
                    mon["wander_dy"] = random.uniform(-1, 1)
                    mon["blocked_count"] = 0
        else:
            over = (player_radius + mon["radius"]) - math.hypot(mon["x"] - player_x, mon["y"] - player_y)
            if over > 0:
                mon["x"] -= dx * over * 0.5
                mon["y"] -= dy * over * 0.5

        if d <= mon["attack_range"] and mon["attack_cooldown"] <= 0:
            if Knight and is_shield_active():
                reduced_dmg = int(mon["attack_damage"] * 0.8)
                player_health -= reduced_dmg
                damage_texts.append(DamageText(player_x, player_y - 60, str(reduced_dmg), (100, 200, 255)))
            else:
                player_health -= mon["attack_damage"]
                screen_shake_timer = 1
                damage_texts.append(DamageText(player_x, player_y - 60, str(mon["attack_damage"]), (255, 255, 0)))

            if player_health <= 0:
                restart_game()

            mon["attack_cooldown"] = mon["attack_max_cooldown"]
            last_combat_time = pygame.time.get_ticks()
            add_attack_effect(mon["x"], mon["y"], mon["radius"], mon["attack_range"], ORANGE, 15)

            if not monster_attack_sound_played:
                player_attack_sound.play()
                monster_attack_sound_played = True
        else:
            monster_attack_sound_played = False
            
# Font nên được tạo ngoài hàm, chỉ 1 lần khi game khởi động
monster_font = pygame.font.SysFont("arial", 16)

def draw_monsters(current_map, screen, camera_x, camera_y):
    now = time.time()
    monsters = current_map.get("monsters", [])
    lake_poly = current_map.get("lake_polygon")

    for mon in monsters:
        mx = int(mon["x"] - camera_x)
        my = int(mon["y"] - camera_y)

        base_r = mon["radius"]
        r = int(base_r + math.sin(now * 3 + mon["x"] + mon["y"]) * 2)

        # Cắt dưới mặt nước nếu quái trong hồ
        in_lake = lake_poly and point_in_polygon(mon["x"], mon["y"] + base_r * 0.5, lake_poly)
        if in_lake:
            cut_y = int(mon["y"] - base_r + base_r * 0.5 - camera_y)
            clip_rect = pygame.Rect(0, 0, SCREEN_WIDTH, cut_y)
            old_clip = screen.get_clip()
            screen.set_clip(clip_rect)

        if -r <= mx <= SCREEN_WIDTH + r and -r <= my <= SCREEN_HEIGHT + r:
            # Vẽ thân quái
            pygame.draw.circle(screen, (0, 0, 0), (mx + 1, my + 1), r + 3)
            pygame.draw.circle(screen, (20, 20, 20), (mx, my), r + 2)
            pygame.draw.circle(screen, get_monster_color(mon), (mx, my), r)

            # Vẽ tên (luôn hiện)
            name = mon.get("name", "Quái")
            level = mon.get("level", 1)
            label = f"{name} Lv {level}"
            text_surface = monster_font.render(label, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(mx, my - r - 22))
            screen.blit(text_surface, text_rect)

            # Vẽ thanh máu (chỉ nếu bị đánh)
            if mon["health"] < mon["max_health"]:
                hr = mon["health"] / mon["max_health"]
                bw = r * 2
                bh = 5
                bx = mx - r
                by = my - r - 10
                pygame.draw.rect(screen, (0, 0, 0), (bx + 1, by + 1, bw, bh), border_radius=3)
                pygame.draw.rect(screen, (60, 0, 0), (bx, by, bw, bh), border_radius=3)
                pygame.draw.rect(screen, (0, 200, 0), (bx, by, int(bw * hr), bh), border_radius=3)

        if in_lake:
            screen.set_clip(old_clip)
            

            
def checkskill():
    global skill_cooldown, skill_max_cooldown
    global skill2_cooldown, skill2_max_cooldown
    global skill3_cooldown, skill3_max_cooldown

    if player_level < 3:
        skill_cooldown = skill_max_cooldown = 120
    else:
        pass

    if player_level < 5:
        skill2_cooldown = skill2_max_cooldown = 240
    else:
        pass

    if player_level < 8:
        skill3_cooldown = skill3_max_cooldown = 300
    else:
        pass
	
mouse_down_stat = False
talk_button_rect = None
npc_hovered = None

RAIN_COUNT = 300
rain_drops = []
for _ in range(RAIN_COUNT):
    rain_drops.append({
        "x": random.randint(0, MAP_WIDTH),
        "y": random.randint(0, MAP_HEIGHT),
        "length": random.randint(10, 20),
        "speed": random.uniform(7, 11)
    })
    
def draw_rain(screen, rain_drops, camera_x, camera_y):
    for drop in rain_drops:
        x = drop["x"] - camera_x
        y = drop["y"] - camera_y

        if 0 <= x <= screen.get_width() and 0 <= y <= screen.get_height():
            pygame.draw.line(screen, (180, 180, 255), (x, y), (x, y + drop["length"]), 1)

        drop["y"] += drop["speed"]
        if drop["y"] > MAP_HEIGHT:
            drop["y"] = random.randint(-100, -10)
            drop["x"] = random.randint(0, MAP_WIDTH)

rain_active = False
rain_timer = 0
next_rain_time = time.time() + random.randint(240, 300)

while running:
    checkskill()
    level_circle_radius = int(SCREEN_HEIGHT * 0.08)
    level_circle_x = int(SCREEN_WIDTH * 0.05)
    level_circle_y = int(SCREEN_HEIGHT * 0.1)
    avatar_center = (level_circle_x, level_circle_y)
    mx, my = pygame.mouse.get_pos()

    avatar_rect = pygame.Rect(
        level_circle_x - level_circle_radius,
        level_circle_y - level_circle_radius,
        level_circle_radius * 2,
        level_circle_radius * 2
    )
    settings_btn_rect = draw_settings_button()

    if screen_shake_timer > 0:
    	screen_shake_timer -= 1
    	shake_offset_x = random.randint(-5, 5)
    	shake_offset_y = random.randint(-5, 5)
    else:
    	shake_offset_x = 0
    	shake_offset_y = 0
    half_w, half_h = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    camera_x = max(0, min(player_x - half_w, MAP_WIDTH - SCREEN_WIDTH)) + shake_offset_x
    camera_y = max(0, min(player_y - half_h, MAP_HEIGHT - SCREEN_HEIGHT)) + shake_offset_y
    current_time = time.time()
    current_time = time.time()
    if not rain_active and current_time >= next_rain_time:
    	rain_active = True
    	rain_timer = current_time + random.randint(60, 120)
    elif rain_active and current_time >= rain_timer:
    	rain_active = False
    	next_rain_time = current_time + random.randint(240, 300)
    
    draw_background(current_map, camera_x, camera_y)
    if "transition_zones" in current_map:
    	draw_transition_zones(current_map["transition_zones"])

    for patch in current_map.get("grass", []):
        pygame.draw.circle(screen, (0, 110, 0), (patch["x"] - camera_x, patch["y"] - camera_y), patch["radius"])

    if "roads" in current_map:
        draw_roads(current_map.get("roads", []), camera_x, camera_y, screen)

    mx, my = pygame.mouse.get_pos()

    # Reset lại trạng thái click chuột
    if not pygame.mouse.get_pressed()[0]:
        mouse_down = False
    update_respawn()
    btn_x = int(SCREEN_WIDTH * 0.02)
    btn_y = int(SCREEN_HEIGHT * 0.2)
    btn_w = int(SCREEN_WIDTH * 0.1)
    btn_h = int(SCREEN_HEIGHT * 0.08)
    backpack_btn = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

    for dmg_text in damage_texts[:]:
        dmg_text.update()
        dmg_text.draw(screen, font, camera_x, camera_y)
        if dmg_text.is_expired():
            damage_texts.remove(dmg_text)

    # --- Xử lý NPC (vẽ và chuẩn bị "nút nói") ---
    talk_button_rect = None
    npc_hovered = None

    for npc in npcs:
        if npc["map_id"] != current_map["id"]:
            continue

        # Vẽ NPC
        if npc["id"] == "guardian":
            draw_guardian(npc["x"], npc["y"], player_radius, camera_x, camera_y)
        elif npc["id"] == "old_man":
            draw_player3(npc["x"], npc["y"], player_radius, camera_x, camera_y)
        else:
            draw_player(npc["x"], npc["y"], player_radius, camera_x, camera_y)

        dist = math.hypot(player_x - npc["x"], player_y - npc["y"])
        if dist <= 150 and not (npc["id"] == "guardian" and npc_interacted):
            btn_size = int(SCREEN_WIDTH * 0.08)
            btn_margin_right = int(SCREEN_WIDTH * 0.03)  # dịch sang phải một chút
            btn_margin_bottom = int(SCREEN_HEIGHT * 0.55)

            talk_button_rect = pygame.Rect(
                SCREEN_WIDTH - btn_margin_right - btn_size,
                SCREEN_HEIGHT - btn_margin_bottom - btn_size,
                btn_size,
                btn_size
            )

            pygame.draw.circle(screen, (200, 200, 255), talk_button_rect.center, btn_size // 2)
            pygame.draw.circle(screen, WHITE, talk_button_rect.center, btn_size // 2, 3)

            font_size = int(btn_size * 0.3)
            text = font.render("Nói", True, (0, 0, 0))
            screen.blit(text, (
                talk_button_rect.centerx - text.get_width() // 2,
                talk_button_rect.centery - text.get_height() // 2
            ))

            npc_hovered = npc

    # --- Xử lý sự kiện ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_current_character()
            running = False

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_down_stat = False
            joystick_active = False
            joystick_offset_x = joystick_offset_y = 0

        elif event.type == pygame.MOUSEMOTION:
            mx, my = pygame.mouse.get_pos()
            if joystick_active:
                dx, dy = mx - joystick_x, my - joystick_y
                d = math.hypot(dx, dy)
                if d > joystick_radius:
                    scale = joystick_radius / d
                    dx *= scale
                    dy *= scale
                joystick_offset_x, joystick_offset_y = dx, dy

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Nếu đang hiển thị hộp thoại NPC
            if show_npc_popup:
                if show_npc_popup.get("id") == "guardian":
                    if npc_yes_btn.collidepoint(mx, my):
                        npc_interacted = True
                        show_npc_popup = None
                    elif npc_no_btn.collidepoint(mx, my):
                        show_npc_popup = None
                else:
                    if npc_exit_btn.collidepoint(mx, my):
                        show_npc_popup = None

            # Nếu chưa có popup, mà có NPC đang gần và bấm vào nút nói
            elif talk_button_rect and talk_button_rect.collidepoint(mx, my) and npc_hovered:
                show_npc_popup = npc_hovered

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            if event.type == pygame.FINGERDOWN:
                mx = int(event.x * SCREEN_WIDTH)
                my = int(event.y * SCREEN_HEIGHT)
            else:
                mx, my = event.pos

            if math.hypot(mx - avatar_center[0], my - avatar_center[1]) <= level_circle_radius:
                show_stat_popup = not show_stat_popup

            if show_stat_popup:
            	if close_stat_btn.collidepoint(mx, my):
            		show_stat_popup = False
            	elif hp_plus_btn.collidepoint(mx, my) and unspent_points >= 1 and not mouse_down_stat:
            		player_max_health += 5
            		unspent_points -= 1
            		mouse_down_stat = True
            	elif dmg_plus_btn.collidepoint(mx, my) and unspent_points >= 1 and not mouse_down_stat:
            		player_attack_damage += 1
            		unspent_points -= 1
            		mouse_down_stat = True

            if show_settings_menu:
                menu_rect, btn_rects, vol_dec_rect, vol_inc_rect = draw_settings_menu()
                handle_settings_input(event, menu_rect, btn_rects, vol_dec_rect, vol_inc_rect)

            if settings_btn_rect.collidepoint((mx, my)):
                show_settings_menu = True

            if math.hypot(mx - joystick_x, my - joystick_y) <= joystick_radius:
                joystick_active = True

            # Kỹ năng
            if math.hypot(mx - skill3_button_center[0], my - skill3_button_center[1]) <= skill3_button_radius:
                if skill3_cooldown == 0:
                    if Archer == 1:
                        use_archer_skill3()
                    elif Knight == 1:
                        skill3_cooldown = use_archer_skill2(current_map, player_x, player_y, player_attack_range, player_attack_damage, skill3_max_cooldown, damage_texts, handle_monster_death, RED, effects_list)
                    elif Wizard == 1:
                                        skill3_cooldown = use_wizard_skill3(player_x, player_y, player_attack_damage, current_time, skill3_max_cooldown)

            if math.hypot(mx - skill2_button_center[0], my - skill2_button_center[1]) <= skill2_button_radius:
                if skill2_cooldown == 0:
                    if Knight == 1:
                    	current_time = pygame.time.get_ticks()
                    	skill2_cooldown = use_knight_skill2(current_time, skill2_max_cooldown)
                    elif Archer == 1:
                        skill2_cooldown = use_knight_skill3(player_x, player_y, player_attack_damage, skill2_max_cooldown)
                    elif Wizard == 1:
                        skill2_cooldown = use_wizard_skill2(player_x, player_y, player_attack_damage, current_map, damage_texts, handle_monster_death, camera_x, camera_y, screen, wizard_skill2_explosions)

            if math.hypot(mx - skill_button_center[0], my - skill_button_center[1]) <= skill_button_radius:
                if skill_cooldown == 0:
                    if Knight == 1:
                        skill_cooldown, player_health = use_knight_skill(current_map, player_x, player_y, player_radius, player_attack_range, player_attack_damage, player_health, damage_texts, handle_monster_death, skill_max_cooldown, add_attack_effect)
                    elif Archer == 1:
                        skill_cooldown = use_archer_skill(current_map, player_x, player_y, player_attack_range, player_attack_damage, skill_max_cooldown, shoot_skill_arrow)
                    elif Wizard == 1:
                        skill_cooldown = use_wizard_skill1(player_x, player_y, player_attack_damage, current_map, damage_texts, handle_monster_death, camera_x, camera_y, screen)

            if math.hypot(mx - attack_button_center[0], my - attack_button_center[1]) <= attack_button_radius:
                if player_attack_cooldown <= 0:
                    if Knight == 1:
                        add_attack_effect(player_x, player_y, player_radius, player_attack_range, YELLOW, 15)
                        for i in range(len(current_map["monsters"]) - 1, -1, -1):
                            mon = current_map["monsters"][i]
                            if math.hypot(mon["x"] - player_x, mon["y"] - player_y) <= (player_attack_range + mon["radius"]):
                                mon["health"] -= player_attack_damage
                                damage_texts.append(DamageText(mon["x"], mon["y"] - 60, str(player_attack_damage), RED))
                                if mon["health"] <= 0:
                                    handle_monster_death(mon)
                                    del current_map["monsters"][i]
                    elif Archer == 1 or Wizard == 1:
                        nearest_idx = None
                        nearest_dist = float("inf")
                        for i in range(len(current_map["monsters"])):
                            mon = current_map["monsters"][i]
                            dist = math.hypot(mon["x"] - player_x, mon["y"] - player_y)
                            if dist <= (player_attack_range + mon["radius"]) and dist < nearest_dist:
                                nearest_dist = dist
                                nearest_idx = i
                        if nearest_idx is not None:
                            mon = current_map["monsters"][nearest_idx]
                            shoot_arrow(player_x, player_y, mon["x"], mon["y"], player_attack_damage)
                    player_attack_cooldown = player_max_cooldown

            if potion_button.collidepoint((mx, my)):
                healing()

    # INVENTORY
    mouse_pressed = pygame.mouse.get_pressed()[0]
    clicked_inventory_slot = False
    if show_inventory and mouse_pressed and not mouse_down:
        inv_w, inv_h = 400, 300
        inv_x = SCREEN_WIDTH // 2 - inv_w // 2
        inv_y = SCREEN_HEIGHT // 2 - inv_h // 2
        slot_size = 80
        padding = 20
        keys = list(ITEM_DEFS.keys())
        for idx, key in enumerate(keys):
            row = idx // 2
            col = idx % 2
            sx = inv_x + padding + col * (slot_size + padding)
            sy = inv_y + padding + row * (slot_size + padding)
            slot_rect = pygame.Rect(sx, sy, slot_size, slot_size)
            if slot_rect.collidepoint(mx, my):
                clicked_inventory_slot = True
                if equipped[key]:
                    unequip(key)
                elif inventory[key] > 0:
                    equip(key)

    if mouse_pressed and not mouse_down and not clicked_inventory_slot and backpack_btn.collidepoint((mx, my)):
        show_inventory = not show_inventory
    if mouse_pressed and not mouse_down:
        if math.hypot(mx - avatar_center[0], my - avatar_center[1]) <= level_circle_radius:
        	show_stat_popup = not show_stat_popup

    mouse_down = mouse_pressed
    if player_attack_cooldown > 0:
        player_attack_cooldown -= 1
    if skill_cooldown > 0:
        skill_cooldown -= 1
    if skill2_cooldown > 0:
        skill2_cooldown -= 1
    if skill3_cooldown > 0:
        skill3_cooldown -= 1

    if Archer == 1 and time.time() > archer_speed_boost_until:
        if player_attack_range != original_attack_range:
            player_attack_range = original_attack_range
            
    new_px, new_py = player_x, player_y
    dx, dy = joystick_offset_x, joystick_offset_y
    if joystick_active and (dx or dy) and not show_inventory:
        ang = math.atan2(dy, dx)
        speed_scale = math.hypot(dx, dy) / joystick_radius
        effective_speed = player_speed
        if Archer == 1 and time.time() < archer_speed_boost_until:
            effective_speed *= 1.8
        new_px += math.cos(ang) * effective_speed * speed_scale
        new_py += math.sin(ang) * effective_speed * speed_scale
        coll = False
        pr = player_radius

        for mon in current_map.get("monsters", []):
            if is_colliding(new_px, new_py, pr, mon["x"], mon["y"], mon["radius"]):
                coll = True
                break
        if not coll:
            for house in current_map.get("houses", []):
                if circle_rect_collision(new_px, new_py, pr, house["x"], house["y"], house["width"], house["height"]):
                    coll = True
                    break
        if not coll:
            for tree in current_map.get("trees", []):
                if circle_rect_collision(new_px, new_py, pr, tree["x"], tree["y"] - tree["trunk_height"],
                                         tree["trunk_width"], tree["trunk_height"]):
                    coll = True
                    break
        if not coll:
            for tw in current_map.get("tree_wall", []):
                if circle_rect_collision(new_px, new_py, pr, tw["x"], tw["y"], tw["trunk_width"], tw["trunk_height"]):
                    coll = True
                    break

        if not coll:
        	if 0 + player_radius <= new_px <= MAP_WIDTH - player_radius and 0 + player_radius <= new_py <= MAP_HEIGHT - player_radius:
        		player_x, player_y = new_px, new_py

    pr = player_radius

    for portal in current_map.get("portals", []):
        if portal is None:
            continue

        if portal["target"] == -999:
            if circle_rect_collision(player_x, player_y, player_radius, portal["x"], portal["y"], portal["width"], portal["height"]):
                show_dungeon_stage_menu()
                break
        else:
            if circle_rect_collision(player_x, player_y, player_radius,
                                     portal["x"], portal["y"], portal["width"], portal["height"]):
                transition_effect()
                source_map_id = current_map["id"]
                current_map = maps[portal["target"]]

                spawn_x = current_map["width"] // 2
                spawn_y = current_map["height"] // 2

                for back_portal in current_map.get("portals", []):
                    if back_portal["target"] == source_map_id:
                        if back_portal["x"] + back_portal["width"] < current_map["width"] // 2:
                            spawn_x = back_portal["x"] + back_portal["width"] + SAFE_DISTANCE
                            spawn_y = back_portal["y"] + back_portal["height"] // 2
                        elif back_portal["x"] > current_map["width"] // 2:
                            spawn_x = back_portal["x"] - SAFE_DISTANCE
                            spawn_y = back_portal["y"] + back_portal["height"] // 2
                        elif back_portal["y"] + back_portal["height"] < current_map["height"] // 2:
                            spawn_x = back_portal["x"] + back_portal["width"] // 2
                            spawn_y = back_portal["y"] + back_portal["height"] + SAFE_DISTANCE
                        else:
                            spawn_x = back_portal["x"] + back_portal["width"] // 2
                            spawn_y = back_portal["y"] - SAFE_DISTANCE
                        break

                player_x, player_y = spawn_x, spawn_y
                map_name = f"Map: {map_names.get(current_map['id'], current_map['id'])}"
                map_change_time = time.time()
                break

    # Xử lý blackholes tương tự như portal
    for blackhole in current_map.get("blackholes", []):
        if circle_rect_collision(player_x, player_y, player_radius,
                                 blackhole["x"], blackhole["y"],
                                 blackhole["width"], blackhole["height"]):
            transition_effect()
            source_map_id = current_map["id"]
            current_map = maps[blackhole["target"]]

            spawn_x = current_map["width"] // 2
            spawn_y = current_map["height"] // 2

            for back_portal in current_map.get("portals", []):
                if back_portal["target"] == source_map_id:
                    if back_portal["x"] + back_portal["width"] < current_map["width"] // 2:
                        spawn_x = back_portal["x"] + back_portal["width"] + SAFE_DISTANCE
                        spawn_y = back_portal["y"] + back_portal["height"] // 2
                    elif back_portal["x"] > current_map["width"] // 2:
                        spawn_x = back_portal["x"] - SAFE_DISTANCE
                        spawn_y = back_portal["y"] + back_portal["height"] // 2
                    elif back_portal["y"] + back_portal["height"] < current_map["height"] // 2:
                        spawn_x = back_portal["x"] + back_portal["width"] // 2
                        spawn_y = back_portal["y"] + back_portal["height"] + SAFE_DISTANCE
                    else:
                        spawn_x = back_portal["x"] + back_portal["width"] // 2
                        spawn_y = back_portal["y"] - SAFE_DISTANCE
                    break

            player_x, player_y = spawn_x, spawn_y
            map_name = f"Map: {map_names.get(current_map['id'], current_map['id'])}"
            map_change_time = time.time()
            break

    # --- Ship portal xử lý riêng ---
    ship = current_map.get("ship_portal")
    if ship and circle_rect_collision(player_x, player_y, player_radius, ship["x"], ship["y"], ship["width"], ship["height"]):
        transition_effect()
        source_map_id = current_map["id"]
        current_map = maps[ship["target"]]
        player_x = current_map["width"] // 2
        player_y = current_map["height"] // 2
        map_name = f"Map: {map_names.get(current_map['id'], current_map['id'])}"
        map_change_time = time.time()

    # --- Vẽ portal ---
    

    for grass in current_map.get("dry_grass", []):
        draw_dry_grass(grass, camera_x, camera_y, screen)
    if current_map["id"] == 12:
    	draw_lake_polygon(current_map["lake_polygon"], camera_x, camera_y, screen)

    in_lake = "lake_polygon" in current_map and point_in_polygon(
        player_x, player_y + player_radius * 0.3, current_map["lake_polygon"]
    )
    
    if in_lake:
        cut_y = int(player_y - player_radius * 0.4 - camera_y)
        clip_rect = pygame.Rect(0, 0, SCREEN_WIDTH, cut_y)
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect)

    if current_map["id"] == 4 and npc_interacted:
        transition_effect()
        current_map = maps[100]
        current_map["monsters"] = []
        player_x, player_y = 300, 300
        heart_hp = heart_max_hp
        defense_start_time = pygame.time.get_ticks()
        defense_spawn_timer = 0
        defense_active = True
        npc_interacted = False

    if current_map["id"] == 100 and defense_active:
        now = pygame.time.get_ticks()
        hx, hy = heart_pos

        # 1. ĐỒNG HỒ ĐẾM NGƯỢC
        remaining = max(0, (defense_duration - (now - defense_start_time)) // 1000)
        text = big_font.render(f"{remaining // 60}:{remaining % 60:02}", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH - 140, 30))

        # 2. VẼ TRÁI TIM + CẢNH BÁO MÀU KHI GẦN CHẾT
        draw_heart_defense(screen, camera_x, camera_y, heart_pos, heart_hp, heart_max_hp)

        # 3. LỌC QUÁI CHẾT
        current_map["monsters"] = [m for m in current_map["monsters"] if m["health"] > 0]

        # 4. SPAWN QUÁI (nếu dưới 12 con, mỗi 10s)
        if now - defense_spawn_timer >= 10000 and len(current_map["monsters"]) < 12:
            to_spawn = min(12 - len(current_map["monsters"]), random.randint(2, 3))
            for _ in range(to_spawn):
                tries = 0
                while tries < 10:
                    new_mon = spawn_monsters(MAP_WIDTH, MAP_HEIGHT, 1, random.randint(1, 9999), "monsters10")[0]
                    too_close = any(
                        math.hypot(m["x"] - new_mon["x"], m["y"] - new_mon["y"]) < 40
                        for m in current_map["monsters"]
                    ) or math.hypot(new_mon["x"] - hx, new_mon["y"] - hy) < 100
                    if not too_close:
                        new_mon["next_attack_time"] = now + 1000  # delay tấn công lần đầu
                        current_map["monsters"].append(new_mon)
                        break
                    tries += 1
            defense_spawn_timer = now

        # 5. AI TẤN CÔNG TRÁI TIM
        for mon in current_map["monsters"]:
            dx = hx - mon["x"]
            dy = hy - mon["y"]
            dist = math.hypot(dx, dy)
            if dist > mon.get("radius", 20):
                mon["x"] += dx / dist * mon.get("speed", 1.2)
                mon["y"] += dy / dist * mon.get("speed", 1.2)
            else:
                if now >= mon.get("next_attack_time", 0):
                    heart_hp -= mon.get("attack_damage", 5)
                    mon["next_attack_time"] = now + 2000  # delay 2s giữa mỗi lần đánh

        # 6. THẮNG / THUA
        if heart_hp <= 0 or remaining == 0:
            transition_effect()
            current_map = maps[4]
            player_x, player_y = 400, 400
            defense_active = False

    if current_map["id"] == 99 and dungeon_active:
        now = pygame.time.get_ticks()

        # 1) Thoát dungeon nếu hết giờ và boss đã chết
        if now - dungeon_start_time >= dungeon_duration_ms:
            if not any(m.get("boss") for m in current_map["monsters"]):
                player_x = current_map["width"] // 2
                player_y = current_map["height"] // 2
                exit_dungeon()
            else:
                warn = unable_exit_font.render(
                    " ",
                    True, (255, 80, 80)
                )
                warn_rect = warn.get_rect(
                    center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.2))
                )
                screen.blit(warn, warn_rect)

        # 2) Spawn 2–3 quái mỗi 4.5s, max 12
        if len(current_map["monsters"]) < 12 and now - spawn_timer >= 4500:
            for _ in range(random.randint(2, 3)):
                mon_type = random.choice(["monsters7", "monsters8", "monsters9"])
                mon = spawn_monsters(
                    MAP_WIDTH, MAP_HEIGHT, 1,
                    random.randint(1, 9999),
                    mon_type
                )[0]
                current_map["monsters"].append(mon)
            spawn_timer = now

        # 3) Spawn boss đúng 1 lần sau 2 phút
        if not boss_spawned and now - dungeon_start_time >= 120000:
            boss = spawn_monsters(
                MAP_WIDTH, MAP_HEIGHT, 1,
                99999, "monsters6"
            )[0]
            boss["health"]        *= 3
            boss["attack_damage"] *= 2
            boss["boss"] = True
            current_map["monsters"].append(boss)
            boss_spawned = True

        # 4) Đồng hồ đếm ngược
        remaining = max(
            0,
            (dungeon_duration_ms - (now - dungeon_start_time)) // 1000
        )
        text = big_font.render(
            f"{remaining // 60}:{remaining % 60:02}",
            True, (255, 255, 255)
        )
        text_rect = text.get_rect()
        text_rect.topright = (
            SCREEN_WIDTH - int(SCREEN_WIDTH * 0.05),
            int(SCREEN_HEIGHT * 0.04)
        )
        screen.blit(text, text_rect)

        # 5) Cảnh báo sụp đổ khi còn 30s (chớp 1s/lần)
        if remaining <= 30 and remaining % 2 == 0:
            warn = warning_font.render(" ", True, (255, 50, 50))
            warn_rect = warn.get_rect(
                center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.15))
            )
            screen.blit(warn, warn_rect)

        # 6) Rung màn hình khi có boss
        if any(mon.get("boss") for mon in current_map["monsters"]):
            if now % 200 < 100:
                camera_x += random.randint(-3, 3)
                camera_y += random.randint(-3, 3)

        # 7) Chết là thua
        if player_health <= 0:
            restart_game()
            exit_dungeon()
           

    # --- Vẽ người chơi ---
    if Knight == 1:
        draw_player(player_x, player_y, player_radius, camera_x, camera_y)
        draw_knight_shield(screen, player_x, player_y, player_radius, camera_x, camera_y, is_shield_active)
    if Archer == 1:
        draw_player2(player_x, player_y, player_radius, camera_x, camera_y)
    if Wizard == 1:
        update_and_draw_lightning_ring(player_x, player_y, current_map, screen, camera_x, camera_y, damage_texts, handle_monster_death)
        draw_player3(player_x, player_y, player_radius, camera_x, camera_y)
  	
    if in_lake:
        screen.set_clip(old_clip)
        
    update_npcs()
    draw_npcs(camera_x, camera_y)
    if Wizard == 1:
        for exp in wizard_skill2_explosions:
            exp.draw(screen, camera_x, camera_y)
            
    update_monsters(current_map)
    draw_monsters(current_map, screen, camera_x, camera_y)
            
    for tree in current_map.get("acacia", []):
    	draw_acacia_tree(tree, camera_x, camera_y, screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    
    for pine in sorted(current_map.get("pine_trees", []), key=lambda t: t["y"]):

    	draw_pine_tree(pine, camera_x, camera_y, screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    	
    for house in current_map.get("houses", []):
    	draw_house(house, camera_x, camera_y, screen)
    	
    for tree in current_map.get("trees", []):
    	if abs(tree["x"] - camera_x) < SCREEN_WIDTH + 100 and abs(tree["y"] - camera_y) < SCREEN_HEIGHT + 100:
    		draw_tree(tree, camera_x, camera_y, screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    		
    for blackhole in current_map.get("blackholes", []):
    	draw_blackhole(blackhole, camera_x, camera_y, screen)
       
    for portal in current_map.get("portals", []):
        if current_map["id"] == 6:
        	draw_rope_portal(portal, camera_x, camera_y, screen)
        	continue  # tránh vẽ thêm
        if portal["target"] == -999:
        	draw_portal_dungeon(portal, camera_x, camera_y, screen)
        else:
        	draw_portal(portal, camera_x, camera_y, screen)
    pygame.draw.circle(screen, (50, 50, 50), (joystick_x, joystick_y), joystick_radius)
    pygame.draw.circle(screen, WHITE, (joystick_x, joystick_y), joystick_radius, 5)
    inner_pos = (int(joystick_x + joystick_offset_x), int(joystick_y + joystick_offset_y))
    
    for i, popup in enumerate(exp_popups[:]):
        if popup.is_expired():
        	exp_popups.remove(popup)
        	continue
        surface = popup.get_surface(exp_font)
        x = 10  # gần sát lề trái
        total_height = len(exp_popups) * 30
        y = (MAP_HEIGHT - total_height) // 2 -700+ i * 30
        screen.blit(surface, (x, y))

    def draw_map_name():
    	elapsed = time.time() - map_change_time
    	if elapsed < MAP_NAME_DURATION:
    	   alpha = max(0, int(255 * (1 - elapsed / MAP_NAME_DURATION)))
    	   text_surface = map_title_font.render(map_name, True, (255, 255, 255))
    	   text_surface.set_alpha(alpha)
    	   text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 7))
    	   screen.blit(text_surface, text_rect)
    joystick()

    update_attack_effects()

    if Archer == 1 and time.time() < archer_speed_boost_until:
    	glow_surf = pygame.Surface((player_radius * 4, player_radius * 4), pygame.SRCALPHA)
    	pygame.draw.circle(glow_surf, (50, 150, 255, 100), (player_radius * 2, player_radius * 2), player_radius * 2)
    	screen.blit(glow_surf, (player_x - player_radius * 2 - camera_x, player_y - player_radius * 2 - camera_y))
    	
    now = pygame.time.get_ticks()
    if now - last_combat_time > 8000:
        if player_health < player_max_health:
            glow_surf = pygame.Surface((player_radius * 4, player_radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (0, 255, 0, 80), (player_radius * 2, player_radius * 2), player_radius * 2)
            screen.blit(glow_surf, (player_x - player_radius * 2 - camera_x, player_y - player_radius * 2 - camera_y))
        if now % 1000 < clock.get_time():
            player_health += 3
        if player_health > player_max_health:
            player_health = player_max_health
            
        ship = current_map.get("ship_portal")
        
        if ship:
        	draw_ship(ship["x"], ship["y"], camera_x, camera_y)
    for exp in explosions[:]:
    	exp.update()
    	exp.draw(screen, camera_x, camera_y)
    	if exp.is_done():
    		explosions.remove(exp)
    draw_attack_effects(camera_x, camera_y)
    update_and_draw_projectiles(current_map, damage_texts, camera_x, camera_y, screen, handle_monster_death)
    current_time = pygame.time.get_ticks()
    
    draw_skill_button(screen, skill_button_center, skill_button_radius, skill_cooldown, skill_max_cooldown)
    draw_skill2_button(screen, skill2_button_center, skill2_button_radius, skill2_cooldown, skill2_max_cooldown)
    draw_skill3_button(screen, skill3_button_center, skill3_button_radius, skill3_cooldown, skill3_max_cooldown)
    update_and_draw_level_up_effects(camera_x, camera_y)
    ms()
    draw_map_name()
    update_skill3(current_map, damage_texts, handle_monster_death, DamageText, RED)
    
    for exp in wizard_skill2_explosions[:]:
    	exp.draw(screen, camera_x, camera_y)
    	exp.update()
    	if exp.is_done():
    		wizard_skill2_explosions.remove(exp)

    draw_skill3_effect(camera_x, camera_y, screen)
    update_and_draw_skill_arrows(current_map, damage_texts, camera_x, camera_y, screen, handle_monster_death)
    update_and_draw_magic_bolts(current_map, damage_texts, camera_x, camera_y, screen, handle_monster_death)

    for effect in effects_list[:]:
        if effect["type"] == "slash_ring":
            t = pygame.time.get_ticks() - effect["start_time"]
            if t > effect["duration"]:
                effects_list.remove(effect)
                continue

            ratio = t / effect["duration"]
            r = int(effect["radius"] * ratio)
            alpha = 255 - int(ratio * 255)
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 200, 100, alpha), (r, r), r, 3)
            screen.blit(s, (int(effect["x"] - r - camera_x), int(effect["y"] - r - camera_y)))

    base_color = (70, 70, 70)
    shadow_color = (30, 30, 30)
    border_color = (160, 160, 160)
    text_color = WHITE

    shadow_offset = 4
    shadow_rect = backpack_btn.copy()
    shadow_rect.topleft = (btn_x + shadow_offset, btn_y + shadow_offset)
    pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=8)

    pygame.draw.rect(screen, border_color, backpack_btn.inflate(4, 4), border_radius=10)
    pygame.draw.rect(screen, base_color, backpack_btn, border_radius=8)

    balo_text = font.render("Balo", True, text_color)
    screen.blit(balo_text, balo_text.get_rect(center=backpack_btn.center))
    if rain_active:
    	draw_rain(screen, rain_drops, camera_x, camera_y)
    potion_button_radius = int(SCREEN_HEIGHT * 0.05)

    potion_button_center = (int(SCREEN_WIDTH * 0.92), int(SCREEN_HEIGHT * 0.57))
    potion_button = pygame.Rect(0, 0, potion_button_radius * 2, potion_button_radius * 2)
    potion_button.center = potion_button_center

    pygame.draw.circle(screen, (255, 255, 255), potion_button_center, potion_button_radius + 4)  # viền ngoài trắng
    pygame.draw.circle(screen, (200, 0, 200), potion_button_center, potion_button_radius)   
    text = font.render("HP", True, (255, 255, 255))
    screen.blit(text, (potion_button_center[0] - 20, potion_button_center[1] - 10))
    count_text = font.render(str(player_potion), True, (255, 255, 0))
    screen.blit(count_text, (potion_button_center[0] - 10, potion_button_center[1] - 40))
    
    attack()
    text = font.render("", True, (255, 215, 0))
    rect = text.get_rect(center=attack_button_center)
    screen.blit(text, (rect.x - 2, rect.y - 2))
    screen.blit(font.render("", True, WHITE), rect)
    pygame.draw.circle(screen, (30, 30, 100), (level_circle_x + 3, level_circle_y + 3), level_circle_radius)
    pygame.draw.circle(screen, (100, 100, 255), (level_circle_x, level_circle_y), level_circle_radius)
    pygame.draw.circle(screen, WHITE, (level_circle_x, level_circle_y), level_circle_radius, 4)

    small_r = level_circle_radius * 0.5
    if Knight:
        draw_player(player_x, player_y, small_r, player_x - level_circle_x, player_y - level_circle_y)
    elif Archer:
        draw_player2(player_x, player_y, small_r, player_x - level_circle_x, player_y - level_circle_y)
    elif Wizard:
    	draw_player3(player_x, player_y, small_r, player_x - level_circle_x, player_y - level_circle_y)

    rect_w = int(level_circle_radius * 1.4)
    rect_h = int(level_circle_radius * 0.4)
    rect_x = level_circle_x - rect_w // 2
    rect_y = level_circle_y + level_circle_radius - rect_h // 2 - 4

    pygame.draw.rect(screen, (50, 70, 120), (rect_x + 2, rect_y + 2, rect_w, rect_h), border_radius=8)
    pygame.draw.rect(screen, (80, 130, 200), (rect_x, rect_y, rect_w, rect_h), border_radius=8)
    pygame.draw.rect(screen, WHITE, (rect_x, rect_y, rect_w, rect_h), 2, border_radius=8)

    level_text = level_font.render(f"Lv {player_level}", True, WHITE)
    level_text_rect = level_text.get_rect(center=(level_circle_x, rect_y + rect_h // 2))
    screen.blit(level_text, level_text_rect)

    def lerp(current, target, speed=0.1):
        return current + (target - current) * speed

    def color_lerp(ratio):
        ratio = max(0, min(1, ratio))
        if ratio > 0.5:
            t = (ratio - 0.5) * 2
            return (int(255 * (1 - t)), 220, 0)
        else:
            t = ratio * 2
            return (255, int(220 * t), 0)

    if "hp_disp" not in globals():
        hp_disp = player_health
        exp_disp = player_exp

    hp_disp = lerp(hp_disp, player_health)
    exp_disp = lerp(exp_disp, player_exp)

    # === VỊ TRÍ THANH HP & EXP ===
    hp_bar_w, hp_bar_h = int(SCREEN_WIDTH * 0.25), int(SCREEN_HEIGHT * 0.05)
    hp_bar_x, hp_bar_y = level_circle_x + level_circle_radius + 10, level_circle_y - hp_bar_h
    exp_bar_w, exp_bar_h = hp_bar_w, int(SCREEN_HEIGHT * 0.04)
    exp_bar_x, exp_bar_y = hp_bar_x, level_circle_y + 10

    # === THANH MÁU ===
    hp_ratio = hp_disp / player_max_health
    hp_color = color_lerp(hp_ratio)

    pygame.draw.rect(screen, (20, 20, 20), (hp_bar_x + 2, hp_bar_y + 2, hp_bar_w, hp_bar_h), border_radius=6)
    pygame.draw.rect(screen, (100, 0, 0), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), border_radius=6)
    pygame.draw.rect(screen, hp_color, (hp_bar_x, hp_bar_y, int(hp_bar_w * hp_ratio), hp_bar_h), border_radius=6)

    hp_text = font.render(f"HP: {int(hp_disp)}/{player_max_health}", True, WHITE)
    screen.blit(hp_text, (hp_bar_x + 8, hp_bar_y + 6))

    # === THANH EXP ===
    exp_ratio = exp_disp / exp_to_next

    pygame.draw.rect(screen, (20, 20, 20), (exp_bar_x + 2, exp_bar_y + 2, exp_bar_w, exp_bar_h), border_radius=6)
    pygame.draw.rect(screen, (60, 60, 120), (exp_bar_x, exp_bar_y, exp_bar_w, exp_bar_h), border_radius=6)
    pygame.draw.rect(screen, (0, 160, 255), (exp_bar_x, exp_bar_y, int(exp_bar_w * exp_ratio), exp_bar_h), border_radius=6)

    exp_text = font.render(f"EXP: {int(exp_disp)}/{exp_to_next}", True, WHITE)
    screen.blit(exp_text, (exp_bar_x + 8, exp_bar_y + 4))
    if show_inventory:
    	draw_inventory()
    settings_btn_rect = draw_settings_button()
    if show_settings_menu:
    	menu_rect, menu_btn_rects, vol_dec_rect, vol_inc_rect = draw_settings_menu()
    update_and_draw_monster_death_effects(camera_x, camera_y, screen)
    update_and_draw_healing_effects(camera_x, camera_y, screen)
    if show_inventory:
        draw_inventory()

    if Wizard == 1:
        for exp in wizard_skill2_explosions[:]:
            if exp.should_damage():
                for m in current_map["monsters"][:]:
                    if math.hypot(m["x"] - exp.x, m["y"] - exp.y) <= exp.max_r:
                        m["health"] -= exp.damage
                        damage_texts.append(DamageText(m["x"], m["y"] - 60, exp.damage, RED))
                        if m["health"] <= 0:
                            handle_monster_death(m)
                            current_map["monsters"].remove(m)
                exp.mark_damaged()
            exp.update()
            if exp.is_done():
                wizard_skill2_explosions.remove(exp)
    if show_stat_popup:
        close_stat_btn, hp_plus_btn, dmg_plus_btn = draw_stat_popup(screen, SCREEN_WIDTH, SCREEN_HEIGHT, player_max_health, player_attack_damage, unspent_points, stat_title_font, stat_label_font, stat_value_font)
    if show_npc_popup:
        draw_npc_popup()
    if time.time() - last_autosave_time >= AUTOSAVE_INTERVAL:
    	save_current_character()
    	last_autosave_time = time.time()
    	exp_popups.append(ExpPopup("Auto-saved"))
    pygame.display.flip()
    clock.tick(60)
    
save_current_character()
pygame.quit()