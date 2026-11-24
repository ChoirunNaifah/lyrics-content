import tkinter as tk
import time
import math
import random

LYRICS = [
    (0.0,  "Cantiknya memacari terang"),
    (4.0,  "Kata siapa"),
    (6.5,  "Kau tak sempurna"),
    (9.5,  "Biar matamu merona"),
    (12.5, "Sungguh kau berharga"),
    (16.5, "Jangan lah berhenti"),
    (19.5, "Tuk percaya dirimu"),
    (22.5, "Ingat sinarmu berarti"),
]

# Pengaturan Kartu Lirik (Minimalis & Soft)
BOX_W, BOX_H        = 420, 185
FONT                = ("Georgia", 20)
DECOR_FONT          = ("Georgia", 10)
BG_COLOR            = "#1C151B"   # Deep velvet plum
BORDER_COLOR        = "#B5838D"   # Hairline dusty rose
FG_COLOR            = "#FAF0EB"   # Warm ivory
ACCENT_COLOR        = "#E5989B"   # Soft blush
RISE_SPEED          = 52          # Gerak naik lebih lambat & mengalir
STACK_SPACING       = 28

# Pengaturan Partikel (Jarang, kecil, & halus)
HEART_COUNT         = 12
SPARKLE_COUNT       = 22
HEART_COLORS        = ["#E5989B", "#FFB4A2", "#FFCDB2", "#D88C9A", "#F4ACB7"]
SPARKLE_COLORS      = ["#FFF8F0", "#F3D5B5", "#FFE5D9"]


def get_heart_points(cx, cy, scale):
    """Menghasilkan koordinat poligon bentuk hati yang halus."""
    pts = []
    steps = 28
    for i in range(steps):
        t = (2 * math.pi * i) / steps
        x = 16 * (math.sin(t) ** 3)
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.extend([cx + x * scale, cy + y * scale])
    return pts


def get_sparkle_points(cx, cy, r_outer, r_inner):
    """Menghasilkan koordinat bintang kilau tipis 4 sudut."""
    pts = []
    for i in range(8):
        angle = i * math.pi / 4
        r = r_outer if i % 2 == 0 else r_inner
        pts.extend([cx + r * math.cos(angle), cy + r * math.sin(angle)])
    return pts


class AestheticLoveOverlay:
    def __init__(self, parent, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.parent   = parent
        self.active   = True

        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.geometry(f"{screen_w}x{screen_h}+0+0")
        self.win.configure(bg="#000001")
        try:
            self.win.attributes("-transparentcolor", "#000001")
        except tk.TclError:
            pass
        try:
            self.win.attributes("-alpha", 0.78)
        except tk.TclError:
            pass

        self.canvas = tk.Canvas(
            self.win, width=screen_w, height=screen_h,
            bg="#000001", highlightthickness=0
        )
        self.canvas.pack()

        self.hearts = [self._create_heart(random_y=True) for _ in range(HEART_COUNT)]
        self.sparkles = [self._create_sparkle() for _ in range(SPARKLE_COUNT)]
        self.gentle_drifts = []

        self.last_time = time.time()
        self._draw()

    def _create_heart(self, random_y=False):
        return {
            "x": random.uniform(40, self.screen_w - 40),
            "y": random.uniform(0, self.screen_h) if random_y else random.uniform(self.screen_h + 20, self.screen_h + 180),
            "speed": random.uniform(30, 65),
            "scale": random.uniform(0.35, 0.78),
            "sway_amp": random.uniform(12, 28),
            "sway_freq": random.uniform(0.6, 1.2),
            "phase": random.uniform(0, math.pi * 2),
            "color": random.choice(HEART_COLORS),
            "hollow": random.choice([True, False]),
        }

    def _create_sparkle(self):
        return {
            "x": random.uniform(30, self.screen_w - 30),
            "y": random.uniform(30, self.screen_h - 30),
            "max_r": random.uniform(4, 8),
            "speed": random.uniform(1.0, 2.2),
            "phase": random.uniform(0, math.pi * 2),
            "color": random.choice(SPARKLE_COLORS),
        }

    def spawn_gentle_hearts(self, cx, cy):
        """Memunculkan 4 hati kecil yang melayang lambat saat lirik baru muncul."""
        for _ in range(4):
            offset_x = random.uniform(-110, 110)
            self.gentle_drifts.append({
                "x": cx + offset_x,
                "y": cy + random.uniform(-20, 20),
                "vx": random.uniform(-14, 14),
                "vy": random.uniform(-50, -30),
                "scale": random.uniform(0.32, 0.55),
                "life": 1.0,
                "color": random.choice(HEART_COLORS),
            })

    def stop(self):
        self.active = False

    def _draw(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        if not self.active:
            self.canvas.delete("all")
            try:
                self.win.destroy()
            except tk.TclError:
                pass
            return

        self.canvas.delete("all")

        # 1. Gambar kilau bintang halus
        for sp in self.sparkles:
            pulse = (math.sin(now * sp["speed"] + sp["phase"]) + 1) / 2
            r_outer = sp["max_r"] * pulse
            if r_outer > 1.0:
                pts = get_sparkle_points(sp["x"], sp["y"], r_outer, r_outer * 0.22)
                self.canvas.create_polygon(pts, fill=sp["color"], outline="")

        # 2. Gambar beberapa hati melayang pelan
        for h in self.hearts:
            h["y"] -= h["speed"] * dt
            draw_x = h["x"] + math.sin(now * h["sway_freq"] + h["phase"]) * h["sway_amp"]

            if h["y"] > -40:
                pts = get_heart_points(draw_x, h["y"], h["scale"])
                if h["hollow"]:
                    self.canvas.create_polygon(pts, fill="", outline=h["color"], width=1.4)
                else:
                    self.canvas.create_polygon(pts, fill=h["color"], outline="")
            else:
                new_h = self._create_heart(random_y=False)
                h.update(new_h)

        # 3. Gambar hati kecil yang mengambang perlahan dari kartu lirik
        alive_drifts = []
        for gd in self.gentle_drifts:
            gd["x"] += gd["vx"] * dt
            gd["y"] += gd["vy"] * dt
            gd["life"] -= dt * 0.5

            if gd["life"] > 0:
                current_scale = gd["scale"] * (0.4 + 0.6 * gd["life"])
                pts = get_heart_points(gd["x"], gd["y"], current_scale)
                self.canvas.create_polygon(pts, fill=gd["color"], outline="")
                alive_drifts.append(gd)
        self.gentle_drifts = alive_drifts

        self.win.after(16, self._draw)


class LyricCard:
    def __init__(self, parent, text, x, y):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=BORDER_COLOR)
        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(x)}+{int(y)}")
        self.win.resizable(False, False)
        try:
            self.win.attributes("-alpha", 0.92)
        except tk.TclError:
            pass

        self.inner = tk.Frame(self.win, bg=BG_COLOR)
        self.inner.pack(expand=True, fill="both", padx=1, pady=1)

        self.top_decor = tk.Label(
            self.inner,
            text="—  ♡  —",
            font=DECOR_FONT,
            bg=BG_COLOR,
            fg=ACCENT_COLOR,
        )
        self.top_decor.pack(pady=(18, 0))

        self.full_text = text
        self.label = tk.Label(
            self.inner,
            text="",
            font=FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
            wraplength=BOX_W - 60,
            justify="center",
        )
        self.label.pack(expand=True, fill="both", padx=30, pady=(4, 22))

        self.typewriter_index = 0
        self.base_x = float(x)
        self.y = float(y)
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.typewriter()

    def typewriter(self):
        if self.typewriter_index <= len(self.full_text):
            self.label.config(text=self.full_text[: self.typewriter_index])
            self.typewriter_index += 1
            self.win.after(70, self.typewriter)

    def rise(self, dy, now):
        self.y -= dy
        sway_x = self.base_x + math.sin(now * 0.9 + self.sway_phase) * 8
        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(sway_x)}+{int(self.y)}")

    def is_offscreen(self):
        return self.y + BOX_H < -50


