# -*- coding: utf-8 -*-
"""
XAN — servidor web (biblioteca padrão apenas).

    python3 motor/servidor/app.py [--porta 8000] [--host 0.0.0.0]

Serve o livro de regras, o rolar auditado, os geradores de NPC/personagem/mundo/
besta, o simulador de combate, as tabelas e o certificado de justiça.

Nenhuma decisão é tomada aqui: o servidor só monta Declarações e as entrega ao
motor imparcial. Toda rolagem feita pela interface pode ser gravada num diário
encadeado — o mesmo que a CLI produz.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.abspath(os.path.join(_AQUI, "..", ".."))
sys.path.insert(0, os.path.join(_RAIZ, "motor"))

from xan import __motor__, __nome__, __version__          # noqa: E402
from xan.mundo import VERSAO_DO_GERADOR as VERSAO_GERADOR  # noqa: E402
from xan.entropia import Aleatoriedade, FonteSemeada, FonteViva  # noqa: E402

LIVRO_DIR = os.path.join(_RAIZ, "LIVRO")
DOCS_DIR = os.path.join(_RAIZ, "docs")
MUNDOS_DIR = os.path.join(_RAIZ, "mundos")
AUDITORIA_WEB = os.path.join(MUNDOS_DIR, "web", "auditoria", "diario.jsonl")


# ==========================================================================
# Markdown mínimo (suficiente para o LIVRO, sem dependências)
# ==========================================================================
_INLINE = [
    (re.compile(r"`([^`]+)`"), lambda m: f"<code>{m.group(1)}</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), lambda m: f"<strong>{m.group(1)}</strong>"),
    (re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)"), lambda m: f"<em>{m.group(1)}</em>"),
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)"),
     lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>'),
]


def _inline(texto: str) -> str:
    s = html.escape(texto, quote=False)
    s = s.replace("&lt;code&gt;", "<code>")  # nunca acontece; defensivo
    for padrao, trocador in _INLINE:
        s = padrao.sub(lambda m, t=trocador: t(m), s)
    return s


def markdown_para_html(md: str) -> str:
    linhas = md.split("\n")
    saida: List[str] = []
    i = 0
    n = len(linhas)
    while i < n:
        linha = linhas[i]

        # bloco de código
        if linha.strip().startswith("```"):
            lingua = linha.strip()[3:].strip()
            corpo: List[str] = []
            i += 1
            while i < n and not linhas[i].strip().startswith("```"):
                corpo.append(linhas[i])
                i += 1
            i += 1
            cls = f' class="lingua-{html.escape(lingua)}"' if lingua else ""
            saida.append("<pre><code%s>%s</code></pre>"
                         % (cls, html.escape("\n".join(corpo))))
            continue

        # tabela
        if linha.strip().startswith("|") and i + 1 < n and re.match(
                r"^\s*\|[\s:|-]+\|\s*$", linhas[i + 1]):
            cabecalho = [c.strip() for c in linha.strip().strip("|").split("|")]
            i += 2
            corpo_t = []
            while i < n and linhas[i].strip().startswith("|"):
                corpo_t.append([c.strip()
                                for c in linhas[i].strip().strip("|").split("|")])
                i += 1
            t = ["<div class='tabela-scroll'><table><thead><tr>"]
            t += [f"<th>{_inline(c)}</th>" for c in cabecalho]
            t.append("</tr></thead><tbody>")
            for linha_t in corpo_t:
                t.append("<tr>" + "".join(f"<td>{_inline(c)}</td>"
                                          for c in linha_t) + "</tr>")
            t.append("</tbody></table></div>")
            saida.append("".join(t))
            continue

        # citação
        if linha.strip().startswith(">"):
            bloco = []
            while i < n and linhas[i].strip().startswith(">"):
                bloco.append(linhas[i].strip().lstrip(">").strip())
                i += 1
            saida.append(f"<blockquote>{_inline(' '.join(bloco))}</blockquote>")
            continue

        # títulos
        m = re.match(r"^(#{1,6})\s+(.*)$", linha)
        if m:
            nivel = len(m.group(1))
            texto = m.group(2).strip()
            ancora = re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")
            saida.append(f'<h{nivel} id="{ancora}">{_inline(texto)}</h{nivel}>')
            i += 1
            continue

        # separador
        if re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", linha):
            saida.append("<hr/>")
            i += 1
            continue

        # lista não ordenada
        if re.match(r"^\s*[-*+]\s+", linha):
            itens = []
            while i < n and re.match(r"^\s*[-*+]\s+", linhas[i]):
                itens.append(re.sub(r"^\s*[-*+]\s+", "", linhas[i]))
                i += 1
            saida.append("<ul>" + "".join(f"<li>{_inline(x)}</li>"
                                          for x in itens) + "</ul>")
            continue

        # lista ordenada
        if re.match(r"^\s*\d+[.)]\s+", linha):
            itens = []
            while i < n and re.match(r"^\s*\d+[.)]\s+", linhas[i]):
                itens.append(re.sub(r"^\s*\d+[.)]\s+", "", linhas[i]))
                i += 1
            saida.append("<ol>" + "".join(f"<li>{_inline(x)}</li>"
                                          for x in itens) + "</ol>")
            continue

        # parágrafo
        if linha.strip():
            par = [linha.strip()]
            i += 1
            while i < n and linhas[i].strip() and not re.match(
                    r"^\s*(#{1,6}\s|[-*+]\s|\d+[.)]\s|>|\||```|-{3,}\s*$)",
                    linhas[i]):
                par.append(linhas[i].strip())
                i += 1
            saida.append(f"<p>{_inline(' '.join(par))}</p>")
            continue

        i += 1
    return "\n".join(saida)


# ==========================================================================
# CSS
# ==========================================================================
CSS = """
:root{
  --papel:#f5efe0; --papel2:#ebe2cd; --tinta:#241d15; --tinta2:#5a4b38;
  --ouro:#a8842f; --ouro2:#d9b45c; --selo:#7d1f14; --jade:#2f6b4f;
  --agua:#2f5f8f; --linha:#c9b994;
}
*{box-sizing:border-box}
body{margin:0;background:var(--papel);color:var(--tinta);
  font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  line-height:1.62;font-size:17px}
a{color:var(--selo)}
code,pre,.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
pre{background:#1e1a14;color:#f0e6d2;padding:14px 16px;border-radius:8px;
  overflow-x:auto;font-size:13.5px;line-height:1.5}
