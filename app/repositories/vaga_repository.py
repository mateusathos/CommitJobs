from app.database import db
from app.models import Vaga
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, time, timedelta
from sqlalchemy import or_
from zoneinfo import ZoneInfo


class VagaRepository:
    def buscar_todas(self):
        return Vaga.query.order_by(Vaga.data_coleta.desc()).all()

    def buscar_por_id(self, vaga_id):
        return Vaga.query.get(vaga_id)

    def buscar_por_link(self, link):
        return Vaga.query.filter_by(link=link).first()

    def buscar_por_empresa(self, empresa):
        return Vaga.query.filter(Vaga.empresa.ilike(f"%{empresa}%")).all()

    def buscar_por_tecnologia(self, tecnologia):
        return Vaga.query.filter(Vaga.tecnologias.ilike(f"%{tecnologia}%")).all()

    def buscar_por_localizacao(self, localizacao):
        return Vaga.query.filter(Vaga.localizacao.ilike(f"%{localizacao}%")).all()
    
    def buscar_por_modalidade(self, modalidade):
        return Vaga.query.filter(Vaga.modalidade.ilike(f"%{modalidade}%")).all()
    
    def buscar_com_filtros_paginado(self, filtros=None, page=1, per_page=20):
        filtros = filtros or {}

        query = Vaga.query

        busca = filtros.get("busca")
        empresa = filtros.get("empresa")
        tecnologia = filtros.get("tecnologia")
        localizacao = filtros.get("localizacao")
        modalidade = filtros.get("modalidade")
        nivel = filtros.get("nivel")
        periodo = filtros.get("periodo")

        if busca:
            termo = f"%{busca.strip()}%"

            query = query.filter(
                or_(
                    Vaga.titulo.ilike(termo),
                    Vaga.descricao.ilike(termo),
                    Vaga.tecnologias.ilike(termo),
                )
            )

        if empresa:
            query = query.filter(
                Vaga.empresa.ilike(f"%{empresa}%")
            )

        if tecnologia:
            query = query.filter(
                Vaga.tecnologias.ilike(f"%{tecnologia}%")
            )

        if localizacao:
            query = query.filter(
                Vaga.localizacao.ilike(f"%{localizacao}%")
            )

        if modalidade:
            query = query.filter(
                Vaga.modalidade.in_(modalidade)
            )

        if nivel:
            query = query.filter(
                Vaga.nivel.in_(nivel)
            )

        if periodo:
            fuso_brasilia = ZoneInfo("America/Sao_Paulo")
            agora = datetime.now(fuso_brasilia)

            if periodo == "hoje":
                inicio = datetime.combine(
                    agora.date(),
                    time.min,
                )
                fim = inicio + timedelta(days=1)

                query = query.filter(
                    Vaga.data_publicacao >= inicio,
                    Vaga.data_publicacao < fim,
                )
            elif periodo == "semana":
                data_limite = (
                    agora - timedelta(days=7)
                ).replace(tzinfo=None)

                query = query.filter(
                    Vaga.data_publicacao >= data_limite
                )
            elif periodo == "mes":
                data_limite = (
                    agora - timedelta(days=30)
                ).replace(tzinfo=None)

                query = query.filter(
                    Vaga.data_publicacao >= data_limite
                )

        query = query.order_by(
            Vaga.data_publicacao.desc().nullslast(),
            Vaga.data_coleta.desc(),
        )

        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

    def salvar(self, vaga):
        try:
            db.session.add(vaga)
            db.session.commit()
            return vaga
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def excluir(self, vaga):
        db.session.delete(vaga)
        db.session.commit()
