"""
Genera las ilustraciones de los inmuebles de prueba (SVG, 1600x1000).
Estilo: formas planas, paleta del sitio y un grano suave de impresion.
Uso: python tools/generar_ilustraciones.py app/static/img/inmuebles
"""
import sys
import pathlib

W, H = 1600, 1000

PAL = {
    'dia': dict(sky1='#a9cfcb', sky2='#eef3ec', sun='#f6ebb0', hill1='#9bbcae', hill2='#6a9a82', hill3='#3f7660',
                ground='#86ad8b', wall='#fffdf8', wall2='#ebe3d1', roof='#b94a36', door='#183c3a', glass='#4f7f92',
                glass2='#b4d6dc', wood='#c89b6d', wood2='#a87a4e', accent='#d26045', dark='#183c3a', trim='#285a54',
                lamp='#e5d78e', floor='#d9b48a', sofa='#365c70', sea='#5d93a3', sea2='#9cc6cc'),
    'alba': dict(sky1='#f1c7a4', sky2='#f8eddb', sun='#f6e4a2', hill1='#c2b6a0', hill2='#8fa388', hill3='#4f7867',
                 ground='#93a97f', wall='#fffaf0', wall2='#eadfca', roof='#9c4a38', door='#285a54', glass='#5b8294',
                 glass2='#f0d7b3', wood='#c79a6a', wood2='#a37548', accent='#d26045', dark='#183c3a', trim='#39715e',
                 lamp='#f0d98a', floor='#d6ad80', sofa='#875340', sea='#6f9aa4', sea2='#e2c9a6'),
    'tarde': dict(sky1='#dd8a62', sky2='#f3d6a6', sun='#f1b45b', hill1='#9a8591', hill2='#53707b', hill3='#2c4b4c',
                  ground='#66856c', wall='#fbf3e4', wall2='#e6d7bd', roof='#8f3f2f', door='#183c3a', glass='#365c70',
                  glass2='#efba7e', wood='#bd8a5c', wood2='#946339', accent='#d26045', dark='#14302f', trim='#285a54',
                  lamp='#f4d27a', floor='#c99c6f', sofa='#365c70', sea='#4f7f90', sea2='#e8b27c'),
}


