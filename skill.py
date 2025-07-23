import math, pygame, os, time, random
RED = (255, 0, 0)

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
archer_projectiles = []

def shoot_arrow(x1, y1, x2, y2, damage, pierce=False):
    angle = math.atan2(y2 - y1, x2 - x1)
    speed = 30
    archer_projectiles.append({
        "x": x1,
        "y": y1,
        "vx": math.cos(angle) * speed,
        "vy": math.sin(angle) * speed,
        "radius": 10,
        "damage": damage,
        "color": (255, 200, 100),
        "life": 20,
        "pierce": pierce
    })

projectile_glow_cache = {}

def get_projectile_glow(radius, color):
    key = (radius, color)
    if key not in projectile_glow_cache:
        surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        center = radius * 2
        pygame.draw.circle(surf, (*color, 32), (center, center), radius + 6)
        pygame.draw.circle(surf, (*color, 64), (center, center), radius + 3)
        pygame.draw.circle(surf, (*color, 128), (center, center), radius)
        projectile_glow_cache[key] = surf
    return projectile_glow_cache[key]

def update_and_draw_projectiles(current_map, damage_texts, camera_x, camera_y, screen, handle_monster_death):
    global archer_projectiles
    updated_projectiles = []

    for proj in archer_projectiles:
        proj["x"] += proj["vx"]
        proj["y"] += proj["vy"]
        proj["life"] -= 1
        hit = False

        # Kiểm tra va chạm với quái
        for i in range(len(current_map["monsters"]) - 1, -1, -1):
            mon = current_map["monsters"][i]
            dx = mon["x"] - proj["x"]
            dy = mon["y"] - proj["y"]
            if dx * dx + dy * dy <= (proj["radius"] + mon["radius"]) ** 2:
                mon["health"] -= proj["damage"]
                damage_texts.append(DamageText(mon["x"], mon["y"] - 60, str(proj["damage"]), RED))
                if mon["health"] <= 0:
                    handle_monster_death(mon)
                    del current_map["monsters"][i]
                if not proj.get("pierce", False):
                    hit = True
                break

        if proj["life"] > 0 and not hit:
            updated_projectiles.append(proj)

        # Vẽ đạn với hiệu ứng phát sáng
        px = int(proj["x"] - camera_x)
        py = int(proj["y"] - camera_y)
        glow = get_projectile_glow(proj["radius"], proj["color"])
        rect = glow.get_rect(center=(px, py))
        screen.blit(glow, rect)

    archer_projectiles = updated_projectiles

skill_arrows = []

def shoot_skill_arrow(x1, y1, x2, y2, damage):
    angle = math.atan2(y2 - y1, x2 - x1)
    speed = 40
    skill_arrows.append({
        "x": x1,
        "y": y1,
        "vx": math.cos(angle) * speed,
        "vy": math.sin(angle) * speed,
        "width": 30,
        "height": 12,
        "damage": damage,
        "color": (50, 200, 255),
        "life": 30,
        "angle": angle,
        "pierce": True
    })

skill_arrow_glow_cache = {}

def get_arrow_surface(width, height, color):
    key = (width, height, color)
    if key in skill_arrow_glow_cache:
        return skill_arrow_glow_cache[key]

    surf = pygame.Surface((width * 2, height * 2), pygame.SRCALPHA)
    center = (width, height)
    # Mũi tên hình tam giác nhọn
    points = [
        (width * 2, height),
        (0, 0),
        (0, height * 2),
    ]
    pygame.draw.polygon(surf, (*color, 50), points)
    pygame.draw.polygon(surf, (*color, 100), points, width=1)
    pygame.draw.polygon(surf, (*color, 200), points, width=0)

    skill_arrow_glow_cache[key] = surf
    return surf

def update_and_draw_skill_arrows(current_map, damage_texts, camera_x, camera_y, screen, handle_monster_death):
    global skill_arrows
    updated_arrows = []

    for arrow in skill_arrows:
        arrow["x"] += arrow["vx"]
        arrow["y"] += arrow["vy"]
        arrow["life"] -= 1
        hit = False

        for i in range(len(current_map["monsters"]) - 1, -1, -1):
            mon = current_map["monsters"][i]
            if math.hypot(mon["x"] - arrow["x"], mon["y"] - arrow["y"]) <= max(arrow["width"], arrow["height"]):
                mon["health"] -= arrow["damage"]
                damage_texts.append(DamageText(mon["x"], mon["y"] - 60, str(arrow["damage"]), RED))
                if mon["health"] <= 0:
                    handle_monster_death(mon)
                    del current_map["monsters"][i]
                if not arrow.get("pierce", False):
                    hit = True
                break

        if arrow["life"] > 0 and not hit:
            updated_arrows.append(arrow)

        # Vẽ mũi tên xoay góc + glow
        base_surf = get_arrow_surface(arrow["width"], arrow["height"], arrow["color"])
        rotated = pygame.transform.rotate(base_surf, -math.degrees(arrow["angle"]))
        rect = rotated.get_rect(center=(arrow["x"] - camera_x, arrow["y"] - camera_y))
        screen.blit(rotated, rect)

    skill_arrows = updated_arrows