class LyricFloatApp:
    def __init__(self, root, overlay=None, on_done=None):
        self.root            = root
        self.overlay         = overlay
        self.screen_w        = root.winfo_screenwidth()
        self.screen_h        = root.winfo_screenheight()
        self.next_lyric_idx  = 0
        self.boxes           = []
        self.last_frame_time = None
        self.current_side    = "left"
        self.on_done         = on_done

    def random_safe_x(self):
        center_x = self.screen_w // 2
        spacing  = BOX_W + 50
        left_x   = max(20, center_x - spacing)
        right_x  = min(self.screen_w - BOX_W - 20, center_x + 50)
        if self.current_side == "left":
            self.current_side = "right"
            return left_x
        else:
            self.current_side = "left"
            return right_x

    def lowest_y(self):
        spawn_base = int(self.screen_h * 0.65)
        if not self.boxes:
            return spawn_base
        return max(spawn_base, max(box.y for box in self.boxes) + BOX_H + STACK_SPACING)

    def start(self):
        self.start_time      = time.time()
        self.last_frame_time = self.start_time
        self.tick()

    def tick(self):
        now     = time.time()
        elapsed = now - self.start_time
        dt      = now - self.last_frame_time
        self.last_frame_time = now

        while (
            self.next_lyric_idx < len(LYRICS)
            and LYRICS[self.next_lyric_idx][0] <= elapsed
        ):
            t, text = LYRICS[self.next_lyric_idx]
            x   = self.random_safe_x()
            y   = self.lowest_y()
            box = LyricCard(self.root, text, x, y)
            self.boxes.append(box)

            if self.overlay:
                self.overlay.spawn_gentle_hearts(x + BOX_W / 2, y + 20)

            self.next_lyric_idx += 1

        dy = RISE_SPEED * dt
        for box in self.boxes:
            box.rise(dy, now)

        still_visible = []
        for box in self.boxes:
            if box.is_offscreen():
                try:
                    box.win.destroy()
                except tk.TclError:
                    pass
            else:
                still_visible.append(box)
        self.boxes = still_visible

        if self.next_lyric_idx < len(LYRICS) or self.boxes:
            self.root.after(16, self.tick)
        else:
            if self.on_done:
                self.on_done()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    love_overlay = AestheticLoveOverlay(root, screen_w, screen_h)

    def on_lyrics_done():
        love_overlay.stop()
        root.after(600, root.quit)

    lyrics_app = LyricFloatApp(root, overlay=love_overlay, on_done=on_lyrics_done)
    lyrics_app.start()

    root.mainloop()