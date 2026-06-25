from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from app.services.coleta_service import ColetaService
from app.services.vaga_service import VagaService
import hmac
from flask import current_app


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return redirect(url_for("main.pagina_vagas"))


@main_bp.get("/vagas")
def pagina_vagas():
    service = VagaService()

    filtros = {
        "busca": request.args.get("busca"),
        "empresa": request.args.get("empresa"),
        "tecnologia": request.args.get("tecnologia"),
        "localizacao": request.args.get("localizacao"),
        "modalidade": request.args.getlist("modalidade"),
        "nivel": request.args.getlist("nivel"),
        "periodo": request.args.get("periodo"),
    }

    page = request.args.get(
        "page",
        default=1,
        type=int,
    )

    page = max(page, 1)

    paginacao = service.listar_vagas_paginadas(
        filtros=filtros,
        page=page,
        per_page=12,
    )

    return render_template(
        "vagas.html",
        vagas=paginacao.items,
        paginacao=paginacao,
        filtros=filtros,
    )


@main_bp.get("/api/vagas")
def listar_vagas():
    service = VagaService()

    filtros = {
        "busca": request.args.get("busca"),
        "empresa": request.args.get("empresa"),
        "tecnologia": request.args.get("tecnologia"),
        "localizacao": request.args.get("localizacao"),
        "modalidade": request.args.getlist("modalidade"),
        "nivel": request.args.getlist("nivel"),
        "periodo": request.args.get("periodo"),
    }

    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)

    page = max(page, 1)
    per_page = min(max(per_page, 1), 100)

    paginacao = service.listar_vagas_paginadas(
        filtros=filtros,
        page=page,
        per_page=per_page,
    )

    return jsonify({
        "items": [
            vaga.to_dict()
            for vaga in paginacao.items
        ],
        "pagination": {
            "page": paginacao.page,
            "per_page": paginacao.per_page,
            "total": paginacao.total,
            "pages": paginacao.pages,
            "has_next": paginacao.has_next,
            "has_prev": paginacao.has_prev,
        },
    })


@main_bp.get("/api/vagas/<int:vaga_id>")
def buscar_vaga(vaga_id):
    service = VagaService()

    vaga = service.repository.buscar_por_id(vaga_id)

    if not vaga:
        return jsonify({"erro": "Vaga não encontrada."}), 404

    return jsonify(vaga.to_dict())


@main_bp.post("/api/vagas")
def criar_vaga():
    service = VagaService()
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Corpo JSON é obrigatório."}), 400

    try:
        vaga, criada = service.criar_vaga(dados)
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

    status_code = 201 if criada else 200

    return jsonify({
        "criada": criada,
        "vaga": vaga.to_dict(),
    }), status_code


@main_bp.post("/api/coletar")
def executar_coleta():
    token_recebido = request.headers.get(
        "Authorization",
    )

    segredo = current_app.config.get("CRON_SECRET")

    token_esperado = f"Bearer {segredo}"

    if (
        not segredo
        or not hmac.compare_digest(
            token_recebido or "",
            token_esperado,
        )
    ):
        return jsonify({
            "erro": "Não autorizado."
        }), 401

    service = ColetaService()
    resultado = service.executar_coleta()

    return jsonify(resultado)
