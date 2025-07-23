import pygame, math

triangle_cache = {}

def curved_triangle_points(left, top, right, depth=8, steps=4):
    lx, ly = left
    rx, ry = right
    dx = rx - lx
    dy = ry - ly
    inv_steps = 1 / steps
    points = [left]
    append = points.append
    for i in range(steps + 1):
        t = i * inv_steps
        mt = 1 - t
        y_offset = depth * 4 * t * mt
        # dùng int thay cho round để nhanh hơn
        append((
            int(lx + t * dx),
            int(ly + t * dy + y_offset)
        ))
    points.append(top)
    return points

def get_cached_triangle(left, top, right, depth):
    # thay round(x, 1) bằng int(x * 10) để tăng tốc cache key
    key = (
        int(left[0] * 10), int(left[1] * 10),
        int(top[0] * 10), int(top[1] * 10),
        int(right[0] * 10), int(right[1] * 10),
        int(depth * 10)
    )
    val = triangle_cache.get(key)
    if val is None:
        val = curved_triangle_points(left, top, right, depth)
        triangle_cache[key] = val
    return val

def draw_pine_tree(t, cx, cy, screen, SCREEN_WIDTH, SCREEN_HEIGHT):
    tx = t["x"] - cx
    ty = t["y"] - cy
    r = t["canopy_radius"]
    trunk_h = t["trunk_height"]
    trunk_w = t["trunk_width"]
    tx_trunk = tx + trunk_w // 2

    if tx + r < -50 or tx - r > SCREEN_WIDTH + 50 or ty - trunk_h - r > SCREEN_HEIGHT + 50 or ty < -50:
        return

    draw_poly = pygame.draw.polygon
    draw_rect = pygame.draw.rect
    color_fill = (15, 65, 15)
    color_line = (10, 40, 10)
    color_trunk = (80, 50, 20)

    r7 = r * 0.7
    get_tri = get_cached_triangle

    top_base = ty - trunk_h
    for i in (2, 1, 0):
        i5 = i * 5
        top_y = top_base - r7 * (i + 1)
        left_y = top_base - r7 * i
        left_x = tx_trunk - r + i5
        right_x = tx_trunk + r - i5

        if right_x >= -50 and left_x <= SCREEN_WIDTH + 50 and -50 <= top_y <= SCREEN_HEIGHT + 50:
            pts = get_tri(
                (left_x, left_y),
                (tx_trunk, top_y),
                (right_x, left_y),
                4 + i * 2
            )
            draw_poly(screen, color_fill, pts)
            draw_poly(screen, color_line, pts, 1)

    draw_rect(screen, color_trunk, (tx, ty - trunk_h, trunk_w, trunk_h))

