from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone


class BaseCollector(ABC):
    def __init__(self, max_age_days=90):
        self.max_age_days = max_age_days
        self.data_limite = (
            datetime.now(timezone.utc)
            - timedelta(days=max_age_days)
        )

    def definir_data_limite(self, data_limite):
        self.data_limite = self._converter_para_utc(
            data_limite
        )

    def data_dentro_do_periodo(self, data_publicacao):
        if not data_publicacao:
            return False

        data_publicacao = self._converter_para_utc(
            data_publicacao
        )

        return data_publicacao >= self.data_limite

    def pagina_totalmente_antiga(self, vagas):
        datas = [
            self._converter_para_utc(
                vaga["data_publicacao"]
            )
            for vaga in vagas
            if vaga.get("data_publicacao")
        ]

        if not datas:
            return False

        return max(datas) < self.data_limite

    def _converter_para_utc(self, data):
        if data.tzinfo is None:
            return data.replace(tzinfo=timezone.utc)

        return data.astimezone(timezone.utc)
    
    def obter_data_mais_recente(self, vagas):
        datas = [
            self._converter_para_utc(
                vaga["data_publicacao"]
            )
            for vaga in vagas
            if vaga.get("data_publicacao")
        ]

        return max(datas) if datas else None

    @property
    @abstractmethod
    def fonte(self):
        pass

    @property
    @abstractmethod
    def chave_consulta(self):
        pass

    @abstractmethod
    def coletar(self):
        pass