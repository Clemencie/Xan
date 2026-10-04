# -*- coding: utf-8 -*-
"""
XAN — Mapas em SVG (sem dependências externas).
===============================================

Desenha o mundo gerado como uma grade hexagonal: províncias coloridas pelo
elemento dominante, marcadores por tipo de sítio, legenda, escala e a semente
gravada no próprio arquivo — para que qualquer pessoa possa regenerar o mapa e
conferir que é o mesmo mundo.

Saída: SVG 1.1 puro, texto UTF-8, abrível em qualquer navegador.
"""

from __future__ import annotations

import html
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

__all__ = [
    "COR_POR_ELEMENTO", "SIMBOLO_POR_TIPO", "axial_para_pixel",
    "poligono_hexagonal", "mapa_do_mundo", "mapa_da_provincia", "salvar_svg",
]

COR_POR_ELEMENTO: Dict[str, str] = {
    "madeira": "#3f7d43",
    "fogo": "#a83a26",
    "terra": "#a8842f",
    "metal": "#8f9aa6",
    "agua": "#2f5f8f",
    "nenhum": "#6b6b6b",
    "vazio": "#4a3b6b",
}
_COR_FUNDO = {
    "montanhas": "#5d5346", "planicies": "#7d8a52", "florestas": "#3f6b3f",
    "deserto": "#c2a86b", "tundra": "#a9bcc4", "litoral": "#5d8fa8",
    "arquipelago": "#4a7f9e", "pantano": "#5c6b4a", "vales": "#6f8a55",
    "planalto": "#8a7f5d", "vulcanico": "#7d4030", "estepe": "#98a06a",
}

SIMBOLO_POR_TIPO: Dict[str, str] = {
    "seita_ortodoxa": "☯", "seita_nao_ortodoxa": "☰", "culto_demoniaco": "☠",
    "cla_nobre": "⚑", "cidade": "▣", "vila": "▪", "mercado_negro": "◈",
    "ruina": "⌂", "caverna_de_bestas": "⩕", "floresta_proibida": "⫯",
    "pico_de_cultivo": "▲", "lago_espiritual": "◉", "templo": "卍",
    "reino_secreto": "✦", "fortaleza": "♜", "porto": "⚓",
    "passo_de_montanha": "⌃", "campo_de_batalha": "⚔", "veia_espiritual": "≋",
    "tumba_antiga": "†", "mosteiro": "☸", "torre_de_observacao": "⌖",
}


def axial_para_pixel(q: int, r: int, tamanho: float) -> Tuple[float, float]:
    """Conversão axial → pixel para hexágonos de topo pontiagudo."""
    x = tamanho * math.sqrt(3.0) * (q + r / 2.0)
    y = tamanho * 1.5 * r
    return x, y


def poligono_hexagonal(cx: float, cy: float, tamanho: float) -> str:
    pts = []
    for i in range(6):
        ang = math.pi / 180.0 * (60 * i - 30)
        pts.append(f"{cx + tamanho * math.cos(ang):.2f},"
                   f"{cy + tamanho * math.sin(ang):.2f}")
    return " ".join(pts)


def _esc(texto: Any) -> str:
    return html.escape(str(texto), quote=True)


