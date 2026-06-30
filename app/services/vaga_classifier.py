import unicodedata

SOFTWARE_KEYWORDS = [
    # Linguagens
    "python",
    "java",
    "javascript",
    "typescript",
    "js",
    "ts",
    "c",
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
    "r",
    "shell",
    "bash",
    "powershell",

    # Front-end
    "html",
    "css",
    "sass",
    "scss",
    "tailwind",
    "bootstrap",
    "react",
    "reactjs",
    "react.js",
    "angular",
    "vue",
    "vuejs",
    "vue.js",
    "next.js",
    "nextjs",
    "nuxt",
    "jquery",
    "redux",
    "vite",

    # Back-end / Frameworks
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
    ".net",
    "dotnet",
    "dot net",
    "asp.net",
    "laravel",
    "rails",

    # APIs / Arquitetura
    "api",
    "apis",
    "rest",
    "restful",
    "graphql",
    "microservices",
    "microsserviços",
    "web services",

    # Mobile
    "mobile",
    "android",
    "ios",
    "react native",
    "flutter",
    "xamarin",

    # Banco de dados
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

    # DevOps / Cloud
    "docker",
    "kubernetes",
    "k8s",
    "git",
    "github",
    "gitlab",
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "jenkins",
    "github actions",
    "gitlab ci",
    "ci/cd",
    "terraform",
    "linux",
    "nginx",

    # Testes / Qualidade
    "testes",
    "qa",
    "quality assurance",
    "selenium",
    "cypress",
    "jest",
    "pytest",
    "junit",
    "unit tests",
    "testes unitários",
    "testes automatizados",

    # Dados / IA
    "data science",
    "ciência de dados",
    "data analyst",
    "analista de dados",
    "machine learning",
    "inteligência artificial",
    "ia",
    "pandas",
    "numpy",
    "pytorch",
    "tensorflow",
    "power bi",
    "etl",
    "big data",

    # Cargos
    "dev",
    "developer",
    "software developer",
    "software engineer",
    "engenheiro de software",
    "engenheira de software",
    "desenvolvedor",
    "desenvolvedora",
    "programador",
    "programadora",
    "analista de sistemas",
    "analista desenvolvedor",
    "analista de desenvolvimento",
    "estágio em desenvolvimento",
    "estagiário de desenvolvimento",
    "estagiária de desenvolvimento",
    "estágio em ti",
    "trainee desenvolvimento",
    "trainee tecnologia",

    # Áreas / Termos gerais
    "backend",
    "back-end",
    "frontend",
    "front-end",
    "full stack",
    "fullstack",
    "desenvolvimento de software",
    "engenharia de software",
    "programação",
    "sistemas",
    "sistemas de informação",
    "análise e desenvolvimento de sistemas",
    "ciência da computação",
    "computação",
    "tecnologia da informação",
    "ti",
    "software",
    "web development",
    "desenvolvimento web",
    "desenvolvimento backend",
    "desenvolvimento frontend",
    "desenvolvimento full stack",
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