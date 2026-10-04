# -*- coding: utf-8 -*-
"""
XAN — interface de linha de comando.
====================================

Todo verbo do sistema tem um comando. Nada aqui decide nada por conta própria:
a CLI apenas monta Declarações e as entrega ao motor imparcial.

    python3 -m xan.cli motor info
    python3 -m xan.cli rolar "4d6kh3" --ator mesa
    python3 -m xan.cli mundo gerar --semente rios-e-lagos --saida ../../mundos/exemplo
    python3 -m xan.cli justica --saida ../../docs/CERTIFICADO_DE_JUSTICA

Sem ``--semente`` o motor usa a fonte viva (ruído do sistema operacional).
Com ``--semente`` fica reproduzível — útil para preparar sessão e para testar.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from typing import Any, Dict, List, Optional, Sequence

from . import __version__, __motor__, __nome__
from .entropia import Aleatoriedade, FonteSemeada, FonteViva

__all__ = ["main", "construir_parser"]


# --------------------------------------------------------------------------
# utilidades
# --------------------------------------------------------------------------
def _aleatoriedade(args: argparse.Namespace) -> Aleatoriedade:
    semente = getattr(args, "semente", None)
    contexto = getattr(args, "contexto_da_fonte", "cli")
    if semente:
        return Aleatoriedade(FonteSemeada(semente, contexto))
    return Aleatoriedade(FonteViva())


def _diario(caminho: Optional[str], criar: bool = True):
    from .auditoria import DiarioDeAuditoria
    if not caminho:
        return None
    os.makedirs(os.path.dirname(os.path.abspath(caminho)) or ".", exist_ok=True)
    return DiarioDeAuditoria(caminho, criar=criar)


def _fatos(texto: Optional[str]) -> Dict[str, Any]:
    if not texto:
        return {}
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"--fatos precisa ser JSON válido: {exc}")
    if not isinstance(dados, dict):
        raise SystemExit("--fatos precisa ser um objeto JSON")
    return dados


def _lista(texto: Optional[str]) -> tuple:
    if not texto:
        return ()
    return tuple(x.strip() for x in texto.split(",") if x.strip())


def _imprimir(texto: str) -> None:
    print(texto)


# --------------------------------------------------------------------------
# comandos
# --------------------------------------------------------------------------
def cmd_motor_info(args: argparse.Namespace) -> int:
    a = _aleatoriedade(args)
    _imprimir(f"{__nome__} {__version__} — {__motor__}")
    _imprimir(f"fonte de entropia : {a.fonte.descricao()}")
    _imprimir(f"semente declarada : {getattr(args, 'semente', None) or '— (fonte viva)'}")
    _imprimir("")
    _imprimir("Amostra (10 rolagens de 1d20): "
              + ", ".join(str(a.entre(1, 20)) for _ in range(10)))
    c = a.consumo()
    _imprimir("")
    _imprimir(f"chamadas à fonte  : {c.chamadas}")
    _imprimir(f"bytes solicitados : {c.bytes_solicitados}")
    _imprimir("")
    _imprimir("A mesma semente reproduz exatamente a mesma sequência:")
    b1 = Aleatoriedade(FonteSemeada("demonstracao", "cli"))
    b2 = Aleatoriedade(FonteSemeada("demonstracao", "cli"))
    s1 = [b1.entre(1, 20) for _ in range(8)]
    s2 = [b2.entre(1, 20) for _ in range(8)]
    _imprimir(f"  {s1}")
    _imprimir(f"  {s2}  → {'iguais' if s1 == s2 else 'DIFERENTES (falha grave)'}")
    return 0 if s1 == s2 else 1


def cmd_motor_autoteste(args: argparse.Namespace) -> int:
    from .resolucao import verificar_invariantes
    rel = verificar_invariantes()
    _imprimir(rel.texto())
    if not rel.ok:
        return 1
    from .regras import conflitos, REGISTRO
    _imprimir(f"\nregras registradas: {len(REGISTRO)}")
    _imprimir(f"conflitos declarados: {conflitos(tuple(REGISTRO))}")
    a = _aleatoriedade(args)
    from .dados import rolar
    totais = [rolar("1d20", a).total for _ in range(2000)]
    _imprimir(f"\n2000×1d20: média {sum(totais)/len(totais):.3f} "
              f"(teórico 10.500), mín {min(totais)}, máx {max(totais)}")
    _imprimir("AUTO-TESTE: OK")
    return 0


def cmd_justica(args: argparse.Namespace) -> int:
    from .justica import bateria_completa, emitir_certificado
    _imprimir(f"Executando a bateria de justiça ({args.amostras} amostras "
              f"por teste pesado)…")
    if args.saida:
        os.makedirs(os.path.dirname(os.path.abspath(args.saida)) or ".",
                    exist_ok=True)
        cert, arq_md, arq_json = emitir_certificado(
            args.saida, _aleatoriedade(args), amostras=args.amostras,
            amostras_leves=args.leves)
        _imprimir(cert.resumo)
        _imprimir(f"VEREDITO: {cert.veredito}")
        _imprimir(f"gravado em {arq_md}")
        _imprimir(f"           {arq_json}")
        return 0 if cert.aprovado else 1
    cert = bateria_completa(_aleatoriedade(args), amostras=args.amostras,
                            amostras_leves=args.leves)
    for t in cert.testes:
        marca = "OK " if t.ok else "FAL"
        _imprimir(f" {marca} [{t.familia}] {t.nome:40} p={t.p_valor:.4g}")
    _imprimir(cert.resumo)
    _imprimir(f"VEREDITO: {cert.veredito}")
    return 0 if cert.aprovado else 1


def cmd_rolar(args: argparse.Namespace) -> int:
    from .dados import rolar, valor_esperado, minimo_maximo, ErroDeNotacao
    from .compromisso import rolagem_auditada
    a = _aleatoriedade(args)
    diario = _diario(args.diario)
    ator = args.ator or "mesa"
    try:
        if diario is not None:
            r, comp, indice = rolagem_auditada(args.expressao, a, diario,
                                               ator=ator)
        else:
            r = rolar(args.expressao, a)
            indice = None
    except ErroDeNotacao as exc:
        _imprimir(f"notação inválida: {exc}")
        return 2
    _imprimir(f"{args.expressao} → {r.total}")
    for t in r.termos:
        _imprimir(f"  {t.expressao()}: faces {list(t.faces)} → mantidas "
                  f"{list(t.mantidas)}" + (f" (descartadas {list(t.descartadas)})"
                                           if t.descartadas else "")
                  + (f" · explosões {t.explosivos}" if t.explosivos else ""))
    if r.constante:
        _imprimir(f"  constante: {r.constante:+d}")
    if args.teoria:
        from .dados import _parsear
        termos, c = _parsear(args.expressao)
        _imprimir(f"  valor esperado: {float(valor_esperado(termos, c)):.4f} "
                  f"= {valor_esperado(termos, c)}")
        _imprimir(f"  mínimo/máximo: {minimo_maximo(termos, c)}")
    if diario is not None:
        _imprimir(f"  registrado no diário no índice #{indice}")
        _imprimir(f"  token do compromisso (gravado ANTES do dado): {comp.token}")
    return 0


def cmd_teste(args: argparse.Namespace) -> int:
    from .resolucao import Declaracao, resolver, Resultado
    a = _aleatoriedade(args)
    diario = _diario(args.diario)
    fatos = _fatos(args.fatos)
    decl = Declaracao(
        acao=args.acao, ator=args.ator, atributo=args.atributo,
        valor_atributo=args.valor, pericia=args.pericia,
        graduacao=args.graduacao, dificuldade=args.dd,
        regras=_lista(args.regras), fatos=fatos,
        contexto=_fatos(args.contexto_json),
    )
    res = resolver(decl, a, diario)
    _imprimir(res.resumo())
    if args.json:
        _imprimir(json.dumps(res.como_dict() if hasattr(res, "como_dict")
                             else {"total": res.total, "margem": res.margem,
                                   "grau": res.grau, "sucesso": res.sucesso},
                             ensure_ascii=False, indent=2))
    return 0 if res.sucesso else 1


def cmd_oposto(args: argparse.Namespace) -> int:
    from .resolucao import Declaracao, teste_oposto
    a = _aleatoriedade(args)
    diario = _diario(args.diario)
    da = Declaracao(acao=args.acao, ator=args.ator_a, atributo=args.atributo,
                    valor_atributo=args.valor_a, pericia=args.pericia,
                    graduacao=args.graduacao_a, dificuldade=0,
                    regras=_lista(args.regras), fatos=_fatos(args.fatos),
                    contexto=_fatos(args.contexto_json))
    db = Declaracao(acao=args.acao, ator=args.ator_b, atributo=args.atributo,
                    valor_atributo=args.valor_b, pericia=args.pericia,
                    graduacao=args.graduacao_b, dificuldade=0,
                    regras=_lista(args.regras), fatos=_fatos(args.fatos),
                    contexto=_fatos(args.contexto_json))
    res = teste_oposto(da, db, a, diario)
    _imprimir(res.resumo())
    _imprimir(f"vencedor: {res.vencedor} ({res.criterio})")
    return 0


def cmd_mundo_gerar(args: argparse.Namespace) -> int:
    from .mundo import gerar_mundo, gerar_npcs_do_mundo
    from .mapas import mapa_do_mundo, mapa_da_provincia, salvar_svg
    if not args.semente:
        raise SystemExit("gerar mundo exige --semente (o mundo precisa ser reproduzível)")
    _imprimir(f"Gerando mundo a partir da semente {args.semente!r}…")
    mundo = gerar_mundo(args.semente, provincias=args.provincias,
                        eventos=args.eventos,
                        anos_de_historia=args.anos_de_historia)
    os.makedirs(args.saida, exist_ok=True)
    base = os.path.join(args.saida, "mundo")
    mundo.exportar_json(base + ".json")
    with open(base + ".md", "w", encoding="utf-8") as fh:
        fh.write(mundo.markdown())
    salvar_svg(mapa_do_mundo(mundo.como_dict()), base + ".svg")
    os.makedirs(os.path.join(args.saida, "provincias"), exist_ok=True)
    for p in mundo.provincias:
        salvar_svg(mapa_da_provincia(p.como_dict(), nome_do_mundo=mundo.nome),
                   os.path.join(args.saida, "provincias", f"{p.nome}.svg"))
    if args.npcs:
        a = Aleatoriedade(FonteSemeada(args.semente, "npcs-do-mundo"))
        npcs = gerar_npcs_do_mundo(mundo, a, args.npcs)
        with open(os.path.join(args.saida, "npcs.md"), "w", encoding="utf-8") as fh:
            fh.write(f"# NPCs notáveis de {mundo.nome}\n\n"
                     f"*Semente `{args.semente}` — sempre os mesmos rostos.*\n\n")
            for n in npcs:
                fh.write(n.ficha() + "\n\n---\n\n")
        with open(os.path.join(args.saida, "npcs.json"), "w", encoding="utf-8") as fh:
            json.dump([_npc_para_json(n) for n in npcs], fh, ensure_ascii=False,
                      indent=2)
    _imprimir(f"  {len(mundo.provincias)} províncias, {len(mundo.faccoes)} facções, "
              f"{len(mundo.todos_os_sitios())} sítios, {len(mundo.linha_do_tempo)} "
              f"eventos históricos")
    _imprimir(f"  gravado em {args.saida}/")
    return 0


def _npc_para_json(n: Any) -> Dict[str, Any]:
    return {
        "nome": n.nome, "sexo": n.sexo, "idade": n.idade, "raca": n.raca,
        "ocupacao": n.ocupacao, "faccao": n.faccao, "posto": n.posto,
        "localizacao": n.localizacao, "nivel": n.nivel, "caminho": n.caminho,
        "lei": n.lei, "atributos": dict(n.atributos), "pericias": dict(n.pericias),
        "virtudes": {"ren": n.virtudes.ren, "yi": n.virtudes.yi,
                     "li": n.virtudes.li, "zhi": n.virtudes.zhi,
                     "xin": n.virtudes.xin},
        "temperamento": n.temperamento.codigo, "tracos": list(n.tracos),
        "desejos": {"imediato": n.desejos.imediato, "ambicao": n.desejos.ambicao,
                    "obsessao": n.desejos.obsessao, "medo": n.desejos.medo,
                    "dever": n.desejos.dever, "segredo": n.desejos.segredo,
                    "linha_vermelha": n.desejos.linha_vermelha,
                    "preco": n.desejos.preco},
        "raiz": {"elementos": list(n.raiz.elementos), "grau": n.raiz.grau,
                 "pureza": n.raiz.pureza, "mutacao": n.raiz.mutacao},
        "face": n.face, "estado_mental": n.estado_mental,
        "pedras_espirituais": n.pedras_espirituais,
        "tecnicas": list(n.tecnicas),
        "identificador": n.identificador,
    }


def cmd_npc(args: argparse.Namespace) -> int:
    from .npcs import gerar_npc
    a = _aleatoriedade(args)
    n = gerar_npc(a, nivel=args.nivel, ocupacao=args.ocupacao,
                  faccao=args.faccao or "", localizacao=args.local or "",
                  caminho=args.caminho, tabela_de_raiz=args.raiz,
                  agendas=args.agendas)
    _imprimir(n.ficha())
    return 0


def cmd_personagem(args: argparse.Namespace) -> int:
    from .personagens import criar_personagem, EstadoDeJogo
    a = _aleatoriedade(args)
    p = criar_personagem(nome=args.nome, aleat=a, raca=args.raca,
                         metodo=args.metodo, pontos=args.pontos,
                         caminho=args.caminho, nivel=args.nivel, lei=args.lei,
                         pontos_de_pericia=args.pericias,
                         faccao=args.faccao or "", posto=args.posto or "",
                         tabela_de_raiz=args.raiz,
                         grau_do_nucleo=args.nucleo)
    _imprimir(p.resumo())
    _imprimir("")
    _imprimir("Perícias: " + (", ".join(f"{k} {v}" for k, v in sorted(p.pericias.items()))
                              or "nenhuma"))
    if p.lei:
        m, razoes = p.compatibilidade()
        _imprimir(f"Compatibilidade com a Lei: {m}%")
        for r in razoes:
            _imprimir(f"  - {r}")
    e = EstadoDeJogo.de_personagem(p)
    _imprimir(f"Qi {e.qi}/{e.qi_maximo} · Vitalidade {e.vitalidade}/"
              f"{e.vitalidade_maxima} · Longevidade {e.longevidade} anos")
    _imprimir(f"Defesa: esquiva {p.defesa('esquiva')} · resistência "
              f"{p.defesa('resistencia')} · aparar {p.defesa('aparar')}")
    return 0


def cmd_besta(args: argparse.Namespace) -> int:
    from .bestiario import gerar_besta, BESTAS
    if args.catalogo:
        for b in BESTAS.values():
            _imprimir(b.ficha() + "\n" + "-" * 70)
        return 0
    a = _aleatoriedade(args)
    b = gerar_besta(a, nivel=args.nivel, elemento=args.elemento,
                    terreno=args.terreno, classe=args.classe)
    _imprimir(b.ficha())
    return 0


def cmd_ruptura(args: argparse.Namespace) -> int:
    from .reinos import (tentar_ruptura, lei_de, dd_de_ruptura, reino_de,
                         compatibilidade_de_lei)
    lei = lei_de(args.lei)
    a = _aleatoriedade(args)
    diario = _diario(args.diario)
    if reino_de(args.nivel).metodo != "rolagem":
        _imprimir(f"O nível {args.nivel} sai por "
                  f"'{reino_de(args.nivel).metodo}', não por rolagem.")
        _imprimir("Use 'xan nucleo' (pontuação) ou 'xan tribulacao'.")
        return 2
    attrs = {"per": args.per, "con": args.con, "cha": args.cha,
             "int": args.int_, "luk": args.luk, "pot": args.pot}
    match, razoes = compatibilidade_de_lei(attrs, lei)
    _imprimir(f"Lei: {lei.nome} ({lei.chines}) — compatibilidade {match}%")
    for r in razoes:
        _imprimir(f"  - {r}")
    _imprimir(f"DD da ruptura: {dd_de_ruptura(args.nivel, match, lei)}")
    fatos = {"fengshui": args.fengshui, "densidade_qi": args.densidade,
             "elixir": args.elixir, "meditou": args.meditou}
    res = tentar_ruptura(ator=args.ator, nivel_atual=args.nivel,
                         compatibilidade=match, lei=lei, valor_de_int=args.int_,
                         graduacao_de_compreensao=args.compreensao,
                         fatos=fatos, aleat=a, diario=diario)
    _imprimir("")
    _imprimir(res.resumo())
    if res.desvio_de_qi:
        _imprimir(f"\nDESVIO DE QI (走火入魔) — face {res.desvio_de_qi[0]}: "
                  f"{res.desvio_de_qi[1]}")
    return 0 if res.avancou else 1


def cmd_nucleo(args: argparse.Namespace) -> int:
    from .reinos import formar_nucleo_dourado
    from .calendario import harmonia_elemental
    harmonia = args.harmonia
    if args.elemento:
        harmonia, razoes = harmonia_elemental(
            args.elemento, args.estacao, args.dia, args.polaridade, args.clima)
        _imprimir("Harmonia elemental do momento:")
        for r in razoes:
            _imprimir(f"  - {r}")
        _imprimir(f"  total: {harmonia}/12\n")
    g = formar_nucleo_dourado(
        qi_maximo_atual=args.qi, fengshui=args.fengshui,
        densidade_qi=args.densidade, harmonia=harmonia,
        estado_mental=args.mental, elixir=args.elixir,
        compatibilidade=args.compat, compreensao=args.compreensao,
        mestre_presente=args.mestre, artefato=args.artefato)
    _imprimir(g.markdown())
    return 0


def cmd_tribulacao(args: argparse.Namespace) -> int:
    from .reinos import tribulacao_celestial, raios_de_tribulacao
    a = _aleatoriedade(args)
    diario = _diario(args.diario)
    _imprimir(f"Raios previstos: {raios_de_tribulacao(args.nivel, args.demoniaca)}")
    t = tribulacao_celestial(
        ator=args.ator, nivel=args.nivel, demoniaca=args.demoniaca,
        valor_de_con=args.con, graduacao_de_defesa=args.defesa,
        vitalidade=args.vitalidade, qi_atual=args.qi,
        fatos={"artefato": args.artefato, "formacao": args.formacao,
               "elixir": args.elixir, "anos_queimados": args.anos_queimados},
        aleat=a, diario=diario)
    _imprimir("")
    _imprimir(t.resumo_texto)
    return 0 if t.sobreviveu else 1


def cmd_combate(args: argparse.Namespace) -> int:
    from .combate import (Combatente, Cenario, ModoDeDefesa, atacar, defender,
                          encerrar, iniciar_encontro)
    from .personagens import criar_personagem
    from .npcs import gerar_npc
    a = _aleatoriedade(args)
    diario = _diario(args.diario)
    heroi = criar_personagem(nome=args.heroi, aleat=a, tabela_de_raiz="heroica",
                             caminho="xiandao", nivel=args.nivel,
                             lei=args.lei, faccao="Aliança")
    rival = gerar_npc(a, nome=args.rival, nivel=args.nivel, faccao="Oposição",
                      caminho="marcial", tabela_de_raiz="heroica")
    c1 = Combatente.de_personagem(heroi)
    c2 = Combatente.de_npc(rival)
    c1.modo = ModoDeDefesa(args.defesa_heroi)
    c2.modo = ModoDeDefesa(args.defesa_rival)
    cenario = Cenario(terreno=args.terreno, luz=args.luz, clima=args.clima,
                      fengshui=args.fengshui, densidade_qi=args.densidade,
                      formacao=args.formacao, descricao="Duelo gerado pela CLI.")
    enc = iniciar_encontro(cenario, [c1, c2], a, diario)
    _imprimir(f"{heroi.resumo()}\n\n{rival.ficha().splitlines()[0]}\n")
    _imprimir(f"Cenário: {cenario.fatos()}\n")
    _imprimir("Ordem de iniciativa: " + " → ".join(enc.ordem) + "\n")
    turnos = 0
    while not enc.encerrado and turnos < args.max_turnos:
        nome = enc.proximo()
        if nome is None:
            break
        atac = enc.get(nome)
        alvos = [c for c in enc.ativos() if c.nome != nome]
        if not alvos:
            encerrar(enc, "sem alvos")
            break
        if args.defensivo and atac.estado.vitalidade * 2 < atac.estado.vitalidade_maxima:
            defender(enc, nome, acao_de_defesa=True)
            _imprimir(f"[rodada {enc.rodada}] {nome} defende.")
            turnos += 1
            continue
        g = atacar(enc, nome, alvos[0].nome, a, distancia="toque")
        _imprimir(f"[rodada {enc.rodada}] {g.resumo()}")
        turnos += 1
    _imprimir("")
    for c in enc.combatentes.values():
        _imprimir(f"  {c.nome:22} Vitalidade {c.estado.vitalidade:5}/"
                  f"{c.estado.vitalidade_maxima:5}  Qi {c.estado.qi:5}  "
                  f"{'CAÍDO' if c.caido else 'de pé'}")
    _imprimir(f"\nRodadas: {enc.rodada} · turnos: {turnos}")
    if diario is not None:
        rel = diario.verificar()
        _imprimir(f"Diário íntegro: {rel.ok} ({len(diario.registros)} registros)")
    return 0


def cmd_auditoria(args: argparse.Namespace) -> int:
    from .auditoria import DiarioDeAuditoria
    from .compromisso import conferir
    d = DiarioDeAuditoria(args.diario, criar=False)
    if args.acao == "verificar":
        rel = d.verificar()
        _imprimir(f"íntegro : {rel.ok}")
        _imprimir(f"registros: {len(d.registros)}")
        _imprimir(f"raiz merkle: {d.raiz_merkle()}")
        if not rel.ok:
            _imprimir(f"MOTIVO: {rel.motivo}")
        rep = conferir(d)
        _imprimir(f"compromisso/revelação: {'OK' if rep.ok else 'FALHA'}")
        return 0 if rel.ok and rep.ok else 1
    if args.acao == "selar":
        cabeca = d.cabeca
        caminho = args.saida or (args.diario + ".selo")
        d.selar(caminho)
        _imprimir(f"selo gravado em {caminho}")
        _imprimir(f"hash da cabeça: {cabeca}")
        _imprimir("Guarde este arquivo fora do repositório da mesa: ele prova")
        _imprimir("que ninguém reescreveu o diário depois desta data.")
        return 0
    if args.acao == "resumo":
        tipos = {}
        for r in d.registros:
            tipos[r.tipo] = tipos.get(r.tipo, 0) + 1
        _imprimir(f"registros: {len(d.registros)}")
        for t in sorted(tipos):
            _imprimir(f"  {t:26} {tipos[t]}")
        return 0
    raise SystemExit(f"ação desconhecida {args.acao}")


def cmd_listar(args: argparse.Namespace) -> int:
    qual = args.tabela
    if qual == "leis":
        from .reinos import LEIS
        for c in sorted(LEIS):
            l = LEIS[c]
            req = ", ".join(f"{k.upper()}≥{v}" for k, v in sorted(l.requisitos.items()))
            _imprimir(f"{c:24} {l.nome:44} {l.elemento:8} {l.caminho:8} {req}")
    elif qual == "regras":
        from .regras import listar_regras
        for r in listar_regras():
            _imprimir(f"{r.codigo:32} cap.{r.capitulo:6} limite {r.limite}  "
                      f"requer {list(r.requer)}")
            _imprimir(f"    {r.descricao}")
    elif qual == "tecnicas":
        from .artes import TECNICAS
        for c in sorted(TECNICAS):
            t = TECNICAS[c]
            _imprimir(f"{c:26} nv{t.nivel_minimo:<2} {t.tipo:9} {t.elemento:8} "
                      f"qi{t.custo_qi:<4} {t.nome} ({t.chines}) — {t.dado_base or '—'}")
    elif qual == "pericias":
        from .personagens import PERICIAS
        for c in sorted(PERICIAS):
            p = PERICIAS[c]
            _imprimir(f"{c:24} {p.nome:26} {p.atributo:4} {p.grupo:9} "
                      f"{'livre' if p.sem_treinamento else 'treinada'}")
    elif qual == "reinos":
        from .reinos import REINOS
        _imprimir(f"{'nv':>3} {'trilha':22} {'xiandao':22} {'marcial':28} "
                  f"{'método':11} {'dd':>3} {'xp':>8} {'vida':>6}")
        for r in REINOS:
            _imprimir(f"{r.nivel:>3} {r.trilha:22} {r.xiandao:22} {r.marcial:28} "
                      f"{r.metodo:11} {r.dd_ruptura:>3} {r.xp_necessario:>8} "
                      f"{r.longevidade:>6}")
    elif qual == "bestiario":
        from .bestiario import BESTAS
        for b in sorted(BESTAS.values(), key=lambda x: x.nivel):
            _imprimir(f"nv{b.nivel:<3} {b.nome:34} {b.chines:8} {b.classe:18} "
                      f"{b.elemento:8} {b.tamanho:10} vit{b.vitalidade:<5} "
                      f"def{b.defesa}")
    elif qual == "predios":
        from .seitas import PREDIOS
        for c in sorted(PREDIOS):
            p = PREDIOS[c]
            _imprimir(f"{c:24} {p.nome:24} {p.custo:>7} pedras  nv≥{p.nivel_minimo_da_seita}"
                      f"  → {p.produz} {p.quantidade_base}/mês")
    elif qual == "missoes":
        from .seitas import MISSOES
        for c in sorted(MISSOES):
            m = MISSOES[c]
            _imprimir(f"{c:24} DD{m.dificuldade:<3} risco{m.risco} "
                      f"prestígio{m.prestigio:<4} {m.pedras}  {m.nome}")
    else:
        raise SystemExit(f"tabela desconhecida {qual}")
    return 0


def cmd_seita(args: argparse.Namespace) -> int:
    from .seitas import (Seita, aceitar_discipulo, construir, executar_missao,
                         producao_mensal)
    a = _aleatoriedade(args)
    diario = _diario(args.diario)
    s = Seita(nome=args.nome, chines=args.chines or "", alinhamento=args.alinhamento,
              provincia=args.provincia or "—", nivel_do_mestre=args.nivel_mestre,
              prestigio=args.prestigio, pedras=args.pedras, comida=args.comida)
    for codigo in _lista(args.predios):
        construir(s, codigo, diario)
    for membro in _lista(args.membros):
        nome, _, nivel = membro.partition(":")
        aceitar_discipulo(s, nome, int(nivel or 1), interno=int(nivel or 1) >= 3)
    _imprimir(s.ficha())
    if args.mes:
        _imprimir("\nProdução do mês: "
                  + json.dumps(producao_mensal(s, args.densidade, diario),
                               ensure_ascii=False))
    if args.missao:
        executor = args.executor or (sorted(s.membros)[0] if s.membros else None)
        if not executor:
            raise SystemExit("a missão exige um membro na seita")
        nivel = s.niveis.get(executor, 1)
        r = executar_missao(s, args.missao, executor, a, nivel=nivel,
                            valor_atributo=args.valor, graduacao=args.graduacao,
                            diario=diario)
        _imprimir("")
        _imprimir(r.resumo())
    return 0


def cmd_exemplo(args: argparse.Namespace) -> int:
    """Gera o mundo de exemplo completo do repositório."""
    ns = argparse.Namespace(
        semente=args.semente, saida=args.saida, provincias=9, eventos=40,
        anos_de_historia=900, npcs=args.npcs)
    return cmd_mundo_gerar(ns)


# --------------------------------------------------------------------------
# parser
# --------------------------------------------------------------------------
def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="xan",
        description=f"{__nome__} {__version__} — {__motor__}. "
                    "Rolagens imparciais, mundo procedural, NPCs com desejos.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Sem --semente o motor usa a fonte viva (ruído do SO). "
               "Com --semente tudo é reproduzível.")
    p.add_argument("--versao", action="version",
                   version=f"{__nome__} {__version__}")
    sub = p.add_subparsers(dest="comando", required=True)

    def comum(sp):
        sp.add_argument("--semente", help="semente para geração reproduzível")
        sp.add_argument("--contexto-da-fonte", default="cli")
        return sp

    # motor
    motor = sub.add_parser("motor", help="informações e auto-teste do motor")
    msub = motor.add_subparsers(dest="acao_motor", required=True)
    comum(msub.add_parser("info", help="fonte de entropia e consumo"))
    comum(msub.add_parser("autoteste", help="invariantes + amostra estatística"))

    # justica
    j = comum(sub.add_parser("justica", help="bateria de certificação de imparcialidade"))
    j.add_argument("--amostras", type=int, default=20000)
    j.add_argument("--leves", type=int, default=8000)
    j.add_argument("--saida", help="prefixo dos arquivos .md e .json")

    # rolar
    r = comum(sub.add_parser("rolar", help="rola uma expressão de dados"))
    r.add_argument("expressao", help='ex.: "4d6kh3", "2d20kh1+5", "1d20!"')
    r.add_argument("--ator", default="mesa")
    r.add_argument("--diario", help="caminho do diário JSONL (append-only)")
    r.add_argument("--teoria", action="store_true",
                   help="mostra valor esperado e mínimo/máximo exatos")

    # teste
    t = comum(sub.add_parser("teste", help="teste de perícia contra uma DD"))
    t.add_argument("--acao", default="ação declarada")
    t.add_argument("--ator", default="personagem")
    t.add_argument("--atributo", required=True,
                   choices=["per", "con", "cha", "int", "luk", "pot"])
    t.add_argument("--valor", type=int, required=True, help="valor bruto 1..30")
    t.add_argument("--pericia", default="")
    t.add_argument("--graduacao", type=int, default=0)
    t.add_argument("--dd", type=int, required=True)
    t.add_argument("--regras", help="códigos separados por vírgula")
    t.add_argument("--fatos", help="objeto JSON com os fatos das regras")
    t.add_argument("--contexto-json", help="objeto JSON de contexto livre")
    t.add_argument("--diario")
    t.add_argument("--json", action="store_true")

    # oposto
    o = comum(sub.add_parser("oposto", help="teste oposto entre dois atores"))
    o.add_argument("--acao", default="disputa")
    o.add_argument("--ator-a", required=True)
    o.add_argument("--ator-b", required=True)
    o.add_argument("--atributo", required=True,
                   choices=["per", "con", "cha", "int", "luk", "pot"])
    o.add_argument("--valor-a", type=int, required=True)
    o.add_argument("--valor-b", type=int, required=True)
    o.add_argument("--pericia", default="")
    o.add_argument("--graduacao-a", type=int, default=0)
    o.add_argument("--graduacao-b", type=int, default=0)
    o.add_argument("--regras")
    o.add_argument("--fatos")
    o.add_argument("--contexto-json")
    o.add_argument("--diario")

    # mundo
    mundo = sub.add_parser("mundo", help="geração procedural de mundo")
    wsub = mundo.add_subparsers(dest="acao_mundo", required=True)
    w = wsub.add_parser("gerar", help="gera mundo completo + mapa SVG")
    w.add_argument("--semente", required=True)
    w.add_argument("--saida", required=True, help="diretório de saída")
    w.add_argument("--provincias", type=int, default=9)
    w.add_argument("--eventos", type=int, default=40)
    w.add_argument("--anos-de-historia", type=int, default=900)
    w.add_argument("--npcs", type=int, default=0,
                   help="quantos NPCs notáveis gerar junto")

    # tabelas
    tb = sub.add_parser("tabelas", help="lista as tabelas do sistema")
    tb.add_argument("tabela", choices=["leis", "regras", "tecnicas", "pericias",
                                       "reinos", "bestiario", "predios",
                                       "missoes"])

    # npc / personagem / besta
    n = comum(sub.add_parser("npc", help="gera um NPC completo"))
    n.add_argument("--nivel", type=int)
    n.add_argument("--ocupacao")
    n.add_argument("--faccao")
    n.add_argument("--local")
    n.add_argument("--caminho", choices=["xiandao", "shendao", "corpo",
                                         "marcial", "monstro"])
    n.add_argument("--raiz", default="realista",
                   choices=["realista", "heroica", "lendária", "mortal"])
    n.add_argument("--agendas", type=int, default=1)

    pc = comum(sub.add_parser("personagem", help="cria um personagem de jogador"))
    pc.add_argument("--nome", required=True)
    pc.add_argument("--raca", default="humano")
    pc.add_argument("--metodo", default="sorteio",
                    choices=["sorteio", "pontos", "manual"])
    pc.add_argument("--pontos", type=int, default=78)
    pc.add_argument("--caminho", default="xiandao",
                    choices=["xiandao", "shendao", "corpo", "marcial", "monstro"])
    pc.add_argument("--nivel", type=int, default=1)
    pc.add_argument("--lei")
    pc.add_argument("--pericias", type=int, default=12)
    pc.add_argument("--faccao")
    pc.add_argument("--posto")
    pc.add_argument("--raiz", default="heroica",
                    choices=["realista", "heroica", "lendária", "mortal"])
    pc.add_argument("--nucleo", type=int, help="grau do Núcleo Dourado (1..9)")

    b = comum(sub.add_parser("besta", help="gera ou lista bestas espirituais"))
    b.add_argument("--nivel", type=int)
    b.add_argument("--elemento")
    b.add_argument("--terreno", default="florestas")
    b.add_argument("--classe")
    b.add_argument("--catalogo", action="store_true",
                   help="lista as bestas do cânone")

    # ruptura / nucleo / tribulacao
    ru = comum(sub.add_parser("ruptura", help="tenta romper para o próximo nível"))
    ru.add_argument("--ator", default="cultivador")
    ru.add_argument("--nivel", type=int, required=True)
    ru.add_argument("--lei", required=True)
    ru.add_argument("--int", dest="int_", type=int, default=12)
    ru.add_argument("--per", type=int, default=12)
    ru.add_argument("--con", type=int, default=12)
    ru.add_argument("--cha", type=int, default=12)
    ru.add_argument("--luk", type=int, default=12)
    ru.add_argument("--pot", type=int, default=12)
    ru.add_argument("--compreensao", type=int, default=2)
    ru.add_argument("--fengshui", default="neutro")
    ru.add_argument("--densidade", default="comum")
    ru.add_argument("--elixir", default="nenhum")
    ru.add_argument("--meditou", action="store_true")
    ru.add_argument("--diario")

    nu = sub.add_parser("nucleo", help="forma o Núcleo Dourado (sem dado)")
    nu.add_argument("--qi", type=int, required=True)
    nu.add_argument("--fengshui", default="neutro")
    nu.add_argument("--densidade", default="comum")
    nu.add_argument("--mental", type=int, default=70)
    nu.add_argument("--elixir", default="nenhum")
    nu.add_argument("--compat", type=int, required=True)
    nu.add_argument("--compreensao", type=int, default=0)
    nu.add_argument("--mestre", action="store_true")
    nu.add_argument("--artefato", default="nenhum")
    nu.add_argument("--harmonia", type=int, default=0)
    nu.add_argument("--elemento", help="calcula a harmonia a partir do momento")
    nu.add_argument("--estacao", default="primavera")
    nu.add_argument("--dia", type=int, default=1)
    nu.add_argument("--polaridade", default="yang", choices=["yin", "yang"])
    nu.add_argument("--clima", default="limpo")

    tr = comum(sub.add_parser("tribulacao", help="enfrenta a Tribulação Celestial"))
    tr.add_argument("--ator", default="cultivador")
    tr.add_argument("--nivel", type=int, required=True)
    tr.add_argument("--con", type=int, default=16)
    tr.add_argument("--defesa", type=int, default=2)
    tr.add_argument("--vitalidade", type=int, required=True)
    tr.add_argument("--qi", type=int, required=True)
    tr.add_argument("--demoniaca", action="store_true")
    tr.add_argument("--artefato", default="nenhum")
    tr.add_argument("--formacao", default="nenhuma")
    tr.add_argument("--elixir", default="nenhum")
    tr.add_argument("--anos-queimados", type=int, default=0)
    tr.add_argument("--diario")

    # combate
    cb = comum(sub.add_parser("combate", help="simula um duelo completo"))
    cb.add_argument("--heroi", default="Herói")
    cb.add_argument("--rival", default="Rival")
    cb.add_argument("--nivel", type=int, default=6)
    cb.add_argument("--lei", default="SETE_MASSACRES")
    cb.add_argument("--defesa-heroi", default="esquiva",
                    choices=["esquiva", "resistencia", "aparar"])
    cb.add_argument("--defesa-rival", default="resistencia",
                    choices=["esquiva", "resistencia", "aparar"])
    cb.add_argument("--terreno", default="neutro")
    cb.add_argument("--luz", default="plena")
    cb.add_argument("--clima", default="limpo")
    cb.add_argument("--fengshui", default="neutro")
    cb.add_argument("--densidade", default="comum")
    cb.add_argument("--formacao", default="nenhuma")
    cb.add_argument("--max-turnos", type=int, default=200)
    cb.add_argument("--defensivo", action="store_true",
                    help="combatentes feridos passam a defender")
    cb.add_argument("--diario")

    # seita
    se = comum(sub.add_parser("seita", help="cria e administra uma seita"))
    se.add_argument("--nome", required=True)
    se.add_argument("--chines")
    se.add_argument("--alinhamento", default="ortodoxa",
                    choices=["ortodoxa", "nao_ortodoxa", "demoniaca",
                             "imperial", "neutra"])
    se.add_argument("--provincia")
    se.add_argument("--nivel-mestre", type=int, default=7)
    se.add_argument("--prestigio", type=int, default=0)
    se.add_argument("--pedras", type=int, default=20000)
    se.add_argument("--comida", type=int, default=500)
    se.add_argument("--predios", help="códigos separados por vírgula")
    se.add_argument("--membros", help="nome:nível separados por vírgula")
    se.add_argument("--mes", action="store_true", help="roda a produção mensal")
    se.add_argument("--densidade", default="comum")
    se.add_argument("--missao")
    se.add_argument("--executor")
    se.add_argument("--valor", type=int, default=13)
    se.add_argument("--graduacao", type=int, default=2)
    se.add_argument("--diario")

    # auditoria
    au = sub.add_parser("auditoria", help="verifica, resume ou sela um diário")
    au.add_argument("acao", choices=["verificar", "selar", "resumo"])
    au.add_argument("--diario", required=True)
    au.add_argument("--saida")

    # exemplo
    ex = sub.add_parser("exemplo", help="gera o mundo de exemplo do repositório")
    ex.add_argument("--semente", default="xan-mundo-exemplo")
    ex.add_argument("--saida", default=os.path.join("mundos", "exemplo"))
    ex.add_argument("--npcs", type=int, default=8)

    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argv)
    tabela = {
        ("motor", "info"): cmd_motor_info,
        ("motor", "autoteste"): cmd_motor_autoteste,
        ("justica", None): cmd_justica,
        ("rolar", None): cmd_rolar,
        ("teste", None): cmd_teste,
        ("oposto", None): cmd_oposto,
        ("mundo", "gerar"): cmd_mundo_gerar,
        ("tabelas", None): cmd_listar,
        ("npc", None): cmd_npc,
        ("personagem", None): cmd_personagem,
        ("besta", None): cmd_besta,
        ("ruptura", None): cmd_ruptura,
        ("nucleo", None): cmd_nucleo,
        ("tribulacao", None): cmd_tribulacao,
        ("combate", None): cmd_combate,
        ("seita", None): cmd_seita,
        ("auditoria", None): cmd_auditoria,
        ("exemplo", None): cmd_exemplo,
    }
    chave = (args.comando, getattr(args, "acao_motor", None)
             or getattr(args, "acao_mundo", None))
    fn = tabela.get(chave) or tabela.get((args.comando, None))
    if fn is None:
        parser.error(f"comando desconhecido: {args.comando}")
        return 2
    try:
        return fn(args)
    except (ValueError, KeyError, TypeError) as exc:
        _imprimir(f"ERRO: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
