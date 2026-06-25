import unicodedata

SOFTWARE_KEYWORDS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "angular",
    "vue",
    "node",
    "node.js",
    "flask",
    "django",
    "spring",
    ".net",
    "c#",
    "php",
    "ruby",
    "go",
    "golang",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "docker",
    "git",
    "backend",
    "back-end",
    "frontend",
    "front-end",
    "full stack",
    "fullstack",
    "desenvolvedor",
    "desenvolvedora",
    "desenvolvimento de software",
    "engenharia de software",
    "programação",
    "programador",
    "programadora",
    "sistemas",
    "análise e desenvolvimento de sistemas",
    "ciência da computação",
]

TITULOS_SOFTWARE = [
    "desenvolvedor",
    "desenvolvedora",
    "developer",
    "software engineer",
    "programador",
    "programadora",
    "backend",
    "back-end",
    "frontend",
    "front-end",
    "fullstack",
    "full stack",
    "firmware",
    "sistemas embarcados",
    "desenvolvimento de sistemas",
    "desenvolvimento de software",
]

TITULOS_EXCLUIDOS = [
    "recruiter",
    "recrutador",
    "recrutadora",
    "recursos humanos",
    "pedagogico",
    "pedagogica",
    "projetista",
    "business intelligence",
]

def normalizar_texto(texto):
    texto = texto or ""

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    return texto.lower()


def identificar_nivel(dados):
    texto = normalizar_texto(
        " ".join([
            dados.get("titulo") or "",
            dados.get("tipo_origem") or "",
        ])
    )

    texto = f" {texto} "

    if "vacancy_type_internship" in texto:
        return "Estágio"

    if any(termo in texto for termo in [
        "estagio",
        "estagiario",
        "estagiaria",
        "internship",
        " intern ",
    ]):
        return "Estágio"

    possui_junior = any(termo in texto for termo in [
        "junior",
        " jr ",
        " jr.",
        "nivel i ",
        "desenvolvedor i ",
        "software engineer i ",
    ])

    possui_pleno = any(termo in texto for termo in [
        "pleno",
        " pl ",
        " pl.",
        "mid level",
        "mid-level",
        "midlevel",
        "nivel ii",
        "software engineer ii",
    ])

    possui_senior = any(termo in texto for termo in [
        "senior",
        " sr ",
        " sr.",
        "nivel iii",
        "software engineer iii",
    ])

    if possui_junior and possui_pleno:
        return "Júnior/Pleno"

    if possui_pleno and possui_senior:
        return "Pleno/Sênior"

    if possui_senior:
        return "Sênior"

    if possui_pleno:
        return "Pleno"

    if possui_junior:
        return "Júnior"

    return "Não informado"


def vaga_eh_de_software(dados):
    titulo = normalizar_texto(dados.get("titulo"))

    if any(termo in titulo for termo in TITULOS_EXCLUIDOS):
        return False

    if any(termo in titulo for termo in TITULOS_SOFTWARE):
        return True

    texto_completo = normalizar_texto(
        " ".join([
            dados.get("descricao") or "",
            dados.get("tecnologias") or "",
        ])
    )

    tecnologias_encontradas = sum(
        1
        for termo in SOFTWARE_KEYWORDS
        if termo in texto_completo
    )

    titulo_generico_valido = any(termo in titulo for termo in [
        "estagio",
        "estagiario",
        "estagiaria",
        "analista",
        "engenheiro",
        "engenheira",
    ])

    return titulo_generico_valido and tecnologias_encontradas >= 2