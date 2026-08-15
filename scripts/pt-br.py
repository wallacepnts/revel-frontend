#!/usr/bin/env python3
"""Convert the upstream European Portuguese catalogue into Brazilian Portuguese.

The upstream `messages/pt.json` is pt-PT: "palavra-passe", "ficheiro",
"bilhete", and second-person "tu" throughout. For a Rio de Janeiro site that
reads foreign on every form. This fork ships pt-BR instead.

WHY A SCRIPT AND NOT A PATCH
----------------------------
The conversion touches ~2400 of 8146 strings in a file upstream edits every
release. As a diff it would conflict on every rebase, 2700 lines at a time,
with no sane way to resolve it by hand. As a script, the conflict resolution
is mechanical:

    git checkout --theirs messages/pt.json
    python3 scripts/pt-br.py
    git add messages/pt.json

Run it from the repo root. It rewrites messages/pt.json in place and is
idempotent: running it twice changes nothing the second time.

THE ONE RULE THAT MATTERS
-------------------------
Imperatives are replaced ONLY at the start of a sentence. An earlier version
replaced them anywhere and quietly corrupted real text — "a pesquisa" became
"a pesquise", "não há volta atrás" became "não há volte atrás", "imagem de
marca" became "imagem de marque". Nouns and third-person verbs share their
spelling with imperatives in Portuguese; position is the only cheap signal.
If you add a verb to IMPERATIVO, keep it anchored.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CATALOGO = Path("messages/pt.json")

# --------------------------------------------------------------------------
# 1. Marca. Títulos levam o nome completo; corpo de texto, a forma curta.
# --------------------------------------------------------------------------
CHAVES_DE_TITULO = ("title", "pagetitle", "metatitle", "heading", "sitename", "brand")

# --------------------------------------------------------------------------
# 2. Substantivos e expressões. Seguros: não são verbos, não dependem de
#    posição na frase.
# --------------------------------------------------------------------------
VOCABULARIO: list[tuple[str, str]] = [
    ("palavras-passe", "senhas"),
    ("palavra-passe", "senha"),
    ("utilizadores", "usuários"),
    ("utilizador", "usuário"),
    ("ficheiros", "arquivos"),
    ("ficheiro", "arquivo"),
    ("separadores", "abas"),
    (r"\bseparador\b", "aba"),
    ("definições", "configurações"),
    ("contactos", "contatos"),
    ("contacto", "contato"),
    ("moradas", "endereços"),
    (r"\bmorada\b", "endereço"),
    ("câmaras", "câmeras"),
    ("câmara", "câmera"),
    ("ecrãs", "telas"),
    ("ecrã", "tela"),
    ("telemóveis", "celulares"),
    ("telemóvel", "celular"),
    ("bilheteira", "bilheteria"),
    ("bilhetes", "ingressos"),
    ("bilhete", "ingresso"),
    (r"\bequipa\b", "equipe"),
    (r"\bsondagens\b", "enquetes"),
    (r"\bsondagem\b", "enquete"),
    (r"\bapelido\b", "sobrenome"),
    ("código postal", "CEP"),
    ("link de transferência", "link de download"),
    (r"n\.º", "nº"),
    ("a decorrer", "em andamento"),
    ("eliminação", "exclusão"),
    # Achados ao ler as frases uma a uma — os marcadores automáticos não pegam
    # palavra que só difere por um "c" ou por sufixo.
    ("subscrições", "assinaturas"),
    ("subscrição", "assinatura"),
    ("subscreve", "assina"),
    ("faturação", "faturamento"),
    ("registados", "registrados"),
    ("registadas", "registradas"),
    ("registado", "registrado"),
    ("registada", "registrada"),
    ("contactar", "contatar"),
    ("respetiva", "respectiva"),
    ("respetivo", "respectivo"),
    ("geridas", "gerenciadas"),
    ("geridos", "gerenciados"),
    ("proporcionalidade", "proporcionalidade"),
    (r"\bligação da reunião\b", "link da reunião"),
    # DuRock é uma agenda de rock: o que o Revel chama de "evento" aqui é show.
    # Trocar aqui, e não no catálogo, porque são ~720 strings num arquivo que o
    # upstream reescreve a cada release. Gênero e artigos não mudam ("o evento"
    # -> "o show"), então a concordância se mantém sozinha. O \b protege
    # "eventual"/"eventualmente", que não são a mesma palavra.
    (r"\beventos\b", "shows"),
    (r"\bevento\b", "show"),
]

# --------------------------------------------------------------------------
# 3. Pronomes e possessivos de 2ª pessoa. Seguros.
# --------------------------------------------------------------------------
PRONOMES: list[tuple[str, str]] = [
    (r"\bteus\b", "seus"),
    (r"\btuas\b", "suas"),
    (r"\bteu\b", "seu"),
    (r"\btua\b", "sua"),
    (r"\bcontigo\b", "com você"),
    (r"\bti\b", "você"),
]

# --------------------------------------------------------------------------
# 4. Gerúndio: "A carregar…" -> "Carregando…". Ancorado no "A " + infinitivo.
# --------------------------------------------------------------------------
GERUNDIO: dict[str, str] = {
    # Como o gerúndio roda por ÚLTIMO, as chaves têm de ser as formas JÁ
    # convertidas: "A guardar" vira "A salvar" na troca de vocabulário, e
    # procurar por "guardar" aqui não acha mais nada. Por isso salvar/excluir
    # aparecem ao lado de guardar/eliminar, e não no lugar deles.
    "salvar": "salvando",
    "excluir": "excluindo",
    "carregar": "carregando",
    "criar": "criando",
    "processar": "processando",
    "guardar": "salvando",
    "enviar": "enviando",
    "atualizar": "atualizando",
    "eliminar": "excluindo",
    "gerar": "gerando",
    "verificar": "verificando",
    "aguardar": "aguardando",
    "preparar": "preparando",
    "sincronizar": "sincronizando",
    "buscar": "buscando",
    "procurar": "procurando",
    "importar": "importando",
    "exportar": "exportando",
    "calcular": "calculando",
    "publicar": "publicando",
    "cancelar": "cancelando",
    "redirecionar": "redirecionando",
    # Verbos que só apareceram ao olhar a tela: a lista era pequena demais e 84
    # ocorrências passaram. Vem de dados, não de palpite — foram extraídos do
    # próprio catálogo procurando "A <infinitivo>". Uma regra genérica por
    # sufixo seria pior: "A cor" viraria "A condo", "A mulher" viraria
    # "mulhendo". E "a partir de" fica FORA de propósito: ali é preposição.
    "mostrar": "mostrando",
    "editar": "editando",
    "pedir": "pedindo",
    "confirmar": "confirmando",
    "usar": "usando",
    "adicionar": "adicionando",
    "seguir": "seguindo",
    "duplicar": "duplicando",
    "ligar": "conectando",
    "mudar": "mudando",
    "desativar": "desativando",
    "participar": "participando",
    "repor": "redefinindo",
    "remover": "removendo",
    "organizar": "organizando",
    "converter": "convertendo",
    "resgatar": "resgatando",
    "reivindicar": "reivindicando",
    "entrar": "entrando",
    "sair": "saindo",
    "reembolsar": "reembolsando",
    "anular": "cancelando",
    "validar": "validando",
    "inicializar": "inicializando",
    "desligar": "desligando",
    "gravar": "gravando",
    "aplicar": "aplicando",
    "pausar": "pausando",
    "retomar": "retomando",
    "promover": "promovendo",
    "fazer": "fazendo",
    "encaminhar": "encaminhando",
}

# --------------------------------------------------------------------------
# 5. Infinitivo pessoal de 2ª pessoa -> infinitivo simples.
#    Lista EXPLÍCITA de propósito: uma regra por sufixo (-ares/-eres/-ires)
#    engoliria substantivos — caracteres, lugares, titulares, alimentares,
#    jantares. Esses ficam de fora e são conferidos na verificação.
# --------------------------------------------------------------------------
INFINITIVO_PESSOAL: dict[str, str] = {
    "acederes": "acessar",
    "aceitares": "aceitar",
    "aderires": "aderir",
    "adicionares": "adicionar",
    "alterares": "alterar",
    "aprovares": "aprovar",
    "associares": "associar",
    "cancelares": "cancelar",
    "candidatares": "candidatar",
    "carregares": "carregar",
    "clicares": "clicar",
    "começares": "começar",
    "comprares": "comprar",
    "confirmares": "confirmar",
    "consultares": "consultar",
    "continuares": "continuar",
    "criares": "criar",
    "cumprires": "cumprir",
    "definires": "definir",
    "descobrires": "descobrir",
    "dispensares": "dispensar",
    "duplicares": "duplicar",
    "eliminares": "excluir",
    "encontrares": "encontrar",
    "enviares": "enviar",
    "explorares": "explorar",
    "fazeres": "fazer",
    "fechares": "fechar",
    "guardares": "salvar",
    "iniciares": "iniciar",
    "inscreveres": "inscrever",
    "juntares": "juntar",
    "ligares": "conectar",
    "manteres": "manter",
    "mudares": "mudar",
    "obteres": "obter",
    "organizares": "organizar",
    "participares": "participar",
    "partilhares": "compartilhar",
    "precisares": "precisar",
    "puderes": "puder",
    "quiseres": "quiser",
    "receberes": "receber",
    "registares": "cadastrar",
    "reivindicares": "reivindicar",
    "removeres": "remover",
    "retomares": "retomar",
    "seguires": "seguir",
    "selecionares": "selecionar",
    "solicitares": "solicitar",
    "subscreveres": "assinar",
    "testares": "testar",
    "tiveres": "tiver",
    "usares": "usar",
    "veres": "ver",
    "verificares": "verificar",
    "vires": "ver",
    "votares": "votar",
    "estiveres": "estiver",
    "fores": "for",
}

# --------------------------------------------------------------------------
# 6. Presente de 2ª pessoa -> 3ª. Formas inequívocas.
# --------------------------------------------------------------------------
PRESENTE: dict[str, str] = {
    "estás": "está",
    "fazes": "faz",
    "perdes": "perde",
    "podes": "pode",
    "precisas": "precisa",
    "preferes": "prefere",
    "queres": "quer",
    "recebes": "recebe",
    "tens": "tem",
    "vais": "vai",
    "sabes": "sabe",
    "vês": "vê",
    "geres": "gerencia",
    "voltaste": "voltou",
    "esqueceste": "esqueceu",
    "tenhas": "tenha",
    "chegaste": "chegou",
    "possas": "possa",
    "faças": "faça",
}

# --------------------------------------------------------------------------
# 7. Imperativos — SÓ no início de frase. Ver o aviso no topo do arquivo.
# --------------------------------------------------------------------------
IMPERATIVO: dict[str, str] = {
    "escreve": "escreva",
    "cria": "crie",
    "começa": "comece",
    "usa": "use",
    "consulta": "consulte",
    "adiciona": "adicione",
    "seleciona": "selecione",
    "escolhe": "escolha",
    "introduz": "digite",
    "confirma": "confirme",
    "verifica": "verifique",
    "clica": "clique",
    "tenta": "tente",
    "volta": "volte",
    "gere": "gerencie",
    "explora": "explore",
    "descobre": "descubra",
    "partilha": "compartilhe",
    "guarda": "salve",
    "envia": "envie",
    "preenche": "preencha",
    "atualiza": "atualize",
    "completa": "complete",
    "define": "defina",
    "ativa": "ative",
    "desativa": "desative",
    "convida": "convide",
    "pesquisa": "pesquise",
    "copia": "copie",
    "abre": "abra",
    "fecha": "feche",
    "continua": "continue",
    "aceita": "aceite",
    "recusa": "recuse",
    "mostra": "mostre",
    "cola": "cole",
    "marca": "marque",
    "arrasta": "arraste",
    "elimina": "exclua",
    "regista": "cadastre",
    "junta": "junte",
    "inscreve": "inscreva",
    "inicia": "inicie",
    "edita": "edite",
    "retoma": "retome",
    "agrupa": "agrupe",
}

# --------------------------------------------------------------------------
# 8. Verbos fora de imperativo, inequívocos em qualquer posição.
# --------------------------------------------------------------------------
VERBOS_GERAIS: list[tuple[str, str]] = [
    (r"\bgerir\b", "gerenciar"),
    (r"\bguardar\b", "salvar"),
    (r"\beliminar\b", "excluir"),
    (r"\bregistar\b", "cadastrar"),
    (r"\bpretendes?\b", "deseja"),
    (r"\bestá a ser\b", "está sendo"),
    (r"\bestão a ser\b", "estão sendo"),
    (r"\bnão pode ser anulad([ao])\b", r"não pode ser desfeit\1"),
]

# Verbos que podem abrir a frase: a troca preserva a caixa, senão o rótulo do
# botão vira minúsculo ("Inicia sessão" -> "entre").
#
# As expressões de sessão rodam AQUI, depois da conversão de infinitivo
# pessoal, e não junto do vocabulário: "iniciares sessão" só vira "iniciar
# sessão" naquela etapa, e uma regra que rodasse antes deixaria passar — o que
# quebrava a idempotência (a segunda execução mudava o arquivo).
VERBOS_COM_CAIXA: list[tuple[str, str]] = [
    (r"\bterminar sessão\b", "sair"),
    (r"\biniciar sessão\b", "entrar"),
    (r"\binício de sessão\b", "login"),
    (r"\binicia sessão\b", "entre"),
    (r"\bmanténs\b", "mantém"),
    (r"\bcontinuas\b", "continua"),
    (r"\bterminámos\b", "encerramos"),
]

# --------------------------------------------------------------------------
# 9. Frases que a troca mecânica não resolve bem. Reescritas à mão, por chave.
#    Mantidas aqui e não no catálogo para que o script continue sendo a única
#    fonte da verdade da conversão.
# --------------------------------------------------------------------------
FRASES: dict[str, str] = {
    "login.welcomeBack": "Que bom te ver de volta",
    "accountPrivacyPage.deletionEmailIgnore": (
        "Se não foi você que pediu isso, pode ignorar o e-mail com segurança e sua conta "
        "não será alterada."
    ),
    "orgAdmin.members.plans.form.paymentOffline": "Offline — registre os pagamentos manualmente",
    "accountSecurityPage.emailChange_signoutWarning": (
        "Ao confirmar, você sairá em todos os outros dispositivos. Aqui, continua conectado."
    ),
    "confirmEmailChange.confirm_warningBody": (
        "Confirmar altera uma parte essencial da sua identidade, por isso todas as outras "
        "sessões são encerradas."
    ),
    "confirmEmailChange.success_signoutNotice": (
        "Por segurança, encerramos sua sessão em todos os outros dispositivos. Aqui, você "
        "continua conectado."
    ),
    "accountSecurityPage.emailChange_newEmailPlaceholder": "voce@exemplo.com",
    "guest_attendance.email_placeholder": "voce@exemplo.com",
    "login.emailPlaceholder": "voce@exemplo.com",
    "register.emailPlaceholder": "voce@exemplo.com",
    "passwordResetPage.emailPlaceholder": "voce@exemplo.com",
}


def _caixa(original: str, novo: str) -> str:
    """Keep the original capitalisation when swapping a word."""
    if original.isupper():
        return novo.upper()
    if original[:1].isupper():
        return novo[:1].upper() + novo[1:]
    return novo


def _troca(texto: str, padrao: str, novo: str) -> str:
    return re.sub(padrao, lambda m: _caixa(m.group(0), novo), texto, flags=re.I)


def converte(texto: str, caminho: str) -> str:
    """Convert one string. `caminho` is the dotted key path, e.g. "login.welcomeBack"."""
    if caminho in FRASES:
        return FRASES[caminho]

    t = texto
    chave = caminho.rsplit(".", 1)[-1]

    if "Revel" in t:
        nome = "DuRock RJ" if any(h in chave.lower() for h in CHAVES_DE_TITULO) else "DuRock"
        t = re.sub(r"\bRevel\b", nome, t)

    for padrao, novo in VOCABULARIO:
        t = _troca(t, padrao, novo)


    # Clíticos de 2ª pessoa. Os nomeados vêm antes da regra geral, que apenas
    # remove o "-te" restante — "convidamos-te" -> "convidamos".
    t = _troca(t, r"\bEsqueceste-te d[ao]\b", "Esqueceu a")
    t = _troca(t, r"\bJunta-te\b", "Junte-se")
    t = _troca(t, r"\bRegista-te\b", "Cadastre-se")
    t = _troca(t, r"\bInscreve-te\b", "Inscreva-se")
    t = _troca(t, r"\bCertifica-te\b", "Certifique-se")
    t = _troca(t, r"\bComprometeste-te\b", "Você se comprometeu")
    for verbo, novo in (
        ("enviar-te", "enviar para você"),
        ("avisar-te", "avisar você"),
        ("reencaminhar-te", "redirecionar você"),
        ("redirecionar-te", "redirecionar você"),
        ("ter-te", "ter você"),
        ("permite-te", "permite que você"),
    ):
        t = re.sub(rf"\b{verbo}\b", novo, t, flags=re.I)
    t = re.sub(r"-te\b", "", t)

    for padrao, novo in PRONOMES:
        t = _troca(t, padrao, novo)

    for tabela in (INFINITIVO_PESSOAL, PRESENTE):
        t = re.sub(
            r"\b(" + "|".join(tabela) + r")\b",
            lambda m: _caixa(m.group(0), tabela[m.group(1).lower()]),  # noqa: B023
            t,
            flags=re.I,
        )

    # Expressões de sessão ANTES do imperativo: "Inicia sessão" precisa virar
    # "Entre" enquanto ainda casa. Com a ordem invertida, o imperativo fazia
    # "Inicia" -> "Inicie" e a expressão não achava mais nada, devolvendo
    # "Inicie sessão" no lugar de "Entre" — regressão pega na tela, não no teste.
    for padrao, novo in VERBOS_COM_CAIXA:
        t = _troca(t, padrao, novo)

    # Imperativo ancorado: início da string, ou logo após . ! ? — : ou quebra.
    t = re.sub(
        r"(^|[.!?—:]\s+|\n)(" + "|".join(IMPERATIVO) + r")\b",
        lambda m: m.group(1) + _caixa(m.group(2), IMPERATIVO[m.group(2).lower()]),
        t,
        flags=re.I,
    )

    for padrao, novo in VERBOS_GERAIS:
        t = re.sub(padrao, novo, t, flags=re.I)


    # Gerúndio POR ÚLTIMO entre as trocas de verbo: "A iniciar sessão" só vira
    # "A entrar" na etapa acima, e converter antes dela deixaria "A entrar" no
    # texto — que a execução seguinte transformaria em "Entrando", quebrando a
    # idempotência de que o uso em rebase depende.
    t = re.sub(
        r"\bA (" + "|".join(GERUNDIO) + r")\b",
        lambda m: _caixa(m.group(0), GERUNDIO[m.group(1).lower()]),
        t,
        flags=re.I,
    )

    t = re.sub(r"\s{2,}", " ", t)

    # Rótulo curto que perdeu a maiúscula numa troca de verbo ("cadastrar" no
    # botão). Placeholders de e-mail e URL ficam de fora: são minúsculos.
    if t[:1].islower() and len(t.split()) <= 3 and not re.match(r"^[a-z]+[@.]", t):
        t = t[:1].upper() + t[1:]

    return t


def percorre(node: object, caminho: str = "", em_lista: bool = False) -> object:
    """Walk the catalogue, six levels deep.

    A list's own strings are Paraglide parameter declarations ("input count",
    "countPlural") and must be left alone — but the dicts inside a list hold
    the plural variants, which are user-facing and do get converted.
    """
    if isinstance(node, dict):
        return {
            k: percorre(v, f"{caminho}.{k}" if caminho else k) for k, v in node.items()
        }
    if isinstance(node, list):
        return [percorre(v, caminho, em_lista=True) for v in node]
    if isinstance(node, str):
        return node if em_lista else converte(node, caminho)
    return node


def main() -> int:
    if not CATALOGO.exists():
        print(f"erro: {CATALOGO} não encontrado — rode a partir da raiz do repo", file=sys.stderr)
        return 1

    original = json.loads(CATALOGO.read_text(encoding="utf-8"))
    convertido = percorre(original)
    CATALOGO.write_text(
        json.dumps(convertido, ensure_ascii=False, indent="\t") + "\n", encoding="utf-8"
    )

    def conta(node: object) -> int:
        if isinstance(node, dict):
            return sum(conta(v) for v in node.values())
        return 1 if isinstance(node, str) else 0

    print(f"catálogo convertido para pt-BR: {conta(convertido)} strings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