code{background:var(--papel2);padding:1px 5px;border-radius:4px;font-size:.9em}
pre code{background:none;padding:0}
header{background:linear-gradient(180deg,#1b1710,#2c2419);color:#f3e9d2;
  padding:26px 22px;border-bottom:4px solid var(--ouro)}
header .wrap{max-width:1180px;margin:0 auto;display:flex;flex-wrap:wrap;
  gap:18px;align-items:baseline;justify-content:space-between}
header h1{margin:0;font-size:30px;letter-spacing:.5px}
header h1 span{color:var(--ouro2)}
header p{margin:4px 0 0;color:#c9b994;font-size:14px}
nav{position:sticky;top:0;z-index:9;background:#241d15;border-bottom:1px solid #4a3d2c}
nav .wrap{max-width:1180px;margin:0 auto;display:flex;flex-wrap:wrap;gap:2px;padding:0 12px}
nav a{color:#d8cbb0;text-decoration:none;padding:11px 13px;font-size:14px;
  border-bottom:3px solid transparent}
nav a:hover{color:#fff;background:#33291d}
nav a.ativo{color:var(--ouro2);border-bottom-color:var(--ouro2)}
main{max-width:1180px;margin:0 auto;padding:26px 22px 80px}
article{background:#fffdf7;border:1px solid var(--linha);border-radius:10px;
  padding:30px 34px;box-shadow:0 2px 10px rgba(60,45,20,.07)}
h2{color:var(--selo);border-bottom:2px solid var(--ouro);padding-bottom:6px;margin-top:38px}
h3{color:var(--tinta);margin-top:30px}
h4{color:var(--tinta2)}
blockquote{border-left:4px solid var(--ouro);background:var(--papel2);
  margin:18px 0;padding:12px 18px;border-radius:0 8px 8px 0;color:var(--tinta2)}
.tabela-scroll{overflow-x:auto;margin:18px 0}
table{border-collapse:collapse;width:100%;font-size:14.5px}
th,td{border:1px solid var(--linha);padding:7px 10px;text-align:left;vertical-align:top}
th{background:var(--papel2);font-weight:600}
tbody tr:nth-child(even){background:#fbf7ec}
hr{border:0;border-top:1px solid var(--linha);margin:34px 0}
.grid{display:grid;gap:18px}
.cols2{grid-template-columns:repeat(auto-fit,minmax(340px,1fr))}
.card{background:#fffdf7;border:1px solid var(--linha);border-radius:10px;padding:20px}
.card h3{margin-top:0}
label{display:block;font-size:13px;color:var(--tinta2);margin:10px 0 3px;
  text-transform:uppercase;letter-spacing:.06em}
input,select,textarea,button{font-family:inherit;font-size:15px}
input,select,textarea{width:100%;padding:9px 11px;border:1px solid var(--linha);
  border-radius:6px;background:#fffdf7;color:var(--tinta)}
button{background:var(--selo);color:#fff;border:0;padding:11px 20px;border-radius:6px;
  cursor:pointer;font-weight:600;letter-spacing:.02em}
button:hover{background:#96281a}
button.sec{background:var(--jade)}
button.sec:hover{background:#3a8260}
button.ouro{background:var(--ouro);color:#241d15}
.linha-form{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end}
.linha-form>div{flex:1;min-width:150px}
.saida{margin-top:18px}
.resultado-dado{font-size:52px;font-weight:700;color:var(--selo);line-height:1}
.resultado-dado.ok{color:var(--jade)}
.selo{font-size:11px;word-break:break-all;color:var(--tinta2);
  background:var(--papel2);padding:8px 10px;border-radius:6px;margin-top:8px}
.tag{display:inline-block;background:var(--papel2);border:1px solid var(--linha);
  border-radius:20px;padding:2px 10px;font-size:12px;margin:2px 3px 2px 0}
.tag.ok{background:#e2f0e6;border-color:#9dc4a8;color:#22512f}
.tag.ruim{background:#f6e0dc;border-color:#d3a29a;color:#7d1f14}
.tag.ouro{background:#f7ecd2;border-color:var(--ouro2);color:#6b5314}
ul.log{list-style:none;padding:0;margin:10px 0;font-size:13.5px}
ul.log li{padding:7px 10px;border-left:3px solid var(--linha);margin-bottom:5px;
  background:#fffdf7}
ul.log li.acerto{border-left-color:var(--jade)}
ul.log li.erro{border-left-color:#c9b994}
ul.log li.critico{border-left-color:var(--selo);background:#fdf3f1}
.kpi{display:flex;gap:14px;flex-wrap:wrap;margin:14px 0}
.kpi div{background:var(--papel2);border:1px solid var(--linha);border-radius:8px;
  padding:10px 16px;min-width:120px}
.kpi b{display:block;font-size:24px;color:var(--selo)}
.kpi span{font-size:12px;color:var(--tinta2);text-transform:uppercase;letter-spacing:.05em}
.mapa{background:#fffdf7;border:1px solid var(--linha);border-radius:10px;padding:10px;
  overflow:auto}
.mapa svg{max-width:100%;height:auto}
.indice-livro{columns:2;column-gap:34px}
.indice-livro a{display:block;padding:5px 0;text-decoration:none;
  border-bottom:1px dotted var(--linha)}
.rodape{max-width:1180px;margin:0 auto;padding:22px;color:var(--tinta2);font-size:13px}
.aviso{background:#fdf3f1;border:1px solid #d3a29a;border-radius:8px;padding:12px 16px;
  margin:16px 0;font-size:14.5px}
.nota{background:#eef4ef;border:1px solid #9dc4a8;border-radius:8px;padding:12px 16px;
  margin:16px 0;font-size:14.5px}
@media(max-width:760px){article{padding:20px 16px}.indice-livro{columns:1}
  .resultado-dado{font-size:40px}}
"""

JS = """
async function chamar(rota, corpo, alvo, antes){
  const el = document.getElementById(alvo);
  if(antes) el.innerHTML = antes;
  el.innerHTML = '<p class="tag">rolando…</p>';
  try{
    const r = await fetch(rota,{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify(corpo||{})});
    const j = await r.json();
    if(!r.ok){ el.innerHTML = '<div class="aviso"><b>Erro:</b> '+
      String(j.erro||r.status).replace(/</g,'&lt;')+'</div>'; return null; }
    el.innerHTML = j.html || '';
    return j;
  }catch(e){
    el.innerHTML = '<div class="aviso"><b>Falha de rede:</b> '+
      String(e).replace(/</g,'&lt;')+'</div>';
    return null;
  }
}
function pegar(form){
  const o={}; new FormData(form).forEach((v,k)=>{o[k]=v;}); return o;
}
function enviar(id, form, alvo){
  document.getElementById(id).addEventListener('submit', e=>{
    e.preventDefault();
    chamar(form.getAttribute('action'), pegar(form), alvo);
  });
}
"""


# ==========================================================================
# HTML base
# ==========================================================================
ABAS = [
    ("/", "Início"),
    ("/livro", "Livro"),
    ("/dados", "Dados"),
    ("/npc", "NPCs"),
    ("/personagem", "Personagem"),
    ("/mundo", "Mundo"),
    ("/combate", "Combate"),
    ("/tabelas", "Tabelas"),
    ("/justica", "Justiça"),
    ("/auditoria", "Auditoria"),
]


def pagina(titulo: str, corpo: str, ativo: str = "") -> str:
    pecas = []
    for href, rot in ABAS:
        classe = ' class="ativo"' if href == ativo else ""
        pecas.append(f'<a href="{href}"{classe}>{rot}</a>')
    nav = "".join(pecas)
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{html.escape(titulo)} — XAN</title>
<style>{CSS}</style></head><body>
<header><div class="wrap">
  <div><h1>XAN <span>仙道</span> · Rios e Lagos</h1>
  <p>{html.escape(__motor__)} — {__nome__} {__version__}</p></div>
  <div><p>A Regra de Ouro: depois que os dados e os modificadores são declarados,
  nada mais pode mudar o resultado.</p></div>
</div></header>
<nav><div class="wrap">{nav}</div></nav>
<main>{corpo}</main>
<div class="rodape">Motor do Destino Imparcial · Python biblioteca padrão ·
260 testes automatizados · certificado de justiça publicado</div>
<script>{JS}</script>
</body></html>"""


def _art(titulo: str, interno: str) -> str:
    return f"<article><h2>{html.escape(titulo)}</h2>{interno}</article>"


# ==========================================================================
# Páginas
# ==========================================================================
def pagina_inicio() -> str:
    try:
        with open(os.path.join(_RAIZ, "README.md"), encoding="utf-8") as fh:
            readme = fh.read()
    except OSError:
        readme = "# XAN\n\nLeia `LIVRO/00-indice.md`."
    corpo = markdown_para_html(readme)
    return pagina("Início", f"<article>{corpo}</article>", "/")


def _capitulos() -> List[Tuple[str, str]]:
    if not os.path.isdir(LIVRO_DIR):
        return []
    arquivos = sorted(f for f in os.listdir(LIVRO_DIR) if f.endswith(".md"))
    return [(f, f[:-3]) for f in arquivos]


def pagina_livro(capitulo: Optional[str] = None) -> str:
    caps = _capitulos()
    if capitulo is None:
        itens = "".join(
            f'<a href="/livro/{slug}">{html.escape(arq[:-3])}</a>'
            for arq, slug in caps)
        fichas = ""
        dirf = os.path.join(LIVRO_DIR, "fichas")
        if os.path.isdir(dirf):
            fichas = "<h3>Fichas</h3><div class='indice-livro'>" + "".join(
                f'<a href="/livro/fichas/{f[:-3]}">{html.escape(f[:-3])}</a>'
                for f in sorted(os.listdir(dirf)) if f.endswith(".md")) + "</div>"
        corpo = _art("O Livro de Regras",
                     "<p>22 capítulos e 4 fichas, em português.</p>"
                     f"<div class='indice-livro'>{itens}</div>{fichas}")
        return pagina("Livro", corpo, "/livro")

    caminho = os.path.join(LIVRO_DIR, capitulo + ".md")
    if not os.path.isfile(caminho) or ".." in capitulo:
        return pagina("Não encontrado", _art("Capítulo não encontrado",
                                             "<p>Volte ao <a href='/livro'>índice</a>.</p>"),
                      "/livro")
    with open(caminho, encoding="utf-8") as fh:
        md = fh.read()
    anterior = proximo = None
    nomes = [s for _, s in caps]
    if capitulo in nomes:
        k = nomes.index(capitulo)
        anterior = nomes[k - 1] if k > 0 else None
        proximo = nomes[k + 1] if k + 1 < len(nomes) else None
    naveg = "<hr/><p>"
    if anterior:
        naveg += f"<a href='/livro/{anterior}'>← {html.escape(anterior)}</a> &nbsp;·&nbsp; "
    naveg += "<a href='/livro'>índice</a>"
    if proximo:
        naveg += f" &nbsp;·&nbsp; <a href='/livro/{proximo}'>{html.escape(proximo)} →</a>"
    naveg += "</p>"
    return pagina(capitulo, f"<article>{markdown_para_html(md)}{naveg}</article>",
                  "/livro")


def pagina_dados() -> str:
    corpo = """
<div class="grid cols2">
<div class="card">
<h3>Rolar dados</h3>
<form id="f-rolar" action="/api/rolar">
  <label>Expressão</label>
  <input name="expressao" value="4d6kh3" required/>
  <div class="linha-form">
    <div><label>Ator</label><input name="ator" value="mesa"/></div>
    <div><label>Semente (opcional)</label><input name="semente" placeholder="fonte viva"/></div>
  </div>
  <label><input type="checkbox" name="auditar" value="1" checked style="width:auto"/>
    gravar no diário encadeado (compromisso → rolagem → revelação)</label>
  <p><button>Rolar</button></p>
</form>
<div class="saida" id="out-rolar"></div>
</div>
<div class="card">
<h3>Teste contra uma DD</h3>
<form id="f-teste" action="/api/teste">
  <div class="linha-form">
    <div><label>Atributo</label>
      <select name="atributo">
        <option value="per">Percepção</option><option value="con" selected>Constituição</option>
        <option value="cha">Carisma</option><option value="int">Inteligência</option>
        <option value="luk">Sorte</option><option value="pot">Potencial</option>
      </select></div>
    <div><label>Valor (1–30)</label><input name="valor" type="number" value="16" min="1" max="30"/></div>
  </div>
  <div class="linha-form">
    <div><label>Perícia</label><input name="pericia" value="espada"/></div>
    <div><label>Graduação (0–5)</label><input name="graduacao" type="number" value="4" min="0" max="5"/></div>
    <div><label>DD</label><input name="dd" type="number" value="18" min="1" max="60"/></div>
  </div>
  <label>Regras (códigos separados por vírgula)</label>
  <input name="regras" value="ELEMENTO:RELACAO,POSICAO:TERRENO"/>
  <label>Fatos (JSON)</label>
  <textarea name="fatos" rows="3">{"elemento_atacante":"metal","elemento_alvo":"madeira","terreno":"alto"}</textarea>
  <label>Semente (opcional)</label><input name="semente"/>
  <p><button>Resolver</button></p>
</form>
<div class="saida" id="out-teste"></div>
</div>
</div>
<div class="card" style="margin-top:18px">
<h3>Notação aceita</h3>
<p><code>NdS</code> · <code>NdS!</code> (explosivo) · <code>NdS!T</code> ·
<code>NdS kh M</code> · <code>NdS kl M</code> · <code>NdF</code> · <code>d%</code> ·
expressões com <code>+</code> e <code>−</code>, incluindo termos negativos
(<code>1d20-1d4</code>).</p>
<p>Marque <b>gravar no diário</b> e cada rolagem passa pelo protocolo de
compromisso: o hash da declaração é gravado <em>antes</em> do dado. Confira
depois na aba <a href="/auditoria">Auditoria</a>.</p>
</div>
"""
    extra = """
<script>enviar('f-rolar',document.getElementById('f-rolar'),'out-rolar');
enviar('f-teste',document.getElementById('f-teste'),'out-teste');</script>"""
    return pagina("Dados", corpo, "/dados").replace("</body>", extra + "</body>")


def pagina_npc() -> str:
    from xan.npcs import OCUPACOES, PEDIDOS_TIPICOS, TEMPERAMENTOS
    ocup = "".join(f"<option>{html.escape(o[0])}</option>" for o in OCUPACOES)
    mags = "".join(f"<option value='{k}'>{k} (DD {v})</option>"
                   for k, v in sorted(PEDIDOS_TIPICOS.items(),
                                      key=lambda kv: kv[1]))
    corpo = f"""
<div class="card">
<h3>Gerar NPC</h3>
<form id="f-npc" action="/api/npc">
  <div class="linha-form">
    <div><label>Semente</label><input name="semente" value="mesa-npc-01"/></div>
    <div><label>Nível (vazio = sorteado)</label><input name="nivel" type="number" min="0" max="13"/></div>
    <div><label>Facção</label><input name="faccao" value="Seita do Monte Hua"/></div>
  </div>
  <div class="linha-form">
    <div><label>Ocupação</label><select name="ocupacao"><option value="">sortear</option>{ocup}</select></div>
    <div><label>Caminho</label><select name="caminho"><option value="">sortear</option>
      <option>xiandao</option><option>shendao</option><option>corpo</option>
      <option>marcial</option><option>monstro</option></select></div>
    <div><label>Tabela de raiz</label><select name="raiz">
      <option value="realista" selected>realista (população)</option>
      <option value="heroica">heroica</option><option value="lendária">lendária</option>
      <option value="mortal">mortal</option></select></div>
    <div><label>Agendas</label><input name="agendas" type="number" value="2" min="0" max="4"/></div>
  </div>
  <p><button>Gerar</button></p>
</form>
<div class="saida" id="out-npc"></div>
</div>
<div class="card" style="margin-top:18px">
<h3>O que ele faria? — conduta resolvida no dado</h3>
<p>O mestre <b>não</b> decide. Rola-se contra a magnitude do pedido e a
disposição registrada; a conduta sai da tabela e a camada de desejo que a
produz é derivada da personalidade dele.</p>
<form id="f-conduta" action="/api/conduta">
  <div class="linha-form">
    <div><label>Semente do NPC</label><input name="semente" value="mesa-npc-01" required/></div>
    <div><label>Nível</label><input name="nivel" type="number" value="6" min="0" max="13"/></div>
    <div><label>Alvo</label><input name="alvo" value="O Grupo"/></div>
  </div>
  <div class="linha-form">
    <div><label>Magnitude do pedido</label><select name="magnitude">{mags}</select></div>
    <div><label>Pedido</label><input name="pedido" value="emprestar o manual da seita"/></div>
  </div>
  <div class="linha-form">
    <div><label>Eventos já registrados (código:peso do catálogo, separados por vírgula)</label>
      <input name="eventos" value="compartilhou_uma_refeicao,salvou_a_vida"/></div>
  </div>
  <p><button>Resolver conduta</button></p>
</form>
<div class="saida" id="out-conduta"></div>
</div>
<div class="card" style="margin-top:18px">
<h3>Conflito de desejos</h3>
<p>Quando duas camadas mandam condutas incompatíveis, o dado decide. A
<b>linha vermelha não vai ao dado</b>: é veto absoluto.</p>
<form id="f-conflito" action="/api/conflito">
  <div class="linha-form">
    <div><label>Semente do NPC</label><input name="semente" value="mesa-npc-01" required/></div>
    <div><label>Camada A</label><select name="a">
      <option>medo</option><option selected>dever</option><option>obsessao</option>
      <option>ambicao</option><option>imediato</option><option>preco</option>
      <option>segredo</option><option>linha_vermelha</option></select></div>
    <div><label>Camada B</label><select name="b">
      <option>medo</option><option>dever</option><option>obsessao</option>
      <option selected>ambicao</option><option>imediato</option><option>preco</option>
      <option>segredo</option><option>linha_vermelha</option></select></div>
  </div>
  <p><button>Resolver</button></p>
</form>
<div class="saida" id="out-conflito"></div>
</div>
"""
    extra = """<script>
enviar('f-npc',document.getElementById('f-npc'),'out-npc');
enviar('f-conduta',document.getElementById('f-conduta'),'out-conduta');
enviar('f-conflito',document.getElementById('f-conflito'),'out-conflito');
</script>"""
    return pagina("NPCs", corpo, "/npc").replace("</body>", extra + "</body>")


def pagina_personagem() -> str:
    from xan.reinos import LEIS
    leis = "".join(f"<option value='{c}'>{html.escape(LEIS[c].nome)} ({c})</option>"
                   for c in sorted(LEIS))
    corpo = f"""
<div class="grid cols2">
<div class="card">
<h3>Criar personagem</h3>
<form id="f-pj" action="/api/personagem">
  <label>Nome</label><input name="nome" value="Lin Yue" required/>
  <div class="linha-form">
    <div><label>Semente</label><input name="semente" value="mesa-pj-01"/></div>
    <div><label>Método</label><select name="metodo">
      <option value="sorteio" selected>sorteio (4d6kh3)</option>
      <option value="pontos">pontos (78)</option></select></div>
  </div>
  <div class="linha-form">
    <div><label>Caminho</label><select name="caminho">
      <option value="xiandao" selected>Xiandao 仙道</option>
      <option value="shendao">Shendao 神道</option>
      <option value="corpo">Corpo 體修</option>
      <option value="marcial">Marcial 武林</option></select></div>
    <div><label>Nível</label><input name="nivel" type="number" value="1" min="0" max="13"/></div>
  </div>
  <label>Lei (功法)</label><select name="lei"><option value="">nenhuma</option>{leis}</select>
  <div class="linha-form">
    <div><label>Tabela de raiz</label><select name="raiz">
      <option value="heroica" selected>heroica (padrão para PJs)</option>
      <option value="realista">realista</option>
      <option value="lendária">lendária</option>
      <option value="mortal">mortal</option></select></div>
    <div><label>Grau do Núcleo (só nível 7+)</label>
      <input name="nucleo" type="number" min="1" max="9"/></div>
  </div>
  <div class="linha-form">
    <div><label>Facção</label><input name="faccao" value="Seita do Monte Hua"/></div>
    <div><label>Posto</label><input name="posto" value="Discípula Interna"/></div>
  </div>
  <p><button>Criar</button></p>
</form>
<div class="saida" id="out-pj"></div>
</div>
<div class="card">
<h3>Gerar besta espiritual</h3>
<form id="f-besta" action="/api/besta">
  <div class="linha-form">
    <div><label>Semente</label><input name="semente" value="mesa-besta-01"/></div>
    <div><label>Nível</label><input name="nivel" type="number" min="0" max="13" value="6"/></div>
  </div>
  <div class="linha-form">
    <div><label>Terreno</label><select name="terreno">
      <option>montanhas</option><option selected>florestas</option><option>planicies</option>
      <option>deserto</option><option>tundra</option><option>litoral</option>
      <option>arquipelago</option><option>pantano</option><option>vales</option>
      <option>planalto</option><option>vulcanico</option><option>estepe</option>
      </select></div>
    <div><label>Elemento</label><select name="elemento"><option value="">sortear</option>
      <option>madeira</option><option>fogo</option><option>terra</option>
      <option>metal</option><option>agua</option><option>nenhum</option>
      <option>vazio</option></select></div>
  </div>
  <p><button>Gerar</button></p>
</form>
<div class="saida" id="out-besta"></div>
<h3 style="margin-top:26px">Núcleo Dourado (sem dado)</h3>
<p>A ruptura do nível 6 para o 7 não se rola: <b>conta-se</b>. Grau 9 (escória) a
1 (Taiyi), uma única vez na vida.</p>
<form id="f-nucleo" action="/api/nucleo">
  <div class="linha-form">
    <div><label>Qi máximo</label><input name="qi" type="number" value="420" required/></div>
    <div><label>Estado mental (0–200)</label><input name="mental" type="number" value="150"/></div>
  </div>
  <div class="linha-form">
    <div><label>Feng Shui</label><select name="fengshui">
      <option>muito_sinistro</option><option>sinistro</option><option>neutro</option>
      <option>auspicioso</option><option selected>muito_auspicioso</option></select></div>
    <div><label>Densidade de Qi</label><select name="densidade">
      <option>esteril</option><option>pobre</option><option>comum</option>
      <option>rica</option><option>veia_espiritual</option>
      <option selected>terra_imortal</option></select></div>
  </div>
  <div class="linha-form">
    <div><label>Elixir</label><select name="elixir"><option>nenhum</option><option>menor</option>
      <option>medio</option><option selected>maior</option><option>celestial</option></select></div>
    <div><label>Artefato</label><select name="artefato"><option>nenhum</option><option>mortal</option>
      <option>terra</option><option selected>ceu</option><option>primordial</option></select></div>
  </div>
  <div class="linha-form">
    <div><label>Compatibilidade (%)</label><input name="compat" type="number" value="141" min="0" max="150"/></div>
    <div><label>Compreensão</label><input name="compreensao" type="number" value="2400"/></div>
  </div>
  <div class="linha-form">
    <div><label>Elemento da Lei</label><select name="elemento"><option value="">não calcular harmonia</option>
      <option selected>metal</option><option>madeira</option><option>agua</option>
      <option>fogo</option><option>terra</option><option>nenhum</option></select></div>
    <div><label>Estação</label><select name="estacao"><option>primavera</option><option>verao</option>
      <option>outono</option><option selected>inverno</option></select></div>
    <div><label>Dia (1–30)</label><input name="dia" type="number" value="25" min="1" max="30"/></div>
  </div>
  <div class="linha-form">
    <div><label>Polaridade da hora</label><select name="polaridade">
      <option>yang</option><option selected>yin</option></select></div>
    <div><label>Clima</label><select name="clima"><option>limpo</option><option>nublado</option>
      <option>chuva</option><option>nevoeiro</option><option>nevasca</option>
      <option selected>tempestade</option><option>miasma</option>
      <option>calor_extremo</option><option>frio_extremo</option></select></div>
    <div><label><input type="checkbox" name="mestre" value="1" checked style="width:auto"/> mestre presente</label></div>
  </div>
  <p><button>Calcular o grau</button></p>
</form>
<div class="saida" id="out-nucleo"></div>
</div>
</div>
"""
    extra = """<script>
enviar('f-pj',document.getElementById('f-pj'),'out-pj');
enviar('f-besta',document.getElementById('f-besta'),'out-besta');
enviar('f-nucleo',document.getElementById('f-nucleo'),'out-nucleo');
</script>"""
    return pagina("Personagem", corpo, "/personagem").replace("</body>", extra + "</body>")


def pagina_mundo() -> str:
    corpo = """
<div class="card">
<h3>Gerar mundo</h3>
<p>Uma semente gera continente, províncias, sítios, facções, matriz de relações,
história com consequências materiais, tesouros lendários, clima dos 360 dias e
mapa SVG. Mesma semente, mesmo mundo — sempre.</p>
<form id="f-mundo" action="/api/mundo">
  <div class="linha-form">
    <div><label>Semente</label><input name="semente" value="rios-e-lagos" required/></div>
    <div><label>Províncias</label><input name="provincias" type="number" value="9" min="3" max="20"/></div>
    <div><label>Eventos históricos</label><input name="eventos" type="number" value="40" min="1" max="200"/></div>
    <div><label>Anos de história</label><input name="anos" type="number" value="900" min="10" max="5000"/></div>
  </div>
  <p><button class="ouro">Gerar mundo</button></p>
</form>
<div class="saida" id="out-mundo"></div>
</div>
"""
    extra = """<script>enviar('f-mundo',document.getElementById('f-mundo'),'out-mundo');</script>"""
    return pagina("Mundo", corpo, "/mundo").replace("</body>", extra + "</body>")


def pagina_combate() -> str:
    corpo = """
<div class="card">
<h3>Simular duelo</h3>
<p>Cada golpe é uma Declaração comprometida e rolada pelo motor imparcial. O Qi
absorve dano antes da Vitalidade. Três ou mais níveis abaixo do alvo, o ataque
<b>nem rola</b>.</p>
<form id="f-combate" action="/api/combate">
  <div class="linha-form">
    <div><label>Semente</label><input name="semente" value="duelo-01" required/></div>
    <div><label>Nível</label><input name="nivel" type="number" value="6" min="1" max="13"/></div>
    <div><label>Herói</label><input name="heroi" value="Lin Yue"/></div>
    <div><label>Rival</label><input name="rival" value="Zhang Hei"/></div>
  </div>
  <div class="linha-form">
    <div><label>Defesa do herói</label><select name="defesa_heroi">
      <option selected>esquiva</option><option>resistencia</option><option>aparar</option></select></div>
    <div><label>Defesa do rival</label><select name="defesa_rival">
      <option>esquiva</option><option selected>resistencia</option><option>aparar</option></select></div>
  </div>
  <div class="linha-form">
    <div><label>Terreno</label><select name="terreno"><option selected>neutro</option>
      <option>alto</option><option>baixo</option></select></div>
    <div><label>Luz</label><select name="luz"><option selected>plena</option>
      <option>penumbra</option><option>escuridao</option><option>trevas</option></select></div>
    <div><label>Clima</label><select name="clima"><option selected>limpo</option>
      <option>nublado</option><option>chuva</option><option>nevoeiro</option>
      <option>nevasca</option><option>tempestade</option><option>miasma</option>
      <option>calor_extremo</option><option>frio_extremo</option></select></div>
  </div>
  <div class="linha-form">
    <div><label>Feng Shui</label><select name="fengshui"><option>muito_sinistro</option>
      <option>sinistro</option><option selected>neutro</option><option>auspicioso</option>
      <option>muito_auspicioso</option></select></div>
    <div><label>Densidade de Qi</label><select name="densidade"><option>esteril</option>
      <option>pobre</option><option selected>comum</option><option>rica</option>
      <option>veia_espiritual</option><option>terra_imortal</option></select></div>
    <div><label>Formação</label><select name="formacao"><option selected>nenhuma</option>
      <option>aliada</option><option>hostil</option></select></div>
  </div>
  <label><input type="checkbox" name="defensivo" value="1" checked style="width:auto"/>
    combatentes muito feridos passam a defender</label>
  <label><input type="checkbox" name="auditar" value="1" checked style="width:auto"/>
    gravar tudo no diário encadeado</label>
  <p><button class="ouro">Lutar</button></p>
</form>
<div class="saida" id="out-combate"></div>
</div>
"""
    extra = """<script>enviar('f-combate',document.getElementById('f-combate'),'out-combate');</script>"""
    return pagina("Combate", corpo, "/combate").replace("</body>", extra + "</body>")


def pagina_tabelas() -> str:
    abas = [("reinos", "Reinos"), ("leis", "Leis"), ("regras", "Registro de Regras"),
            ("tecnicas", "Técnicas"), ("pericias", "Perícias"),
            ("bestiario", "Bestiário"), ("predios", "Prédios de seita"),
            ("missoes", "Missões")]
    botoes = "".join(
        f"<button class='sec' onclick=\"chamar('/api/tabelas',{json.dumps({'tabela': t})},"
        f"'out-tabela')\">{html.escape(rot)}</button> " for t, rot in abas)
    corpo = f"""
<div class="card">
<h3>Tabelas do sistema</h3>
<p>{botoes}</p>
<div class="saida" id="out-tabela"><p class="tag">escolha uma tabela</p></div>
</div>"""
    return pagina("Tabelas", corpo, "/tabelas")


def pagina_justica() -> str:
    corpo = """
<div class="card">
<h3>Certificado de imparcialidade</h3>
<p>40 testes estatísticos sobre mais de 3,5 milhões de amostras: uniformidade de
cada face, distribuição exata dos totais, Kolmogorov–Smirnov, autocorrelação,
corridas, testes do NIST SP 800-22 (com a distribuição da maior corrida obtida
<b>exatamente</b> por programação dinâmica), independência, imparcialidade de
<code>kh</code>/<code>kl</code>, Fisher–Yates, eficiência da rejeição,
determinismo e imparcialidade entre atores.</p>
<p><button class="ouro"
  onclick="chamar('/api/justica',{},'out-justica','<p class=tag>rodando a bateria… leva cerca de um minuto</p>')">
  Rodar a bateria agora</button>
  <button class="sec" onclick="chamar('/api/certificado',{},'out-justica')">
  Ver o certificado publicado</button></p>
<div class="nota">Rodar a bateria no navegador leva ~60 s e usa um núcleo inteiro.
O certificado já publicado em <code>docs/CERTIFICADO_DE_JUSTICA.md</code> é o
resultado da mesma bateria.</div>
<div class="saida" id="out-justica"></div>
</div>
"""
    return pagina("Justiça", corpo, "/justica")


def pagina_auditoria() -> str:
    corpo = f"""
<div class="card">
<h3>Diário de auditoria da interface</h3>
<p>Tudo o que você rolar nesta interface com <em>gravar no diário</em> marcado
vai para <code>{html.escape(os.path.relpath(AUDITORIA_WEB, _RAIZ))}</code>: um
arquivo JSONL append-only, encadeado por SHA-256, com raiz de Merkle.</p>
<p><button onclick="chamar('/api/auditoria',{json.dumps({'acao': 'verificar'})},'out-aud')">
  Verificar integridade</button>
 <button class="sec" onclick="chamar('/api/auditoria',{json.dumps({'acao': 'resumo'})},'out-aud')">
  Resumo por tipo</button>
 <button class="ouro" onclick="chamar('/api/auditoria',{json.dumps({'acao': 'ultimos'})},'out-aud')">
  Últimos registros</button></p>
<div class="saida" id="out-aud"><p class="tag">nada verificado ainda</p></div>
</div>
<div class="card" style="margin-top:18px">
<h3>O que o diário prova</h3>
<ol>
<li><b>Ordem.</b> Cada rolagem tem um compromisso gravado <em>antes</em> e uma
revelação gravada <em>depois</em>. Se a declaração mudou no meio, o token não
bate.</li>
<li><b>Integridade.</b> Cada linha carrega o hash da anterior. Editar uma linha
quebra a cadeia inteira dali em diante.</li>
<li><b>Resumo único.</b> A raiz de Merkle resume o diário inteiro em 64
caracteres hexadecimais.</li>
<li><b>Selo externo.</b> <code>./xan auditoria selar</code> grava o hash da cabeça
num arquivo separado. Guarde-o fora do repositório: ele prova que ninguém
reescreveu o histórico depois daquela data.</li>
</ol>
</div>
"""
    return pagina("Auditoria", corpo, "/auditoria")


# ==========================================================================
# API
# ==========================================================================
def _aleat(dados: Dict[str, Any], contexto: str = "web") -> Aleatoriedade:
    semente = (dados.get("semente") or "").strip()
    if semente:
        return Aleatoriedade(FonteSemeada(semente, contexto))
    return Aleatoriedade(FonteViva())


def _diario_web(auditar: Any):
    if not auditar:
        return None
    from xan.auditoria import DiarioDeAuditoria
    os.makedirs(os.path.dirname(AUDITORIA_WEB), exist_ok=True)
    return DiarioDeAuditoria(AUDITORIA_WEB)


def _int(dados: Dict[str, Any], chave: str, padrao: Optional[int] = None,
         lo: Optional[int] = None, hi: Optional[int] = None) -> Optional[int]:
    v = (dados.get(chave) or "").strip() if isinstance(dados.get(chave), str) \
        else dados.get(chave)
    if v in ("", None):
        return padrao
    n = int(v)
    if lo is not None and n < lo:
        raise ValueError(f"{chave} deve ser ≥ {lo}")
    if hi is not None and n > hi:
        raise ValueError(f"{chave} deve ser ≤ {hi}")
    return n


def api_rolar(dados: Dict[str, Any]) -> Dict[str, Any]:
    from xan.dados import minimo_maximo, rolar, valor_esperado, _parsear
    from xan.compromisso import rolagem_auditada
    expressao = (dados.get("expressao") or "").strip()
    if not expressao:
        raise ValueError("informe uma expressão")
    a = _aleat(dados, "rolar")
    diario = _diario_web(dados.get("auditar"))
    if diario is not None:
        r, comp, indice = rolagem_auditada(expressao, a, diario,
                                           ator=dados.get("ator") or "mesa")
    else:
        r, comp, indice = rolar(expressao, a), None, None
    termos, c = _parsear(expressao)
    linhas = []
    for t in r.termos:
        det = f"faces {list(t.faces)} → mantidas {list(t.mantidas)}"
        if t.descartadas:
            det += f" · descartadas {list(t.descartadas)}"
        if t.explosivos:
            det += f" · explosões {t.explosivos}"
        linhas.append(f"<li><b>{html.escape(t.expressao())}</b> — {html.escape(det)}</li>")
    selo = ""
    if comp is not None:
        selo = (f"<div class='selo'><b>compromisso gravado antes do dado</b><br/>"
                f"token {html.escape(comp.token)}<br/>índice no diário #{indice}</div>")
    html_saida = f"""
<div class="kpi">
  <div><b>{r.total}</b><span>total</span></div>
  <div><b>{html.escape(expressao)}</b><span>expressão</span></div>
  <div><b>{float(valor_esperado(termos, c)):.3f}</b><span>valor esperado exato</span></div>
  <div><b>{minimo_maximo(termos, c)[0]}–{minimo_maximo(termos, c)[1]}</b><span>faixa</span></div>
</div>
<ul class="log">{''.join(linhas)}</ul>
{selo}
<p class="tag">valor esperado exato = {valor_esperado(termos, c)}</p>
"""
    return {"html": html_saida, "total": r.total}


def api_teste(dados: Dict[str, Any]) -> Dict[str, Any]:
    from xan.resolucao import Declaracao, resolver
    fatos = json.loads(dados.get("fatos") or "{}")
    if not isinstance(fatos, dict):
        raise ValueError("fatos precisa ser um objeto JSON")
    regras = tuple(x.strip() for x in (dados.get("regras") or "").split(",")
                   if x.strip())
    valor = _int(dados, "valor", 12, 1, 30)
    decl = Declaracao(
        acao=dados.get("acao") or "ação declarada pela interface",
        ator=dados.get("ator") or "personagem",
        atributo=dados.get("atributo") or "con",
        valor_atributo=valor,
        bonus_atributo=(valor - 10) // 2,
        pericia=dados.get("pericia") or "",
        graduacao=_int(dados, "graduacao", 0, 0, 5),
        dificuldade=_int(dados, "dd", 15, 1, 60),
        regras=regras, fatos=fatos,
    )
    res = resolver(decl, _aleat(dados, "teste"), _diario_web(True))
    classe = "ok" if res.sucesso else ""
    mods = "".join(f"<span class='tag'>{html.escape(m.codigo)} {m.valor:+d}</span>"
                   for m in res.modificadores)
    return {"html": f"""
<div class="kpi">
  <div><b>{res.total}</b><span>total</span></div>
  <div><b>{res.declaracao.dificuldade}</b><span>DD</span></div>
  <div><b>{res.margem:+d}</b><span>margem</span></div>
  <div><b>{html.escape(res.grau)}</b><span>grau</span></div>
</div>
<p class="tag {'ok' if res.sucesso else 'ruim'}">
  {'SUCESSO' if res.sucesso else 'FRACASSO'} — {html.escape(res.grau)}</p>
<p>{mods or "<span class='tag'>sem modificadores de regra</span>"}</p>
<pre>{html.escape(res.resumo())}</pre>
<div class="selo">selo do resultado: {html.escape(res.hash_resultado)}</div>
""", "total": res.total, "sucesso": res.sucesso, "classe": classe}


def api_npc(dados: Dict[str, Any]) -> Dict[str, Any]:
    from xan.npcs import gerar_npc
    n = gerar_npc(
        _aleat(dados, "npc"),
        nivel=_int(dados, "nivel", None, 0, 13),
        ocupacao=(dados.get("ocupacao") or None),
        faccao=(dados.get("faccao") or ""),
        localizacao=(dados.get("local") or ""),
        caminho=(dados.get("caminho") or None),
        tabela_de_raiz=(dados.get("raiz") or "realista"),
        agendas=_int(dados, "agendas", 1, 0, 4))
    return {"html": f"<pre>{html.escape(n.ficha())}</pre>"}


def api_conduta(dados: Dict[str, Any]) -> Dict[str, Any]:
    from xan.npcs import EVENTOS_DE_RELACAO, gerar_npc, resolver_conduta
    a = _aleat(dados, "conduta")
    n = gerar_npc(a, nivel=_int(dados, "nivel", 6, 0, 13))
    alvo = dados.get("alvo") or "O Grupo"
    for codigo in [x.strip() for x in (dados.get("eventos") or "").split(",")
                   if x.strip()]:
        if codigo not in EVENTOS_DE_RELACAO:
            raise ValueError(f"evento de relação desconhecido: {codigo}")
        n.registrar_relacao(alvo, codigo, "antes da cena", "registrado na interface")
    c = resolver_conduta(n, alvo, dados.get("pedido") or "um pedido", a,
                         magnitude=dados.get("magnitude") or "favor_sem_risco")
    disp, cat = n.disposicao_para(alvo)
    return {"html": f"""
<div class="kpi">
  <div><b>{c.resultado.total}</b><span>total</span></div>
  <div><b>{c.resultado.declaracao.dificuldade}</b><span>DD</span></div>
  <div><b>{c.resultado.margem:+d}</b><span>margem</span></div>
  <div><b>{disp:+d}</b><span>disposição ({html.escape(cat)})</span></div>
</div>
<p class="tag ouro">{html.escape(c.codigo)}</p>
<p><b>{html.escape(n.nome)}</b> ({html.escape(n.ocupacao)}, nível {n.nivel})</p>
<pre>{html.escape(c.resumo())}</pre>
<p><b>Camada de desejo que se manifesta:</b> {html.escape(c.desejo_ativo)} —
derivada de <code>prioridade × 10 + bônus da virtude governante</code> para este
NPC, não sorteada depois.</p>
<details><summary>Ficha completa do NPC</summary>
<pre>{html.escape(n.ficha())}</pre></details>
"""}


def api_conflito(dados: Dict[str, Any]) -> Dict[str, Any]:
    from xan.npcs import gerar_npc, resolver_conflito_de_desejos
    a = _aleat(dados, "conflito")
    n = gerar_npc(a, nivel=_int(dados, "nivel", 6, 0, 13))
    r = resolver_conflito_de_desejos(n, dados.get("a") or "dever",
                                     dados.get("b") or "ambicao", a)
    veto = r.resultado is None
    return {"html": f"""
<p class="tag {'ouro' if veto else 'ok'}">vence: {html.escape(r.vencedor)}</p>
<pre>{html.escape(r.resumo())}</pre>
<p><b>{html.escape(n.nome)}</b> — linha vermelha: <em>{html.escape(n.desejos.linha_vermelha)}</em></p>
"""}


def api_personagem(dados: Dict[str, Any]) -> Dict[str, Any]:
    from xan.personagens import EstadoDeJogo, criar_personagem
    a = _aleat(dados, "personagem")
    nivel = _int(dados, "nivel", 1, 0, 13)
    nucleo = _int(dados, "nucleo", None, 1, 9)
    if nivel >= 7 and dados.get("caminho", "xiandao") == "xiandao" and nucleo is None:
        nucleo = 5
    p = criar_personagem(
        nome=dados.get("nome") or "Sem Nome", aleat=a,
        metodo=dados.get("metodo") or "sorteio",
        caminho=dados.get("caminho") or "xiandao", nivel=nivel,
        lei=(dados.get("lei") or None),
        faccao=(dados.get("faccao") or ""), posto=(dados.get("posto") or ""),
        tabela_de_raiz=(dados.get("raiz") or "heroica"),
        grau_do_nucleo=nucleo)
    e = EstadoDeJogo.de_personagem(p)
    per = " · ".join(f"{k} {v}" for k, v in sorted(p.pericias.items()))
    compat = ""
    if p.lei:
        m, razoes = p.compatibilidade()
        compat = ("<p><b>Compatibilidade com a Lei:</b> " + str(m) + "%</p><ul>"
                  + "".join(f"<li>{html.escape(r)}</li>" for r in razoes) + "</ul>")
    tecnicas = ""
    from xan.artes import tecnicas_de_lei, tecnicas_livres
    aprendiveis = list(tecnicas_livres(nivel))
    if p.lei:
        aprendiveis += [t for t in tecnicas_de_lei(p.lei) if t.nivel_minimo <= nivel]
    if aprendiveis:
        tecnicas = ("<p><b>Técnicas disponíveis nesta Lei e nível:</b></p><ul>"
                    + "".join(f"<li><code>{t.codigo}</code> {html.escape(t.nome)} "
                              f"({html.escape(t.chines)}) — {t.tipo}, Qi {t.custo_qi}, "
                              f"{html.escape(t.dado_base) or 'sem dano'}</li>"
                              for t in aprendiveis) + "</ul>")
    return {"html": f"""
<pre>{html.escape(p.resumo())}</pre>
<div class="kpi">
  <div><b>{e.qi}</b><span>Qi máx</span></div>
  <div><b>{e.vitalidade}</b><span>Vitalidade máx</span></div>
  <div><b>{e.longevidade}</b><span>anos de vida</span></div>
  <div><b>{p.defesa('esquiva')}/{p.defesa('resistencia')}/{p.defesa('aparar')}</b>
    <span>defesa esq/res/ap</span></div>
</div>
<p><b>Perícias:</b> {html.escape(per) or 'nenhuma'}</p>
{compat}{tecnicas}
"""}


def api_besta(dados: Dict[str, Any]) -> Dict[str, Any]:
    from xan.bestiario import gerar_besta
    b = gerar_besta(_aleat(dados, "besta"),
                    nivel=_int(dados, "nivel", None, 0, 13),
                    elemento=(dados.get("elemento") or None),
                    terreno=dados.get("terreno") or "florestas")
    return {"html": f"<pre>{html.escape(b.ficha())}</pre>"}


def api_nucleo(dados: Dict[str, Any]) -> Dict[str, Any]:
    from xan.calendario import harmonia_elemental
    from xan.reinos import formar_nucleo_dourado
    harmonia = _int(dados, "harmonia", 0, 0, 12)
    razoes_h: List[str] = []
    elemento = (dados.get("elemento") or "").strip()
    if elemento:
        harmonia, razoes_h = harmonia_elemental(
            elemento, dados.get("estacao") or "primavera",
            _int(dados, "dia", 1, 1, 30), dados.get("polaridade") or "yang",
            dados.get("clima") or "limpo")
    g = formar_nucleo_dourado(
        qi_maximo_atual=_int(dados, "qi", 400, 0, 10 ** 7),
        fengshui=dados.get("fengshui") or "neutro",
        densidade_qi=dados.get("densidade") or "comum",
        harmonia=harmonia,
        estado_mental=_int(dados, "mental", 70, 0, 200),
        elixir=dados.get("elixir") or "nenhum",
        compatibilidade=_int(dados, "compat", 100, 0, 150),
        compreensao=_int(dados, "compreensao", 0, 0, 100000),
        mestre_presente=bool(dados.get("mestre")),
        artefato=dados.get("artefato") or "nenhum")
    harm = ""
    if razoes_h:
        harm = ("<p><b>Harmonia elemental do momento:</b> " + str(harmonia) +
                "/12</p><ul>" + "".join(f"<li>{html.escape(r)}</li>"
                                        for r in razoes_h) + "</ul>")
    return {"html": f"""
<div class="kpi">
  <div><b>{g.grau}</b><span>grau do núcleo</span></div>
  <div><b>{g.pontuacao}</b><span>pontuação</span></div>
  <div><b>{(10 - g.grau) * 25}</b><span>Qi bônus no nível 7</span></div>
</div>
<p class="tag ouro">{html.escape(g.titulo)}</p>
{harm}
{markdown_para_html(g.markdown())}
"""}


def api_mundo(dados: Dict[str, Any]) -> Dict[str, Any]:
    from xan.mapas import mapa_do_mundo
    from xan.mundo import gerar_mundo
    semente = (dados.get("semente") or "").strip()
    if not semente:
        raise ValueError("informe uma semente")
    m = gerar_mundo(semente,
                    provincias=_int(dados, "provincias", 9, 3, 20),
                    eventos=_int(dados, "eventos", 40, 1, 200),
                    anos_de_historia=_int(dados, "anos", 900, 10, 5000))
    svg = mapa_do_mundo(m.como_dict())
    nomes = [f.nome for f in m.faccoes]
    pares = [(a, b, m.relacao(a, b), m.relacao_como_fato(a, b))
             for a in nomes[:8] for b in nomes[:8] if a < b]
    pares.sort(key=lambda t: t[2])
    rel = "".join(
        f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td>"
        f"<td>{v:+d}</td><td><span class='tag {'ruim' if v<=-20 else ('ok' if v>=20 else '')}'>"
        f"{html.escape(f)}</span></td></tr>" for a, b, v, f in pares[:24])
    eventos = "".join(
        f"<tr><td>{e.ano}</td><td><b>{html.escape(e.titulo)}</b><br/>"
        f"<small>{html.escape(e.descricao)}</small></td>"
        f"<td><small>{html.escape(' · '.join(e.consequencias))}</small></td></tr>"
        for e in sorted(m.linha_do_tempo, key=lambda x: x.ano)[-14:])
    provincias = "".join(
        f"<tr><td><b>{html.escape(p.nome)}</b> {html.escape(p.chines)}</td>"
        f"<td>{html.escape(p.elemento)}</td><td>{html.escape(p.terreno)}</td>"
        f"<td>{p.densidade_qi}/10 <span class='tag'>{html.escape(p.densidade_fato)}</span></td>"
        f"<td>{p.perigo}/10</td><td>{len(p.sitios)}</td></tr>" for p in m.provincias)
    tesouros = "".join(
        f"<li><b>{html.escape(t.nome)}</b> ({html.escape(t.chines)}) — grau "
        f"{html.escape(t.grau)}<br/><small>{html.escape(t.onde)} · guardião: "
        f"{html.escape(t.guardiao)} · maldição: {html.escape(t.maldicao)}</small></li>"
        for t in m.tesouros[:6])
    return {"html": f"""
<div class="kpi">
  <div><b>{len(m.provincias)}</b><span>províncias</span></div>
  <div><b>{len(m.faccoes)}</b><span>facções</span></div>
  <div><b>{len(m.todos_os_sitios())}</b><span>sítios</span></div>
  <div><b>{len(m.linha_do_tempo)}</b><span>eventos</span></div>
  <div><b>{m.ano_atual}</b><span>ano corrente</span></div>
</div>
<h3>{html.escape(m.nome)}</h3>
<p>Semente <code>{html.escape(m.semente)}</code> · gerador
{html.escape(VERSAO_GERADOR)}</p>
<div class="mapa">{svg}</div>
<h3>Províncias</h3>
<div class="tabela-scroll"><table><thead><tr><th>Província</th><th>Elemento</th>
<th>Terreno</th><th>Qi</th><th>Perigo</th><th>Sítios</th></tr></thead>
<tbody>{provincias}</tbody></table></div>
<h3>Relações mais tensas</h3>
<div class="tabela-scroll"><table><thead><tr><th>A</th><th>B</th><th>Valor</th>
<th>Fato</th></tr></thead><tbody>{rel}</tbody></table></div>
<h3>Últimos eventos históricos</h3>
<div class="tabela-scroll"><table><thead><tr><th>Ano</th><th>Evento</th>
<th>Consequências no presente</th></tr></thead><tbody>{eventos}</tbody></table></div>
<h3>Tesouros lendários</h3><ul>{tesouros}</ul>
"""}


def api_combate(dados: Dict[str, Any]) -> Dict[str, Any]:
    from xan.combate import (Cenario, Combatente, ModoDeDefesa, atacar, defender,
                             encerrar, iniciar_encontro)
    from xan.npcs import gerar_npc
    from xan.personagens import criar_personagem
    a = _aleat(dados, "combate")
    diario = _diario_web(dados.get("auditar"))
    nivel = _int(dados, "nivel", 6, 1, 13)
    heroi = criar_personagem(nome=dados.get("heroi") or "Herói", aleat=a,
                             tabela_de_raiz="heroica", nivel=nivel,
                             caminho="xiandao", lei="PUREZA_JADE",
                             grau_do_nucleo=5 if nivel >= 7 else None,
                             faccao="Aliança")
    rival = gerar_npc(a, nome=dados.get("rival") or "Rival", nivel=nivel,
                      caminho="marcial", tabela_de_raiz="heroica",
                      faccao="Oposição")
    c1 = Combatente.de_personagem(heroi)
    c2 = Combatente.de_npc(rival)
    c1.modo = ModoDeDefesa(dados.get("defesa_heroi") or "esquiva")
    c2.modo = ModoDeDefesa(dados.get("defesa_rival") or "resistencia")
    cenario = Cenario(terreno=dados.get("terreno") or "neutro",
                      luz=dados.get("luz") or "plena",
                      clima=dados.get("clima") or "limpo",
                      fengshui=dados.get("fengshui") or "neutro",
                      densidade_qi=dados.get("densidade") or "comum",
                      formacao=dados.get("formacao") or "nenhuma",
                      descricao="Duelo gerado pela interface web.")
    enc = iniciar_encontro(cenario, [c1, c2], a, diario)
    itens: List[str] = []
    turnos = 0
    defensivo = bool(dados.get("defensivo"))
    while not enc.encerrado and turnos < 240:
        nome = enc.proximo()
        if nome is None:
            break
        atac = enc.get(nome)
        alvos = [c for c in enc.ativos() if c.nome != nome]
        if not alvos:
            encerrar(enc, "sem alvos")
            break
        if defensivo and atac.estado.vitalidade * 3 < atac.estado.vitalidade_maxima:
            defender(enc, nome, acao_de_defesa=True)
            itens.append(f"<li><b>rodada {enc.rodada}</b> — {html.escape(nome)} "
                         f"dedica o turno a defender (+3)</li>")
            turnos += 1
            continue
        g = atacar(enc, nome, alvos[0].nome, a, distancia="toque")
        classe = ("acerto" if g.acertou else "erro")
        if g.resultado is not None and g.resultado.critico:
            classe = "critico"
        det = ""
        if g.resultado is not None:
            det = (f" · total {g.resultado.total} vs DD "
                   f"{g.resultado.declaracao.dificuldade} ({g.resultado.margem:+d})")
        dano = ""
        if g.acertou:
            dano = (f" · <b>dano {g.dano}</b> (Qi absorveu {g.absorvido_pelo_qi}, "
                    f"Vitalidade perdeu {g.dano_na_vitalidade})")
        itens.append(f"<li class='{classe}'><b>rodada {enc.rodada}</b> — "
                     f"{html.escape(g.resumo().splitlines()[0])}{det}{dano}</li>")
        turnos += 1
    final = "".join(
        f"<div><b>{c.estado.vitalidade}</b><span>{html.escape(c.nome)} "
        f"({'CAÍDO' if c.caido else 'de pé'}) · Qi {c.estado.qi}</span></div>"
        for c in enc.combatentes.values())
    selo = ""
    if diario is not None:
        rel = diario.verificar()
        from xan.compromisso import conferir
        conf = conferir(diario)
        selo = (f"<div class='selo'>diário: {len(diario.registros)} registros · "
                f"cadeia íntegra: {'sim' if rel.ok else 'NÃO'} · "
                f"compromisso/revelação: {'ok' if conf.ok else 'FALHA'} · "
                f"raiz de Merkle {diario.raiz_merkle()[:32]}…</div>")
    return {"html": f"""
<p><b>Ordem de iniciativa:</b> {' → '.join(html.escape(x) for x in enc.ordem)}</p>
<p><b>Cenário:</b> {html.escape(json.dumps(cenario.fatos(), ensure_ascii=False))}</p>
<div class="kpi">{final}</div>
<p class="tag">rodadas: {enc.rodada} · turnos: {turnos}</p>
<ul class="log">{''.join(itens)}</ul>
{selo}
"""}


def api_tabelas(dados: Dict[str, Any]) -> Dict[str, Any]:
    qual = (dados.get("tabela") or "reinos").lower()
    linhas: List[str] = []

    def tabela(cabecalho: List[str], corpo: List[List[str]]):
        linhas.append("<div class='tabela-scroll'><table><thead><tr>"
                      + "".join(f"<th>{html.escape(str(c))}</th>" for c in cabecalho)
                      + "</tr></thead><tbody>")
        for l in corpo:
            linhas.append("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>"
                                           for c in l) + "</tr>")
        linhas.append("</tbody></table></div>")

    if qual == "reinos":
        from xan.reinos import REINOS
        tabela(["Nv.", "Trilha", "Xiandao", "Shendao", "Corpo", "Marcial",
                "Longevidade", "Qi base", "Vit. base", "Saída", "DD", "XP"],
               [[r.nivel, r.trilha, r.xiandao, r.shendao, r.corpo, r.marcial,
                 r.longevidade, r.qi_base, r.vitalidade_base, r.metodo,
                 r.dd_ruptura or "—", r.xp_necessario or "—"] for r in REINOS])
    elif qual == "leis":
        from xan.reinos import LEIS
        tabela(["Código", "Nome", "中文", "Caminho", "Elemento", "Família",
                "Requisitos", "DD extra", "Descrição"],
               [[c, LEIS[c].nome, LEIS[c].chines, LEIS[c].caminho,
                 LEIS[c].elemento, LEIS[c].familia,
                 ", ".join(f"{k.upper()}≥{v}"
                           for k, v in sorted(LEIS[c].requisitos.items())),
                 LEIS[c].dd_extra, LEIS[c].descricao] for c in sorted(LEIS)])
    elif qual == "regras":
        from xan.regras import listar_regras
        tabela(["Código", "Cap.", "Limite", "Fatos exigidos", "Descrição"],
               [[r.codigo, r.capitulo, f"{r.limite[0]:+d} a {r.limite[1]:+d}",
                 ", ".join(r.requer), r.descricao] for r in listar_regras()])
    elif qual == "tecnicas":
        from xan.artes import TECNICAS
        tabela(["Código", "Nome", "中文", "Tipo", "Lei", "Nv.", "Elemento",
                "Qi", "Alcance", "Dano", "Perícia", "Efeitos", "Suprema"],
               [[c, TECNICAS[c].nome, TECNICAS[c].chines, TECNICAS[c].tipo,
                 TECNICAS[c].lei, TECNICAS[c].nivel_minimo, TECNICAS[c].elemento,
                 TECNICAS[c].custo_qi, TECNICAS[c].alcance,
                 TECNICAS[c].dado_base or "—", TECNICAS[c].pericia,
                 "; ".join(TECNICAS[c].efeitos),
                 "sim" if TECNICAS[c].ignora_supressao else ""]
                for c in sorted(TECNICAS)])
    elif qual == "pericias":
        from xan.personagens import PERICIAS
        tabela(["Código", "Nome", "中文", "Atributo", "Grupo", "Uso sem treino",
                "Descrição"],
               [[c, PERICIAS[c].nome, PERICIAS[c].chines, PERICIAS[c].atributo,
                 PERICIAS[c].grupo,
                 "sim" if PERICIAS[c].sem_treinamento else "não",
                 PERICIAS[c].descricao] for c in sorted(PERICIAS)])
    elif qual == "bestiario":
        from xan.bestiario import BESTAS
        tabela(["Nv.", "Nome", "中文", "Classe", "Elemento", "Tamanho",
                "Vitalidade", "Qi", "Defesa", "Iniciativa", "Ataques",
                "Fraqueza", "Domável", "Inteligente"],
               [[b.nivel, b.nome, b.chines, b.classe, b.elemento, b.tamanho,
                 b.vitalidade, b.qi, b.defesa, f"{b.iniciativa:+d}",
                 "; ".join(f"{a.nome} {a.dado or '—'}" for a in b.ataques),
                 b.fraqueza, "sim" if b.domavel else "não",
                 "sim" if b.inteligente else "não"]
                for b in sorted(BESTAS.values(), key=lambda x: x.nivel)])
    elif qual == "predios":
        from xan.seitas import PREDIOS
        tabela(["Código", "Nome", "中文", "Custo", "Nv. mín.", "Produz",
                "Qtd/mês", "Efeito"],
               [[c, PREDIOS[c].nome, PREDIOS[c].chines, PREDIOS[c].custo,
                 PREDIOS[c].nivel_minimo_da_seita, PREDIOS[c].produz,
                 PREDIOS[c].quantidade_base, PREDIOS[c].efeito]
                for c in sorted(PREDIOS)])
    elif qual == "missoes":
        from xan.seitas import MISSOES
        tabela(["Código", "Missão", "DD", "Risco", "Prestígio", "Pedras", "XP",
                "Perícia", "Descrição"],
               [[c, MISSOES[c].nome, MISSOES[c].dificuldade, MISSOES[c].risco,
                 MISSOES[c].prestigio, f"{MISSOES[c].pedras[0]}–{MISSOES[c].pedras[1]}",
                 MISSOES[c].xp, MISSOES[c].pericia, MISSOES[c].descricao]
                for c in sorted(MISSOES)])
    else:
        raise ValueError(f"tabela desconhecida: {qual}")
    return {"html": "".join(linhas)}


def api_justica(dados: Dict[str, Any]) -> Dict[str, Any]:
    from xan.justica import bateria_completa
    a = _aleat(dados, "justica")
    cert = bateria_completa(a, amostras=_int(dados, "amostras", 20000, 1000, 200000),
                            amostras_leves=_int(dados, "leves", 8000, 500, 100000))
    linhas = []
    for t in cert.testes:
        linhas.append(
            f"<tr><td><span class='tag {'ok' if t.ok else 'ruim'}'>{'OK' if t.ok else 'FALHA'}</span></td>"
            f"<td>{html.escape(t.familia)}</td><td>{html.escape(t.nome)}</td>"
            f"<td class='mono'>{t.estatistica:.4f}</td>"
            f"<td class='mono'>{t.p_valor:.4g}</td><td>{t.amostras}</td>"
            f"<td><small>{html.escape(t.nota)}</small></td></tr>")
    return {"html": f"""
<div class="kpi">
  <div><b>{len(cert.testes)}</b><span>testes</span></div>
  <div><b>{cert.total_de_amostras:,}</b><span>amostras</span></div>
  <div><b>{sum(1 for t in cert.testes if t.ok)}</b><span>aprovados</span></div>
  <div><b>{html.escape(cert.veredito)}</b><span>veredito</span></div>
</div>
<p>{html.escape(cert.resumo)}</p>
<div class="tabela-scroll"><table><thead><tr><th></th><th>Fam.</th><th>Teste</th>
<th>Estatística</th><th>p-valor</th><th>n</th><th>Nota</th></tr></thead>
<tbody>{''.join(linhas)}</tbody></table></div>
"""}


def api_certificado(dados: Dict[str, Any]) -> Dict[str, Any]:
    caminho = os.path.join(DOCS_DIR, "CERTIFICADO_DE_JUSTICA.md")
    if not os.path.isfile(caminho):
        return {"html": "<div class='aviso'>Certificado ainda não gerado. Rode "
                        "<code>./xan justica --saida docs/CERTIFICADO_DE_JUSTICA</code>.</div>"}
    with open(caminho, encoding="utf-8") as fh:
        return {"html": markdown_para_html(fh.read())}


def api_auditoria(dados: Dict[str, Any]) -> Dict[str, Any]:
    from xan.auditoria import DiarioDeAuditoria
    from xan.compromisso import conferir
    if not os.path.isfile(AUDITORIA_WEB):
        return {"html": "<div class='nota'>Ainda não há diário da interface. "
                        "Faça uma rolagem com <em>gravar no diário</em> marcado.</div>"}
    d = DiarioDeAuditoria(AUDITORIA_WEB, criar=False)
    acao = dados.get("acao") or "verificar"
    if acao == "verificar":
        rel = d.verificar()
        conf = conferir(d)
        return {"html": f"""
<div class="kpi">
  <div><b>{len(d.registros)}</b><span>registros</span></div>
  <div><b>{'ÍNTegro' if rel.ok else 'VIOLADO'}</b><span>cadeia SHA-256</span></div>
  <div><b>{conf.compromissos}/{conf.rolagens}/{conf.revelacoes}</b>
    <span>compromissos/rolagens/revelações</span></div>
</div>
<p class="tag {'ok' if rel.ok else 'ruim'}">cadeia: {'ok' if rel.ok else rel.motivo}</p>
<p class="tag {'ok' if conf.ok else 'ruim'}">ordem compromisso→rolagem→revelação:
 {'ok' if conf.ok else '; '.join(conf.problemas[:5])}</p>
<div class="selo">raiz de Merkle: {d.raiz_merkle()}<br/>cabeça: {d.cabeca}</div>
<p>Arquivo: <code>{html.escape(AUDITORIA_WEB)}</code></p>
"""}
    if acao == "resumo":
        tipos: Dict[str, int] = {}
        for r in d.registros:
            tipos[r.tipo] = tipos.get(r.tipo, 0) + 1
        corpo = "".join(f"<tr><td>{html.escape(t)}</td><td>{tipos[t]}</td></tr>"
                        for t in sorted(tipos))
        return {"html": f"<div class='tabela-scroll'><table><thead><tr>"
                        f"<th>Tipo</th><th>Quantidade</th></tr></thead>"
                        f"<tbody>{corpo}</tbody></table></div>"
                        f"<div class='selo'>raiz de Merkle: {d.raiz_merkle()}</div>"}
    # últimos registros
    linhas = []
    for r in d.registros[-25:]:
        conteudo = json.dumps(r.conteudo, ensure_ascii=False, sort_keys=True)
        if len(conteudo) > 240:
            conteudo = conteudo[:240] + "…"
        linhas.append(f"<tr><td>{r.indice}</td><td>{html.escape(r.tipo)}</td>"
                      f"<td>{html.escape(r.ator)}</td>"
                      f"<td class='mono'><small>{html.escape(conteudo)}</small></td>"
                      f"<td class='mono'><small>{html.escape(r.hash[:16])}…</small></td></tr>")
    return {"html": f"<div class='tabela-scroll'><table><thead><tr><th>#</th>"
                    f"<th>Tipo</th><th>Ator</th><th>Conteúdo</th><th>Hash</th>"
                    f"</tr></thead><tbody>{''.join(linhas)}</tbody></table></div>"}


ROTAS_POST = {
    "/api/rolar": api_rolar,
    "/api/teste": api_teste,
    "/api/npc": api_npc,
    "/api/conduta": api_conduta,
    "/api/conflito": api_conflito,
    "/api/personagem": api_personagem,
    "/api/besta": api_besta,
    "/api/nucleo": api_nucleo,
    "/api/mundo": api_mundo,
    "/api/combate": api_combate,
    "/api/tabelas": api_tabelas,
    "/api/justica": api_justica,
    "/api/certificado": api_certificado,
    "/api/auditoria": api_auditoria,
}


# ==========================================================================
# Handler HTTP
# ==========================================================================
class Handler(BaseHTTPRequestHandler):
    server_version = f"XAN/{__version__}"
    protocol_version = "HTTP/1.1"

    def log_message(self, formato: str, *args: Any) -> None:  # noqa: D102
        sys.stderr.write("[xan] %s\n" % (formato % args))

    # -- utilidades ---------------------------------------------------------
    def _enviar(self, corpo: bytes, tipo: str = "text/html; charset=utf-8",
                codigo: int = 200) -> None:
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(corpo)

    def _html(self, texto: str, codigo: int = 200) -> None:
        self._enviar(texto.encode("utf-8"), codigo=codigo)

    def _json(self, dados: Any, codigo: int = 200) -> None:
        self._enviar(json.dumps(dados, ensure_ascii=False).encode("utf-8"),
                     "application/json; charset=utf-8", codigo)

    # -- rotas --------------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802
        rota = urlparse(self.path).path.rstrip("/") or "/"
        try:
            if rota == "/":
                return self._html(pagina_inicio())
            if rota == "/livro":
                return self._html(pagina_livro())
            if rota.startswith("/livro/"):
                return self._html(pagina_livro(rota[len("/livro/"):]))
            if rota == "/dados":
                return self._html(pagina_dados())
            if rota == "/npc":
                return self._html(pagina_npc())
            if rota == "/personagem":
                return self._html(pagina_personagem())
            if rota == "/mundo":
                return self._html(pagina_mundo())
            if rota == "/combate":
                return self._html(pagina_combate())
            if rota == "/tabelas":
                return self._html(pagina_tabelas())
            if rota == "/justica":
                return self._html(pagina_justica())
            if rota == "/auditoria":
                return self._html(pagina_auditoria())
            if rota == "/api/saude":
                return self._json({"ok": True, "motor": __motor__,
                                   "versao": __version__})
            if rota.startswith("/api/"):
                consulta = {k: v[0] for k, v in
                            parse_qs(urlparse(self.path).query).items()}
                fn = ROTAS_POST.get(rota)
                if fn is None:
                    return self._json({"erro": f"rota desconhecida {rota}"}, 404)
                return self._json(fn(consulta))
            return self._html(pagina("Não encontrado",
                                     _art("404", "<p>Rota inexistente.</p>")), 404)
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            return self._json({"erro": f"{type(exc).__name__}: {exc}"}, 500)

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def do_POST(self) -> None:  # noqa: N802
        rota = urlparse(self.path).path.rstrip("/") or "/"
        fn = ROTAS_POST.get(rota)
        if fn is None:
            return self._json({"erro": f"rota desconhecida {rota}"}, 404)
        try:
            tamanho = int(self.headers.get("Content-Length") or 0)
            bruto = self.rfile.read(tamanho) if tamanho else b"{}"
            dados = json.loads(bruto.decode("utf-8") or "{}")
            if not isinstance(dados, dict):
                raise ValueError("o corpo precisa ser um objeto JSON")
            return self._json(fn(dados))
        except (ValueError, KeyError, TypeError) as exc:
            return self._json({"erro": str(exc)}, 400)
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            return self._json({"erro": f"{type(exc).__name__}: {exc}"}, 500)


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Servidor web do XAN")
    p.add_argument("--host", default=os.environ.get("XAN_HOST", "0.0.0.0"))
    p.add_argument("--porta", type=int,
                   default=int(os.environ.get("XAN_PORTA", "8000")))
    args = p.parse_args(argv)
    servidor = ThreadingHTTPServer((args.host, args.porta), Handler)
    servidor.daemon_threads = True
    print(f"{__nome__} {__version__} — {__motor__}")
    print(f"servindo em http://{args.host}:{args.porta}/  (Ctrl-C para parar)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nencerrando.")
    finally:
        servidor.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
