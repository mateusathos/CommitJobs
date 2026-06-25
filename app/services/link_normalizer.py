from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


PARAMETROS_RASTREAMENTO = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "jobboardsource",
    "source",
    "origem",
    "p",
    "pos",
    "rgn",
    "cid",
    "ckey",
    "jobage",
    "relb",
    "brelb",
    "scr",
    "bscr",
    "aq",
    "elckey",
}


def normalizar_link(link):
    if not link:
        return None

    partes = urlsplit(link.strip())

    parametros = parse_qsl(
        partes.query,
        keep_blank_values=True,
    )

    parametros_filtrados = [
        (chave, valor)
        for chave, valor in parametros
        if chave.lower() not in PARAMETROS_RASTREAMENTO
    ]

    query_normalizada = urlencode(parametros_filtrados)

    caminho = partes.path.rstrip("/") or "/"

    return urlunsplit((
        partes.scheme.lower(),
        partes.netloc.lower(),
        caminho,
        query_normalizada,
        "",
    ))