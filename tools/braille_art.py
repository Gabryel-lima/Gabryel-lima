#!/usr/bin/env python3
"""Gera as animações em pontos braille do README (SVG animado, sem JavaScript).

O desenho segue o motor Grade do CharyRick: uma tela de pontos em que cada bloco de
2x4 pontos é uma célula braille, um ponto a cada 4 px, as cores da paleta curta de
`lib/grade/palette.c` e a fonte 5x7 de `lib/grade/sprites.c`. Nada aqui é captura do
jogo: cada ponto é calculado por este script.

Peças (em assets/braille/):
  header.svg   céu em Jogo da Vida que corre e rebobina, nome na fonte 5x7 com brilho,
               lua morta com a rachadura em brasa, serra, cristais e o portal.
  orbit.svg    buraco negro: três anéis de pontos girando, com a metade de trás escondida.
  divider.svg  pulso de pontos correndo da esquerda para a direita (divisória de seção).

Uso:  python3 tools/braille_art.py [--out assets/braille] [--seed 7]
Só a biblioteca padrão. Mesma semente, mesmos arquivos (byte a byte).

Como a animação funciona: cada quadro é um <g> em <defs>; a linha do tempo é uma
sequência de <use> com a mesma animação CSS (visível só em 1/N do ciclo) e atrasos
negativos escalonados. O ping-pong (ida e volta) do céu reusa os quadros sem
duplicar pontos. Com prefers-reduced-motion, fica só o primeiro quadro.
"""
import argparse
import math
import os
import random

PITCH = 4          # px entre pontos (o passo da tela do jogo a 960x640)
DOT = 2.6          # px, espessura do ponto (traço de comprimento zero, ponta redonda)

# Paleta de lib/grade/palette.c (DotColor -> RGB).
C = {
    "bg": "#080a0c", "shadow": "#3a424e", "gray": "#78808a", "white": "#ecece2",
    "yellow": "#ffd448", "orange": "#ff8a28", "red": "#e4463e", "magenta": "#ce60dc",
    "blue": "#547cf0", "cyan": "#54d4e8", "green": "#64d674", "gold_dark": "#b07828",
    "gray_dark": "#464c5c", "ink_sky": "#2a3039", "red_dark": "#82222c", "green_dark": "#2c784a",
    "blue_dark": "#223684", "magenta_dark": "#702e84", "ink": "#12101a",
}

# Fonte 5x7 de lib/grade/sprites.c (FONT_5X7, FONT_5X7_DIGITS, DASH).
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    " ": (".....",) * 7,
}


# ---- tela de pontos -------------------------------------------------------------------

