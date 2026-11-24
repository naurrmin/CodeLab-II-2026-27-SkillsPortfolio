"""Shared coquette post-office theme: fonts, paper textures, illustrations and cute effects.

A copy of this file lives in each exercise folder so every project stays self-contained.
Everything is drawn with Tkinter only (no image files needed).
"""
import math
import os
import random
import sys
import tkinter as tk
from tkinter import ttk, font as tkfont

BG = "#fdeaf3"
PAPER = "#fcf8f5"
INK = "#3a2e2b"
PINK = "#fbcfe8"
ROSE = "#e58aa1"
SOFT = "#fde9f2"
GOOD = "#3f8a5a"
BAD = "#c0405a"
PARCH = "#f4e8cf"
WAX = "#a82b3d"
GOLD = "#d4a73c"
OAK = "#b98a5e"
OAK_DARK = "#7a5233"
STAMP_BLUE = "#2f5d8a"
SCRIPT = "Georgia"      # swapped for a calligraphy font if one is installed
HEAD = "Georgia"        # swapped for Playfair Display / Didot / Bodoni if installed
BODY = "Courier New"    # swapped for Courier Prime / American Typewriter if installed
SCRIPT_REAL = False
TRAIL = ["♥", "♡", "✿", "✦"]
CONFETTI = ["♥", "✿", "✦", "♡", "★"]
RANKS = [(0, "Mail Room Trainee"), (20, "Apprentice Stamper"), (40, "Sorting Clerk"),
         (65, "Head Courier"), (90, "Certified Chief Postmistress")]
HEADER = 104  # height of the masthead on the paper sheet

_tiles = {}   # base texture tiles
_cache = {}   # tiled photos by (name, w, h)


def rankFor(points):
    """Passport rank title for a 0-100 points value."""
    title = RANKS[0][1]
    for needed, name in RANKS:
        if points >= needed:
            title = name
    return title


# ---------- fonts ----------

