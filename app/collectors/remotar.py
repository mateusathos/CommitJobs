from datetime import datetime

import requests
from bs4 import BeautifulSoup

from app.collectors.base import BaseCollector


class RemotarCollector(BaseCollector):
    BASE_URL = "https://api.remotar.com.br/jobs"

    NIVEIS_POR_TAG = {
        10: "Estágio",
        17: "Júnior",
        21: "Pleno",
        23: "Sênior",
    }

    def __init__(
        self,
        tag_id,
        category_ids=None,
        max_pages=2,
        max_age_days=90,
    ):
        super().__init__(max_age_days)

        self.tag_id = tag_id
        self.category_ids = category_ids or [4, 7, 13, 14]
        self.max_pages = max_pages
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RastreadorDeVagas/1.0)"
        }

    def coletar(self):
        vagas = []
        pagina = 1

        while pagina <= self.max_pages:
            payload = self._buscar_pagina(pagina)
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

            if self.pagina_totalmente_antiga(
                vagas_da_pagina
            ):
                break

            ultima_pagina = payload.get("meta", {}).get(
                "last_page",
                pagina,
            )

            if pagina >= ultima_pagina:
                break

            pagina += 1

        return vagas

    def _buscar_pagina(self, pagina):
        params = {
            "search": "",
            "tagId": self.tag_id,
            "categoryId": ",".join(
                str(category_id)
                for category_id in self.category_ids
            ),
            "page": pagina,
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            headers=self.headers,
            timeout=20,
        )

        response.raise_for_status()

        return response.json()
    
    def _obter_link(self, item):
        link_externo = item.get("externalLink")

        if link_externo:
            return link_externo

        vaga_id = item.get("id")

        if vaga_id:
            return f"https://remotar.com.br/job/{vaga_id}"

        return None

    def _normalizar_vaga(self, item):
        return {
            "titulo": item.get("title"),
            "descricao": self._limpar_html(item.get("description")),
            "empresa": self._obter_empresa(item),
            "localizacao": self._montar_localizacao(item),
            "modalidade": self._normalizar_modalidade(item),
            "nivel": self._identificar_nivel(item),
            "tecnologias": self._montar_categorias(item),
            "fonte": "Remotar",
            "link": self._obter_link(item),
            "data_publicacao": self._parse_data(item.get("createdAt")),
        }

    def _identificar_nivel(self, item):
        for job_tag in item.get("jobTags") or []:
            tag = job_tag.get("tag") or {}
            tag_id = tag.get("id")

            if tag_id in self.NIVEIS_POR_TAG:
                return self.NIVEIS_POR_TAG[tag_id]

        return self.NIVEIS_POR_TAG.get(self.tag_id)

    def _obter_empresa(self, item):
        if item.get("companyDisplayName"):
            return item["companyDisplayName"]

        empresa = item.get("company") or {}

        return empresa.get("name")

    def _montar_localizacao(self, item):
        partes = [
            item.get("city"),
            item.get("state"),
        ]

        partes = [
            parte.strip()
            for parte in partes
            if parte and parte.strip()
        ]

        if partes:
            return ", ".join(partes)

        if item.get("type") == "remote":
            return "Remoto"

        return None

    def _normalizar_modalidade(self, item):
        modalidades = {
            "remote": "Remoto",
            "hybrid": "Híbrido",
            "on-site": "Presencial",
        }

        return modalidades.get(item.get("type"))

    def _montar_categorias(self, item):
        nomes = []

        for job_category in item.get("jobCategories") or []:
            categoria = job_category.get("category") or {}
            nome = categoria.get("name")

            if nome:
                nomes.append(nome)

        if not nomes:
            return None

        return ", ".join(dict.fromkeys(nomes))

    def _limpar_html(self, html):
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        return soup.get_text(separator=" ", strip=True)

    def _parse_data(self, valor):
        if not valor:
            return None

        try:
            return datetime.fromisoformat(valor)
        except ValueError:
            return None
        
    @property
    def fonte(self):
        return "Remotar"

    @property
    def chave_consulta(self):
        categorias = ",".join(
            str(category_id)
            for category_id in sorted(self.category_ids)
        )

        return f"tag={self.tag_id};categories={categorias}"
