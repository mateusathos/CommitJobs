from datetime import datetime

import requests
from bs4 import BeautifulSoup

from app.collectors.base import BaseCollector


class SolidesCollector(BaseCollector):
    BASE_URL = (
        "https://apigw.solides.com.br/"
        "jobs/v3/portal-vacancies-new"
    )

    def __init__(
        self,
        query,
        take=14,
        max_pages=2,
        max_age_days=90,
    ):
        super().__init__(max_age_days)

        self.query = query
        self.take = take
        self.max_pages = max_pages
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; RastreadorDeVagas/1.0)"
            )
        }

    def coletar(self):
        vagas = []
        pagina = 1

        while pagina <= self.max_pages:
            payload = self._buscar_pagina(pagina)
            conteudo = payload.get("data") or {}
            itens = conteudo.get("data") or []

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

            total_paginas = conteudo.get(
                "totalPages",
                pagina,
            )

            if pagina >= total_paginas:
                break

            if self.pagina_totalmente_antiga(vagas_da_pagina):
                break

            pagina += 1

        return vagas

    def _buscar_pagina(self, pagina):
        params = {
            "page": pagina,
            "title": self.query,
            "take": self.take,
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
            "titulo": self._limpar_texto(item.get("title")),
            "descricao": self._limpar_html(
                item.get("description")
            ),
            "empresa": item.get("companyName"),
            "localizacao": self._montar_localizacao(item),
            "modalidade": self._normalizar_modalidade(item),
            "nivel": self._identificar_nivel(item),
            "tecnologias": self._montar_tecnologias(item),
            "fonte": "Sólides",
            "link": item.get("redirectLink"),
            "data_publicacao": self._parse_data(
                item.get("createdAt")
            ),
        }

    def _identificar_nivel(self, item):
        senioridades = [
            nivel.get("name", "").strip().lower()
            for nivel in item.get("seniority") or []
        ]

        contratos = [
            contrato.get("name", "").strip().lower()
            for contrato in item.get("recruitmentContractType") or []
        ]

        termos = senioridades + contratos

        termos_estagio = {
            "estágio",
            "estagio",
            "estagiário",
            "estagiario",
            "estagiária",
            "estagiaria",
            "intern",
        }

        if any(termo in termos_estagio for termo in termos):
            return "Estágio"

        termos_senior = {
            "sênior",
            "senior",
            "sr",
        }

        if any(termo in termos_senior for termo in termos):
            return "Sênior"

        termos_pleno = {
            "pleno",
            "pl",
        }

        if any(termo in termos_pleno for termo in termos):
            return "Pleno"

        termos_junior = {
            "júnior",
            "junior",
            "jr",
        }

        if any(termo in termos_junior for termo in termos):
            return "Júnior"

        return None

    def _montar_localizacao(self, item):
        cidade = (item.get("city") or {}).get("name")
        estado = (item.get("state") or {}).get("name")

        partes = [
            parte.strip()
            for parte in [cidade, estado]
            if parte and parte.strip()
        ]

        return ", ".join(partes) if partes else None

    def _normalizar_modalidade(self, item):
        modalidades = {
            "remoto": "Remoto",
            "hibrido": "Híbrido",
            "presencial": "Presencial",
        }

        return modalidades.get(item.get("jobType"))

    def _montar_tecnologias(self, item):
        nomes = [
            skill.get("name")
            for skill in item.get("hardSkills") or []
            if skill.get("name")
        ]

        return ", ".join(nomes) if nomes else None

    def _limpar_html(self, html):
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        return soup.get_text(separator=" ", strip=True)

    def _limpar_texto(self, texto):
        return texto.strip() if texto else None

    def _parse_data(self, valor):
        if not valor:
            return None

        try:
            return datetime.fromisoformat(valor)
        except ValueError:
            return None
        
    @property
    def fonte(self):
        return "Solides"

    @property
    def chave_consulta(self):
        return f"query={self.query.strip().lower()}"