def loadLocalFonts():
    """On Windows, register any .ttf/.otf files placed in a 'fonts' folder next to this file."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
        for name in os.listdir(folder):
            if name.lower().endswith((".ttf", ".otf")):
                ctypes.windll.gdi32.AddFontResourceExW(os.path.join(folder, name), 0x10, 0)
    except (OSError, AttributeError):
        pass


def scriptFont(size):
    """Font tuple for flourishes (italic fallback when no calligraphy font is installed)."""
    return (SCRIPT, size) if SCRIPT_REAL else (SCRIPT, int(size * .85), "italic")


# ---------- textures (generated, tiled) ----------

def _make(size, pixel):
    img = tk.PhotoImage(width=size, height=size)
    rows = ["{" + " ".join("#%02x%02x%02x" % pixel(x, y) for x in range(size)) + "}" for y in range(size)]
    img.put(" ".join(rows))
    return img


def _clamp(*values):
    return tuple(max(0, min(255, int(v))) for v in values)


def buildTextures():
    rnd = random.Random(7)

    def paper(x, y):
        n = rnd.randint(-5, 0)
        if rnd.random() < 0.012:
            n -= rnd.randint(8, 16)
        if (y * 7 + x // 9) % 41 == 0:
            n -= 4
        return _clamp(252 + n, 248 + n, 245 + n)

    def parch(x, y):
        n = rnd.randint(-9, 0)
        if rnd.random() < 0.015:
            return _clamp(214 + n, 190 + n, 150 + n)
        return _clamp(244 + n, 232 + n, 207 + n)

    def oak(x, y):
        grain = 14 * math.sin(y * 2 * math.pi * 6 / 96 + 2.0 * math.sin(x * 2 * math.pi / 96))
        v = grain + rnd.randint(-6, 6) - (25 if rnd.random() < 0.01 else 0)
        return _clamp(186 + v, 139 + v, 95 + v)

    heart = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
    hearts = {(i * 8 + dx, j * 8 + dy + 1)
              for i in (1, 3, 5, 7) for j in (1, 3, 5, 7)
              for dy, row in enumerate(heart) for dx, ch in enumerate(row) if ch == "1"}

    def wall(x, y):
        if (x, y) in hearts:
            return (255, 248, 251)
        h, v = (y // 8) % 2, (x // 8) % 2
        return [(253, 238, 245), (251, 218, 235), (247, 198, 222)][h + v]

    _tiles["paper"] = _make(96, paper)
    _tiles["parch"] = _make(96, parch)
    _tiles["oak"] = _make(96, oak)
    _tiles["wall"] = _make(64, wall)


def texturePhoto(name, w, h):
    """A photo of exactly w x h filled by tiling one of the generated textures."""
    key = (name, w, h)
    if key not in _cache:
        if len(_cache) > 30:
            _cache.clear()
        img = tk.PhotoImage(width=max(w, 1), height=max(h, 1))
        img.tk.call(str(img), "copy", str(_tiles[name]), "-to", 0, 0, max(w, 1), max(h, 1))
        _cache[key] = img
    return _cache[key]


def paste(canvas, name, x, y, w, h, tag="tex", lower=True):
    """Draw a textured rectangle onto a canvas (underneath everything else)."""
    img = texturePhoto(name, w, h)
    if not hasattr(canvas, "_refs"):
        canvas._refs = {}
    canvas._refs[tag] = img
    item = canvas.create_image(x, y, image=img, anchor="nw", tags=tag)
    if lower:
        canvas.tag_lower(item)
    return item


# ---------- theme ----------

def applyTheme(root):
    """Pick fonts, build textures, style every ttk widget and switch on the heart cursor trail."""
    global SCRIPT, HEAD, BODY, SCRIPT_REAL
    loadLocalFonts()
    families = set(tkfont.families(root))
    pick = lambda options, default: next((f for f in options if f in families), default)
    SCRIPT = pick(("Great Vibes", "Pinyon Script", "Allura", "Parisienne", "Lucida Calligraphy",
                   "Snell Roundhand", "Apple Chancery", "Segoe Script", "Brush Script MT",
                   "Lucida Handwriting", "URW Chancery L", "Z003"), "Georgia")
    SCRIPT_REAL = SCRIPT != "Georgia"
    HEAD = pick(("Playfair Display", "Cormorant Garamond", "Didot", "Bodoni MT", "Baskerville",
                 "Georgia", "Times New Roman", "DejaVu Serif"), "serif")
    BODY = pick(("Courier Prime", "American Typewriter", "Special Elite", "Courier New", "Courier",
                 "DejaVu Sans Mono"), "courier")

    buildTextures()
    root.configure(bg=BG)
    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure(".", background=PAPER, foreground=INK, font=(BODY, 10))
    s.configure("TLabel", background=PAPER, foreground=INK)
    s.configure("Head.TLabel", font=(HEAD, 18, "bold"))
    s.configure("Sub.TLabel", font=scriptFont(18), foreground=ROSE)
    s.configure("TButton", background=PINK, foreground=INK, font=(BODY, 10, "bold"), padding=7,
                bordercolor=INK, lightcolor=PINK, darkcolor=PINK, borderwidth=1, focusthickness=0)
    s.map("TButton", background=[("active", ROSE), ("disabled", "#eee4e6")],
          lightcolor=[("active", ROSE)], darkcolor=[("active", ROSE)],
          foreground=[("disabled", "#a39598")])
    s.configure("Cubby.TButton", font=(BODY, 8, "bold"), padding=7)
    s.configure("Back.TButton", background=PAPER, lightcolor=PAPER, darkcolor=PAPER, padding=4)
    s.map("Back.TButton", background=[("active", PINK)], lightcolor=[("active", PINK)],
          darkcolor=[("active", PINK)])
    s.configure("TEntry", fieldbackground="white", foreground=INK, padding=5, bordercolor=INK)
    s.configure("TCombobox", fieldbackground="white", foreground=INK, bordercolor=INK)
    s.configure("TRadiobutton", background=PAPER, foreground=INK)
    s.configure("Treeview", background="white", fieldbackground="white", foreground=INK,
                rowheight=26, font=(BODY, 9), bordercolor=INK)
    s.configure("Treeview.Heading", background=PINK, foreground=INK, font=(BODY, 9, "bold"),
                relief="flat")
    s.map("Treeview", background=[("selected", ROSE)], foreground=[("selected", "white")])
    s.map("Treeview.Heading", background=[("active", ROSE)])
    enableHeartTrail(root)


# ---------- little illustrations (all drawn with canvas shapes) ----------

def drawSprite(canvas, kind, x, y, s=1.0, tag="sprite"):
    """Draw a cute picture centred on (x, y). kinds: heart, bow, envelope, teddy, star."""
    tags = tag
    if kind == "heart":
        pts = []
        for deg in range(0, 360, 12):
            t = math.radians(deg)
            px = 16 * math.sin(t) ** 3
            py = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            pts += [x + px * s * .9, y + py * s * .9 + 1 * s]
        canvas.create_polygon(pts, fill="#f06f93", outline=INK, width=2, tags=tags)
        canvas.create_oval(x - 9 * s, y - 10 * s, x - 3 * s, y - 5 * s, fill="#fbd0dc", outline="", tags=tags)
    elif kind == "bow":
        for d in (-1, 1):
            canvas.create_polygon(x, y, x + d * 20 * s, y - 12 * s, x + d * 25 * s, y + 3 * s,
                                  x + d * 18 * s, y + 14 * s, fill=ROSE, outline=INK, width=2,
                                  smooth=True, tags=tags)
            canvas.create_polygon(x + d * 2 * s, y + 3 * s, x + d * 13 * s, y + 24 * s, x + d * 6 * s, y + 20 * s,
                                  x + d * 1 * s, y + 26 * s, fill="#d9677f", outline=INK, width=2, tags=tags)
        canvas.create_oval(x - 6 * s, y - 6 * s, x + 6 * s, y + 6 * s, fill="#d9677f", outline=INK, width=2, tags=tags)
    elif kind == "envelope":
        canvas.create_rectangle(x - 20 * s, y - 13 * s, x + 20 * s, y + 13 * s, fill=PARCH, outline=INK, width=2, tags=tags)
        canvas.create_line(x - 20 * s, y - 13 * s, x, y + 3 * s, x + 20 * s, y - 13 * s, fill=INK, width=2, tags=tags)
        canvas.create_oval(x - 4 * s, y - 1 * s, x + 4 * s, y + 7 * s, fill=WAX, outline="#7c1d2b", tags=tags)
    elif kind == "teddy":
        brown, light = "#c99a6e", "#ecd2ae"
        for d in (-1, 1):
            canvas.create_oval(x + d * 12 * s - 7 * s, y - 20 * s, x + d * 12 * s + 7 * s, y - 6 * s, fill=brown, outline=INK, width=2, tags=tags)
            canvas.create_oval(x + d * 12 * s - 3 * s, y - 16 * s, x + d * 12 * s + 3 * s, y - 10 * s, fill=PINK, outline="", tags=tags)
        canvas.create_oval(x - 16 * s, y - 14 * s, x + 16 * s, y + 14 * s, fill=brown, outline=INK, width=2, tags=tags)
        canvas.create_oval(x - 7 * s, y - 1 * s, x + 7 * s, y + 10 * s, fill=light, outline=INK, tags=tags)
        for d in (-1, 1):
            canvas.create_oval(x + d * 7 * s - 2 * s, y - 7 * s, x + d * 7 * s + 2 * s, y - 3 * s, fill=INK, tags=tags)
        canvas.create_oval(x - 2.5 * s, y + 1 * s, x + 2.5 * s, y + 5 * s, fill=INK, tags=tags)
        canvas.create_oval(x - 12 * s, y + 3 * s, x - 7 * s, y + 7 * s, fill=PINK, outline="", tags=tags)
        canvas.create_oval(x + 7 * s, y + 3 * s, x + 12 * s, y + 7 * s, fill=PINK, outline="", tags=tags)
    elif kind == "star":
        pts = []
        for i in range(10):
            r = 17 * s if i % 2 == 0 else 7.5 * s
            a = math.radians(-90 + i * 36)
            pts += [x + r * math.cos(a), y + r * math.sin(a)]
        canvas.create_polygon(pts, fill=GOLD, outline=INK, width=2, tags=tags)


def postageStamp(canvas, x, y, kind="bow", value="14c", w=54, h=66, locked=False, tag="deco"):
    """A perforated postage stamp with a little picture on it."""
    canvas.create_rectangle(x, y, x + w, y + h, fill=PARCH if not locked else PAPER, outline=INK,
                            width=3, dash=(2, 3), tags=tag)
    canvas.create_rectangle(x + 6, y + 6, x + w - 6, y + h - 6, fill=PINK if not locked else "#eee4e6",
                            outline=INK, tags=tag)
    if locked:
        canvas.create_text(x + w / 2, y + h / 2, text="?", font=(HEAD, 22, "bold"), fill="#b9acad", tags=tag)
    else:
        drawSprite(canvas, kind, x + w / 2, y + h / 2 - 3, w / 62, tag)
    canvas.create_text(x + w / 2, y + h - 12, text=value, font=(BODY, 7, "bold"), fill=INK, tags=tag)


def stampTile(parent, kind, label, got, value="14c", alwaysLabel=False):
    """A stamp-collection / sticker slot as a small canvas."""
    c = tk.Canvas(parent, width=88, height=108, bg=PAPER, highlightthickness=0)
    postageStamp(c, 11, 4, kind, value, 66, 80, locked=not got)
    shown = label if (got or alwaysLabel) else "locked"
    c.create_text(44, 98, text=shown, font=(BODY, 8), fill=INK if (got or alwaysLabel) else "#a39598")
    return c


def drawPostbox(canvas, x, y, s=1.0):
    """A red pillar box with a bow on top. (x, y) is the bottom centre."""
    canvas.create_oval(x - 45 * s, y - 172 * s, x + 45 * s, y - 120 * s, fill=WAX, outline=INK, width=2)
    canvas.create_rectangle(x - 45 * s, y - 146 * s, x + 45 * s, y - 10 * s, fill=WAX, outline=INK, width=2)
    canvas.create_rectangle(x - 18 * s, y - 126 * s, x + 18 * s, y - 108 * s, fill=PARCH, outline=INK)
    canvas.create_rectangle(x - 28 * s, y - 116 * s, x + 28 * s, y - 102 * s, fill=INK)
    canvas.create_text(x, y - 72 * s, text="POST", fill=PARCH, font=(HEAD, max(int(15 * s), 8), "bold"))
    canvas.create_text(x, y - 44 * s, text="♥", fill=PINK, font=(HEAD, max(int(14 * s), 8)))
    canvas.create_rectangle(x - 55 * s, y - 10 * s, x + 55 * s, y, fill=INK)
    drawSprite(canvas, "bow", x, y - 178 * s, .55 * s)


def bunting(canvas, x0, x1, y, flags=11):
    """A string of little pennant flags."""
    colours = [PINK, ROSE, PARCH, "#cfe3f2"]
    width = (x1 - x0) / flags
    canvas.create_line(x0, y, x1, y, fill=INK)
    for i in range(flags):
        left = x0 + i * width
        canvas.create_polygon(left + 2, y, left + width - 2, y, left + width / 2, y + 26,
                              fill=colours[i % 4], outline=INK, width=1)


def footerScene(parent, width=480, height=170):
    """A little post-office street scene to fill empty space on a screen."""
    k = height / 170
    c = tk.Canvas(parent, width=width, height=height, bg=PAPER, highlightthickness=0)
    bunting(c, 8, width - 8, 6, flags=11)
    c.create_line(20, height - 6, width - 20, height - 6, fill=INK, width=2)
    drawSprite(c, "teddy", width * .2, height - 40 * k, 1.5 * k)
    drawSprite(c, "envelope", width * .2 + 42 * k, height - 22 * k, .9 * k)
    drawPostbox(c, width * .5, height - 6, .72 * k)
    drawSprite(c, "bow", width * .78, height - 50 * k, 1.2 * k)
    drawSprite(c, "heart", width * .9, height - 85 * k, 1.0 * k)
    drawSprite(c, "envelope", width * .7, height - 118 * k, .8 * k)
    return c


def waxSeal(canvas, x, y, r=34, text="♥"):
    """Draw a red wax seal with a scalloped edge."""
    for i in range(14):
        a = i * 2 * math.pi / 14
        px, py = x + math.cos(a) * r, y + math.sin(a) * r
        canvas.create_oval(px - r * .28, py - r * .28, px + r * .28, py + r * .28, fill=WAX, outline="#7c1d2b")
    canvas.create_oval(x - r, y - r, x + r, y + r, fill=WAX, outline="#7c1d2b")
    canvas.create_oval(x - r * .7, y - r * .7, x + r * .7, y + r * .7, outline="#d9798a", width=2)
    canvas.create_text(x, y, text=text, fill="#f9d5dc", font=(HEAD, int(r * .7), "bold"))


def postmark(canvas, x, y, r=34, text="DELIVERED", color=STAMP_BLUE):
    """Round postmark with wavy cancellation lines."""
    canvas.create_oval(x - r, y - r, x + r, y + r, outline=color, width=2)
    canvas.create_oval(x - r + 6, y - r + 6, x + r - 6, y + r - 6, outline=color)
    canvas.create_text(x, y, text=text, fill=color, font=(BODY, 7, "bold"))
    for dy in (-10, 0, 10):
        canvas.create_line(x + r, y + dy, x + r + 18, y + dy - 4, x + r + 36, y + dy + 4, x + r + 54, y + dy,
                           fill=color, width=2, smooth=True)


def inkStamp(canvas, x, y, text, color=STAMP_BLUE, angle=10, size=18):
    """Press a slanted ink stamp onto a canvas (replaces any earlier one)."""
    canvas.delete("ink")
    canvas.create_text(x, y, text=text, fill=color, font=(HEAD, size, "bold"), angle=angle,
                       justify="center", tags="ink")


def drawPigeon(canvas, x, y):
    """A little carrier pigeon holding a love letter. Returns nothing; items are tagged 'pigeon'."""
    t = "pigeon"
    canvas.create_polygon(x - 22, y - 2, x - 38, y - 9, x - 35, y + 1, x - 38, y + 8, fill="#cfc5d6", outline=INK, tags=t)
    canvas.create_oval(x - 24, y - 9, x + 16, y + 9, fill="#ece8f0", outline=INK, width=2, tags=t)
    canvas.create_oval(x + 11, y - 18, x + 27, y - 3, fill="#ece8f0", outline=INK, width=2, tags=t)
    canvas.create_polygon(x + 26, y - 12, x + 35, y - 9, x + 26, y - 7, fill="#e8a95b", outline=INK, tags=t)
    canvas.create_oval(x + 20, y - 14, x + 23, y - 11, fill=INK, tags=t)
    canvas.create_oval(x + 15, y - 10, x + 19, y - 7, fill=PINK, outline="", tags=t)
    canvas.create_polygon(x - 8, y - 5, x - 2, y - 28, x + 8, y - 7, fill="#d8d0e0", outline=INK, tags=(t, "wingUp"))
    canvas.create_polygon(x - 8, y - 2, x - 4, y + 14, x + 6, y + 1, fill="#d8d0e0", outline=INK, tags=(t, "wingDown"), state="hidden")
    canvas.create_rectangle(x + 30, y - 6, x + 48, y + 6, fill=PARCH, outline=INK, tags=t)
    canvas.create_line(x + 30, y - 6, x + 39, y + 1, x + 48, y - 6, fill=INK, tags=t)
    canvas.create_oval(x + 36, y - 1, x + 42, y + 5, fill=WAX, outline="", tags=t)


def flyPigeon(canvas, y=30, speed=6):
    """Fly the pigeon across the canvas once."""
    try:
        width = canvas.winfo_width()
        canvas.delete("pigeon")
        drawPigeon(canvas, -50, y)
        state = {"x": -50, "t": 0, "dy": 0.0}

        def step():
            try:
                state["t"] += 1
                state["x"] += speed
                dy = math.sin(state["t"] * .35) * 6
                canvas.move("pigeon", speed, dy - state["dy"])
                state["dy"] = dy
                up = state["t"] % 6 < 3
                canvas.itemconfigure("wingUp", state="normal" if up else "hidden")
                canvas.itemconfigure("wingDown", state="hidden" if up else "normal")
                if state["x"] > width + 70:
                    canvas.delete("pigeon")
                else:
                    canvas.after(30, step)
            except tk.TclError:
                pass
        step()
    except tk.TclError:
        pass


# ---------- the newspaper page ----------

def makePaper(root, title, tagline="Special Edition"):
    """Pink gingham wall, a textured paper sheet with an airmail border and masthead.
    Returns the body frame that each screen is built in."""
    wall = tk.Canvas(root, highlightthickness=0, bd=0, bg=BG)
    wall.pack(fill="both", expand=True)
    outer = tk.Frame(wall, bg=INK, padx=2, pady=2)
    outerWin = wall.create_window(16, 16, anchor="nw", window=outer)
    sheet = tk.Canvas(outer, highlightthickness=0, bd=0, bg=PAPER)
    sheet.pack(fill="both", expand=True)
    border = tk.Frame(sheet, bg=INK, padx=1, pady=1)
    body = ttk.Frame(border, padding=(12, 8))
    body.pack(fill="both", expand=True)
    bodyWin = sheet.create_window(22, HEADER, anchor="nw", window=border)
    last = {"wall": None, "sheet": None}

    def drawWall(w, h):
        if last["wall"] == (w, h):
            return
        last["wall"] = (w, h)
        wall.delete("tex")
        paste(wall, "wall", 0, 0, w, h)

    def drawSheet(w, h):
        if last["sheet"] == (w, h):
            return
        last["sheet"] = (w, h)
        sheet.delete("deco", "tex", "twinkle")
        paste(sheet, "paper", 0, 0, w, h)
        sheet.create_rectangle(26, HEADER + 4, w - 18, h - 12, fill="#e3d8cc", outline="", tags="deco")
        colours = [ROSE, "#f6efe8", STAMP_BLUE, "#f6efe8"]
        for i, x in enumerate(range(-12, w + 12, 16)):
            for y0 in (0, h - 9):
                sheet.create_polygon(x, y0, x + 14, y0, x + 6, y0 + 9, x - 8, y0 + 9,
                                     fill=colours[i % 4], outline="", tags="deco")
        size = 38
        while size > 16 and tkfont.Font(font=scriptFont(size)).measure(title) > w - 230:
            size -= 2
        sheet.create_text(w / 2 + 2, 48, text=title, font=scriptFont(size), fill=PINK, tags="deco")
        sheet.create_text(w / 2, 46, text=title, font=scriptFont(size), fill=INK, tags="deco")
        sheet.create_text(w / 2, 80, text=f"✦  {tagline.upper()}  ✦", font=(BODY, 9, "bold"), fill=ROSE, tags="deco")
        for y in (92, 95):
            sheet.create_line(22, y, w - 22, y, fill=INK, tags="deco")
        postageStamp(sheet, 28, 16, "bow", "14c")
        postageStamp(sheet, w - 28 - 54, 16, "heart", "1887")
        for sx, sy in ((100, 24), (112, 70), (w - 100, 28), (w - 114, 66), (w / 2 - 190, 20), (w / 2 + 190, 74)):
            sheet.create_text(sx, sy, text="✦", font=(BODY, 11), fill=PINK, tags=("deco", "twinkle"))

    def onWall(event):
        wall.itemconfigure(outerWin, width=max(event.width - 32, 200), height=max(event.height - 32, 200))
        drawWall(event.width, event.height)

    def onSheet(event):
        sheet.itemconfigure(bodyWin, width=max(event.width - 44, 200), height=max(event.height - HEADER - 16, 100))
        drawSheet(event.width, event.height)

    def twinkle():
        try:
            items = sheet.find_withtag("twinkle")
            if items:
                item = random.choice(items)
                sheet.itemconfigure(item, fill=ROSE if sheet.itemcget(item, "fill") == PINK else PINK)
            sheet.after(450, twinkle)
        except tk.TclError:
            pass

    def deliver():
        try:
            flyPigeon(sheet)
            sheet.after(40000, deliver)
        except tk.TclError:
            pass

    wall.bind("<Configure>", onWall)
    sheet.bind("<Configure>", onSheet)
    sheet.after(1500, deliver)
    sheet.after(450, twinkle)
    body.sheet = sheet
    return body


def clear(body):
    """Remove everything from a screen."""
    for widget in body.winfo_children():
        widget.destroy()


def toast(root, text, ms=2000):
    """Small chocolate notification banner at the top of the window."""
    label = tk.Label(root, text=text, bg=INK, fg=PAPER, font=(BODY, 10, "bold"), padx=14, pady=6)
    label.place(relx=0.5, y=4, anchor="n")
    label.lift()
    root.after(ms, label.destroy)


def enableHeartTrail(root):
    """Little hearts float up wherever you click."""
    def burst(event):
        try:
            x = event.x_root - root.winfo_rootx()
            y = event.y_root - root.winfo_rooty()
            under = root.winfo_containing(event.x_root, event.y_root)
            try:
                bg = under.cget("bg")
            except (tk.TclError, AttributeError):
                bg = PAPER
            heart = tk.Label(root, text=random.choice(TRAIL), fg=ROSE, bg=bg, bd=0,
                             font=(BODY, 12, "bold"))

            def rise(step=0):
                try:
                    if step >= 12:
                        heart.destroy()
                        return
                    heart.place(x=x + (step % 3 - 1) * 2, y=y - step * 4)
                    heart.after(30, lambda: rise(step + 1))
                except tk.TclError:
                    pass
            rise()
        except tk.TclError:
            pass
    root.bind_all("<Button-1>", burst, add="+")


def confetti(canvas, count=45):
    """Drop a burst of hearts and sparkles down a canvas."""
    try:
        w = max(canvas.winfo_width(), 300)
        h = max(canvas.winfo_height(), 60)
        pieces = []
        for _ in range(count):
            item = canvas.create_text(random.randint(10, w - 10), random.randint(-h, 0),
                                      text=random.choice(CONFETTI), fill=random.choice([ROSE, PINK, INK]),
                                      font=(BODY, random.randint(10, 18)), tags="confetti")
            pieces.append((item, random.uniform(2, 5)))
    except tk.TclError:
        return

    def step(n=0):
        try:
            for item, speed in pieces:
                canvas.move(item, random.uniform(-1, 1), speed)
            if n < 60:
                canvas.after(30, lambda: step(n + 1))
            else:
                canvas.delete("confetti")
        except tk.TclError:
            pass
    step()


def scrollable(parent, height=330):
    """Scrollable area. Returns (holder to pack, inner frame to fill)."""
    holder = ttk.Frame(parent)
    canvas = tk.Canvas(holder, bg=PAPER, highlightthickness=0, height=height)
    bar = ttk.Scrollbar(holder, orient="vertical", command=canvas.yview)
    inner = ttk.Frame(canvas)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    window = canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window, width=e.width))
    canvas.configure(yscrollcommand=bar.set)
    canvas.pack(side="left", fill="both", expand=True)
    bar.pack(side="right", fill="y")

    def wheel(event):
        try:
            up = event.num == 4 or event.delta > 0
            canvas.yview_scroll(-1 if up else 1, "units")
        except tk.TclError:
            pass
    for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
        canvas.bind_all(sequence, wheel)
    return holder, inner