class Canvas:
    """Pontos por cor; um ponto por posição (o último pintado vence)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.dots = {}

    def set(self, x, y, color):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.dots[(x, y)] = color

    def get(self, x, y):
        return self.dots.get((x, y))

    def paths(self, opacity=None):
        """Um <path> por cor; cada ponto é 'm dx dy h0' relativo ao anterior."""
        by_color = {}
        for (x, y), col in self.dots.items():
            by_color.setdefault(col, []).append((y, x))
        out = []
        for col in sorted(by_color):
            pts = sorted(by_color[col])
            d, px, py = [], None, None
            for y, x in pts:
                X, Y = x * PITCH + PITCH // 2, y * PITCH + PITCH // 2
                d.append(f"M{X} {Y}h0" if px is None else f"m{X - px} {Y - py}h0")
                px, py = X, Y
            op = f' opacity="{opacity}"' if opacity is not None else ""
            out.append(f'<path stroke="{C[col]}"{op} d="{"".join(d)}"/>')
        return "".join(out)


def text(canvas, s, x, y, color, scale=1, shadow=None):
    """Escreve com a fonte 5x7; cada '#' vira scale x scale pontos. Devolve a largura."""
    cursor = x
    for ch in s:
        glyph = FONT[ch]
        for row, line in enumerate(glyph):
            for col, cell in enumerate(line):
                if cell != "#":
                    continue
                for dy in range(scale):
                    for dx in range(scale):
                        px, py = cursor + col * scale + dx, y + row * scale + dy
                        if shadow:
                            canvas.set(px + 1, py + 1, shadow)
                        canvas.set(px, py, color)
        cursor += 6 * scale
    return cursor - x - scale


def text_width(s, scale=1):
    return len(s) * 6 * scale - scale


def svg_open(w, h, title, extra_css=""):
    W, H = w * PITCH, h * PITCH
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="{title}"><title>{title}</title>'
        f"<style>path{{fill:none;stroke-width:{DOT};stroke-linecap:round}}{extra_css}</style>"
    )


def frame_css(name, total_s, n):
    """Animação 'visível em 1/n do ciclo' com degrau (sem fusão entre quadros)."""
    pct = 100.0 / n
    return (
        f".{name}{{opacity:0;animation:{name} {total_s:.3f}s steps(1,end) infinite}}"
        f"@keyframes {name}{{0%{{opacity:1}}{pct:.4f}%{{opacity:0}}100%{{opacity:0}}}}"
        f"@media (prefers-reduced-motion:reduce){{.{name}{{animation:none}}.{name}.first{{opacity:1}}}}"
    )


def timeline(name, frame_ids, total_s):
    """<use> por posição da linha do tempo, com atraso negativo escalonado."""
    n = len(frame_ids)
    out = []
    for i, fid in enumerate(frame_ids):
        delay = i * total_s / n - total_s
        first = " first" if i == 0 else ""
        out.append(f'<use href="#{fid}" class="{name}{first}" style="animation-delay:{delay:.3f}s"/>')
    return "".join(out)


# ---- cabeçalho ------------------------------------------------------------------------

def life_step(grid, w, h):
    nxt = set()
    counts = {}
    for (x, y) in grid:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    k = ((x + dx) % w, (y + dy) % h)
                    counts[k] = counts.get(k, 0) + 1
    for k, n in counts.items():
        if n == 3 or (n == 2 and k in grid):
            nxt.add(k)
    return nxt


def ridge_height(x, w):
    """Altura da serra (em pontos a partir do chão) em cada coluna: soma de senos."""
    return (9 + 4 * math.sin(x * 0.07) + 3 * math.sin(x * 0.17 + 1.3)
            + 2 * math.sin(x * 0.41 + 0.4) + 5 * math.exp(-((x - w * 0.22) / 14) ** 2)
            + 6 * math.exp(-((x - w * 0.74) / 16) ** 2))


def header(seed):
    W, H = 240, 64
    rng = random.Random(seed)
    ground = H - 3

    # Serra e chão: contorno em gray_dark, interior em xadrez esparso (como o título).
    static = Canvas(W, H)
    top = [ground - int(ridge_height(x, W)) for x in range(W)]
    for x in range(W):
        static.set(x, top[x], "gray")
        for y in range(top[x] + 1, ground):
            if (x + y) % 2 == 0 and (y - top[x]) % 3 != 1:
                static.set(x, y, "gray_dark" if y - top[x] < 3 else "shadow")
        static.set(x, ground, "green_dark" if rng.random() < 0.6 else "green")
        if rng.random() < 0.12:
            static.set(x, ground - 1, "green")

    # Cristais (magenta e ciano) no pé da serra.
    def crystal(cx, color, dark, height):
        for k, hh in enumerate((height - 3, height, height - 1, height - 4)):
            x = cx + k
            for y in range(ground - hh, ground):
                static.set(x, y, color if (y + k) % 3 else dark)
            static.set(x, ground - hh, "white" if k == 1 else color)
    crystal(14, "magenta", "magenta_dark", 7)
    crystal(46, "cyan", "blue_dark", 9)
    crystal(184, "magenta", "magenta_dark", 8)
    crystal(222, "cyan", "blue_dark", 6)

    # Portal: arco de pedra no centro do chão.
    pcx, pw, ph = W // 2, 16, 22
    pbase = ground
    arch = set()
    for y in range(pbase - ph, pbase):
        for x in range(pcx - pw // 2, pcx + pw // 2):
            dx = (x - pcx + 0.5) / (pw / 2)
            ytop = pbase - ph + (pw / 2) * (1 - math.sqrt(max(0.0, 1 - dx * dx)))
            if y < ytop:
                continue
            edge = abs(dx) > 0.72 or y < ytop + 2
            if edge:
                static.set(x, y, "gray" if (x + y) % 3 else "gray_dark")
            else:
                arch.add((x, y))
    for rx, ry, col in ((pcx - 7, pbase - 12, "cyan"), (pcx + 6, pbase - 8, "magenta"),
                        (pcx, pbase - ph + 1, "cyan"), (pcx - 6, pbase - 4, "magenta")):
        static.set(rx, ry, col)

    # Título e subtítulo.
    name, sub = "GABRYEL LIMA", "C11 - SDL2 - BRAILLE DOTS"
    tw = text_width(name, 2)
    tx, ty = (W - tw) // 2 - 14, 9
    title = Canvas(W, H)
    text(title, name, tx, ty, "yellow", scale=2, shadow="gold_dark")
    sw = text_width(sub)
    sx, sy = tx + (tw - sw) // 2, ty + 18
    subtitle = Canvas(W, H)
    text(subtitle, sub, sx, sy, "gray")

    # Lua morta: disco branco com crateras; a rachadura em brasa pisca em 3 variantes.
    mcx, mcy, mr = 214, 20, 13
    moon = Canvas(W, H)
    for y in range(mcy - mr, mcy + mr + 1):
        for x in range(mcx - mr, mcx + mr + 1):
            d = math.hypot(x - mcx, (y - mcy))
            if d <= mr:
                shade = "white" if (x - mcx) < mr * 0.55 - d * 0.1 else "gray"
                moon.set(x, y, shade)
    for cx, cy, r in ((mcx - 5, mcy - 4, 2.2), (mcx - 1, mcy + 6, 1.6), (mcx - 8, mcy + 3, 1.2)):
        for y in range(int(cy - r), int(cy + r) + 1):
            for x in range(int(cx - r), int(cx + r) + 1):
                if math.hypot(x - cx, y - cy) <= r:
                    moon.set(x, y, "gray")
    crack_path = []
    x, y = mcx + 2, mcy - mr + 2
    crng = random.Random(seed * 31 + 5)
    while y < mcy + mr - 1:
        crack_path.append((x, y))
        y += 1
        x += crng.choice((-2, -1, 0, 1, 1, 2))
        x = max(mcx - 2, min(mcx + mr - 2, x))
    embers = []
    for v in range(3):
        e = Canvas(W, H)
        er = random.Random(seed * 97 + v)
        for (x, y) in crack_path:
            for dx in range(0, 1 + er.randint(1, 4)):
                if math.hypot(x + dx - mcx, y - mcy) <= mr - 0.5:
                    e.set(x + dx, y, er.choice(("red", "red", "orange", "red_dark", "yellow")))
        embers.append(e)

    # Exclusões do céu.
    def blocked(x, y):
        if y >= top[x] - 1:
            return True
        if tx - 3 <= x <= tx + tw + 3 and ty - 3 <= y <= sy + 9:
            return True
        if math.hypot(x - mcx, y - mcy) <= mr + 3:
            return True
        return False

    # Céu: Jogo da Vida toroidal; 30 gerações a partir da 24 (a sopa inicial assenta).
    grid = {(x, y) for x in range(W) for y in range(H) if rng.random() < 0.22}
    for _ in range(24):
        grid = life_step(grid, W, H)
    gens = []
    for _ in range(30):
        gens.append(grid)
        grid = life_step(grid, W, H)
    sky_frames = []
    for g in gens:
        c = Canvas(W, H)
        for (x, y) in g:
            if not blocked(x, y):
                c.set(x, y, "gray_dark" if (x * 7 + y * 3) % 11 == 0 else "ink_sky")
        sky_frames.append(c)

    # Interior do portal: redemoinho de pontos em 8 quadros.
    portal_frames = []
    for f in range(8):
        c = Canvas(W, H)
        for (x, y) in arch:
            a = math.atan2(y - (pbase - ph / 2), x - pcx) + f * (2 * math.pi / 8)
            r = math.hypot(x - pcx, y - (pbase - ph / 2))
            v = math.sin(a * 3 + r * 0.9)
            if v > 0.55:
                c.set(x, y, "magenta")
            elif v > 0.15:
                c.set(x, y, "blue")
            elif v < -0.85:
                c.set(x, y, "cyan")
            else:
                if (x + y + f) % 4 == 0:
                    c.set(x, y, "magenta_dark")
        portal_frames.append(c)

    # Estrelas que piscam (CSS por estrela) e o brilho que passa no título (máscara SMIL).
    stars = []
    for i in range(34):
        for _ in range(50):
            x, y = rng.randrange(W), rng.randrange(H)
            if not blocked(x, y):
                break
        col = rng.choice(("white", "white", "cyan", "yellow", "magenta"))
        dur = rng.uniform(2.2, 5.0)
        delay = -rng.uniform(0, dur)
        X, Y = x * PITCH + PITCH // 2, y * PITCH + PITCH // 2
        big = i % 6 == 0
        d = f"M{X} {Y}h0" + (f"M{X - 4} {Y}h0M{X + 4} {Y}h0M{X} {Y - 4}h0M{X} {Y + 4}h0" if big else "")
        stars.append(f'<path class="tw" stroke="{C[col]}" style="animation-duration:{dur:.2f}s;'
                     f'animation-delay:{delay:.2f}s" d="{d}"/>')

    sky_ids = [f"s{i}" for i in range(len(gens))]
    pingpong = sky_ids + sky_ids[-2:0:-1]          # ida e volta: o céu rebobina
    css = (frame_css("sk", len(pingpong) / 5.0, len(pingpong))
           + frame_css("pt", 8 / 10.0, 8)
           + frame_css("em", 3 / 4.0, 3)
           + ".tw{animation:tw 3s ease-in-out infinite}"
           "@keyframes tw{0%,100%{opacity:.15}50%{opacity:1}}"
           "@media (prefers-reduced-motion:reduce){.tw{animation:none;opacity:.7}}")
    Wp, Hp = W * PITCH, H * PITCH
    parts = [svg_open(W, H, "Gabryel Lima, drawn in braille dots", css)]
    parts.append(
        "<defs>"
        f'<radialGradient id="halo"><stop offset="0" stop-color="{C["red"]}" stop-opacity=".28"/>'
        f'<stop offset=".5" stop-color="{C["magenta_dark"]}" stop-opacity=".12"/>'
        '<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="glow"><stop offset="0" stop-color="{C["magenta"]}" stop-opacity=".35"/>'
        '<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>'
        '<linearGradient id="band" x1="0" x2="1"><stop offset="0" stop-color="#000"/>'
        '<stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
        f'<mask id="shine"><rect width="{Wp}" height="{Hp}" fill="#000"/>'
        f'<rect y="0" width="120" height="{Hp}" fill="url(#band)">'
        f'<animate attributeName="x" values="{tx * PITCH - 160};{(tx + tw) * PITCH + 40};{(tx + tw) * PITCH + 40}" '
        'keyTimes="0;.45;1" dur="5s" repeatCount="indefinite"/></rect></mask>'
    )
    for i, c in enumerate(sky_frames):
        parts.append(f'<g id="s{i}">{c.paths()}</g>')
    for i, c in enumerate(portal_frames):
        parts.append(f'<g id="p{i}">{c.paths()}</g>')
    for i, c in enumerate(embers):
        parts.append(f'<g id="e{i}">{c.paths()}</g>')
    parts.append("</defs>")
    parts.append(f'<rect width="{Wp}" height="{Hp}" rx="12" fill="{C["bg"]}"/>')
    parts.append(f'<circle cx="{mcx * PITCH}" cy="{mcy * PITCH}" r="{mr * PITCH * 2.4}" fill="url(#halo)"/>')
    parts.append(f'<ellipse cx="{pcx * PITCH}" cy="{(pbase - ph / 2) * PITCH}" rx="{pw * PITCH * 1.6}" '
                 f'ry="{ph * PITCH * 0.9}" fill="url(#glow)"/>')
    parts.append(timeline("sk", pingpong, len(pingpong) / 5.0))
    parts.append("".join(stars))
    parts.append(static.paths())
    parts.append(timeline("pt", [f"p{i}" for i in range(8)], 8 / 10.0))
    parts.append(moon.paths())
    parts.append(timeline("em", ["e0", "e1", "e2"], 3 / 4.0))
    parts.append(title.paths())
    parts.append(f'<g mask="url(#shine)">{title.paths()}</g>'.replace(C["yellow"], C["white"])
                 .replace(C["gold_dark"], C["yellow"]))
    parts.append(subtitle.paths())
    parts.append("</svg>")
    return "".join(parts)


# ---- buraco negro ---------------------------------------------------------------------

def orbit(seed):
    W, H = 120, 40
    cx, cy, hole = 60, 20, 8.5
    frames = 24
    rings = (  # rx, ry, cor da frente, cor de trás, espaçamento (rad), voltas de espaçamento por ciclo
        (26, 6.5, "yellow", "gold_dark", 0.085, 4),
        (36, 9.0, "orange", "red_dark", 0.07, 3),
        (47, 11.5, "red", "magenta_dark", 0.06, 2),
    )
    tilt = math.radians(-11)
    ct, st = math.cos(tilt), math.sin(tilt)
    rng = random.Random(seed)
    sparks = [(rng.uniform(0, 2 * math.pi), rng.uniform(14, 50), rng.choice(("white", "magenta", "cyan")))
              for _ in range(14)]
    out_frames = []
    for f in range(frames):
        c = Canvas(W, H)
        t = f / frames
        # Anel de fótons em volta do buraco.
        for k in range(48):
            a = k * 2 * math.pi / 48 + t * 2 * math.pi / 48 * 4
            c.set(cx + (hole + 1.2) * math.cos(a) * 1.15, cy + (hole + 1.2) * math.sin(a), "magenta")
        front = []
        for rx, ry, fc, bc, step, laps in rings:
            n = int(2 * math.pi / step)
            phase = t * laps * (2 * math.pi / n)
            for k in range(n):
                a = k * 2 * math.pi / n + phase
                ex, ey = rx * math.cos(a), ry * math.sin(a)
                x, y = cx + ex * ct - ey * st, cy + ex * st + ey * ct
                if math.sin(a) < 0:                       # metade de trás
                    if math.hypot((x - cx) / 1.15, y - cy) > hole + 1.5:
                        c.set(x, y, bc)
                else:
                    front.append((x, y, fc))
        # Faíscas caindo em espiral (cada uma dá uma volta e meia por ciclo).
        for a0, r0, col in sparks:
            r = r0 * (1 - t) + 9 * t if r0 > 20 else r0
            a = a0 + t * 2 * math.pi * 1.5 * (30 / max(r, 10))
            x, y = cx + r * math.cos(a) * 1.2, cy + r * math.sin(a) * 0.45
            if math.hypot((x - cx) / 1.15, y - cy) > hole + 1:
                c.set(x, y, col)
        for x, y, col in front:
            c.set(x, y, col)
        out_frames.append(c)
    css = frame_css("ob", frames / 12.0, frames)
    Wp, Hp = W * PITCH, H * PITCH
    parts = [svg_open(W, H, "A black hole in braille dots", css)]
    parts.append("<defs>"
                 f'<radialGradient id="acc"><stop offset=".25" stop-color="{C["orange"]}" stop-opacity=".22"/>'
                 '<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>')
    for i, c in enumerate(out_frames):
        parts.append(f'<g id="o{i}">{c.paths()}</g>')
    parts.append("</defs>")
    parts.append(f'<rect width="{Wp}" height="{Hp}" rx="12" fill="{C["bg"]}"/>')
    parts.append(f'<ellipse cx="{cx * PITCH}" cy="{cy * PITCH}" rx="{52 * PITCH}" ry="{18 * PITCH}" fill="url(#acc)"/>')
    parts.append(f'<ellipse cx="{cx * PITCH + 2}" cy="{cy * PITCH + 2}" rx="{hole * PITCH * 1.15}" '
                 f'ry="{hole * PITCH}" fill="{C["ink"]}"/>')
    parts.append(timeline("ob", [f"o{i}" for i in range(frames)], frames / 12.0))
    parts.append("</svg>")
    return "".join(parts)


# ---- divisória ------------------------------------------------------------------------

def divider():
    W, H = 240, 8
    frames = 20
    period = 40
    out_frames = []
    for f in range(frames):
        c = Canvas(W, H)
        for x in range(W):
            ph = 2 * math.pi * (x / period - f / frames)
            y = 3.5 + 2.6 * math.sin(ph)
            # Pacote brilhante: um pulso que dá a volta inteira na largura por ciclo.
            head = (f / frames) * W
            dist = (x - head) % W
            if dist > W - 14:
                col = "white" if dist > W - 4 else "cyan"
            else:
                col = "magenta" if x < W * 0.5 else "blue" if x < W * 0.75 else "cyan"
                if (x + f) % 3 == 0:
                    col = col + "_dark" if col + "_dark" in C else "gray_dark"
            c.set(x, y, col)
            if x % 2 == 0:
                c.set(x, 7 - y, "shadow")
        out_frames.append(c)
    css = frame_css("dv", frames / 10.0, frames)
    parts = [svg_open(W, H, "A pulse of braille dots", css), "<defs>"]
    for i, c in enumerate(out_frames):
        parts.append(f'<g id="d{i}">{c.paths()}</g>')
    parts.append("</defs>")
    parts.append(timeline("dv", [f"d{i}" for i in range(frames)], frames / 10.0))
    parts.append("</svg>")
    return "".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "assets", "braille"))
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for name, svg in (("header.svg", header(args.seed)), ("orbit.svg", orbit(args.seed)),
                      ("divider.svg", divider())):
        path = os.path.join(args.out, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        print(f"{path}: {len(svg) / 1024:.0f} KiB")


if __name__ == "__main__":
    main()
