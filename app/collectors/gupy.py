from datetime import datetime

import requests

from app.collectors.base import BaseCollector


class GupyCollector(BaseCollector):
    BASE_URL = "https://employability-portal.gupy.io/api/v1/jobs"

    def __init__(
        self,
        query="desenvolvedor",
        limit=10,
        max_pages=3,
        max_age_days=90,
    ):
        super().__init__(max_age_days)

        self.query = query
        self.limit = limit
        self.max_pages = max_pages
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RastreadorDeVagas/1.0)"
        }

    def coletar(self):
        vagas = []
        offset = 0
        pagina_atual = 0

        while pagina_atual < self.max_pages:
            payload = self._buscar_pagina(offset)
            itens = payload.get("data", [])

            if not itens:
                break

            vagas_da_pagina = [
                self._normalizar_vaga(item)
                for item in itens
            ]

            for vaga in vagas_da_pagina:
                if self.data_dentro_do_periodo(
                    vaga["data_publicacao"]
                ):
                    vagas.append(vaga)

            pagination = payload.get("pagination", {})
            total = pagination.get("total", 0)

            offset += self.limit
            pagina_atual += 1

            if self.pagina_totalmente_antiga(vagas_da_pagina):
                break

            if offset >= total:
                break


        return vagas

    def _buscar_pagina(self, offset):
        params = {
            "jobName": self.query,
            "limit": self.limit,
            "offset": offset,
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            headers=self.headers,
            timeout=20,
        )

        response.raise_for_status()

        return response.json()

    def _normalizar_vaga(self, item):
        return {
            "titulo": item.get("name"),
            "descricao": item.get("description"),
            "empresa": item.get("careerPageName"),
            "localizacao": self._montar_localizacao(item),
            "modalidade": self._normalizar_modalidade(item),
            "tecnologias": self._montar_tecnologias(item),
            "tipo_origem": item.get("type"),
            "fonte": "Gupy",
            "link": item.get("jobUrl"),
            "data_publicacao": self._parse_data(item.get("publishedDate")),
        }

    def _montar_localizacao(self, item):
        partes = [
            item.get("city"),
            item.get("state"),
            item.get("country"),
        ]

        partes = [parte for parte in partes if parte]

        if not partes:
            return None

        return ", ".join(partes)

    def _normalizar_modalidade(self, item):
        workplace_type = item.get("workplaceType")

        if workplace_type == "remote":
            return "Remoto"

        if workplace_type == "hybrid":
            return "Híbrido"

        if workplace_type == "on-site":
            return "Presencial"

        if item.get("isRemoteWork"):
            return "Remoto"

        return None

    def _montar_tecnologias(self, item):
        skills = item.get("skills") or []

        if not skills:
            return None

        nomes = []

        for skill in skills:
            if isinstance(skill, str):
                nomes.append(skill)
            elif isinstance(skill, dict):
                nome = skill.get("name")
                if nome:
                    nomes.append(nome)

        if not nomes:
            return None

        return ", ".join(nomes)

    def _parse_data(self, valor):
        if not valor:
            return None

        try:
            return datetime.fromisoformat(valor.replace("Z", "+00:00"))
        except ValueError:
            return None
        
    @property
    def fonte(self):
        return "Gupy"

    @property
    def chave_consulta(self):
        return f"query={self.query.strip().lower()}"
