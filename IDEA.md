# Rastreador de Vagas de Estágio
## Guia Completo de Arquitetura e Desenvolvimento

# 1. Visão Geral

## Objetivo

Desenvolver uma aplicação web utilizando Flask e PostgreSQL capaz de coletar vagas de estágio de múltiplas fontes, armazená-las em banco de dados, disponibilizá-las através de uma API REST e exibi-las em uma interface web.

O projeto tem como objetivo praticar:

- Python
- Flask
- PostgreSQL
- SQLAlchemy
- APIs REST
- Web Scraping
- Arquitetura de Software
- Git/GitHub
- Boas práticas de desenvolvimento

---

# 2. Requisitos Funcionais

O sistema deverá:

- Coletar vagas de diferentes fontes.
- Salvar vagas no PostgreSQL.
- Evitar duplicidade.
- Listar vagas.
- Filtrar vagas.
- Exibir vagas em interface web.
- Disponibilizar API REST.
- Permitir execução manual da coleta.
- Executar coleta automática futuramente.

---

# 3. Requisitos Não Funcionais

- Código organizado.
- Separação de responsabilidades.
- Fácil manutenção.
- Fácil expansão para novas fontes.
- Tratamento de erros.
- Banco normalizado.
- Boa documentação.

---

# 4. Arquitetura Geral

```text
Usuário
   |
Frontend HTML/CSS/JS
   |
Flask Routes
   |
Services
   |
Repositories (SQLAlchemy)
   |
PostgreSQL

Coletor
   |
Requests
   |
BeautifulSoup
   |
Services
   |
Banco
```

---

# 5. Estrutura de Pastas

