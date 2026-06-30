import re
import unicodedata

TITULOS_SOFTWARE = [
    "desenvolvedor",
    "desenvolvedora",
    "developer",
    "software developer",
    "software engineer",
    "engenheiro de software",
    "engenheira de software",
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
    "analista de sistemas",
    "analista desenvolvedor",
    "analista de desenvolvimento",
]

TITULOS_SOFTWARE_MODERADOS = [
    "devops",
    "site reliability engineer",
    "sre",
    "qa automation",
    "quality assurance automation",
    "engenheiro de dados",
    "engenheira de dados",
    "data engineer",
    "machine learning engineer",
    "ml engineer",
    "engenheiro de machine learning",
    "engenheira de machine learning",
    "arquiteto de software",
    "arquiteta de software",
    "tech lead",
]

TITULOS_EXCLUIDOS = [
    "recruiter",
    "tech recruiter",
    "recrutador",
    "recrutadora",
    "recursos humanos",
    "rh",
    "pedagogico",
    "pedagogica",
    "professor",
    "professora",
    "instrutor",
    "instrutora",
    "projetista",
    "business intelligence",
    "bi analyst",
    "analista de bi",
    "power bi",
    "suporte tecnico",
    "help desk",
    "service desk",
    "infraestrutura",
    "product manager",
    "gerente de produto",
    "product owner",
    "scrum master",
]

TECNOLOGIAS_FORTES = [
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "csharp",
    "c-sharp",
    "php",
    "ruby",
    "go",
    "golang",
    "kotlin",
    "swift",
    "dart",
    "scala",
    "rust",
    "react",
    "reactjs",
    "react.js",
    "angular",
    "vue",
    "vuejs",
    "vue.js",
    "svelte",
    "next.js",
    "nextjs",
    "nuxt",
    "node",
    "node.js",
    "nodejs",
    "node js",
    "express",
    "nestjs",
    "flask",
    "django",
    "fastapi",
    "spring",
    "spring boot",
    ".net",
    "dotnet",
    "dot net",
    "asp.net",
    "laravel",
    "rails",
    "ruby on rails",
    "react native",
    "flutter",
    "android",
    "ios",
]

TECNOLOGIAS_MODERADAS = [
    "html",
    "css",
    "sass",
    "scss",
    "tailwind",
    "bootstrap",
    "jquery",
    "redux",
    "vite",
    "graphql",
    "microservices",
    "microsserviços",
    "microsservicos",
    "web services",
    "xamarin",
    "sql",
    "postgresql",
    "postgres",
    "mysql",
    "mongodb",
    "mongo",
    "mongo db",
    "oracle",
    "sql server",
    "sqlite",
    "redis",
    "firebase",
    "supabase",
    "elasticsearch",
    "dynamodb",
    "docker",
    "kubernetes",
    "k8s",
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "jenkins",
    "github actions",
    "gitlab ci",
    "ci/cd",
    "terraform",
    "nginx",
    "quality assurance",
    "selenium",
    "cypress",
    "jest",
    "pytest",
    "junit",
    "unit tests",
    "testes unitários",
    "testes unitarios",
    "testes automatizados",
    "machine learning",
    "pandas",
    "numpy",
    "pytorch",
    "tensorflow",
    "etl",
    "big data",
    "airflow",
    "spark",
    "databricks",
]

TERMOS_TECNICOS_FRACOS = [
    "api",
    "apis",
    "rest",
    "restful",
    "git",
    "github",
    "gitlab",
    "linux",
    "shell",
    "bash",
    "powershell",
    "qa",
    "testes",
    "mobile",
    "programação",
    "programacao",
    "sistemas",
    "software",
    "web development",
    "desenvolvimento web",
    "tecnologia da informação",
    "tecnologia da informacao",
]

TERMOS_AREA_SOFTWARE = [
    "dev",
    "estágio em desenvolvimento",
    "estagio em desenvolvimento",
    "estagiário de desenvolvimento",
    "estagiario de desenvolvimento",
    "estagiária de desenvolvimento",
    "estagiaria de desenvolvimento",
    "estágio em ti",
    "estagio em ti",
    "trainee desenvolvimento",
    "trainee tecnologia",
    "sistemas de informação",
    "sistemas de informacao",
    "análise e desenvolvimento de sistemas",
    "analise e desenvolvimento de sistemas",
    "computação",
    "computacao",
    "ciência da computação",
    "ciencia da computacao",
    "engenharia de software",
    "desenvolvimento backend",
    "desenvolvimento frontend",
    "desenvolvimento full stack",
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


def contem_termo(texto, termo):
    termo = normalizar_texto(termo)
    padrao = rf"(?<![a-z0-9+#.]){re.escape(termo)}(?![a-z0-9+#.])"

    return re.search(padrao, texto) is not None


def contar_termos(texto, termos):
    return sum(1 for termo in termos if contem_termo(texto, termo))


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

    if any(contem_termo(titulo, termo) for termo in TITULOS_EXCLUIDOS):
        return False

    if any(contem_termo(titulo, termo) for termo in TITULOS_SOFTWARE):
        return True

    texto_completo = normalizar_texto(
        " ".join([
            dados.get("titulo") or "",
            dados.get("descricao") or "",
            dados.get("tecnologias") or "",
        ])
    )

    score = 0
    score += contar_termos(titulo, TITULOS_SOFTWARE_MODERADOS) * 3
    score += contar_termos(texto_completo, TECNOLOGIAS_FORTES) * 2
    score += contar_termos(texto_completo, TECNOLOGIAS_MODERADAS)
    score += contar_termos(texto_completo, TERMOS_TECNICOS_FRACOS)
    score += contar_termos(texto_completo, TERMOS_AREA_SOFTWARE) * 2

    titulo_generico_valido = any(contem_termo(titulo, termo) for termo in [
        "estagio",
        "estagiario",
        "estagiaria",
        "analista",
        "engenheiro",
        "engenheira",
        "assistente",
        "auxiliar",
        "consultor",
        "consultora",
        "especialista",
        "trainee",
    ])

    if titulo_generico_valido:
        return score >= 3

    return score >= 5
