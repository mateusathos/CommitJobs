from datetime import datetime, timezone
from app.database import db

class Vaga(db.Model):
    __tablename__ = "vagas"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    empresa = db.Column(db.String(150))
    localizacao = db.Column(db.String(150))
    modalidade = db.Column(db.String(50))
    nivel = db.Column(db.String(50), nullable=False, default="Não informado")
    tecnologias = db.Column(db.Text)
    fonte = db.Column(db.String(100))
    link = db.Column(db.Text, unique=True, nullable=False)
    data_publicacao = db.Column(db.DateTime)
    data_coleta = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "empresa": self.empresa,
            "localizacao": self.localizacao,
            "modalidade": self.modalidade,
            "nivel": self.nivel,
            "tecnologias": self.tecnologias,
            "fonte": self.fonte,
            "link": self.link,
            "data_publicacao": self.data_publicacao.isoformat() if self.data_publicacao else None,
            "data_coleta": self.data_coleta.isoformat() if self.data_coleta else None,
        }
    
class EstadoColeta(db.Model):
    __tablename__ = "estados_coleta"

    id = db.Column(db.Integer, primary_key=True)

    fonte = db.Column(
        db.String(50),
        nullable=False,
    )

    chave_consulta = db.Column(
        db.String(255),
        nullable=False,
    )

    ultima_execucao = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
    )

    ultima_publicacao_encontrada = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    data_atualizacao = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "fonte",
            "chave_consulta",
            name="uq_estado_coleta_fonte_consulta",
        ),
    )