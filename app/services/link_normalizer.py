import base64
import json
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


def _normalizar_link_gupy(partes):
    if not partes.netloc.lower().endswith(".gupy.io"):
        return None

    segmentos = partes.path.strip("/").split("/")

    if len(segmentos) != 2 or segmentos[0] != "job":
        return None

    token = segmentos[1]

    try:
        padding = "=" * (-len(token) % 4)
        payload = base64.urlsafe_b64decode(
            token + padding
        ).decode()
        dados = json.loads(payload)
    except (
        ValueError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        return None

    job_id = dados.get("jobId")

    if not job_id:
        return None

    payload_canonico = json.dumps(
        {
            "jobId": job_id,
            "source": "gupy_portal",
        },
        separators=(",", ":"),
    ).encode()

    token_canonico = base64.urlsafe_b64encode(
        payload_canonico
    ).decode()

    return urlunsplit((
        partes.scheme.lower(),
        partes.netloc.lower(),
        f"/job/{token_canonico}",
        "",
        "",
    ))


def normalizar_link(link):
    if not link:
        return None

    partes = urlsplit(link.strip())

    link_gupy = _normalizar_link_gupy(partes)

    if link_gupy:
        return link_gupy

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