def draw_tree(tree, cx, cy, screen, SCREEN_WIDTH, SCREEN_HEIGHT):
    tx = tree["x"] - cx
    ty = tree["y"] - cy
    r = tree["canopy_radius"]
    if tx + r < -100 or tx - r > SCREEN_WIDTH + 100 or ty - tree["trunk_height"] - r > SCREEN_HEIGHT + 100 or ty < -100:
        return

    pygame.draw.rect(screen, (50, 30, 10), (tx + 2, ty - tree["trunk_height"] + 2, tree["trunk_width"], tree["trunk_height"]), border_radius=2)
    pygame.draw.rect(screen, (101, 67, 33), (tx, ty - tree["trunk_height"], tree["trunk_width"], tree["trunk_height"]), border_radius=2)

    cx2 = tx + tree["trunk_width"] // 2
    cy2 = ty - tree["trunk_height"] - r // 2
    leaf_color = (34, 139, 34)
    shadow_color = (20, 80, 20)

    offsets = [
        (0, 0), (-r * 0.6, -r * 0.2), (r * 0.6, -r * 0.2),
        (-r * 0.4, r * 0.4), (r * 0.4, r * 0.4), (0, -r * 0.5)
    ]

    # Vẽ bóng trước
    for ox, oy in offsets:
        px = int(cx2 + ox)
        py = int(cy2 + oy)
        if 0 <= px <= SCREEN_WIDTH and 0 <= py <= SCREEN_HEIGHT:
            pygame.draw.circle(screen, shadow_color, (px + 2, py + 2), r // 2 + 1)

    # Vẽ tán lá sau
    for ox, oy in offsets:
        px = int(cx2 + ox)
        py = int(cy2 + oy)
        if 0 <= px <= SCREEN_WIDTH and 0 <= py <= SCREEN_HEIGHT:
            pygame.draw.circle(screen, leaf_color, (px, py), r // 2)

def draw_circle(center, radius, color):
    pygame.draw.circle(pygame.display.get_surface(), color, center, radius)

def draw_rect(topleft, width, height, color):
    pygame.draw.rect(pygame.display.get_surface(), color, pygame.Rect(topleft, (width, height)))

def draw_player(x, y, radius, cx, cy):
    sx, sy = int(x - cx), int(y - cy)
    hr = int(radius * 0.8)
    bw, bh = int(radius * 1.2), int(radius * 1.6)
    lw, lh = int(radius * 0.3), int(radius * 0.8)
    oy = int(hr * 0.4)
    ex = int(hr * 0.4)
    ey = int(hr * 0.2)
    er = int(hr * 0.15)

    draw_circle((sx + 2, sy - bh // 2 + 2), hr + 1, (0, 0, 0))
    draw_circle((sx, sy - bh // 2), hr, (180, 140, 100))

    draw_rect((sx - bw // 2 - lw + 2, sy - lh // 2 + oy + 2), lw, lh, (0, 0, 0))
    draw_rect((sx - bw // 2 - lw, sy - lh // 2 + oy), lw, lh, (200, 200, 200))

    draw_rect((sx - bw // 2 + 2, sy - bh // 2 + oy + 2), bw, bh, (0, 0, 0))
    draw_rect((sx - bw // 2, sy - bh // 2 + oy), bw, bh, (200, 200, 200))

    draw_rect((sx + bw // 2 + 2, sy - lh // 2 + oy + 2), lw, lh, (0, 0, 0))
    draw_rect((sx + bw // 2, sy - lh // 2 + oy), lw, lh, (200, 200, 200))

    draw_rect((sx - lw * 3 // 2 + 1, sy + bh // 2 - lh // 2 + oy + 2), lw, lh, (0, 0, 0))
    draw_rect((sx - lw * 3 // 2, sy + bh // 2 - lh // 2 + oy), lw, lh, (100, 100, 100))

    draw_rect((sx + lw // 2 + 1, sy + bh // 2 - lh // 2 + oy + 2), lw, lh, (0, 0, 0))
    draw_rect((sx + lw // 2, sy + bh // 2 - lh // 2 + oy), lw, lh, (100, 100, 100))

    draw_circle((sx - ex + 1, sy - ey - bh // 2 + 1), er + 1, (0, 0, 0))
    draw_circle((sx + ex + 1, sy - ey - bh // 2 + 1), er + 1, (0, 0, 0))
    draw_circle((sx - ex, sy - ey - bh // 2), er, (255, 255, 255))
    draw_circle((sx + ex, sy - ey - bh // 2), er, (255, 255, 255))

def draw_player2(x, y, radius, cx, cy):
    sx, sy = int(x - cx), int(y - cy)
    hr = int(radius * 0.8)
    bw, bh = int(radius * 1.2), int(radius * 1.6)
    lw, lh = int(radius * 0.3), int(radius * 0.8)
    oy = int(hr * 0.4)
    ex = int(hr * 0.4)
    ey = int(hr * 0.2)
    er = int(hr * 0.15)

    draw_circle((sx + 2, sy - bh // 2 + 2), hr + 1, (0, 0, 0))
    draw_circle((sx, sy - bh // 2), hr, (230, 200, 170))

    pygame.draw.arc(pygame.display.get_surface(), (120, 90, 60),
        pygame.Rect(sx - hr, sy - bh // 2 - hr, hr * 2, hr * 2),
        math.pi, 2 * math.pi, int(hr * 1.2))

    draw_rect((sx - bw // 2 - lw + 2, sy - lh // 2 + oy + 2), lw, lh, (0, 0, 0))
    draw_rect((sx - bw // 2 - lw, sy - lh // 2 + oy), lw, lh, (40, 80, 160))

    draw_rect((sx - bw // 2 + 2, sy - bh // 2 + oy + 2), bw, bh, (0, 0, 0))
    draw_rect((sx - bw // 2, sy - bh // 2 + oy), bw, bh, (40, 80, 160))

    draw_rect((sx + bw // 2 + 2, sy - lh // 2 + oy + 2), lw, lh, (0, 0, 0))
    draw_rect((sx + bw // 2, sy - lh // 2 + oy), lw, lh, (40, 80, 160))

    draw_rect((sx - lw * 3 // 2 + 1, sy + bh // 2 - lh // 2 + oy + 2), lw, lh, (0, 0, 0))
    draw_rect((sx - lw * 3 // 2, sy + bh // 2 - lh // 2 + oy), lw, lh, (100, 100, 100))

    draw_rect((sx + lw // 2 + 1, sy + bh // 2 - lh // 2 + oy + 2), lw, lh, (0, 0, 0))
    draw_rect((sx + lw // 2, sy + bh // 2 - lh // 2 + oy), lw, lh, (100, 100, 100))

    draw_circle((sx - ex + 1, sy - ey - bh // 2 + 1), er + 1, (0, 0, 0))
    draw_circle((sx + ex + 1, sy - ey - bh // 2 + 1), er + 1, (0, 0, 0))
    draw_circle((sx - ex, sy - ey - bh // 2), er, (255, 255, 255))
    draw_circle((sx + ex, sy - ey - bh // 2), er, (255, 255, 255))


def draw_player3(x, y, radius, cx, cy):
    sx, sy = int(x - cx), int(y - cy)
    hr = int(radius * 0.8)
    bw, bh = int(radius * 1.2), int(radius * 2.0)
    lw, lh = int(radius * 0.25), int(radius * 0.7)
    oy = int(hr * 0.4)
    ex = int(hr * 0.4)
    ey = int(hr * 0.2)
    er = int(hr * 0.15)

    draw_circle((sx + 2, sy - bh // 2 + 2), hr + 1, (0, 0, 0))
    draw_circle((sx, sy - bh // 2), hr, (160, 120, 90))

    draw_rect((sx - bw // 2 - lw + 2, sy - lh // 2 + oy + 2), lw, lh, (0, 0, 0))
    draw_rect((sx - bw // 2 - lw, sy - lh // 2 + oy), lw, lh, (70, 70, 160))

    draw_rect((sx - bw // 2 + 2, sy - bh // 2 + oy + 2), bw, bh, (0, 0, 0))
    draw_rect((sx - bw // 2, sy - bh // 2 + oy), bw, bh, (100, 100, 200))

    draw_rect((sx + bw // 2 + 2, sy - lh // 2 + oy + 2), lw, lh, (0, 0, 0))
    draw_rect((sx + bw // 2, sy - lh // 2 + oy), lw, lh, (70, 70, 160))

    draw_rect((sx - lw * 3 // 2 + 1, sy + bh // 2 - lh // 2 + oy + 2), lw, lh, (0, 0, 0))
    draw_rect((sx - lw * 3 // 2, sy + bh // 2 - lh // 2 + oy), lw, lh, (50, 50, 50))

    draw_rect((sx + lw // 2 + 1, sy + bh // 2 - lh // 2 + oy + 2), lw, lh, (0, 0, 0))
    draw_rect((sx + lw // 2, sy + bh // 2 - lh // 2 + oy), lw, lh, (50, 50, 50))

    draw_circle((sx - ex + 1, sy - ey - bh // 2 + 1), er + 1, (0, 0, 0))
    draw_circle((sx + ex + 1, sy - ey - bh // 2 + 1), er + 1, (0, 0, 0))
    draw_circle((sx - ex, sy - ey - bh // 2), er, (255, 255, 255))
    draw_circle((sx + ex, sy - ey - bh // 2), er, (255, 255, 255))
    
def draw_guardian(x, y, radius, cx, cy):
    sx, sy = int(x - cx), int(y - cy)
    hr = int(radius * 0.8)
    bw, bh = int(radius * 1.2), int(radius * 1.6)
    lw, lh = int(radius * 0.3), int(radius * 0.8)
    oy = int(hr * 0.4)
    ex = int(hr * 0.4)
    ey = int(hr * 0.2)
    er = int(hr * 0.15)

    draw_circle((sx, sy - bh // 2), hr, (160, 130, 100))  # đầu

    draw_rect((sx - bw // 2, sy - bh // 2 + oy), bw, bh, (110, 110, 140))  # thân
    draw_rect((sx - bw // 2 - lw, sy - lh // 2 + oy), lw, lh, (110, 110, 140))  # tay trái
    draw_rect((sx + bw // 2, sy - lh // 2 + oy), lw, lh, (110, 110, 140))  # tay phải
    draw_rect((sx - lw * 3 // 2, sy + bh // 2 - lh // 2 + oy), lw, lh, (80, 80, 100))  # chân trái
    draw_rect((sx + lw // 2, sy + bh // 2 - lh // 2 + oy), lw, lh, (80, 80, 100))  # chân phải

    draw_circle((sx - ex, sy - ey - bh // 2), er, (255, 255, 255))  # mắt trái
    draw_circle((sx + ex, sy - ey - bh // 2), er, (255, 255, 255))  # mắt phải

    draw_rect((sx - hr // 2, sy - bh // 2 + hr // 2), hr, hr // 3, (240, 240, 240))  # râu giữa
    draw_rect((sx - hr // 2 - 5, sy - bh // 2 + hr // 2 + 2), hr // 4, hr // 4, (230, 230, 230))  # râu trái
    draw_rect((sx + hr // 2 + 1, sy - bh // 2 + hr // 2 + 2), hr // 4, hr // 4, (230, 230, 230))  # râu phải

WHITE = (255, 255, 255)

def draw_skill_button(screen, center, r, cd, max_cd, font=None):
    # Nếu max_cd là giá trị mặc định khi bị khóa
    required_level = None
    if max_cd == 120:
        required_level = 3
    elif max_cd == 240:
        required_level = 5
    elif max_cd == 300:
        required_level = 8

    # Nếu bị khóa thì vẽ ổ khóa
    if required_level:
        pygame.draw.circle(screen, (30, 30, 30), center, r - 4)
        lock_color = (160, 160, 160)
        x, y = center
        lw, lh = r, r // 2
        pygame.draw.rect(screen, lock_color, (x - lw // 2, y - lh // 2, lw, lh), border_radius=4)
        arc_rect = pygame.Rect(x - lw // 3, y - lh, lw * 2 // 3, lh)
        pygame.draw.arc(screen, lock_color, arc_rect, math.pi, 2 * math.pi, 4)

        # Vẽ số cấp cần
        if font:
            lvl_txt = font.render(str(required_level), True, (255, 255, 0))
            screen.blit(lvl_txt, lvl_txt.get_rect(center=center))
        return

    # Vẽ nút bình thường
    c = (80, 80, 80) if cd > 0 else (60, 220, 60)
    pygame.draw.circle(screen, c, center, r)
    pygame.draw.circle(screen, (255, 255, 255), center, r, 3)

    if cd > 0:
        ratio = 1 - cd / max_cd
        a0 = -math.pi / 2
        a1 = a0 + ratio * 2 * math.pi
        rect = pygame.Rect(0, 0, r * 2 + 4, r * 2 + 4)
        rect.center = center
        pygame.draw.arc(screen, (255, 255, 255), rect, a0, a1, 5)

def draw_skill_button(screen, center, r, cd, max_cd):
    # Màu nút: mượt hơn
    c = (80, 80, 80) if cd > 0 else (60, 220, 60)

    # Vẽ nút
    pygame.draw.circle(screen, c, center, r)
    pygame.draw.circle(screen, (255, 255, 255), center, r, 3)  # viền mảnh hơn

    # Vòng cooldown: bo tròn đẹp hơn, kích cỡ chuẩn
    if cd > 0:
        ratio = 1 - cd / max_cd
        a0 = -math.pi / 2
        a1 = a0 + ratio * 2 * math.pi
        rect = pygame.Rect(0, 0, r * 2 + 4, r * 2 + 4)
        rect.center = center
        pygame.draw.arc(screen, (255, 255, 255), rect, a0, a1, 5)  # vòng mảnh, gọn, khít

draw_skill2_button = draw_skill3_button = draw_skill_button

def draw_roads(roads, cx, cy, screen, screen_rect=None):
    # Màu định nghĩa sẵn
    main_color = (115, 82, 45)
    edge_top_left = (90, 65, 35)
    edge_bottom_right = (70, 50, 30)
    center_highlight = (130, 95, 60)

    if screen_rect is None:
        screen_rect = screen.get_rect()

    for r in roads:
        x = r["x"] - cx
        y = r["y"] - cy
        w = r["width"]
        h = r["height"]

        # Bỏ qua nếu ngoài màn hình
        if x + w < 0 or y + h < 0 or x > screen_rect.width or y > screen_rect.height:
            continue

        # Vẽ nền
        pygame.draw.rect(screen, main_color, (x, y, w, h))

        # Viền cho chiều sâu
        pygame.draw.line(screen, edge_top_left, (x, y), (x + w, y), 2)         # Top
        pygame.draw.line(screen, edge_bottom_right, (x, y + h), (x + w, y + h), 2) # Bottom
        pygame.draw.line(screen, edge_top_left, (x, y), (x, y + h), 2)         # Left
        pygame.draw.line(screen, edge_bottom_right, (x + w, y), (x + w, y + h), 2) # Right

        # Highlight ở giữa
        pygame.draw.rect(screen, center_highlight, (x + 3, y + 3, w - 6, h - 6))

def draw_portal(p, cx, cy, screen):
    x = p["x"] - cx
    y = p["y"] - cy
    w = p["width"]
    h = p["height"]
    c = (x + w // 2, y + h // 2)
    r = pygame.Rect(x, y, w, h)

    t = pygame.time.get_ticks() / 500

    # Phát sáng đơn giản
    glow = (40 + int(5 * math.sin(t)), 30, 80 + int(5 * math.cos(t)))
    pygame.draw.ellipse(screen, glow, r)

    # 2 vòng sáng ngoài
    for i in range(1, 3):
        pulsate = 2 + math.sin(t + i) * 1.2
        g = (
            100 + i * 25 + int(5 * math.sin(t + i)),
            100 + i * 15,
            255 - i * 25
        )
        gr = pygame.Rect(x - i * pulsate, y - i * pulsate, w + i * pulsate * 2, h + i * pulsate * 2)
        pygame.draw.ellipse(screen, g, gr, 1)

    # 4 hạt sáng quay
    for i in range(4):
        a = math.radians(i * 90) + t * 0.5
        rr = min(w, h) // 3 + math.sin(t + i) * 1.5
        px = int(c[0] + math.cos(a) * rr)
        py = int(c[1] + math.sin(a) * rr)
        pygame.draw.circle(screen, (180, 180, 255), (px, py), 2)

    # Đường ngang giữa
    pygame.draw.line(screen, (255, 255, 255), (x + 5, y + h // 2), (x + w - 5, y + h // 2), 1)

    # Viền chính trắng
    pygame.draw.ellipse(screen, (255, 255, 255), r, 1)
    
def draw_house(h, cx, cy, screen):
    x, y = h["x"] - cx, h["y"] - cy
    w, hgt = h["width"], h["height"]
    sw, sh = screen.get_size()

    if x + w < -50 or x > sw + 50 or y + hgt < -50 or y > sh + 50:
        return

    # Thân nhà + viền
    body = h["body_color"]
    darker = (max(0, body[0] - 20), max(0, body[1] - 20), max(0, body[2] - 20))
    pygame.draw.rect(screen, darker, (x, y, w, hgt))
    pygame.draw.rect(screen, body, (x + 2, y + 2, w - 4, hgt - 4))

    # Mái nhà
    roof = h["roof_color"]
    brighter = (min(255, roof[0] + 30), min(255, roof[1] + 30), min(255, roof[2] + 30))
    roof_pts = [(x, y), (x + w, y), (x + w / 2, y - hgt / 2)]
    pygame.draw.polygon(screen, brighter, roof_pts)
    pygame.draw.polygon(screen, roof, roof_pts, 2)

    # Cửa chính
    dw, dh = w * 0.2, hgt * 0.5
    dx, dy = x + (w - dw) / 2, y + hgt - dh
    pygame.draw.rect(screen, (50, 30, 10), (dx, dy, dw, dh))
    pygame.draw.rect(screen, h["door_color"], (dx + 2, dy + 2, dw - 4, dh - 4))

    # Cửa sổ (trái + phải)
    ww, wh = w * 0.2, hgt * 0.3
    wy = y + hgt * 0.3
    for wx in [x + w * 0.1, x + w * 0.7]:
        pygame.draw.rect(screen, (0, 0, 0), (wx, wy, ww, wh))
        pygame.draw.rect(screen, h["window_color"], (wx + 2, wy + 2, ww - 4, wh - 4))
        # Chia ô
        cx, cy = wx + 2, wy + 2
        pygame.draw.line(screen, (30, 30, 30), (cx + ww // 2, cy), (cx + ww // 2, cy + wh - 4), 1)
        pygame.draw.line(screen, (30, 30, 30), (cx, cy + wh // 2), (cx + ww - 4, cy + wh // 2), 1)

def draw_rope_portal(p, cx, cy, screen):
    x, y = p["x"] - cx, p["y"] - cy
    w, h = p["width"], p["height"]
    l = x + w // 4
    r = x + 3 * w // 4
    c = (160, 82, 45)
    pygame.draw.line(screen, c, (l, y), (l, y + h), 5)
    pygame.draw.line(screen, c, (r, y), (r, y + h), 5)
    for i in range(7):
        s = y + i * h // 6
        pygame.draw.line(screen, c, (l, s), (r, s), 3)

def draw_blackhole(bh, cx, cy, screen):
    x = bh["x"] - cx
    y = bh["y"] - cy
    w = bh["width"]
    h = int(bh["height"] * 0.4)
    for col, sc in zip(((90,90,90), (30,30,30), (0,0,0)), (1.4, 1.2, 1.0)):
        sw, sh = int(w * sc), int(h * sc)
        sx, sy = x + (w - sw) // 2, y + (h - sh) // 2
        pygame.draw.ellipse(screen, col, (sx, sy, sw, sh))

DRY_GRASS_SPRITE = None

def draw_dry_grass(grass, camera_x, camera_y, screen):
    global DRY_GRASS_SPRITE
    if DRY_GRASS_SPRITE is None:
        surf = pygame.Surface((14, 18), pygame.SRCALPHA)
        color = (230, 180, 60)
        cx, cy = 7, 17
        for i in (-3, -2, -1, 0, 1, 2, 3):
            h = 10 + (3 - abs(i))
            pygame.draw.line(surf, color, (cx, cy), (cx + i * 2, cy - h), 1)
        DRY_GRASS_SPRITE = surf

    x = grass["x"] - camera_x
    y = grass["y"] - camera_y
    if -14 < x < screen.get_width() + 14 and -18 < y < screen.get_height() + 18:
        screen.blit(DRY_GRASS_SPRITE, (x - 7, y - 18))
        
import pygame
import math
import random

def draw_acacia_tree(tree, camera_x, camera_y, screen, SCREEN_WIDTH, SCREEN_HEIGHT):
    x = tree["x"] - camera_x
    y = tree["y"] - camera_y
    tw = tree["trunk_width"]
    th = tree["trunk_height"]
    cw = tree["canopy_width"]
    ch = int(th * 1)

    if x + cw < -100 or x - cw > SCREEN_WIDTH + 100 or y - th - ch > SCREEN_HEIGHT + 100 or y < -100:
        return

    trunk_color = (100, 70, 40)
    canopy_color = (85, 107, 47)
    canopy_shadow = (60, 80, 30)
    branch_color = (80, 60, 30)
    leaf_color = (110, 130, 60)

    sin_table = [int(math.sin(i / 6 * 3) * 2) for i in range(7)]
    for i in range(6):
        pygame.draw.line(
            screen, trunk_color,
            (x + sin_table[i], y - int(th * i / 6)),
            (x + sin_table[i + 1], y - int(th * (i + 1) / 6)),
            tw
        )

    by = y - th + 5
    half = cw // 2
    pygame.draw.line(screen, branch_color, (x, by), (x - half, by - 5), 3)
    pygame.draw.line(screen, branch_color, (x, by), (x + half, by - 5), 3)

    for i in range(2):
        scale = 1 - i * 0.2
        lw = int(cw * scale)
        lh = int(ch * (0.7 + i * 0.1))
        ly = y - th - lh + i * 6
        pygame.draw.ellipse(screen, canopy_color, (x - lw // 2, ly, lw, lh))

    pygame.draw.ellipse(screen, canopy_shadow, (x - cw // 2 + 4, y - th - ch + 4, cw - 8, ch // 2))

    rng = random.Random(tree["x"] * 73856093 ^ tree["y"] * 19349663)
    half_cw = cw // 2 - 5
    for _ in range(6):
        lx = x + rng.randint(-half_cw, half_cw)
        ly = y - th - rng.randint(ch // 2, ch + 8)
        pygame.draw.circle(screen, leaf_color, (lx, ly), 2)

    pygame.draw.line(screen, trunk_color, (x - tw // 2, y), (x - tw // 2, y + 4), 2)
    pygame.draw.line(screen, trunk_color, (x + tw // 2 - 2, y), (x + tw // 2 - 2, y + 4), 2)
    
import pygame
import math

import pygame
import math

def draw_knight_shield(screen, player_x, player_y, player_radius, camera_x, camera_y, is_shield_active_func):
    if not is_shield_active_func():
        return

    px, py = int(player_x - camera_x), int(player_y - camera_y)

    # Glow nền mờ 2 lớp
    glow_radius = player_radius + 28
    glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
    for alpha, size in [(40, glow_radius), (20, glow_radius - 6)]:
        pygame.draw.circle(glow_surf, (100, 180, 255, alpha), (glow_radius, glow_radius), size)
    screen.blit(glow_surf, (px - glow_radius, py - glow_radius))

    # Viền sáng động với nhịp đập
    pulse = int((math.sin(pygame.time.get_ticks() * 0.006) + 1) * 1.5)
    border_radius = player_radius + 10 + pulse
    pygame.draw.circle(screen, (150, 220, 255), (px, py), border_radius, 3)

    # Các chấm xoay quanh
    swirl_radius = player_radius + 6
    swirl_angle = pygame.time.get_ticks() * 0.005
    for i in range(5):
        angle = swirl_angle + i * (2 * math.pi / 5)
        dot_x = int(px + math.cos(angle) * swirl_radius)
        dot_y = int(py + math.sin(angle) * swirl_radius)
        pygame.draw.circle(screen, (180, 240, 255), (dot_x, dot_y), 2)
        
import pygame
import math
import sys

def show_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, clock, WHITE, fade_into_game, character_menu):
    menu_running = True
    title_font = pygame.font.Font(None, 90)
    button_font = pygame.font.Font(None, 50)

    wave_offset = 0
    pulse = 0
    fade_alpha = 255

    title_base = title_font.render("Jaras Tale", True, WHITE)
    play_text = button_font.render("Play", True, WHITE)
    quit_text = button_font.render("Quit", True, WHITE)

    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill((0, 0, 0))

    play_rect = play_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    play_bg = play_rect.inflate(160, 60)

    quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    quit_bg = quit_rect.inflate(160, 60)

    title_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)

    while menu_running:
        screen.fill((15, 15, 35))

        wave_offset += 1.5
        for y in range(0, SCREEN_HEIGHT, 20):
            wave = int(15 * math.sin((y + wave_offset) * 0.03))
            c = 25 + (wave % 20)
            pygame.draw.line(screen, (c, c, 60 + wave % 25), (0, y + wave), (SCREEN_WIDTH, y + wave), 2)

        pulse += 0.04
        scale = 1.02 + 0.07 * math.sin(pulse)
        title_text = pygame.transform.rotozoom(title_base, 0, scale)
        title_rect = title_text.get_rect(center=title_center)

        glow = pygame.Surface(title_rect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 255, 255, 40), glow.get_rect())
        screen.blit(glow, title_rect.topleft)
        screen.blit(title_text, title_rect)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Play button
        play_hover = play_rect.collidepoint(mouse_x, mouse_y)
        play_color = (130, 180, 240) if play_hover else (100, 160, 210)
        shadow_rect = play_bg.move(4, 4)
        pygame.draw.rect(screen, (30, 30, 30), shadow_rect, border_radius=15)
        pygame.draw.rect(screen, play_color, play_bg, border_radius=15)
        pygame.draw.rect(screen, WHITE, play_bg, 2, border_radius=15)
        screen.blit(play_text, play_rect)

        # Quit button
        quit_hover = quit_rect.collidepoint(mouse_x, mouse_y)
        quit_color = (240, 120, 120) if quit_hover else (210, 80, 80)
        shadow_rect = quit_bg.move(4, 4)
        pygame.draw.rect(screen, (30, 30, 30), shadow_rect, border_radius=15)
        pygame.draw.rect(screen, quit_color, quit_bg, border_radius=15)
        pygame.draw.rect(screen, WHITE, quit_bg, 2, border_radius=15)
        screen.blit(quit_text, quit_rect)

        if fade_alpha > 0:
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))
            fade_alpha = max(0, fade_alpha - 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if play_rect.collidepoint(event.pos):
                    fade_into_game()
                    character_menu()
                    menu_running = False
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)
 
def draw_heart_defense(screen, camera_x, camera_y, heart_pos, heart_hp, heart_max_hp):
    hx, hy = heart_pos
    screen_x = hx - camera_x
    screen_y = hy - camera_y

    heart_radius = 40

    # Glow nhấp nháy
    pulse = int((math.sin(pygame.time.get_ticks() * 0.004) + 1) * 0.5 * 20)
    glow_radius = heart_radius + pulse
    glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (255, 100, 150, 80), (glow_radius, glow_radius), glow_radius)
    screen.blit(glow_surf, (screen_x - glow_radius, screen_y - glow_radius))

    # Trái tim chính
    pygame.draw.circle(screen, (255, 80, 100), (screen_x, screen_y), heart_radius)

    # Viền trắng
    pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), heart_radius, 3)

    # Thanh máu
    hp_ratio = heart_hp / heart_max_hp
    bar_w, bar_h = 120, 14
    bar_x = screen_x - bar_w // 2
    bar_y = screen_y - heart_radius - 25
    pygame.draw.rect(screen, (30, 30, 30), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
    pygame.draw.rect(screen, (255, 100, 120), (bar_x, bar_y, int(bar_w * hp_ratio), bar_h), border_radius=6)
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=6)

def draw_portal_dungeon(portal, camera_x, camera_y, screen):
    x = portal["x"] - camera_x
    y = portal["y"] - camera_y
    w, h = portal["width"], portal["height"]
    t = pygame.time.get_ticks() / 200

    # Aura xoáy tối
    aura_surf = pygame.Surface((w + 80, h + 80), pygame.SRCALPHA)
    for i in range(6):
        radius = w + 60 - i * 6
        distort = int(8 * math.sin(t + i * 0.6))
        alpha = int(40 + 25 * math.sin(t + i))
        color = (50 + i * 10, 0, 100 + i * 25, alpha)
        pygame.draw.ellipse(aura_surf, color, (40 - radius // 2 + distort, 40 - radius // 2 - distort, radius + w, radius + h), 2)
    screen.blit(aura_surf, (x - 40, y - 40))

    # Xoáy ma
    swirl = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    for i in range(30):
        ang = t + i * 0.35
        dx = int(math.cos(ang) * (i * 1.5))
        dy = int(math.sin(ang * 1.7) * (i * 1.3))
        r = 3 + i % 3
        col = (10, 0, 20 + i * 6, 240 - i * 7)
        pygame.draw.circle(swirl, col, (cx + dx, cy + dy), r)
    screen.blit(swirl, (x, y))

    # Pulsing tím ma
    pulse_alpha = int(90 + 60 * math.sin(t * 1.5))
    pulse_surf = pygame.Surface((w + 30, h + 30), pygame.SRCALPHA)
    pygame.draw.ellipse(pulse_surf, (200, 0, 255, pulse_alpha), (0, 0, w + 30, h + 30))
    screen.blit(pulse_surf, (x - 15, y - 15))

    # Thân cổng tối thẫm
    pygame.draw.rect(screen, (30, 0, 50), (x, y, w, h), border_radius=10)

    # Viền rung rợn
    for i in range(4):
        offset = int(3 * math.sin(t * 3 + i))
        pygame.draw.rect(screen, (150, 0, 200), (x - offset, y + offset, w + offset * 2, h - offset * 2), 2, border_radius=14)

    # Đường rạn nứt ánh sáng lạnh
    for i in range(7):
        distortion = int(4 * math.sin(t * 2 + i))
        y_line = y + i * h // 7 + distortion
        pygame.draw.line(screen, (100, 255, 255), (x + 10, y_line), (x + w - 10, y_line), 1)

    # Mắt lấp lóe trong bóng tối (2 chấm sáng)
    eye_offset = int(2 * math.sin(t * 4))
    pygame.draw.circle(screen, (255, 0, 0), (x + w // 3 + eye_offset, y + h // 3), 4)
    pygame.draw.circle(screen, (255, 0, 0), (x + 2 * w // 3 - eye_offset, y + h // 3), 4)
        
import pygame

def draw_stat_popup(screen, SCREEN_WIDTH, SCREEN_HEIGHT, player_max_health, player_attack_damage, unspent_points,
                    stat_title_font, stat_label_font, stat_value_font):
    popup_w = int(SCREEN_WIDTH * 0.5)
    popup_h = int(SCREEN_HEIGHT * 0.45)
    popup = pygame.Rect((SCREEN_WIDTH - popup_w) // 2, (SCREEN_HEIGHT - popup_h) // 2, popup_w, popup_h)

    pygame.draw.rect(screen, (30, 30, 50), popup, border_radius=10)
    pygame.draw.rect(screen, (200, 200, 200), popup, 2, border_radius=10)

    screen.blit(stat_title_font.render("Nâng chỉ số", True, (255, 255, 255)),
                (popup.x + int(popup_w * 0.05), popup.y + int(popup_h * 0.07)))

    y0 = popup.y + int(popup_h * 0.35)
    btn_w = int(popup_w * 0.1)
    btn_h = int(popup_h * 0.15)
    btn_x = popup.x + popup_w - btn_w - int(popup_w * 0.05)

    hp_plus_btn = pygame.Rect(btn_x, y0 - 5, btn_w, btn_h)
    dmg_plus_btn = pygame.Rect(btn_x, y0 + btn_h + 15, btn_w, btn_h)

    txt1 = stat_label_font.render(f"Máu tối đa: {player_max_health}", True, (220, 220, 220))
    screen.blit(txt1, (popup.x + int(popup_w * 0.08), y0))
    pygame.draw.rect(screen, (70, 130, 180), hp_plus_btn, border_radius=5)
    screen.blit(stat_value_font.render("+", True, (255, 255, 255)), (hp_plus_btn.x + 10, hp_plus_btn.y + 5))

    txt2 = stat_label_font.render(f"Sát thương: {player_attack_damage}", True, (220, 220, 220))
    screen.blit(txt2, (popup.x + int(popup_w * 0.08), y0 + btn_h + 15))
    pygame.draw.rect(screen, (70, 130, 180), dmg_plus_btn, border_radius=5)
    screen.blit(stat_value_font.render("+", True, (255, 255, 255)), (dmg_plus_btn.x + 10, dmg_plus_btn.y + 5))

    pts_y = popup.y + popup_h - int(popup_h * 0.25)
    screen.blit(stat_label_font.render(f"Điểm còn: {unspent_points}", True, (255, 215, 0)),
                (popup.x + int(popup_w * 0.08), pts_y))

    close_w = int(popup_w * 0.25)
    close_h = int(popup_h * 0.17)
    close_stat_btn = pygame.Rect(popup.centerx - close_w // 2, popup.y + popup_h - close_h - 10, close_w, close_h)
    pygame.draw.rect(screen, (180, 50, 50), close_stat_btn, border_radius=5)
    screen.blit(stat_label_font.render("Thoát", True, (255, 255, 255)),
                (close_stat_btn.x + 20, close_stat_btn.y + 5))

    return close_stat_btn, hp_plus_btn, dmg_plus_btn