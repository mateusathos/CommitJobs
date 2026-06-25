from datetime import datetime

import requests

from app.collectors.base import BaseCollector
import re


class JoobleCollector(BaseCollector):
    BASE_URL = "https://br.jooble.org/api"

    def __init__(
        self,
        query,
        api_key,
        location="Brasil",
        results_per_page=100,
        max_pages=5,
        max_age_days=90,
    ):
        super().__init__(max_age_days)

        self.query = query
        self.api_key = api_key
        self.location = location
        self.results_per_page = results_per_page
        self.max_pages = max_pages

        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; RastreadorDeVagas/1.0)"
            ),
        }

    @property
    def fonte(self):
        return "Jooble"

    @property
    def chave_consulta(self):
        query = self.query.strip().lower()
        location = self.location.strip().lower()

        return f"query={query};location={location}"

    def coletar(self):
        vagas = []
        pagina = 1

        while pagina <= self.max_pages:
            payload = self._buscar_pagina(pagina)
            itens = payload.get("jobs") or []

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

            total = payload.get("totalCount", 0)

            if pagina * self.results_per_page >= total:
                break

            pagina += 1

        return vagas

    def _buscar_pagina(self, pagina):
        if not self.api_key:
            raise ValueError(
                "JOOBLE_API_KEY não foi configurada."
            )

        url = f"{self.BASE_URL}/{self.api_key}"

        payload = {
            "keywords": self.query,
            "location": self.location,
            "page": str(pagina),
            "ResultOnPage": str(
                self.results_per_page
            ),
            "companysearch": "false",
        }

        response = requests.post(
            url,
            json=payload,
            headers=self.headers,
            timeout=20,
        )

        response.raise_for_status()

        return response.json()

    def _normalizar_vaga(self, item):
        return {
            "titulo": item.get("title"),
            "descricao": item.get("snippet"),
            "empresa": item.get("company"),
            "localizacao": item.get("location"),
            "modalidade": self._identificar_modalidade(item),
            "nivel": None,
            "tecnologias": None,
            "fonte": "Jooble",
            "link": item.get("link"),
            "data_publicacao": self._parse_data(
                item.get("updated")
            ),
        }

    def _identificar_modalidade(self, item):
        texto = " ".join([
            item.get("title") or "",
            item.get("location") or "",
            item.get("snippet") or "",
            item.get("type") or "",
        ]).lower()

        if any(termo in texto for termo in [
            "remoto",
            "remote",
            "home office",
        ]):
            return "Remoto"

        if any(termo in texto for termo in [
            "híbrido",
            "hibrido",
            "hybrid",
        ]):
            return "Híbrido"

        return None

    def _parse_data(self, valor):
        if not valor:
            return None

        valor_ajustado = re.sub(
            r"(\.\d{6})\d+",
            r"\1",
            valor,
        )

        try:
            return datetime.fromisoformat(valor_ajustado)
        except ValueError:
            return None