```text
rastreador-vagas/
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   ├── database.py
│   │
│   ├── collectors/
│   │   ├── base.py
│   │   ├── quickin.py
│   │   ├── gupy.py
│   │   └── empresas.py
│   │
│   ├── services/
│   │   ├── coleta_service.py
│   │   └── vaga_service.py
│   │
│   ├── repositories/
│   │   └── vaga_repository.py
│   │
│   ├── templates/
│   └── static/
│
├── migrations/
├── tests/
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

---

# 6. Modelagem do Banco

## Tabela vagas

```sql
CREATE TABLE vagas (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    empresa VARCHAR(150),
    localizacao VARCHAR(150),
    modalidade VARCHAR(50),
    tecnologias TEXT,
    fonte VARCHAR(100),
    link TEXT UNIQUE,
    data_publicacao TIMESTAMP,
    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# 7. Model SQLAlchemy

```python
class Vaga(db.Model):
    __tablename__ = "vagas"

    id = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(db.String(200), nullable=False)

    empresa = db.Column(db.String(150))

    localizacao = db.Column(db.String(150))

    modalidade = db.Column(db.String(50))

    tecnologias = db.Column(db.Text)

    fonte = db.Column(db.String(100))

    link = db.Column(db.Text, unique=True)

    data_publicacao = db.Column(db.DateTime)

    data_coleta = db.Column(db.DateTime)
```

---

# 8. Padrão dos Coletores

Todo coletor deve retornar:

```python
{
    "titulo": "...",
    "empresa": "...",
    "localizacao": "...",
    "modalidade": "...",
    "tecnologias": "...",
    "fonte": "...",
    "link": "..."
}
```

---

# 9. Interface Base dos Coletores

```python
from abc import ABC, abstractmethod

class BaseCollector(ABC):

    @abstractmethod
    def coletar(self):
        pass
```

---

# 10. Coletor Quickin

Fluxo:

```text
Acessar página
↓
Baixar HTML
↓
Extrair vagas
↓
Converter para padrão interno
↓
Retornar lista
```

Bibliotecas:

```python
requests
beautifulsoup4
```

---

# 11. Service de Coleta

Responsabilidades:

- Executar coletores.
- Validar dados.
- Remover duplicados.
- Salvar no banco.

Fluxo:

```text
Executar coletor
↓
Receber lista
↓
Validar
↓
Verificar duplicidade
↓
Persistir
```

---

# 12. Repository Layer

Objetivo:

Isolar consultas SQL.

Exemplos:

```python
buscar_por_id()

buscar_por_empresa()

buscar_por_tecnologia()

buscar_todas()

salvar()

excluir()
```

---

# 13. API REST

## Listar vagas

```http
GET /api/vagas
```

## Buscar vaga

```http
GET /api/vagas/15
```

## Filtrar empresa

```http
GET /api/vagas?empresa=4mti
```

## Filtrar tecnologia

```http
GET /api/vagas?tecnologia=python
```

## Executar coleta

```http
POST /api/coletar
```

---

# 14. Interface Web

Tela inicial:

```text
Logo
Barra de pesquisa
Filtros
Lista de vagas
Paginação
```

Cada card:

```text
Título
Empresa
Localização
Tecnologias
Link
Fonte
```

---

# 15. Filtros

Implementar:

- Empresa
- Tecnologia
- Cidade
- Modalidade

Exemplos:

```http
/api/vagas?empresa=google

/api/vagas?tecnologia=java

/api/vagas?localizacao=belo horizonte
```

---

# 16. Tratamento de Duplicidade

Critério:

Link da vaga.

Antes de salvar:

```python
vaga_existente = buscar_por_link(link)
```

Se existir:

```python
ignorar
```

---

# 17. Logs

Registrar:

- início da coleta
- fim da coleta
- erros
- vagas encontradas
- vagas inseridas

Exemplo:

```python
logging.info()
logging.warning()
logging.error()
```

---

# 18. Scheduler

Fase futura.

Biblioteca:

```python
APScheduler
```

Fluxo:

```text
A cada 6 horas
↓
Executar coleta
↓
Salvar vagas novas
```

---

# 19. Testes

Criar testes para:

- coletores
- services
- repositories
- API

Bibliotecas:

```python
pytest
pytest-flask
```

---

# 20. Roadmap de Desenvolvimento

## Fase 1

- Flask
- PostgreSQL
- SQLAlchemy
- Migration

## Fase 2

- CRUD de vagas
- API REST

## Fase 3

- Coletor Quickin

## Fase 4

- Interface Web

## Fase 5

- Filtros

## Fase 6

- Scheduler

## Fase 7

- Deploy

---

# 21. Deploy

Opções:

- Render
- Railway
- VPS Ubuntu

Configurar:

- PostgreSQL
- Variáveis de ambiente
- Gunicorn

---

# 22. Melhorias Futuras

## Login

Usuários favoritos.

## Dashboard

Gráficos:

- vagas por empresa
- vagas por tecnologia
- vagas por cidade

## Alertas

- E-mail
- Telegram

## Inteligência

Extração automática de tecnologias:

```text
Python
Java
C#
PostgreSQL
React
Flask
Spring
Docker
```

---

# 23. Tecnologias que Devem Ser Demonstradas

Durante o projeto procurar demonstrar:

- Programação orientada a objetos
- SQL
- PostgreSQL
- Flask
- APIs REST
- Web Scraping
- Arquitetura em camadas
- Git
- Tratamento de erros
- Testes

---

# 24. Como Apresentar na Entrevista

Resumo:

"Desenvolvi um sistema de rastreamento de vagas utilizando Flask e PostgreSQL. O sistema coleta oportunidades em páginas públicas, organiza os dados, evita duplicidades, disponibiliza uma API REST e apresenta os resultados em uma interface web. O projeto foi criado para praticar backend, banco de dados, arquitetura de software e integração com fontes externas."

---

# 25. Objetivo Final

O objetivo final não é apenas exibir vagas.

O verdadeiro objetivo é demonstrar capacidade de:

- Modelar dados.
- Construir APIs.
- Trabalhar com PostgreSQL.
- Organizar código.
- Integrar sistemas.
- Coletar e tratar dados.
- Desenvolver uma aplicação completa do início ao fim.
