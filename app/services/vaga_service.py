from app.models import Vaga
from app.repositories.vaga_repository import VagaRepository
from app.services.vaga_classifier import identificar_nivel
from app.services.link_normalizer import normalizar_link
from sqlalchemy.exc import IntegrityError


class VagaService:
    def __init__(self):
        self.repository = VagaRepository()

    def listar_vagas(self, filtros=None):
        filtros = filtros or {}

        empresa = filtros.get("empresa")
        tecnologia = filtros.get("tecnologia")
        localizacao = filtros.get("localizacao")
        modalidade = filtros.get("modalidade")

        if empresa:
            return self.repository.buscar_por_empresa(empresa)

        if tecnologia:
            return self.repository.buscar_por_tecnologia(tecnologia)

        if localizacao:
            return self.repository.buscar_por_localizacao(localizacao)
        
        if modalidade:
            return self.repository.buscar_por_modalidade(modalidade)

        return self.repository.buscar_todas()
    
    def listar_vagas_paginadas(self, filtros=None, page=1, per_page=20):
        return self.repository.buscar_com_filtros_paginado(
            filtros=filtros,
            page=page,
            per_page=per_page,
        )

    def criar_vaga(self, dados):
        self._validar_dados_obrigatorios(dados)

        link_normalizado = normalizar_link(dados["link"])

        vaga_existente = self.repository.buscar_por_link(link_normalizado)

        if vaga_existente:
            return vaga_existente, False

        vaga = Vaga(
            titulo=dados["titulo"],
            descricao=dados.get("descricao"),
            empresa=dados.get("empresa"),
            localizacao=dados.get("localizacao"),
            modalidade=dados.get("modalidade"),
            nivel=dados.get("nivel") or identificar_nivel(dados),
            tecnologias=dados.get("tecnologias"),
            fonte=dados.get("fonte"),
            link=link_normalizado,
            data_publicacao=dados.get("data_publicacao"),
        )

        try:
            vaga_salva = self.repository.salvar(vaga)
        except IntegrityError:
            vaga_existente = self.repository.buscar_por_link(
                link_normalizado
            )

            if vaga_existente:
                return vaga_existente, False

            raise

        return vaga_salva, True

    def _validar_dados_obrigatorios(self, dados):
        if not dados.get("titulo"):
            raise ValueError("O campo titulo é obrigatório.")

        if not dados.get("link"):
            raise ValueError("O campo link é obrigatório.")