def use_archer_skill2(current_map, player_x, player_y, player_attack_range, player_attack_damage, skill2_max_cooldown, damage_texts, handle_monster_death, RED, effects_list):
    spin_range = 120  # tầm đánh riêng biệt
    spin_damage = int(player_attack_damage * 1.8)

    now = pygame.time.get_ticks()

    # Thêm hiệu ứng mạnh mẽ hơn (nhiều vòng xoáy)
    for i in range(3):
        effects_list.append({
            "type": "slash_ring",
            "x": player_x,
            "y": player_y,
            "radius": spin_range + i * 8,
            "start_time": now,
            "duration": 350 + i * 30
        })

    # Gây sát thương và choáng
    for mon in current_map["monsters"][:]:
        dx = mon["x"] - player_x
        dy = mon["y"] - player_y
        dist = math.hypot(dx, dy)

        if dist <= spin_range + mon["radius"]:
            mon["health"] -= spin_damage
            mon["stunned_until"] = now + 700  # choáng 0.7 giây
            damage_texts.append(DamageText(mon["x"], mon["y"] - 60, str(spin_damage), RED))
            if mon["health"] <= 0:
                handle_monster_death(mon)
                current_map["monsters"].remove(mon)

    return skill3_max_cooldown

skill3_blades = []

def use_knight_skill3(player_x, player_y, player_attack_damage, skill2_max_cooldown):
    global skill3_blades
    for _ in range(15):
        fx = player_x + random.randint(-160, 160)
        fy = player_y - 90 + random.randint(-120, 60)

        skill3_blades.append({
            "x": fx,
            "y": fy,
            "speed": 14,
            "damage": int(player_attack_damage * 1.0)
        })

    return skill2_max_cooldown

def update_skill3(current_map, damage_texts, handle_monster_death, DamageText, RED):
    global skill3_blades
    new_blades = []

    for b in skill3_blades:
        b["y"] += b["speed"]

        hit = False
        for mon in current_map["monsters"][:]:
            if math.hypot(mon["x"] - b["x"], mon["y"] - b["y"]) < mon["radius"] + 5:
                mon["health"] -= b["damage"]
                damage_texts.append(DamageText(mon["x"], mon["y"] - 60, str(b["damage"]), RED))
                if mon["health"] <= 0:
                    handle_monster_death(mon)
                    current_map["monsters"].remove(mon)
                hit = True
                break

        if not hit:
            new_blades.append(b)

    skill3_blades = new_blades

skill3_blade_surface = None

def create_skill3_blade_surface():
    surf = pygame.Surface((6, 24), pygame.SRCALPHA)
    pygame.draw.line(surf, (180, 180, 255, 100), (3, 0), (3, 24), 6)  # glow mờ
    pygame.draw.line(surf, (220, 220, 255, 255), (3, 4), (3, 20), 2)  # lõi sáng
    return surf

