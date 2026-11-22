#!/usr/bin/env python3
"""Sum up 22 November's world news in one image.

Pure Python standard library. Draws a 1024x1024 dense front page with a
hand-defined 5x7 bitmap font and a hand-written PNG encoder.
Deterministic: no randomness, no time, no network, no external files.
"""
import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- colours
BG = (7, 11, 24)
PANEL = (16, 24, 46)
PANEL2 = (22, 32, 60)
HERO_BG = (42, 12, 20)
HERO_BG2 = (28, 10, 18)
RED = (230, 35, 45)
RED_DK = (160, 18, 28)
ORANGE = (255, 122, 26)
YELLOW = (255, 194, 51)
WHITE = (255, 255, 255)
GREY = (171, 180, 204)
GREY2 = (139, 149, 178)
BLUE = (84, 160, 255)
GREEN = (64, 200, 130)
PURPLE = (170, 120, 255)
TEAL = (64, 200, 190)

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 35 chars: 7 rows of 5, '#' = on, '.' = off.
FONT = {
    'A': (".###."
          "#...#"
          "#...#"
          "#####"
          "#...#"
          "#...#"
          "#...#"),
    'B': "####.#...##...#####.#...##...#####.",
    'C': ".#####....#....#....#....#.....####",
    'D': "####.#...##...##...##...##...#####.",
    'E': "######....#....####.#....#....#####",
    'F': "######....#....####.#....#....#....",
    'G': ".#####....#....#..###...##...#.###.",
    'H': "#...##...##...#######...##...##...#",
    'I': ".###...#....#....#....#....#...###.",
    'J': ("..###"
          "...#."
          "...#."
          "...#."
          "...#."
          "#..#."
          ".##.."),
    'K': ("#...#"
          "#..#."
          "#.#.."
          "##..."
          "#.#.."
          "#..#."
          "#...#"),
    'L': "#....#....#....#....#....#....#####",
    'M': "#...###.###.#.##.#.##...##...##...#",
    'N': "#...###..##.#.##..###...##...##...#",
    'O': ".###.#...##...##...##...##...#.###.",
    'P': "####.#...##...#####.#....#....#....",
    'Q': ".###.#...##...##...##.#.##..#..##.#",
    'R': ("####."
          "#...#"
          "#...#"
          "####."
          "#.#.."
          "#..#."
          "#...#"),
    'S': ".#####....#.....###.....#....#####.",
    'T': "#####..#....#....#....#....#....#..",
    'U': "#...##...##...##...##...##...#.###.",
    'V': "#...##...##...##...##...#.#.#...#..",
    'W': "#...##...##...##.#.##.#.###.###...#",
    'X': "#...##...#.#.#...#...#.#.#...##...#",
    'Y': "#...##...#.#.#...#....#....#....#..",
    'Z': ("#####"
          "....#"
          "...#."
          "..#.."
          ".#..."
          "#...."
          "#####"),
    # Digit 0 is a dotted zero: the center dot keeps it distinct from the letter O at every scale.
    '0': (".###."
          "#...#"
          "#...#"
          "#.#.#"
          "#...#"
          "#...#"
          ".###."),
    '1': "..#...##....#....#....#....#...###.",
    '2': (".###."
          "#...#"
          "....#"
          "...#."
          "..#.."
          ".#..."
          "#####"),
    '3': "####.....#....#.###.....#....#####.",
    '4': ("...#."
          "..##."
          ".#.#."
          "#..#."
          "#####"
          "...#."
          "...#."),
    '5': "######....####.....#....##...#.###.",
    '6': ".###.#....#....####.#...##...#.###.",
    '7': "#####....#...#....#...#...#....#...",
    '8': ".###.#...##...#.###.#...##...#.###.",
    '9': ".###.#...##...#.####....#....#.###.",
    ' ': "...................................",
    '.': "..........................##...##..",
    ',': ("....."
          "....."
          "....."
          "....."
          ".##.."
          ".##.."
          ".#..."),
    ':': ("....."
          ".##.."
          ".##.."
          "....."
          ".##.."
          ".##.."
          "....."),
    "'": ("..#.."
          "..#.."
          ".#..."
          "....."
          "....."
          "....."
          "....."),
    '-': ("....."
          "....."
          "....."
          ".###."
          "....."
          "....."
          "....."),
    '(': ("...#."
          "..#.."
          ".#..."
          ".#..."
          ".#..."
          "..#.."
          "...#."),
    ')': ".#.....#....#....#....#....#...#...",
    '%': "#...##..#....#....#...#...#..##...#",
    '$': ("..#.."
          ".###."
          "#.#.."
          ".###."
          "..#.#"
          ".###."
          "..#.."),
    '/': "....#...#....#....#...#...#...#....",
    '+': ("....."
          "..#.."
          "..#.."
          ".###."
          "..#.."
          "..#.."
          "....."),
    '!': ("..#.."
          "..#.."
          "..#.."
          "..#.."
          "..#.."
          "....."
          "..#.."),
    '?': ".###.#...#....#...#....#........#..",
    '~': "..........#.#.#.#.#................",
    '|': "..#....#....#....#....#....#....#..",
    '=': "..........#####.....#####..........",
    '&': (".###."
          "#...#"
          "#...#"
          ".###."
          "#.#.#"
          "#..#."
          ".##.#"),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = (y * self.w + x) * 3
            self.buf[o] = c[0]
            self.buf[o + 1] = c[1]
            self.buf[o + 2] = c[2]

    def fill(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            o = (yy * self.w + x0) * 3
            self.buf[o:o + len(row)] = row

    def hline(self, x, y, w, c):
        self.fill(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill(x, y, 1, h, c)

    def rect(self, x, y, w, h, c):
        self.hline(x, y, w, c)
        self.hline(x, y + h - 1, w, c)
        self.vline(x, y, h, c)
        self.vline(x + w - 1, y, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, c)

    def ring(self, cx, cy, r, c):
        steps = max(24, r * 6)
        for i in range(steps):
            a = 2.0 * math.pi * i / steps
            self.px(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), c)

    def diamond(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            half = r - abs(dy)
            self.hline(cx - half, cy + dy, 2 * half + 1, c)

    def text_w(self, s, scale):
        return len(s) * 6 * scale

    def text(self, x, y, s, scale, c, align="l"):
        if align == "c":
            x -= self.text_w(s, scale) // 2
        elif align == "r":
            x -= self.text_w(s, scale)
        for i, ch in enumerate(s):
            g = FONT.get(ch, FONT[' '])
            gx = x + i * 6 * scale
            for row in range(7):
                for col in range(5):
                    if g[row * 5 + col] == '#':
                        self.fill(gx + col * scale, y + row * scale,
                                  scale, scale, c)

    def wrap(self, s, scale, max_w):
        max_chars = max(1, max_w // (6 * scale))
        words = s.split(' ')
        lines = []
        cur = ''
        for w in words:
            if not cur:
                cur = w
            elif len(cur) + 1 + len(w) <= max_chars:
                cur += ' ' + w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines


# ---------------------------------------------------------------- png
def write_png(path, cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack('>I', len(data)) + typ + data
        out += struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)
        return out

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- icons
def icon(cv, kind, x, y, s, c):
    """Draw a small pictogram of size s inside the box at (x, y)."""
    cx = x + s // 2
    cy = y + s // 2
    if kind == 'burst':
        for k in range(8):
            a = math.pi * k / 4.0
            cv.line(cx, cy,
                    int(cx + (s // 2) * math.cos(a)),
                    int(cy + (s // 2) * math.sin(a)), c)
        cv.disc(cx, cy, max(2, s // 6), c)
    elif kind == 'flame':
        cv.disc(cx, y + s - s // 4, s // 4, c)
        cv.disc(cx, y + s // 2, s // 5, c)
        cv.disc(cx, y + s // 4, max(2, s // 8), YELLOW)
    elif kind == 'ship':
        cv.fill(x + 2, y + s - 10, s - 4, 6, c)
        cv.fill(x + 6, y + s - 20, 8, 10, c)
        cv.fill(x + 16, y + s - 16, 8, 6, c)
        cv.hline(x + 2, y + s - 2, s - 4, c)
    elif kind == 'rocket':
        cv.line(x + 4, y + s - 4, x + s - 4, y + 4, c)
        cv.fill(x + s - 8, y + 2, 6, 4, c)
        cv.line(x + 4, y + s - 4, x + 10, y + s - 10, c)
        cv.line(x + 4, y + s - 4, x + 10, y + s - 4, c)
    elif kind == 'quake':
        pts = [(x + 2, y + s // 2), (x + s // 4, y + s // 4),
               (x + s // 2, y + 3 * s // 4), (x + 3 * s // 4, y + s // 4),
               (x + s - 2, y + s // 2)]
        for a, b in zip(pts, pts[1:]):
            cv.line(a[0], a[1], b[0], b[1], c)
    elif kind == 'globe':
        cv.ring(cx, cy, s // 2 - 2, c)
        cv.hline(x + 3, cy, s - 6, c)
        cv.vline(cx, y + 3, s - 6, c)
    elif kind == 'columns':
        cv.fill(x + 2, y + 3, s - 4, 3, c)
        for k in range(3):
            cv.fill(x + 4 + k * (s // 3), y + 8, 4, s - 14, c)
        cv.fill(x + 2, y + s - 5, s - 4, 3, c)
    elif kind == 'chart':
        cv.vline(x + 3, y + 3, s - 6, c)
        cv.hline(x + 3, y + s - 4, s - 6, c)
        pts = [(x + 5, y + s - 8), (x + s // 3, y + s // 2),
               (x + 2 * s // 3, y + s // 3), (x + s - 4, y + 6)]
        for a, b in zip(pts, pts[1:]):
            cv.line(a[0], a[1], b[0], b[1], c)
    elif kind == 'cross':
        cv.fill(cx - 3, y + 4, 6, s - 8, c)
        cv.fill(x + 4, cy - 3, s - 8, 6, c)
    elif kind == 'star':
        cv.diamond(cx, cy, s // 2 - 2, c)
        cv.disc(cx, cy, max(2, s // 8), BG)
    elif kind == 'boat':
        cv.line(x + 4, y + s - 6, x + s - 4, y + s - 6, c)
        cv.line(x + 4, y + s - 6, x + 8, y + s - 12, c)
        cv.line(x + s - 4, y + s - 6, x + s - 8, y + s - 12, c)
        cv.vline(cx, y + 4, s - 14, c)
        for i in range(s // 2 - 4):
            cv.hline(cx + 2, y + 6 + i, s // 2 - 6 - i, c)
    elif kind == 'chip':
        cv.rect(x + 5, y + 5, s - 10, s - 10, c)
        cv.fill(cx - 3, cy - 3, 6, 6, c)
        for k in range(3):
            cv.fill(x + 5 + k * (s // 3), y + 1, 3, 4, c)
            cv.fill(x + 5 + k * (s // 3), y + s - 5, 3, 4, c)
    elif kind == 'doc':
        cv.rect(x + 6, y + 3, s - 12, s - 6, c)
        for k in range(3):
            cv.hline(x + 9, y + 8 + k * 6, s - 18, c)
    elif kind == 'flag':
        cv.vline(x + 6, y + 3, s - 6, c)
        for i in range(10):
            cv.hline(x + 6, y + 4 + i, 14 - i, c)
    else:  # default diamond
        cv.diamond(cx, cy, s // 2 - 3, c)


# ---------------------------------------------------------------- data
# (headline, fact, icon) — headlines <= 24 chars, facts <= 75 chars.
SECTIONS = [
    ("MIDDLE EAST", ORANGE, [
        ("COP31 OVERTIME",
         "ANTALYA TALKS PAST DEADLINE, NO NEW TEXT. EU: GOOD DEAL OR NO DEAL.",
         "globe"),
        ("GAZA: 4 KILLED",
         "ISRAELI FORCES KILL FOUR IN GAZA, THREE IN DRONE STRIKE ON AID VAN.",
         "burst"),
        ("BASRA PLANT FIRE",
         "FIRE AT HARTHA POWER STATION KILLS 4, INJURES 35. CAUSE UNKNOWN.",
         "flame"),
    ]),
    ("ASIA-PACIFIC", GREEN, [
        ("MALUKU QUAKE 7.2",
         "7.2 QUAKE STRIKES MALUKU, INDONESIA, 125 KM DEEP. NO TSUNAMI.",
         "quake"),
        ("FACTORY FIRE: 39 MISSING",
         "CONFECTIONERY FACTORY FIRE IN INDONESIA LEAVES 39 MISSING.",
         "flame"),
        ("TOXIC ALCOHOL: 11 DEAD",
         "TOXIC ALCOHOL KILLS 11 IN MANIPUR, INDIA. 180+ HOSPITALISED.",
         "cross"),
        ("MODI OPENS NITISH SETU",
         "MODI OPENS NITISH SETU BRIDGE IN BIHAR. INDIA PASSES 1 CRORE HPV DOSES.",
         "columns"),
        ("NEPAL PM TO INDIA",
         "NEPAL PM BALENDRA SHAH IN INDIA FOR FIRST BILATERAL TRIP SINCE MARCH.",
         "flag"),
        ("BANGLADESH: 90 PLATOONS",
         "90 GUARD PLATOONS SENT TO CURB ARSON AMID BNP-AWAMI LEAGUE CLASHES.",
         "star"),
        ("INDIA-JAPAN DEFENCE",
         "INDIA AND JAPAN DEEPEN DEFENCE TIES: JOINT TRAINING, MISSILE DRILLS.",
         "flag"),
    ]),
    ("EUROPE", BLUE, [
        ("RUSSIA'S OLD DEMANDS",
         "MOSCOW REVIVES PRE-2022 DEMANDS ON NATO EXPANSION IN UKRAINE TALKS.",
         "flag"),
        ("STRIKE ON KRYVYI RIH",
         "RUSSIAN STRIKE KILLS TWO. POLAND REPORTS INCURSIONS. NATO VOWS DEFENCE.",
         "burst"),
        ("POLAND: IT WAS A KH-101",
         "CRASHED OBJECT IN POLAND CONFIRMED AS RUSSIAN KH-101 CRUISE MISSILE.",
         "rocket"),
        ("ZELENSKY: SUMMIT FAILED",
         "ZELENSKY CALLS TRUMP-XI-PUTIN SUMMIT VERY UNSUCCESSFUL.",
         "columns"),
        ("SHIP AFIRE OFF FINLAND",
         "RUSSIAN-LINKED SPARTA II BURNS AFTER SUSPECTED DRONE STRIKE. CREW SAFE.",
         "ship"),
        ("EU-INDONESIA DEAL",
         "TRADE DEAL AFTER A DECADE OF TALKS. TARIFFS END ON 98% OF EU EXPORTS.",
         "doc"),
        ("OIL LICENCES VOID",
         "NORWAY SUPREME COURT RULES CLIMATE-DISPUTED OIL LICENCES INVALID.",
         "doc"),
        ("SPAIN BANK LEVY EXTENDED",
         "LEVY EXTENDED THROUGH 2027 TO RAISE EUR 1.4BN FOR HOUSING. VOTE 29 NOV.",
         "chart"),
        ("ECB CHIEF HUNT",
         "EU SEEKS NEW ECB CHIEF AS CHRISTINE LAGARDE RESIGNS.",
         "columns"),
    ]),
    ("WORLD", GREY, [
        ("NO KILLER-ROBOT TREATY",
         "UN TALKS IN GENEVA END WITHOUT BAN ON LETHAL AUTONOMOUS WEAPONS.",
         "chip"),
        ("FBI PROBES DATA BREACH",
         "FBI INVESTIGATES SUSPECTED BREACH OF NATIONAL CRIME DATABASE (NCIC).",
         "doc"),
    ]),
    ("AMERICAS", YELLOW, [
        ("'CHAPO ISIDRO' CAPTURED",
         "MEXICO SEIZES CARTEL BOSS FAUSTO ISIDRO MEZA FLORES. 11 KILLED IN RAID.",
         "star"),
        ("PERU QUAKE 6.8",
         "6.8 QUAKE HITS PERU'S ANDEAN JUNIN REGION. 15 INJURED, NO DEATHS.",
         "quake"),
        ("S&P'S WORST WEEK",
         "S&P 500 WORST WEEK SINCE APRIL 2025. FED HIKE IN DECEMBER NEAR CERTAIN.",
         "chart"),
        ("SOFTBANK'S $1TN IDEA",
         "SON EXPLORED A $1 TRILLION BUYOUT OF SK HYNIX BEFORE SHELVING IT.",
         "chip"),
    ]),
    ("AFRICA", PURPLE, [
        ("BOAT CAPSIZES: 24 DEAD",
         "BOAT CARRYING MOURNERS CAPSIZES IN NIGERIA'S BAYELSA STATE. 24 DEAD.",
         "boat"),
        ("NIGER STATE ATTACK",
         "GUNMEN KILL VILLAGE CHIEF AND FOUR OTHERS. REPRISALS REPORTED IN BORGU.",
         "burst"),
        ("AL-SHABAAB AMBUSH",
         "AL-SHABAAB CLAIMS HUNDREDS DEAD IN AMBUSH ON SOMALI TROOPS.",
         "burst"),
        ("GHANA'S NEW BANKNOTES",
         "GHANA UNVEILS HERITAGE BANKNOTES HONOURING NKRUMAH, ANNAN, TRADERS.",
         "doc"),
        ("EBOLA: LAST PATIENT OUT",
         "KENYA DISCHARGES LAST EBOLA PATIENT AS DRC DEATH TOLL PASSES 5,300.",
         "cross"),
    ]),
]

# Columns: (section indexes) — balanced by story count.
COLUMNS = [
    [0, 1],   # MIDDLE EAST (3) + ASIA-PACIFIC (7) = 10
    [2, 3],   # EUROPE (9) + WORLD (2) = 11
    [4, 5],   # AMERICAS (4) + AFRICA (5) = 9
]


# ---------------------------------------------------------------- layout
def draw_masthead(cv):
    cv.fill(0, 0, W, 8, RED)
    cv.text(W // 2, 16, "THE WORLD IN ONE IMAGE", 6, WHITE, "c")
    cv.text(W // 2, 66, "SUNDAY 22 NOVEMBER 2026", 3, YELLOW, "c")
    cv.hline(10, 94, W - 20, PANEL2)


def draw_hero(cv):
    x, y, w, h = 10, 100, W - 20, 178
    cv.fill(x, y, w, h, HERO_BG)
    cv.rect(x, y, w, h, RED_DK)
    cv.fill(x, y, w, 4, RED)
    cv.text(W // 2, y + 12, "GULF ON EDGE", 8, WHITE, "c")
    cv.text(W // 2, y + 78,
            "IRAN STRIKES BAHRAIN - TANKERS HIT IN HORMUZ - US BASES TARGETED",
            2, GREY, "c")
    stats = [("2", "TANKERS HIT"), ("0", "CASUALTIES"),
             ("3", "MISSILES DOWN")]
    bw = 300
    gap = 12
    total = 3 * bw + 2 * gap
    sx = (W - total) // 2
    sy = y + 116
    for i, (num, label) in enumerate(stats):
        bx = sx + i * (bw + gap)
        cv.fill(bx, sy, bw, 52, HERO_BG2)
        cv.rect(bx, sy, bw, 52, RED_DK)
        cv.text(bx + 18, sy + 12, num, 4, RED, "l")
        cv.text(bx + 62, sy + 19, label, 2, WHITE, "l")


def draw_section(cv, x, y, w, h, name, color, stories):
    # header bar
    cv.fill(x, y, w, 30, PANEL2)
    cv.fill(x, y, w, 3, color)
    cv.text(x + 10, y + 6, name, 3, WHITE, "l")
    cv.text(x + w - 10, y + 8, str(len(stories)), 2, color, "r")
    # story rows
    body_y = y + 30
    body_h = h - 30
    n = len(stories)
    row_h = body_h // n
    for i, (headline, fact, kind) in enumerate(stories):
        ry = body_y + i * row_h
        if i > 0:
            cv.hline(x, ry, w, PANEL)
        # icon box
        isz = 30
        iy = ry + (row_h - isz) // 2
        cv.fill(x + 6, iy, isz, isz, PANEL2)
        icon(cv, kind, x + 6, iy, isz, color)
        # headline + fact, vertically centred
        tx = x + 6 + isz + 8
        tw = w - (6 + isz + 8) - 8
        fact_lines = cv.wrap(fact, 1, tw)
        content_h = 14 + 3 + 7 * len(fact_lines)
        ty = ry + (row_h - content_h) // 2
        cv.text(tx, ty, headline, 2, WHITE, "l")
        for j, fl in enumerate(fact_lines):
            cv.text(tx, ty + 17 + j * 7, fl, 1, GREY, "l")


def draw_sections(cv):
    top, bot = 288, 948
    col_w = 330
    xs = [10, 347, 684]
    for ci, secs in enumerate(COLUMNS):
        x = xs[ci]
        total = sum(len(SECTIONS[s][2]) for s in secs)
        avail = bot - top
        cy = top
        for si in secs:
            name, color, stories = SECTIONS[si]
            sh = avail * len(stories) // total
            draw_section(cv, x, cy, col_w, sh, name, color, stories)
            cy += sh


def draw_bottom(cv):
    y = 956
    cv.hline(10, y, W - 20, RED)
    cv.text(10, y + 10,
            "BY THE NUMBERS  |  33 STORIES  |  6 REGIONS  |  5,300+ EBOLA DEATHS IN DRC",
            2, YELLOW, "l")
    cv.text(10, y + 28,
            "2 TANKERS HIT  |  3 MISSILES DOWN  |  11 KILLED IN MEXICO  |  6.8 PERU QUAKE",
            2, WHITE, "l")
    cv.text(10, y + 46,
            "7.2 MALUKU QUAKE  |  24 DROWNED IN NIGERIA  |  39 MISSING  |  $93 OIL",
            2, WHITE, "l")


def main():
    cv = Canvas(W, H, BG)
    draw_masthead(cv)
    draw_hero(cv)
    draw_sections(cv)
    draw_bottom(cv)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, cv)
    print("wrote %s (%d bytes)" % (path, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
