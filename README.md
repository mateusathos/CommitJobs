<p align="center">
  <img src="app/static/images/logo-commitjobs-quadrada.png" width="150" alt="Logo do CommitJobs">
</p>

<h1 align="center">CommitJobs</h1>

<p align="center">
  Rastreador e agregador de vagas de desenvolvimento de software.
</p>

<p align="center">
  <a href="https://commitjobs.onrender.com/">Aplicação publicada</a>
</p>

## Sobre

O CommitJobs centraliza vagas de desenvolvimento de software publicadas em diferentes plataformas. A aplicação coleta, normaliza e classifica as oportunidades, elimina duplicidades e disponibiliza os dados em uma interface web responsiva e em uma API REST.

O sistema trabalha com vagas de diferentes níveis de senioridade, modalidades e localidades. A coleta considera publicações dos últimos 90 dias e utiliza checkpoints independentes por fonte e consulta para evitar o reprocessamento integral das páginas a cada execução.

## Funcionalidades

- Coleta de vagas em múltiplas fontes.
- Execução paralela dos coletores.
- Coleta incremental com checkpoint por consulta.
- Janela de segurança de cinco dias entre execuções.
- Classificação de vagas por senioridade.
- Identificação de oportunidades relacionadas a desenvolvimento de software.
- Normalização de links e prevenção de duplicidades.
- Busca textual em título, descrição e tecnologias.
- Filtros combináveis por empresa, localização, nível, modalidade e período.
- Paginação na interface e na API.
- Relatório de coleta com métricas por fonte.
- Endpoint de coleta protegido por token.

## Fontes

| Fonte | Integração | Estratégia |
|---|---|---|
| Gupy | API JSON | Busca por termos e paginação por offset |
| Sólides | API JSON | Busca por título e paginação |
| Remotar | API JSON | Filtros nativos por categoria e senioridade |
| Jooble | API JSON autenticada | Busca por palavra-chave e localização |

Cada fonte é adaptada para um formato interno comum antes de passar pelas regras de classificação e persistência.

## Arquitetura

```mermaid
flowchart LR
    A[Fontes de vagas] --> B[Coletores]
    B --> C[ColetaService]
    C --> D[Classificação e normalização]
    D --> E[VagaService]
    E --> F[Repositories]
    F --> G[(PostgreSQL)]
    G --> H[API REST]
    G --> I[Interface Flask/Jinja]
```

O projeto utiliza uma arquitetura em camadas:

- `collectors`: comunicação e normalização dos dados de cada fonte.
- `services`: regras de negócio, classificação, coleta e deduplicação.
- `repositories`: consultas e persistência com SQLAlchemy.
- `models`: entidades persistidas no PostgreSQL.
- `routes`: interface HTTP, API e renderização da página.

## Coleta incremental

Cada combinação de fonte e consulta possui um registro em `estados_coleta`, contendo:

- data da última execução concluída;
- publicação mais recente encontrada;
- chave única da consulta.

Na primeira execução, o coletor pesquisa vagas dos últimos 90 dias. Nas execuções seguintes, utiliza a publicação mais recente conhecida com uma sobreposição de cinco dias. Essa margem reduz o risco de perder vagas indexadas com atraso, enquanto a normalização dos links impede inserções repetidas.

As chamadas externas são executadas com `ThreadPoolExecutor`. O acesso ao banco permanece centralizado na thread principal para evitar o compartilhamento inadequado da sessão SQLAlchemy.

## Deduplicação

Antes da persistência, os links são normalizados:

- domínio e protocolo são padronizados;
- barras finais são removidas;
- parâmetros de rastreamento são descartados;
- a restrição `UNIQUE` do PostgreSQL funciona como proteção final.

Isso permite reconhecer a mesma vaga quando ela aparece em consultas diferentes ou é republicada por um agregador.

## Interface

A interface apresenta as vagas em cards responsivos e permite combinar:

- busca por cargo ou tecnologia;
- empresa;
- localização;
- níveis de senioridade;
- modalidades;
- publicações de hoje, dos últimos sete dias ou dos últimos 30 dias.

## API REST

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/vagas` | Lista vagas com filtros e paginação |
| `GET` | `/api/vagas/<id>` | Retorna uma vaga |
| `POST` | `/api/vagas` | Cadastra uma vaga manualmente |
| `POST` | `/api/coletar` | Executa a coleta autenticada |

Exemplo de consulta:

```http
GET /api/vagas?busca=python&nivel=Júnior&modalidade=Remoto&periodo=semana&page=1
```

O endpoint `/api/coletar` exige:

```http
Authorization: Bearer <CRON_SECRET>
```

## Tecnologias

- Python 3.10
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- Psycopg 3
- Requests
- Beautiful Soup
- Jinja
- Gunicorn
- HTML e CSS

## Configuração

Variáveis de ambiente necessárias:

```env
DATABASE_URL=postgresql+psycopg://usuario:senha@host/banco
SECRET_KEY=chave-da-aplicacao
JOOBLE_API_KEY=chave-da-api-jooble
CRON_SECRET=token-da-coleta
```

Instalação e execução local:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python run.py
```

Criação das tabelas:

```powershell
.\.venv\Scripts\python -c "from app import create_app; from app.database import db; import app.models; app=create_app(); app.app_context().push(); db.create_all()"
```

Execução em produção:

```text
gunicorn run:app --workers 1 --timeout 900
```

## Estrutura

```text
app/
├── collectors/
├── repositories/
├── services/
├── static/
├── templates/
├── database.py
├── models.py
└── routes.py

config.py
requirements.txt
run.py
```

## Modelo de dados

`vagas` armazena os dados normalizados das oportunidades, incluindo título, descrição, empresa, localização, modalidade, senioridade, tecnologias, fonte, link e datas.

`estados_coleta` mantém os checkpoints usados pela coleta incremental.

## Deploy

A aplicação está preparada para execução com Gunicorn e PostgreSQL externo. A versão publicada utiliza Render para o serviço web e pode utilizar um agendador externo para chamar periodicamente o endpoint protegido de coleta.