def draw_skill3_effect(camera_x, camera_y, screen):
    global skill3_blade_surface
    if not skill3_blade_surface:
        skill3_blade_surface = create_skill3_blade_surface()

    for b in skill3_blades:
        angle_deg = (pygame.time.get_ticks() // 5) % 360  # góc xoay động
        rotated = pygame.transform.rotate(skill3_blade_surface, angle_deg)
        rect = rotated.get_rect(center=(int(b["x"] - camera_x), int(b["y"] - camera_y)))
        screen.blit(rotated, rect)

shield_active_until = 0
shield_duration = 10000 # ~3 giây (60 FPS * 3)

def use_knight_skill2(current_time, skill2_max_cooldown):
    global shield_active_until
    shield_active_until = current_time + shield_duration
    return skill2_max_cooldown

def is_shield_active():
    return pygame.time.get_ticks() < shield_active_until

ORANGE = (255, 165, 0)

def use_knight_skill(current_map, player_x, player_y, player_radius, player_attack_range, player_attack_damage,
                     player_health, damage_texts, handle_monster_death, skill_max_cooldown, add_attack_effect):
    add_attack_effect(player_x, player_y, player_radius, player_attack_range * 1.5, ORANGE, 25)

    for i in range(len(current_map["monsters"]) - 1, -1, -1):
        mon = current_map["monsters"][i]
        if math.hypot(mon["x"] - player_x, mon["y"] - player_y) <= player_attack_range * 1.5 + mon["radius"]:
            mon["health"] -= player_attack_damage * 2
            heal = player_attack_damage // 2
            player_health += heal

            damage_texts.append(DamageText(mon["x"], mon["y"] - 60, str(int(player_attack_damage * 2)), RED))
            damage_texts.append(DamageText(player_x, player_y - 80, f"+{heal}", (100, 255, 100)))

            if mon["health"] <= 0:
                handle_monster_death(mon)
                del current_map["monsters"][i]

    return skill_max_cooldown, player_health

def use_archer_skill(current_map, player_x, player_y, player_attack_range, player_attack_damage,
                     skill_max_cooldown, shoot_skill_arrow):
    nearest = None
    min_dist = float('inf')
    for mon in current_map["monsters"]:
        dist = math.hypot(mon["x"] - player_x, mon["y"] - player_y)
        if dist < min_dist and dist <= player_attack_range + mon["radius"]:
            nearest = mon
            min_dist = dist

    if nearest:
        shoot_skill_arrow(player_x, player_y, nearest["x"], nearest["y"], int(player_attack_damage * 1.8))

    return skill_max_cooldown
    
# ——— Wizard Skill Module ———

skill3_max_cooldown = 300
skill2_max_cooldown = 240
skill1_max_cooldown = 120

wizard_skill1_projectiles = []

def shoot_magic_bolt(x1, y1, x2, y2, damage, split=False):
    angle = math.atan2(y2 - y1, x2 - x1)  # <- đúng rồi
    speed = 35
    wizard_skill1_projectiles.append({
        "x": x1, "y": y1,
        "vx": math.cos(angle) * speed,
        "vy": math.sin(angle) * speed,
        "radius": 8 if not split else 5,
        "damage": damage if not split else damage // 2,
        "color": (150, 50, 250) if not split else (100, 255, 200),
        "life": 25,
        "pierce": False,
        "split": split
    })

def update_and_draw_magic_bolts(current_map, damage_texts, camera_x, camera_y, screen, handle_monster_death):
    global wizard_skill1_projectiles
    new_list = []

    for p in wizard_skill1_projectiles:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1
        hit = False

        for i in range(len(current_map["monsters"]) - 1, -1, -1):
            m = current_map["monsters"][i]
            if math.hypot(m["x"] - p["x"], m["y"] - p["y"]) <= p["radius"] + m["radius"]:
                m["health"] -= p["damage"]
                damage_texts.append(DamageText(m["x"], m["y"] - 60, p["damage"], RED))
                if m["health"] <= 0:
                    handle_monster_death(m)
                    del current_map["monsters"][i]

                if not p.get("split", False):
                    angle = math.atan2(p["vy"], p["vx"])
                    for offset in [-0.4, 0.4]:
                        new_angle = angle + offset
                        target_x = p["x"] + math.cos(new_angle) * 50
                        target_y = p["y"] + math.sin(new_angle) * 50
                        shoot_magic_bolt(p["x"], p["y"], target_x, target_y, p["damage"], split=True)

                hit = True
                break

        if p["life"] > 0 and not hit:
            new_list.append(p)
            px, py = int(p["x"] - camera_x), int(p["y"] - camera_y)

            # Vẽ glow mờ đẹp
            glow_radius = p["radius"] * 3
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            glow_color = (*p["color"], 80)
            pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (px - glow_radius + p["radius"], py - glow_radius + p["radius"]))

            # Vẽ đạn phép chính giữa
            pygame.draw.circle(screen, p["color"], (px, py), p["radius"])
            pygame.draw.circle(screen, (255, 255, 255), (px, py), p["radius"], 1)  # viền sáng nhẹ

    wizard_skill1_projectiles = new_list

def use_wizard_skill1(player_x, player_y, player_attack_damage,
                      current_map, damage_texts, handle_monster_death, camera_x, camera_y, screen):

    # Tìm quái gần nhất trong tầm
    nearest, min_dist = None, float('inf')
    for m in current_map["monsters"]:
        d = math.hypot(m["x"] - player_x, m["y"] - player_y)
        if d < min_dist and d <= 200 + m["radius"]:  # tầm bắn skill1
            nearest, min_dist = m, d

    # Nếu có quái, bắn về nó
    if nearest:
        shoot_magic_bolt(player_x, player_y, nearest["x"], nearest["y"], player_attack_damage)

    # Cập nhật + vẽ đạn phép
    update_and_draw_magic_bolts(current_map, damage_texts, camera_x, camera_y, screen, handle_monster_death)

    return skill1_max_cooldown


# Skill 2: Arcane Explosion
wizard_skill2_explosions = []

