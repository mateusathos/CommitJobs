from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from app.database import db
from app.models import EstadoColeta


class EstadoColetaRepository:
    def _normalizar_utc(self, data):
        if data is None:
            return None

        if data.tzinfo is None:
            return data.replace(tzinfo=timezone.utc)

        return data.astimezone(timezone.utc)

    def buscar(self, fonte, chave_consulta):
        return EstadoColeta.query.filter_by(
            fonte=fonte,
            chave_consulta=chave_consulta,
        ).first()

    def atualizar(
        self,
        fonte,
        chave_consulta,
        ultima_publicacao_encontrada,
    ):
        agora = datetime.now(timezone.utc)

        estado = self.buscar(
            fonte,
            chave_consulta,
        )

        ultima_publicacao_encontrada = self._normalizar_utc(
            ultima_publicacao_encontrada
        )

        if estado:
            estado.ultima_execucao = agora

            publicacao_anterior = self._normalizar_utc(
                estado.ultima_publicacao_encontrada
            )

            if (
                ultima_publicacao_encontrada
                and (
                    not publicacao_anterior
                    or ultima_publicacao_encontrada > publicacao_anterior
                )
            ):
                estado.ultima_publicacao_encontrada = (
                    ultima_publicacao_encontrada
                )
        else:
            estado = EstadoColeta(
                fonte=fonte,
                chave_consulta=chave_consulta,
                ultima_execucao=agora,
                ultima_publicacao_encontrada=(
                    ultima_publicacao_encontrada
                ),
            )

            db.session.add(estado)

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise

        return estado