def R(x, y, w, h, fill, rx=0, extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" {extra}/>'


def P(points, fill, extra=''):
    pts = ' '.join(f'{x},{y}' for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" {extra}/>'


def C(cx, cy, r, fill, extra=''):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" {extra}/>'


def E(cx, cy, rx, ry, fill, extra=''):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" {extra}/>'


def L(x1, y1, x2, y2, stroke, w=2, extra=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{w}" {extra}/>'


def PATH(d, fill='none', stroke='none', w=0, extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" {extra}/>'


def envolver(cuerpo, p, semilla):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">
<defs>
<linearGradient id="cielo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p['sky1']}"/><stop offset="1" stop-color="{p['sky2']}"/></linearGradient>
<linearGradient id="vidrio" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p['glass2']}"/><stop offset="1" stop-color="{p['glass']}"/></linearGradient>
<linearGradient id="agua" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p['sea2']}"/><stop offset="1" stop-color="{p['sea']}"/></linearGradient>
<linearGradient id="sombra" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".22"/></linearGradient>
<filter id="grano" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="{semilla}"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 .09"/></feComponentTransfer></filter>
</defs>
{cuerpo}
<rect width="{W}" height="{H}" filter="url(#grano)"/>
</svg>
'''


# ---------------------------------------------------------------- piezas
def cielo(p, horizonte=640, sol=(1180, 220), nubes=True):
    s = [R(0, 0, W, horizonte + 60, 'url(#cielo)'), C(sol[0], sol[1], 70, p['sun'], 'opacity=".95"'),
         C(sol[0], sol[1], 120, p['sun'], 'opacity=".18"')]
    if nubes:
        for (x, y, k) in [(220, 160, 1.0), (620, 110, .7), (1380, 330, .8)]:
            s.append(f'<g opacity=".8" fill="{p["sky2"]}">' + E(x, y, 130 * k, 26 * k, p['sky2']) +
                     E(x + 70 * k, y - 18 * k, 80 * k, 24 * k, p['sky2']) + '</g>')
    return ''.join(s)


def colinas(p, base=640, capas=3):
    cols = [p['hill1'], p['hill2'], p['hill3']]
    alt = [150, 110, 70]
    desfase = [0, 260, 520]
    s = []
    for i in range(capas):
        y = base - alt[i]
        d = f'M0 {base + 120} L0 {y + 40} '
        for k in range(0, 9):
            x = k * 220 - desfase[i] % 220
            d += f'Q{x + 110} {y - 70 + (k * 37 + i * 29) % 80} {x + 220} {y + 20 + (k * 53) % 40} '
        d += f'L{W} {base + 120} Z'
        s.append(PATH(d, p[['hill1', 'hill2', 'hill3'][i]]))
    return ''.join(s)


def arbol(x, y, k, p, tono=0):
    copas = [p['hill3'], p['hill2'], '#2f5f4d']
    t = [R(x - 9 * k, y - 120 * k, 18 * k, 120 * k, p['wood2'], 4 * k),
         C(x, y - 150 * k, 74 * k, copas[tono % 3]),
         C(x - 48 * k, y - 118 * k, 52 * k, copas[(tono + 1) % 3]),
         C(x + 50 * k, y - 124 * k, 48 * k, copas[(tono + 2) % 3]),
         C(x + 10 * k, y - 190 * k, 42 * k, copas[(tono + 1) % 3])]
    return ''.join(t)


def arbusto(x, y, k, p):
    return E(x, y, 70 * k, 38 * k, p['hill3']) + E(x + 38 * k, y + 6 * k, 52 * k, 30 * k, p['hill2'])


def ventana(x, y, w, h, p, divisiones=2, persiana=False):
    s = [R(x - 10, y - 10, w + 20, h + 20, p['trim'], 6), R(x, y, w, h, 'url(#vidrio)', 2),
         P([(x + w * .1, y + h), (x + w * .45, y), (x + w * .62, y), (x + w * .27, y + h)], '#fff', 'opacity=".22"')]
    for i in range(1, divisiones):
        s.append(L(x + w * i / divisiones, y, x + w * i / divisiones, y + h, p['trim'], 6))
    s.append(L(x, y + h * .5, x + w, y + h * .5, p['trim'], 6))
    s.append(R(x - 18, y + h + 10, w + 36, 12, p['wall2'], 3))
    return ''.join(s)


def suelo_madera(y, p, alto=None):
    alto = alto or (H - y)
    s = [R(0, y, W, alto, p['floor'])]
    for i in range(0, 14):
        yy = y + 12 + i * 34
        if yy < y + alto:
            s.append(L(0, yy, W, yy, p['wood2'], 2, 'opacity=".35"'))
    s.append(R(0, y, W, alto, 'url(#sombra)'))
    return ''.join(s)


def planta(x, y, k, p, maceta=None):
    maceta = maceta or p['accent']
    hojas = ''.join(
        PATH(f'M{x} {y - 70 * k} Q{x + dx * k} {y - 150 * k} {x + dx * 1.5 * k} {y - 210 * k - dy * k} Q{x + dx * .4 * k} {y - 150 * k} {x} {y - 70 * k}',
             [p['hill3'], p['hill2']][i % 2])
        for i, (dx, dy) in enumerate([(-70, 0), (-30, 40), (20, 20), (70, 0), (0, 70)]))
    return hojas + P([(x - 34 * k, y - 76 * k), (x + 34 * k, y - 76 * k), (x + 26 * k, y), (x - 26 * k, y)], maceta)


def sofa(x, y, w, p, color=None):
    c = color or p['sofa']
    return ''.join([
        R(x, y - 150, w, 130, c, 28), R(x - 36, y - 80, 70, 110, c, 24), R(x + w - 34, y - 80, 70, 110, c, 24),
        R(x + 20, y - 78, w - 40, 78, c, 18, 'opacity=".85"'),
        R(x + 34, y - 84, w / 2 - 44, 70, p['wall'], 14, 'opacity=".25"'),
        R(x + w / 2 + 10, y - 84, w / 2 - 44, 70, p['wall'], 14, 'opacity=".25"'),
        R(x - 10, y + 10, w + 20, 18, '#000', 8, 'opacity=".18"'),
        R(x + 40, y + 28, 14, 30, p['wood2']), R(x + w - 54, y + 28, 14, 30, p['wood2']),
        R(x + 60, y - 120, 100, 70, p['accent'], 14, 'transform="rotate(-6 %d %d)"' % (x + 110, y - 85)),
    ])


def lampara_pie(x, y, p):
    return L(x, y, x, y - 300, p['dark'], 8) + E(x, y, 46, 12, p['dark']) + \
        P([(x - 70, y - 300), (x + 70, y - 300), (x + 44, y - 380), (x - 44, y - 380)], p['lamp']) + \
        E(x, y - 296, 70, 10, p['lamp'], 'opacity=".5"')


def cuadro(x, y, w, h, p, tipo=0):
    s = [R(x - 10, y - 10, w + 20, h + 20, p['dark'], 4), R(x, y, w, h, p['wall2'])]
    if tipo == 0:
        s += [C(x + w * .62, y + h * .35, w * .16, p['accent']), P([(x, y + h), (x + w * .45, y + h * .45), (x + w * .8, y + h)], p['hill3'])]
    elif tipo == 1:
        s += [R(x + w * .15, y + h * .15, w * .3, h * .7, p['hill2']), R(x + w * .55, y + h * .3, w * .3, h * .55, p['accent'])]
    else:
        s += [E(x + w / 2, y + h / 2, w * .3, h * .3, p['glass']), E(x + w / 2, y + h / 2, w * .14, h * .14, p['lamp'])]
    return ''.join(s)


def vista_ventana(x, y, w, h, p, vista, id_clip):
    """Dibuja el paisaje que se ve desde adentro, recortado a la ventana."""
    s = [f'<clipPath id="{id_clip}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath><g clip-path="url(#{id_clip})">',
         R(x, y, w, h, 'url(#cielo)')]
    if vista == 'cerros':
        s.append(PATH(f'M{x} {y + h} L{x} {y + h * .55} Q{x + w * .2} {y + h * .25} {x + w * .4} {y + h * .5} Q{x + w * .65} {y + h * .15} {x + w} {y + h * .45} L{x + w} {y + h} Z', p['hill2']))
        s.append(PATH(f'M{x} {y + h} L{x} {y + h * .72} Q{x + w * .3} {y + h * .5} {x + w * .6} {y + h * .75} Q{x + w * .85} {y + h * .6} {x + w} {y + h * .7} L{x + w} {y + h} Z', p['hill3']))
    elif vista == 'mar':
        s.append(R(x, y + h * .55, w, h * .45, 'url(#agua)'))
        for i in range(5):
            s.append(L(x + w * .1, y + h * (.64 + i * .07), x + w * .9, y + h * (.64 + i * .07), p['sky2'], 3, 'opacity=".45"'))
        s.append(P([(x + w * .72, y + h * .55), (x + w * .86, y + h * .55), (x + w * .79, y + h * .3)], p['wall']))
    elif vista == 'ciudad':
        for i in range(9):
            bw = w / 9
            bh = h * (.25 + ((i * 37) % 5) * .09)
            s.append(R(x + i * bw, y + h - bh, bw - 4, bh, [p['hill3'], p['hill2'], p['trim']][i % 3]))
            for j in range(3):
                s.append(R(x + i * bw + 10, y + h - bh + 16 + j * 34, bw - 24, 14, p['lamp'], 2, 'opacity=".7"'))
    else:
        s.append(R(x, y + h * .6, w, h * .4, p['ground']))
        s.append(arbol(x + w * .25, y + h * .9, .8, p, 0))
        s.append(arbol(x + w * .75, y + h * .92, .6, p, 1))
    s.append('</g>')
    return ''.join(s)


# ---------------------------------------------------------------- escenas
def casa_fachada(p, pool=False, chimenea=False, semilla=1):
    s = [cielo(p, 640), colinas(p, 640, 3), R(0, 650, W, 350, p['ground']), R(0, 650, W, 350, 'url(#sombra)', 0, 'opacity=".5"')]
    s.append(arbol(150, 770, 1.15, p, 0))
    s.append(arbol(1480, 760, 1.05, p, 1))
    # camino
    s.append(P([(740, 770), (860, 770), (1010, 1000), (590, 1000)], p['wall2']))
    s.append(L(800, 790, 800, 1000, p['wall'], 4, 'opacity=".6" stroke-dasharray="24 18"'))
    # volumen principal y ala
    s.append(R(1170, 520, 250, 250, p['wall2']))
    s.append(P([(1150, 520), (1445, 520), (1400, 460), (1190, 460)], p['roof']))
    s.append(R(400, 380, 780, 390, p['wall']))
    s.append(R(400, 380, 780, 390, 'url(#sombra)', 0, 'opacity=".25"'))
    s.append(P([(360, 385), (790, 190), (1220, 385)], p['roof']))
    s.append(P([(790, 190), (1220, 385), (1190, 385), (790, 215)], '#000', 'opacity=".18"'))
    if chimenea:
        s.append(R(1000, 210, 66, 150, p['wood2'], 4))
        s.append(R(990, 200, 86, 18, p['dark'], 4))
    s.append(R(400, 600, 780, 14, p['wall2']))
    # ventanas
    s.append(ventana(490, 440, 150, 120, p, 2))
    s.append(ventana(940, 440, 150, 120, p, 2))
    s.append(ventana(490, 650, 150, 90, p, 2))
    s.append(ventana(940, 650, 150, 90, p, 2))
    s.append(ventana(1230, 590, 140, 110, p, 2))
    s.append(ventana(715, 430, 150, 110, p, 3))
    # puerta
    s.append(R(722, 620, 136, 150, p['trim'], 6))
    s.append(R(734, 632, 112, 138, p['door'], 4))
    s.append(C(826, 704, 7, p['lamp']))
    s.append(R(700, 770, 180, 14, p['wall2'], 3))
    s.append(R(680, 784, 220, 14, p['wall'], 3))
    s.append(R(760, 590, 60, 14, p['lamp'], 4, 'opacity=".9"'))
    # jardineria
    for x in (330, 470, 1020, 1160):
        s.append(arbusto(x, 780, .9, p))
    if pool:
        s.append(PATH('M140 905 Q200 860 360 870 L470 880 Q430 960 260 975 Q150 975 140 905Z', 'url(#agua)'))
        s.append(L(190, 915, 400, 925, p['sky2'], 4, 'opacity=".5"'))
    s.append(R(0, 900, W, 100, 'url(#sombra)', 0, 'opacity=".5"'))
    return envolver(''.join(s), p, semilla)


def torre_fachada(p, fondo='cerros', semilla=1, noche_calida=False):
    s = [cielo(p, 700, (1260, 210))]
    if fondo == 'cerros':
        s.append(colinas(p, 760, 3))
    elif fondo == 'mar':
        s.append(R(0, 600, W, 260, 'url(#agua)'))
        for i in range(9):
            s.append(L(100 + (i * 113) % 300, 640 + i * 24, 520 + (i * 97) % 500, 640 + i * 24, p['sky2'], 3, 'opacity=".4"'))
        s.append(R(0, 840, W, 60, p['sea2']))
    else:
        for i in range(14):
            bw, bh = 110, 220 + ((i * 53) % 6) * 50
            s.append(R(i * 118 - 20, 860 - bh, bw, bh, [p['hill2'], p['hill3'], p['trim']][i % 3], 0, 'opacity=".85"'))
    s.append(R(0, 840, W, 160, p['ground'] if fondo != 'mar' else p['sea2']))
    s.append(R(0, 880, W, 120, '#4a5558', 0, 'opacity=".8"'))
    s.append(L(0, 940, W, 940, p['wall'], 6, 'stroke-dasharray="60 40" opacity=".7"'))
    # edificios vecinos
    s.append(R(230, 360, 230, 500, p['wall2']))
    s.append(R(1150, 300, 260, 560, p['wall2']))
    for (bx, by, bw, bh) in ((230, 360, 230, 500), (1150, 300, 260, 560)):
        for r in range(bh // 80):
            for c in range(bw // 70):
                s.append(R(bx + 20 + c * 70, by + 24 + r * 80, 40, 46, p['glass'], 2, 'opacity=".75"'))
    # torre principal
    tx, ty, tw, th = 560, 110, 480, 750
    s.append(R(tx - 14, ty - 14, tw + 28, 28, p['dark'], 6))
    s.append(R(tx, ty, tw, th, p['wall']))
    s.append(R(tx + tw - 90, ty, 90, th, p['wall2']))
    s.append(R(tx, ty, tw, th, 'url(#sombra)', 0, 'opacity=".3"'))
    filas, cols = 8, 4
    for r in range(filas):
        for c in range(cols):
            wx = tx + 36 + c * 108
            wy = ty + 50 + r * 82
            lit = ((r * 3 + c * 5) % 7) < 2
            s.append(R(wx, wy, 70, 52, p['lamp'] if lit else 'url(#vidrio)', 3))
            s.append(L(wx + 35, wy, wx + 35, wy + 52, p['trim'], 3))
        if r % 2 == 1 and r < filas - 1:
            s.append(R(tx - 16, ty + 50 + r * 82 + 58, tw + 32, 14, p['wall2'], 3))
            s.append(R(tx - 16, ty + 50 + r * 82 + 40, tw + 32, 6, p['dark'], 2, 'opacity=".7"'))
    # base y portal
    s.append(R(tx - 20, ty + th - 130, tw + 40, 130, p['trim']))
    s.append(R(tx + 160, ty + th - 118, 160, 118, 'url(#vidrio)', 4))
    s.append(L(tx + 240, ty + th - 118, tx + 240, ty + th, p['trim'], 5))
    s.append(P([(tx + 130, ty + th - 128), (tx + 350, ty + th - 128), (tx + 380, ty + th - 150), (tx + 100, ty + th - 150)], p['accent']))
    for x in (440, 1120):
        s.append(arbol(x, 880, .9, p, 1))
    return envolver(''.join(s), p, semilla)


def local_fachada(p, semilla=1):
    s = [cielo(p, 520, (1340, 170))]
    s.append(R(0, 380, 300, 480, p['hill2'], 0, 'opacity=".55"'))
    s.append(R(1300, 330, 300, 530, p['hill3'], 0, 'opacity=".55"'))
    s.append(R(280, 220, 1040, 600, p['wall']))
    s.append(R(280, 220, 1040, 600, 'url(#sombra)', 0, 'opacity=".22"'))
    s.append(R(250, 190, 1100, 40, p['dark'], 4))
    s.append(R(360, 262, 880, 96, p['trim'], 8))
    s.append(R(380, 280, 840, 60, p['dark'], 4))
    for i in range(5):
        s.append(R(430 + i * 150, 298, 100, 24, p['lamp'], 12, 'opacity=".9"'))
    # toldo
    for i in range(10):
        s.append(P([(330 + i * 94, 395), (424 + i * 94, 395), (440 + i * 94, 470), (314 + i * 94, 470)], p['accent'] if i % 2 == 0 else p['wall']))
    for i in range(10):
        s.append(E(377 + i * 94, 470, 47, 14, p['accent'] if i % 2 == 0 else p['wall']))
    # vitrina
    s.append(R(350, 510, 640, 270, p['dark'], 6))
    s.append(R(368, 528, 604, 236, 'url(#vidrio)', 4))
    for i in range(3):
        s.append(R(390 + i * 190, 560, 150, 8, p['wood2']))
        s.append(R(400 + i * 190, 590, 40, 60, p['accent'], 6))
        s.append(R(450 + i * 190, 600, 36, 50, p['lamp'], 6))
        s.append(R(496 + i * 190, 580, 30, 70, p['hill3'], 6))
        s.append(R(390 + i * 190, 650, 150, 8, p['wood2']))
    s.append(P([(380, 760), (520, 528), (620, 528), (480, 760)], '#fff', 'opacity=".16"'))
    # puerta
    s.append(R(1030, 510, 200, 270, p['dark'], 6))
    s.append(R(1048, 528, 164, 252, 'url(#vidrio)', 4))
    s.append(L(1130, 528, 1130, 780, p['dark'], 6))
    s.append(R(1100, 640, 10, 50, p['wall'], 4))
    s.append(R(1150, 640, 10, 50, p['wall'], 4))
    # acera, calle
    s.append(R(0, 800, W, 90, p['wall2']))
    s.append(R(0, 890, W, 110, '#4b5659'))
    s.append(L(0, 950, W, 950, p['wall'], 8, 'stroke-dasharray="80 50"'))
    s.append(R(0, 800, W, 14, p['wall'], 0, 'opacity=".7"'))
    s.append(planta(250, 830, 1.0, p))
    s.append(planta(1330, 830, 1.0, p, p['trim']))
    s.append(L(1420, 830, 1420, 560, p['dark'], 10))
    s.append(P([(1380, 560), (1460, 560), (1440, 520), (1400, 520)], p['lamp']))
    return envolver(''.join(s), p, semilla)


def sala(p, vista='cerros', chimenea=False, semilla=1):
    s = [R(0, 0, W, H, p['wall2']), R(0, 0, W, 640, p['wall'], 0, 'opacity=".8"')]
    s.append(suelo_madera(700, p))
    s.append(R(0, 676, W, 26, p['wall'], 0, 'opacity=".95"'))
    if chimenea:
        s.append(R(980, 220, 420, 456, p['wood2']))
        for r in range(7):
            for c in range(4):
                s.append(R(990 + c * 102 + (r % 2) * 40 - 20, 232 + r * 62, 96, 54, [p['wood'], p['wall2'], p['wood2']][(r + c) % 3], 6, 'opacity=".8"'))
        s.append(R(1060, 470, 260, 206, p['dark']))
        s.append(P([(1130, 676), (1190, 520), (1250, 676)], p['accent']))
        s.append(P([(1170, 676), (1200, 580), (1230, 676)], p['lamp']))
        s.append(R(1040, 452, 300, 26, p['wall2'], 4))
        s.append(cuadro(1080, 290, 220, 120, p, 0))
        s.append(vista_ventana(200, 190, 460, 380, p, 'jardin', 'v1'))
        s.append(R(190, 180, 480, 400, 'none', 0, f'stroke="{p["trim"]}" stroke-width="16"'))
        s.append(L(430, 190, 430, 570, p['trim'], 10))
    else:
        s.append(vista_ventana(520, 150, 760, 440, p, vista, 'v1'))
        s.append(R(500, 130, 800, 480, 'none', 0, f'stroke="{p["trim"]}" stroke-width="18"'))
        s.append(L(900, 140, 900, 600, p['trim'], 10))
        s.append(L(510, 380, 1290, 380, p['trim'], 8))
        s.append(R(400, 130, 90, 560, p['accent'], 10, 'opacity=".92"'))
        s.append(R(1310, 130, 90, 560, p['accent'], 10, 'opacity=".92"'))
        s.append(P([(400, 130), (490, 130), (480, 690), (410, 690)], '#000', 'opacity=".12"'))
        s.append(cuadro(120, 260, 190, 240, p, 1))
    # alfombra y muebles
    s.append(E(760, 880, 520, 70, p['accent'], 'opacity=".85"'))
    s.append(E(760, 880, 440, 52, p['wall'], 'opacity=".28"'))
    s.append(sofa(330 if not chimenea else 150, 800, 560, p))
    s.append(R(820, 800, 280, 26, p['wood2'], 8))
    s.append(R(840, 826, 14, 50, p['wood2']))
    s.append(R(1066, 826, 14, 50, p['wood2']))
    s.append(C(900, 780, 20, p['lamp']))
    s.append(R(960, 765, 70, 36, p['wall'], 6))
    s.append(lampara_pie(1450 if not chimenea else 780, 910, p))
    s.append(planta(80 if not chimenea else 1500, 930, 1.3, p))
    s.append(R(0, 940, W, 60, 'url(#sombra)'))
    return envolver(''.join(s), p, semilla)


def cocina(p, semilla=1):
    s = [R(0, 0, W, H, p['wall'])]
    # azulejo
    for r in range(8):
        for c in range(26):
            s.append(R(c * 64 + (r % 2) * 32 - 32, 330 + r * 38, 62, 36, p['wall2'] if (r + c) % 3 else p['glass2'], 2, 'opacity=".9"'))
    s.append(R(0, 80, W, 240, p['wall'], 0))
    # alacenas
    for i in range(7):
        x = 90 + i * 210
        s.append(R(x, 90, 196, 230, p['trim'], 8))
        s.append(R(x + 12, 102, 172, 206, p['trim'], 4, 'opacity=".75"'))
        s.append(R(x + 90, 270, 16, 30, p['lamp'], 4))
    s.append(R(60, 78, W - 120, 20, p['dark'], 4))
    # campana
    s.append(P([(560, 330), (760, 330), (720, 400), (600, 400)], p['dark']))
    # mesón
    s.append(R(0, 640, W, 30, p['wood2']))
    s.append(R(0, 670, W, 330, p['trim']))
    for i in range(9):
        s.append(R(40 + i * 175, 690, 160, 230, p['trim'], 6, 'opacity=".7"'))
        s.append(R(100 + i * 175, 700, 40, 10, p['lamp'], 4))
    s.append(R(0, 920, W, 80, p['dark']))
    s.append(R(440, 560, 220, 80, p['wall2'], 6))
    s.append(R(470, 540, 160, 24, p['dark'], 6))
    # isla
    s.append(R(250, 760, 1100, 40, p['wall'], 8))
    s.append(R(250, 800, 1100, 170, p['wood'], 6))
    s.append(R(250, 800, 1100, 170, 'url(#sombra)', 0, 'opacity=".5"'))
    for i in range(3):
        x = 400 + i * 380
        s.append(L(x, 120, x, 470, p['dark'], 4))
        s.append(PATH(f'M{x - 70} 520 Q{x} 410 {x + 70} 520Z', p['accent']))
        s.append(E(x, 524, 70, 10, p['lamp']))
    for i in range(4):
        x = 360 + i * 240
        s.append(R(x, 850, 120, 26, p['dark'], 12))
        s.append(L(x + 20, 876, x + 14, 980, p['dark'], 8))
        s.append(L(x + 100, 876, x + 106, 980, p['dark'], 8))
    s.append(planta(1480, 770, .7, p))
    s.append(R(1050, 700, 110, 60, p['lamp'], 10))
    return envolver(''.join(s), p, semilla)


def habitacion(p, vista='ciudad', semilla=1):
    s = [R(0, 0, W, H, p['wall2']), R(0, 0, W, 700, p['wall'], 0, 'opacity=".85"'), suelo_madera(720, p)]
    s.append(R(0, 696, W, 26, p['wall2']))
    s.append(vista_ventana(1000, 160, 420, 380, p, vista, 'v2'))
    s.append(R(990, 150, 440, 400, 'none', 0, f'stroke="{p["trim"]}" stroke-width="14"'))
    s.append(L(1210, 160, 1210, 540, p['trim'], 8))
    s.append(R(940, 130, 70, 520, p['sofa'], 10, 'opacity=".9"'))
    s.append(R(1410, 130, 70, 520, p['sofa'], 10, 'opacity=".9"'))
    # cama
    s.append(R(150, 230, 700, 300, p['wood2'], 24))
    s.append(R(180, 260, 640, 250, p['wood'], 14, 'opacity=".55"'))
    s.append(R(130, 520, 740, 210, p['wall'], 26))
    s.append(R(130, 600, 740, 150, p['sofa'], 22))
    for i in range(6):
        s.append(R(130 + i * 124, 600, 62, 150, p['wall'], 0, 'opacity=".12"'))
    s.append(R(130, 580, 740, 26, p['accent'], 8))
    s.append(R(190, 460, 240, 110, p['wall'], 30))
    s.append(R(450, 460, 240, 110, p['wall2'], 30))
    s.append(R(710, 480, 120, 90, p['accent'], 20))
    s.append(R(130, 730, 740, 26, p['wood2'], 6))
    s.append(R(150, 756, 18, 60, p['wood2']))
    s.append(R(832, 756, 18, 60, p['wood2']))
    # mesas de noche
    for x in (30, 880):
        s.append(R(x, 560, 100, 190, p['wood'], 8))
        s.append(R(x + 8, 600, 84, 6, p['wood2']))
        s.append(R(x + 8, 680, 84, 6, p['wood2']))
    s.append(L(80, 560, 80, 490, p['dark'], 6))
    s.append(P([(40, 490), (120, 490), (100, 430), (60, 430)], p['lamp']))
    s.append(L(930, 560, 930, 490, p['dark'], 6))
    s.append(P([(890, 490), (970, 490), (950, 430), (910, 430)], p['lamp']))
    s.append(cuadro(380, 80, 240, 120, p, 2))
    s.append(E(1180, 900, 380, 54, p['accent'], 'opacity=".8"'))
    s.append(planta(1500, 930, 1.2, p))
    s.append(R(0, 940, W, 60, 'url(#sombra)'))
    return envolver(''.join(s), p, semilla)


def interior_local(p, semilla=1):
    s = [R(0, 0, W, H, p['wall'])]
    s.append(suelo_madera(760, p))
    # mezzanine
    s.append(R(0, 290, W, 34, p['dark']))
    s.append(R(0, 324, W, 20, p['dark'], 0, 'opacity=".4"'))
    s.append(R(0, 80, W, 210, p['wall2']))
    for i in range(18):
        s.append(L(i * 96 + 20, 290, i * 96 + 20, 220, p['trim'], 6))
    s.append(L(0, 220, W, 220, p['trim'], 10))
    s.append(R(1180, 150, 320, 140, p['glass2'], 6, 'opacity=".5"'))
    # escalera
    for i in range(8):
        s.append(R(1240 - i * 36, 330 + i * 52, 150, 22, p['wood2']))
        s.append(R(1240 - i * 36, 352 + i * 52, 150, 30, p['wood'], 0, 'opacity=".7"'))
    # estanterias
    for i in range(4):
        x = 70 + i * 250
        s.append(R(x, 410, 220, 350, p['wood2'], 4))
        for r in range(4):
            s.append(R(x + 10, 420 + r * 84, 200, 76, p['wall2']))
            for k in range(5):
                s.append(R(x + 20 + k * 38, 432 + r * 84 + (k % 2) * 8, 28, 56 - (k % 2) * 8, [p['accent'], p['hill2'], p['lamp'], p['glass']][(k + r) % 4], 3))
    # mostrador
    s.append(R(1060, 620, 440, 180, p['trim'], 8))
    s.append(R(1040, 600, 480, 30, p['wood'], 6))
    s.append(R(1200, 540, 130, 60, p['dark'], 6))
    s.append(R(1210, 548, 110, 40, p['glass2'], 4))
    for i in range(3):
        x = 300 + i * 300
        s.append(L(x, 344, x, 520, p['dark'], 4))
        s.append(PATH(f'M{x - 60} 590 Q{x} 500 {x + 60} 590Z', p['lamp']))
    s.append(R(0, 940, W, 60, 'url(#sombra)'))
    return envolver(''.join(s), p, semilla)


def terraza(p, vista='ciudad', bbq=True, semilla=1):
    s = [cielo(p, 560, (1250, 200))]
    if vista == 'mar':
        s.append(R(0, 460, W, 220, 'url(#agua)'))
        for i in range(8):
            s.append(L(120 + (i * 151) % 400, 500 + i * 22, 560 + (i * 97) % 600, 500 + i * 22, p['sky2'], 3, 'opacity=".45"'))
    elif vista == 'ciudad':
        for i in range(16):
            bw, bh = 100, 120 + ((i * 59) % 7) * 36
            s.append(R(i * 104, 640 - bh, bw, bh, [p['hill2'], p['hill3'], p['trim']][i % 3], 0, 'opacity=".9"'))
            for j in range(bh // 40):
                s.append(R(i * 104 + 12, 640 - bh + 14 + j * 40, 28, 16, p['lamp'], 2, 'opacity=".65"'))
    else:
        s.append(colinas(p, 620, 3))
        s.append(R(0, 600, W, 120, p['ground']))
        s.append(arbol(300, 640, .8, p, 1))
        s.append(arbol(1300, 650, .9, p, 0))
    s.append(R(0, 650, W, 350, p['wood']))
    for i in range(16):
        s.append(L(0, 690 + i * 22, W, 690 + i * 22, p['wood2'], 2, 'opacity=".4"'))
    s.append(R(0, 640, W, 24, p['dark']))
    # baranda
    for i in range(34):
        s.append(R(i * 48 + 8, 520, 8, 130, p['dark']))
    s.append(R(0, 500, W, 26, p['dark']))
    s.append(R(0, 526, W, 8, p['dark'], 0, 'opacity=".4"'))
    # mesa y sillas
    s.append(E(520, 870, 190, 36, '#000', 'opacity=".16"'))
    s.append(E(520, 780, 170, 28, p['wall']))
    s.append(R(512, 780, 16, 100, p['dark']))
    for x in (300, 700):
        s.append(R(x - 50, 760, 100, 20, p['accent'], 8))
        s.append(R(x - 46, 700, 14, 70, p['accent'], 6))
        s.append(L(x - 40, 780, x - 44, 880, p['dark'], 8))
        s.append(L(x + 40, 780, x + 44, 880, p['dark'], 8))
    # sombrilla
    s.append(L(520, 780, 520, 420, p['dark'], 8))
    s.append(PATH('M300 460 Q520 280 740 460Z', p['accent']))
    s.append(PATH('M410 400 Q520 290 630 400 Q520 440 410 400Z', p['wall'], '', 0, 'opacity=".35"'))
    if bbq:
        s.append(R(1060, 700, 300, 150, p['dark'], 10))
        s.append(R(1040, 680, 340, 36, p['trim'], 10))
        s.append(R(1090, 650, 240, 14, p['wood2'], 4))
        for i in range(6):
            s.append(R(1100 + i * 40, 716, 28, 100, p['accent'] if i % 2 else p['lamp'], 4, 'opacity=".85"'))
        s.append(L(1090, 850, 1070, 960, p['dark'], 10))
        s.append(L(1330, 850, 1350, 960, p['dark'], 10))
        s.append(E(1120, 620, 18, 40, p['wall'], 'opacity=".5"'))
        s.append(E(1180, 600, 22, 50, p['wall'], 'opacity=".4"'))
    s.append(planta(1480, 900, 1.2, p))
    s.append(planta(80, 930, 1.1, p, p['trim']))
    return envolver(''.join(s), p, semilla)


def jardin_piscina(p, semilla=1):
    s = [cielo(p, 560, (1300, 190)), colinas(p, 560, 2), R(0, 520, W, 480, p['ground'])]
    s.append(arbol(200, 640, 1.1, p, 0))
    s.append(arbol(1400, 620, 1.0, p, 1))
    s.append(R(0, 380, 280, 300, p['wall']))
    s.append(P([(-20, 380), (300, 380), (260, 330), (20, 330)], p['roof']))
    s.append(ventana(60, 450, 150, 120, p, 2))
    # deck + piscina
    s.append(P([(180, 960), (1420, 960), (1320, 640), (280, 640)], p['wood']))
    for i in range(10):
        s.append(L(280 - i * 10, 640 + i * 36, 1320 + i * 10, 640 + i * 36, p['wood2'], 2, 'opacity=".4"'))
    s.append(PATH('M380 700 Q380 660 440 660 L1180 660 Q1240 660 1240 700 L1280 860 Q1280 910 1220 910 L420 910 Q340 910 340 860Z', 'url(#agua)'))
    s.append(PATH('M380 700 Q380 660 440 660 L1180 660 Q1240 660 1240 700 L1280 860 Q1280 910 1220 910 L420 910 Q340 910 340 860Z', 'none', p['wall'], 10))
    for i in range(7):
        s.append(PATH(f'M{440 + i * 20} {700 + i * 30} q60 -16 120 0 t120 0 t120 0', 'none', p['sky2'], 4, 'opacity=".5"'))
    # sillas de sol
    for x in (150, 1330):
        s.append(P([(x, 800), (x + 150, 800), (x + 190, 770), (x + 150, 750), (x + 30, 750)], p['wall']))
        s.append(P([(x + 150, 800), (x + 190, 770), (x + 210, 700), (x + 170, 700)], p['accent']))
        s.append(L(x + 10, 800, x, 850, p['dark'], 6))
        s.append(L(x + 140, 800, x + 150, 850, p['dark'], 6))
    s.append(planta(1500, 960, 1.2, p))
    return envolver(''.join(s), p, semilla)


def lote_panoramica(p, variante=0, semilla=1):
    s = [cielo(p, 520, (330 + variante * 700, 200)), colinas(p, 520, 3)]
    s.append(R(0, 500, W, 500, p['ground']))
    # surcos con perspectiva
    for i in range(-10, 22):
        x = 800 + i * 150
        s.append(PATH(f'M800 520 L{x} 1000 L{x + 90} 1000Z', p['hill2'] if i % 2 else p['ground'], '', 0, 'opacity=".7"'))
    s.append(R(0, 500, W, 80, p['hill1'], 0, 'opacity=".4"'))
    # cerca de linderos
    for i in range(12):
        t = i / 11
        x = 80 + t * 560
        y = 560 + t * t * 380
        h = 60 + t * 150
        s.append(R(x, y - h, 10 + t * 8, h, p['wood2'], 2))
    s.append(PATH('M80 520 Q380 560 700 750 M80 500 Q380 540 700 700', 'none', p['dark'], 3, 'opacity=".7"'))
    # arboles
    for (x, y, k, t) in ((1200, 600, .7, 0), (1320, 620, .9, 1), (1060, 590, .55, 2), (1450, 660, 1.1, 0)):
        s.append(arbol(x, y, k, p, t))
    # letrero
    s.append(R(940, 700, 14, 220, p['wood2']))
    s.append(R(1120, 700, 14, 220, p['wood2']))
    s.append(R(900, 640, 270, 120, p['wall'], 8))
    s.append(R(916, 656, 238, 88, p['accent'], 4))
    s.append(R(940, 676, 190, 14, p['wall'], 3))
    s.append(R(960, 704, 150, 14, p['wall'], 3))
    s.append(R(0, 940, W, 60, 'url(#sombra)'))
    return envolver(''.join(s), p, semilla)


def lote_plano(p, semilla=1):
    papel = p['wall']
    s = [R(0, 0, W, H, papel)]
    for i in range(0, 41):
        s.append(L(i * 40, 0, i * 40, H, p['wall2'], 2))
    for i in range(0, 26):
        s.append(L(0, i * 40, W, i * 40, p['wall2'], 2))
    # lote 40 x 30 m (escala 16 px por metro)
    x0, y0, lw, lh = 440, 250, 640, 480
    s.append(R(x0, y0, lw, lh, p['hill2'], 0, 'opacity=".25"'))
    for i in range(-lh, lw, 28):
        s.append(L(x0 + max(i, 0), y0 + max(-i, 0), x0 + min(i + lh, lw), y0 + min(lw - i, lh), p['hill3'], 2, 'opacity=".35"'))
    s.append(R(x0, y0, lw, lh, 'none', 0, f'stroke="{p["dark"]}" stroke-width="6" stroke-dasharray="22 10"'))
    for (cx, cy) in ((x0, y0), (x0 + lw, y0), (x0, y0 + lh), (x0 + lw, y0 + lh)):
        s.append(C(cx, cy, 14, p['accent']))
    # cotas
    s.append(L(x0, y0 - 54, x0 + lw, y0 - 54, p['dark'], 3))
    s.append(L(x0, y0 - 70, x0, y0 - 38, p['dark'], 3))
    s.append(L(x0 + lw, y0 - 70, x0 + lw, y0 - 38, p['dark'], 3))
    s.append(f'<text x="{x0 + lw / 2}" y="{y0 - 70}" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="30" font-weight="600" fill="{p["dark"]}">40 m</text>')
    s.append(L(x0 + lw + 60, y0, x0 + lw + 60, y0 + lh, p['dark'], 3))
    s.append(L(x0 + lw + 44, y0, x0 + lw + 76, y0, p['dark'], 3))
    s.append(L(x0 + lw + 44, y0 + lh, x0 + lw + 76, y0 + lh, p['dark'], 3))
    s.append(f'<text x="{x0 + lw + 96}" y="{y0 + lh / 2 + 10}" font-family="Segoe UI, Arial, sans-serif" font-size="30" font-weight="600" fill="{p["dark"]}">30 m</text>')
    s.append(f'<text x="{x0 + lw / 2}" y="{y0 + lh / 2 + 12}" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="44" font-weight="700" fill="{p["dark"]}">1.200 m²</text>')
    # via de acceso
    s.append(R(0, y0 + lh + 60, W, 90, '#4b5659'))
    s.append(L(0, y0 + lh + 105, W, y0 + lh + 105, papel, 5, 'stroke-dasharray="50 30"'))
    s.append(R(x0 + 260, y0 + lh, 120, 60, p['wood']))
    # norte
    s.append(PATH('M1360 200 L1400 300 L1360 280 L1320 300Z', p['dark']))
    s.append(f'<text x="1360" y="180" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="32" font-weight="700" fill="{p["dark"]}">N</text>')
    # escala
    s.append(R(180, 880, 160, 10, p['dark']))
    s.append(R(340, 880, 160, 10, papel, 0, f'stroke="{p["dark"]}" stroke-width="3"'))
    s.append(f'<text x="180" y="925" font-family="Segoe UI, Arial, sans-serif" font-size="24" fill="{p["dark"]}">0</text><text x="480" y="925" font-family="Segoe UI, Arial, sans-serif" font-size="24" fill="{p["dark"]}">20 m</text>')
    return envolver(''.join(s), p, semilla)


def lote_entorno(p, semilla=1):
    s = [cielo(p, 480, (1150, 210)), colinas(p, 480, 3), R(0, 470, W, 530, p['ground'])]
    # carretera que se aleja
    s.append(P([(740, 480), (860, 480), (1220, 1000), (260, 1000)], '#4f5a5c'))
    s.append(P([(796, 480), (804, 480), (830, 1000), (770, 1000)], p['wall'], 'opacity=".8"'))
    s.append(P([(740, 480), (748, 480), (270, 1000), (230, 1000)], p['wall2'], 'opacity=".8"'))
    # casas lejanas
    for (x, y, k) in ((1040, 500, .8), (1210, 520, 1.0), (1380, 560, 1.2)):
        s.append(R(x, y - 60 * k, 120 * k, 60 * k, p['wall']))
        s.append(P([(x - 10 * k, y - 60 * k), (x + 60 * k, y - 110 * k), (x + 130 * k, y - 60 * k)], p['roof']))
        s.append(R(x + 44 * k, y - 36 * k, 30 * k, 36 * k, p['door']))
    for (x, y, k, t) in ((120, 640, 1.3, 0), (380, 600, .9, 1), (520, 570, .6, 2), (1010, 640, .7, 1), (1480, 800, 1.4, 0)):
        s.append(arbol(x, y, k, p, t))
    s.append(R(0, 920, W, 80, 'url(#sombra)'))
    return envolver(''.join(s), p, semilla)


# ---------------------------------------------------------------- catalogo
def construir():
    A, D, T = PAL['alba'], PAL['dia'], PAL['tarde']
    return {
        1: [('fachada', 'Fachada del edificio en Chapinero Alto', torre_fachada(D, 'cerros', 11)),
            ('sala', 'Sala con vista a los cerros', sala(D, 'cerros', False, 12)),
            ('cocina', 'Cocina abierta', cocina(D, 13)),
            ('alcoba', 'Alcoba principal', habitacion(D, 'cerros', 14))],
        2: [('fachada', 'Fachada de la casa campestre', casa_fachada(A, False, True, 21)),
            ('sala', 'Sala con chimenea', sala(A, 'jardin', True, 22)),
            ('bbq', 'Zona BBQ y jardín', terraza(A, 'campo', True, 23)),
            ('alcoba', 'Alcoba principal', habitacion(A, 'jardin', 24))],
        3: [('fachada', 'Edificio en El Poblado', torre_fachada(T, 'ciudad', 31)),
            ('sala', 'Sala amoblada', sala(T, 'ciudad', False, 32)),
            ('alcoba', 'Alcoba amoblada', habitacion(T, 'ciudad', 33))],
        4: [('fachada', 'Vitrina a pie de calle', local_fachada(D, 41)),
            ('interior', 'Interior con mezzanine', interior_local(D, 42))],
        5: [('panoramica', 'Vista general del lote', lote_panoramica(A, 0, 51)),
            ('plano', 'Plano y medidas del lote', lote_plano(D, 52)),
            ('entorno', 'Entorno y vía de acceso', lote_entorno(A, 53))],
        6: [('fachada', 'Fachada de la casa', casa_fachada(D, False, False, 61)),
            ('piscina', 'Piscina y patio', jardin_piscina(D, 62)),
            ('sala', 'Sala', sala(D, 'jardin', False, 63))],
        7: [('fachada', 'Edificio en Cabecera del Llano', torre_fachada(A, 'ciudad', 71)),
            ('terraza', 'Terraza con zona BBQ', terraza(A, 'ciudad', True, 72)),
            ('sala', 'Sala del dúplex', sala(A, 'ciudad', False, 73)),
            ('alcoba', 'Alcoba principal', habitacion(A, 'ciudad', 74))],
        8: [('fachada', 'Edificio frente a la bahía', torre_fachada(T, 'mar', 81)),
            ('sala', 'Sala con vista al mar', sala(T, 'mar', False, 82)),
            ('balcon', 'Balcón frente a la bahía', terraza(T, 'mar', False, 83))],
    }


if __name__ == '__main__':
    salida = pathlib.Path(sys.argv[1])
    salida.mkdir(parents=True, exist_ok=True)
    total = 0
    for id_inmueble, vistas in construir().items():
        for orden, (clave, descripcion, svg) in enumerate(vistas, start=1):
            nombre = f'inmueble-{id_inmueble}-{orden}-{clave}.svg'
            (salida / nombre).write_text(svg, encoding='utf-8')
            total += 1
    print(total, 'ilustraciones en', salida)