def mapa_do_mundo(
    mundo: Mapping[str, Any],
    *,
    tamanho_hex: int = 118,
    mostrar_sitios: bool = True,
    titulo: Optional[str] = None,
) -> str:
    """Gera o SVG do continente inteiro."""
    provincias = mundo["provincias"]
    if not provincias:
        raise ValueError("o mundo não tem províncias")

    coords = [(axial_para_pixel(p["q"], p["r"], tamanho_hex)) for p in provincias]
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    margem = tamanho_hex * 2.1
    largura = (max(xs) - min(xs)) + margem * 2
    altura = (max(ys) - min(ys)) + margem * 2 + 190
    dx = -min(xs) + margem
    dy = -min(ys) + margem

    P: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
        f'width="{largura:.0f}" height="{altura:.0f}" '
        f'viewBox="0 0 {largura:.0f} {altura:.0f}" font-family="serif">',
        f'<rect width="{largura:.0f}" height="{altura:.0f}" fill="#f3ead7"/>',
        '<defs>',
        '<filter id="sombra" x="-20%" y="-20%" width="140%" height="140%">',
        '<feDropShadow dx="2" dy="3" stdDeviation="3" flood-opacity="0.35"/>',
        '</filter>',
        '</defs>',
    ]

    cab = titulo or mundo.get("nome", "Mundo")
    P += [
        f'<text x="{largura/2:.0f}" y="34" text-anchor="middle" font-size="26" '
        f'fill="#2b2118" font-weight="bold">{_esc(cab)}</text>',
        f'<text x="{largura/2:.0f}" y="58" text-anchor="middle" font-size="13" '
        f'fill="#6b5a45">semente <tspan font-family="monospace">'
        f'{_esc(mundo.get("semente",""))}</tspan> · ano '
        f'{mundo.get("ano_atual","?")} · gerador '
        f'{_esc(mundo.get("versao_do_gerador",""))}</text>',
    ]

    for p, (px, py) in zip(provincias, coords):
        cx, cy = px + dx, py + dy
        cor = COR_POR_ELEMENTO.get(p["elemento"], "#6b6b6b")
        terreno = _COR_FUNDO.get(p["terreno"], "#7a7a6a")
        P.append(
            f'<polygon points="{poligono_hexagonal(cx, cy, tamanho_hex)}" '
            f'fill="{terreno}" stroke="{cor}" stroke-width="7" '
            f'filter="url(#sombra)" opacity="0.96"/>')
        P.append(
            f'<polygon points="{poligono_hexagonal(cx, cy, tamanho_hex*0.86)}" '
            f'fill="none" stroke="{cor}" stroke-width="1.5" opacity="0.55"/>')
        P.append(
            f'<text x="{cx:.1f}" y="{cy-16:.1f}" text-anchor="middle" '
            f'font-size="19" fill="#fdf7e8" font-weight="bold">'
            f'{_esc(p["nome"])}</text>')
        P.append(
            f'<text x="{cx:.1f}" y="{cy+4:.1f}" text-anchor="middle" '
            f'font-size="16" fill="#f0e6d0">{_esc(p["chines"])}</text>')
        P.append(
            f'<text x="{cx:.1f}" y="{cy+22:.1f}" text-anchor="middle" '
            f'font-size="11" fill="#e8dcc4">{_esc(p["elemento"])} · '
            f'{_esc(p["terreno"])}</text>')
        P.append(
            f'<text x="{cx:.1f}" y="{cy+38:.1f}" text-anchor="middle" '
            f'font-size="11" fill="#e8dcc4">Qi {p["densidade_qi"]}/10 '
            f'({_esc(p["densidade_qi_fato"])}) · perigo {p["perigo"]}/10</text>')

        if mostrar_sitios:
            sitios = sorted(p.get("sitios", []), key=lambda s: -s["nivel"])[:8]
            n = len(sitios)
            for i, s in enumerate(sitios):
                ang = 2 * math.pi * i / max(1, n) - math.pi / 2
                rx = tamanho_hex * 0.58
                sx = cx + rx * math.cos(ang)
                sy = cy + rx * math.sin(ang)
                sim = SIMBOLO_POR_TIPO.get(s["tipo"], "•")
                cor_s = ("#e24b3a" if "demoniaco" in s["tipo"] or
                         s["tipo"] in ("ruina", "campo_de_batalha",
                                       "tumba_antiga", "floresta_proibida")
                         else "#ffe9a8")
                P.append(
                    f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="11" fill="#1d1a15" '
                    f'opacity="0.55"/>')
                P.append(
                    f'<text x="{sx:.1f}" y="{sy+5:.1f}" text-anchor="middle" '
                    f'font-size="14" fill="{cor_s}">{_esc(sim)}</text>')
                P.append(
                    f'<title>{_esc(s["nome"])} ({_esc(s["tipo"])}) — nível '
                    f'{s["nivel"]}, perigo {s["perigo"]}/10, Qi '
                    f'{s["densidade_qi"]}/10. Segredo: {_esc(s["segredo"])}</title>')

    # legenda
    ly = altura - 150
    P.append(f'<rect x="24" y="{ly-24:.0f}" width="{largura-48:.0f}" height="140" '
             'fill="#e7dcc2" stroke="#a89878" rx="6"/>')
    P.append(f'<text x="40" y="{ly:.0f}" font-size="15" fill="#2b2118" '
             'font-weight="bold">Legenda</text>')
    lx = 40
    for i, (tipo, sim) in enumerate(sorted(SIMBOLO_POR_TIPO.items())):
        col = i % 8
        row = i // 8
        x = lx + col * ((largura - 100) / 8)
        y = ly + 22 + row * 17
        P.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="11" fill="#3a2f22">'
                 f'{_esc(sim)} {_esc(tipo.replace("_"," "))}</text>')
    # elementos
    ex = lx
    ey = ly + 22 + ((len(SIMBOLO_POR_TIPO) + 7) // 8) * 17 + 8
    for elem, cor in COR_POR_ELEMENTO.items():
        P.append(f'<rect x="{ex:.0f}" y="{ey-9:.0f}" width="12" height="12" '
                 f'fill="{cor}"/>')
        P.append(f'<text x="{ex+17:.0f}" y="{ey+1:.0f}" font-size="11" '
                 f'fill="#3a2f22">{_esc(elem)}</text>')
        ex += 17 + 9 * len(elem) + 18
    P.append('</svg>')
    return "\n".join(P)


def mapa_da_provincia(
    provincia: Mapping[str, Any],
    *,
    tamanho_hex: int = 92,
    nome_do_mundo: str = "",
) -> str:
    """Mapa de detalhe de uma província: um hexágono por sítio."""
    sitios = provincia.get("sitios", [])
    if not sitios:
        raise ValueError(f"a província {provincia.get('nome')} não tem sítios")
    n = len(sitios)
    colunas = max(1, int(math.ceil(math.sqrt(n * 1.4))))
    linhas = int(math.ceil(n / colunas))
    largura = colunas * tamanho_hex * 1.85 + 120
    altura = linhas * tamanho_hex * 1.7 + 200
    cor = COR_POR_ELEMENTO.get(provincia["elemento"], "#6b6b6b")

    P = [
        f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
        f'width="{largura:.0f}" height="{altura:.0f}" '
        f'viewBox="0 0 {largura:.0f} {altura:.0f}" font-family="serif">',
        f'<rect width="{largura:.0f}" height="{altura:.0f}" '
        f'fill="{_COR_FUNDO.get(provincia["terreno"], "#7a7a6a")}"/>',
        f'<text x="{largura/2:.0f}" y="36" text-anchor="middle" font-size="24" '
        f'fill="#fdf7e8" font-weight="bold">{_esc(provincia["nome"])} '
        f'{_esc(provincia["chines"])}</text>',
        f'<text x="{largura/2:.0f}" y="60" text-anchor="middle" font-size="13" '
        f'fill="#e8dcc4">{_esc(nome_do_mundo)} · elemento '
        f'{_esc(provincia["elemento"])} · Qi {provincia["densidade_qi"]}/10 · '
        f'perigo {provincia["perigo"]}/10 · {n} sítios</text>',
    ]
    for i, s in enumerate(sorted(sitios, key=lambda x: (-x["nivel"], x["nome"]))):
        col = i % colunas
        row = i // colunas
        cx = 70 + col * tamanho_hex * 1.85 + tamanho_hex
        cy = 110 + row * tamanho_hex * 1.7 + tamanho_hex
        sim = SIMBOLO_POR_TIPO.get(s["tipo"], "•")
        demoniaco = "demoniaco" in s["tipo"] or s["tipo"] in (
            "ruina", "campo_de_batalha", "tumba_antiga", "floresta_proibida",
            "caverna_de_bestas")
        P.append(
            f'<polygon points="{poligono_hexagonal(cx, cy, tamanho_hex*0.92)}" '
            f'fill="#2a241c" opacity="0.72" stroke="{cor}" stroke-width="3"/>')
        P.append(f'<text x="{cx:.1f}" y="{cy-6:.1f}" text-anchor="middle" '
                 f'font-size="24" fill="{"#e24b3a" if demoniaco else "#ffe9a8"}">'
                 f'{_esc(sim)}</text>')
        P.append(f'<text x="{cx:.1f}" y="{cy+16:.1f}" text-anchor="middle" '
                 f'font-size="12" fill="#fdf7e8" font-weight="bold">'
                 f'{_esc(s["nome"])}</text>')
        P.append(f'<text x="{cx:.1f}" y="{cy+31:.1f}" text-anchor="middle" '
                 f'font-size="10" fill="#d8cbb0">nível {s["nivel"]} · perigo '
                 f'{s["perigo"]} · Qi {s["densidade_qi"]}</text>')
        P.append(f'<text x="{cx:.1f}" y="{cy+44:.1f}" text-anchor="middle" '
                 f'font-size="10" fill="#c0b49a">'
                 f'{_esc(s["tipo"].replace("_"," "))}</text>')
        if s.get("dono"):
            P.append(f'<text x="{cx:.1f}" y="{cy+57:.1f}" text-anchor="middle" '
                     f'font-size="9" fill="#a89878">{_esc(s["dono"])}</text>')
        P.append(f'<title>{_esc(s["nome"])} — {_esc(s["segredo"])}</title>')
    P.append('</svg>')
    return "\n".join(P)


def salvar_svg(conteudo: str, caminho: str) -> str:
    with open(caminho, "w", encoding="utf-8") as fh:
        fh.write(conteudo)
    return caminho