class ArcaneExplosion:
    def __init__(self, x, y, max_r=80, duration=300, damage=0):
        self.x = x
        self.y = y
        self.max_r = max_r
        self.duration = duration
        self.damage = damage
        self.counter = 0
        self.tick_interval = 30
        self.last_tick = -30

        self.pre_scaled_surfaces = self.create_pre_scaled_effects()

    def create_base_surface(self, r):
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        center = r
        pygame.draw.circle(surf, (150, 100, 255, 40), (center, center), int(r * 0.95))
        pygame.draw.circle(surf, (180, 130, 255, 90), (center, center), int(r * 0.6))
        pygame.draw.circle(surf, (230, 200, 255, 200), (center, center), int(r * 0.3))
        return surf

    def create_pre_scaled_effects(self):
        base = self.create_base_surface(self.max_r)
        scaled = []
        for i in range(10):  # 10 cấp độ lan rộng
            scale = 1.0 + 0.5 * (i / 9)
            size = int(self.max_r * 2 * scale)
            s = pygame.transform.scale(base, (size, size))
            scaled.append(s)
        return scaled

    def update(self):
        self.counter += 1

    def draw(self, surface, cam_x, cam_y):
        if self.counter >= self.duration:
            return

        alpha = max(0, 200 - int(200 * (self.counter / self.duration)))
        index = int(9 * self.counter / self.duration)
        surf = self.pre_scaled_surfaces[min(index, 9)].copy()
        surf.set_alpha(alpha)

        pos_x = int(self.x - surf.get_width() // 2 - cam_x)
        pos_y = int(self.y - surf.get_height() // 2 - cam_y)

        surface.blit(surf, (pos_x, pos_y))

    def is_done(self):
        return self.counter >= self.duration

    def should_damage(self):
        return (self.counter - self.last_tick) >= self.tick_interval and self.counter % self.tick_interval == 0

    def mark_damaged(self):
        self.last_tick = self.counter
        
def use_wizard_skill2(player_x, player_y, player_attack_damage,
                      current_map, damage_texts, handle_monster_death,
                      camera_x, camera_y, screen, explosions_list):

    nearest, md = None, float('inf')
    for m in current_map["monsters"]:
        d = math.hypot(m["x"] - player_x, m["y"] - player_y)
        if d < md and d <= 200 + m["radius"]:
            nearest, md = m, d

    if nearest:
        dmg = int(player_attack_damage * 1.2)
        exp = ArcaneExplosion(nearest["x"], nearest["y"], max_r=80, duration=300, damage=dmg)
        explosions_list.append(exp)

    for exp in explosions_list[:]:
        exp.draw(screen, camera_x, camera_y)
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
            explosions_list.remove(exp)

    return skill2_max_cooldown

# Skill 3: Homing Seeker
thunder_ring_active = False
thunder_ring_start = 0
thunder_ring_duration = 5000
thunder_orbs = []

def use_wizard_skill3(player_x, player_y, player_attack_damage, current_time, skill3_max_cooldown):
    global thunder_ring_active, thunder_ring_start, thunder_orbs
    thunder_ring_active = True
    thunder_ring_start = current_time
    thunder_orbs = []

    orb_count = 6
    for i in range(orb_count):
        angle = (2 * math.pi / orb_count) * i
        thunder_orbs.append({
            "angle": angle,
            "radius": 80,
            "damage": player_attack_damage//2,
            "last_hit": {},
        })

    return skill3_max_cooldown
    
def create_lightning_orb_surface():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    center = 20
    pygame.draw.circle(surf, (255, 255, 150, 40), (center, center), 18)
    pygame.draw.circle(surf, (120, 200, 255, 80), (center, center), 12)
    pygame.draw.circle(surf, (200, 240, 255, 255), (center, center), 6)
    return surf

lightning_orb_surface = create_lightning_orb_surface()

def update_and_draw_lightning_ring(player_x, player_y, current_map, screen, camera_x, camera_y, damage_texts, handle_monster_death):
    global thunder_ring_active

    if not thunder_ring_active:
        return

    now = pygame.time.get_ticks()
    if now - thunder_ring_start > thunder_ring_duration:
        thunder_ring_active = False
        return

    for orb in thunder_orbs:
        orb["angle"] += 0.05  # quay đều
        ox = player_x + math.cos(orb["angle"]) * orb["radius"]
        oy = player_y + math.sin(orb["angle"]) * orb["radius"]

        # Vẽ orb bằng surface hiệu ứng
        screen.blit(lightning_orb_surface, lightning_orb_surface.get_rect(center=(int(ox - camera_x), int(oy - camera_y))))

        for mon in current_map["monsters"]:
            key = id(mon)
            last = orb["last_hit"].get(key, 0)
            if now - last < 500:
                continue
            if math.hypot(mon["x"] - ox, mon["y"] - oy) <= mon["radius"] + 10:
                mon["health"] -= orb["damage"]
                orb["last_hit"][key] = now
                damage_texts.append(DamageText(mon["x"], mon["y"] - 60, str(orb["damage"]), (100, 200, 255)))
                if mon["health"] <= 0:
                    handle_monster_death(mon)