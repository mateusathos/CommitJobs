from app.services.vaga_service import VagaService
from app.collectors.gupy import GupyCollector
from app.collectors.remotar import RemotarCollector
from app.collectors.solides import SolidesCollector
from app.collectors.jooble import JoobleCollector
from app.services.vaga_classifier import identificar_nivel, vaga_eh_de_software
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from app.repositories.estado_coleta_repository import (EstadoColetaRepository,)
from flask import current_app


class ColetaService:
    def __init__(self):
        jooble_api_key = current_app.config.get(
            "JOOBLE_API_KEY"
        )
        self.vaga_service = VagaService()
        self.estado_repository = EstadoColetaRepository()
        self.collectors = [
            GupyCollector(
                query="desenvolvedor",
                limit=50,
                max_pages=200,
                max_age_days=90,
            ),
            GupyCollector(
                query="software engineer",
                limit=50,
                max_pages=200,
                max_age_days=90,
            ),
            GupyCollector(
                query="programador",
                limit=50,
                max_pages=200,
                max_age_days=90,
            ),
            GupyCollector(
                query="backend",
                limit=50,
                max_pages=200,
                max_age_days=90,
            ),
            GupyCollector(
                query="frontend",
                limit=50,
                max_pages=200,
                max_age_days=90,
            ),
            GupyCollector(
                query="fullstack",
                limit=50,
                max_pages=200,
                max_age_days=90,
            ),
            GupyCollector(
                query="dev",
                limit=50,
                max_pages=200,
                max_age_days=90,
            ),
            GupyCollector(
                query="ti",
                limit=50,
                max_pages=200,
                max_age_days=90,
            ),
            GupyCollector(
                query="tecnologia",
                limit=50,
                max_pages=200,
                max_age_days=90,
            ),
            GupyCollector(
                query="tech",
                limit=50,
                max_pages=200,
                max_age_days=90,
            ),


            SolidesCollector(
                query="desenvolvedor",
                take=14,
                max_pages=200,
                max_age_days=90,
            ),
            SolidesCollector(
                query="software engineer",
                take=14,
                max_pages=200,
                max_age_days=90,
            ),
            SolidesCollector(
                query="programador",
                take=14,
                max_pages=200,
                max_age_days=90,
            ),
            SolidesCollector(
                query="backend",
                take=14,
                max_pages=200,
                max_age_days=90,
            ),
            SolidesCollector(
                query="frontend",
                take=14,
                max_pages=200,
                max_age_days=90,
            ),
            SolidesCollector(
                query="fullstack",
                take=14,
                max_pages=200,
                max_age_days=90,
            ),
            SolidesCollector(
                query="ti",
                take=14,
                max_pages=200,
                max_age_days=90,
            ),
            SolidesCollector(
                query="tecnologia",
                take=14,
                max_pages=200,
                max_age_days=90,
            ),
            SolidesCollector(
                query="tech",
                take=14,
                max_pages=200,
                max_age_days=90,
            ),


            RemotarCollector(
                tag_id=10,
                category_ids=[4, 7, 13, 14],
                max_pages=100,
                max_age_days=90,
            ),
            RemotarCollector(
                tag_id=17,
                category_ids=[4, 7, 13, 14],
                max_pages=100,
                max_age_days=90,
            ),
            RemotarCollector(
                tag_id=21,
                category_ids=[4, 7, 13, 14],
                max_pages=100,
                max_age_days=90,
            ),
            RemotarCollector(
                tag_id=23,
                category_ids=[4, 7, 13, 14],
                max_pages=100,
                max_age_days=90,
            ),

            JoobleCollector(
                query="desenvolvedor",
                api_key=jooble_api_key,
                location="Brasil",
                results_per_page=100,
                max_pages=5,
                max_age_days=90,
            ),
            JoobleCollector(
                query="software engineer",
                api_key=jooble_api_key,
                location="Brasil",
                results_per_page=100,
                max_pages=5,
                max_age_days=90,
            ),
            JoobleCollector(
                query="programador",
                api_key=jooble_api_key,
                location="Brasil",
                results_per_page=100,
                max_pages=5,
                max_age_days=90,
            ),
            JoobleCollector(
                query="dev",
                api_key=jooble_api_key,
                location="Brasil",
                results_per_page=100,
                max_pages=5,
                max_age_days=90,
            ),
        ]

    def executar_coleta(self):
        from time import perf_counter
        inicio = perf_counter()

        totais = {
            "encontradas": 0,
            "filtradas_fora": 0,
            "duplicadas": 0,
            "inseridas": 0,
        }

        fontes = {}
        erros = []

        for collector in self.collectors:
            estado = self.estado_repository.buscar(
                collector.fonte,
                collector.chave_consulta,
            )

            if (
                estado
                and estado.ultima_publicacao_encontrada
            ):
                data_limite = (
                    estado.ultima_publicacao_encontrada
                    - timedelta(days=5)
                )
            else:
                data_limite = (
                    datetime.now(timezone.utc)
                    - timedelta(days=90)
                )

            collector.definir_data_limite(data_limite)

        with ThreadPoolExecutor(max_workers=6) as executor:
            tarefas = {
                executor.submit(collector.coletar): collector
                for collector in self.collectors
            }

            for tarefa in as_completed(tarefas):
                collector = tarefas[tarefa]

                nome_fonte = collector.fonte

                if nome_fonte not in fontes:
                    fontes[nome_fonte] = {
                        "encontradas": 0,
                        "filtradas_fora": 0,
                        "duplicadas": 0,
                        "inseridas": 0,
                    }

                estatisticas = fontes[nome_fonte]

                try:
                    vagas = tarefa.result()

                    quantidade = len(vagas)
                    estatisticas["encontradas"] += quantidade
                    totais["encontradas"] += quantidade

                    for dados_vaga in vagas:
                        if not vaga_eh_de_software(dados_vaga):
                            estatisticas["filtradas_fora"] += 1
                            totais["filtradas_fora"] += 1
                            continue

                        nivel = (
                            dados_vaga.get("nivel")
                            or identificar_nivel(dados_vaga)
                        )

                        dados_vaga["nivel"] = nivel

                        vaga, criada = self.vaga_service.criar_vaga(
                            dados_vaga
                        )

                        if criada:
                            estatisticas["inseridas"] += 1
                            totais["inseridas"] += 1
                        else:
                            estatisticas["duplicadas"] += 1
                            totais["duplicadas"] += 1
                    
                    ultima_publicacao = (
                        collector.obter_data_mais_recente(vagas)
                    )

                    # Registra que este coletor terminou com sucesso.
                    self.estado_repository.atualizar(
                        fonte=collector.fonte,
                        chave_consulta=collector.chave_consulta,
                        ultima_publicacao_encontrada=ultima_publicacao,
                    )

                except Exception as erro:
                    erros.append({
                        "fonte": nome_fonte,
                        "erro": str(erro),
                    })

        duracao_segundos = round(
            perf_counter() - inicio,
            2,
        )

        return {
            "totais": totais,
            "fontes": fontes,
            "duracao_segundos": duracao_segundos,
            "erros": erros,
        }