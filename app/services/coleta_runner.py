import threading

from flask import Flask

from app.services.coleta_service import ColetaService


_lock_coleta = threading.Lock()


def coleta_em_andamento():
    return _lock_coleta.locked()


def iniciar_coleta(app: Flask):
    if not _lock_coleta.acquire(blocking=False):
        return False

    thread = threading.Thread(
        target=_executar_coleta,
        args=(app,),
        daemon=True,
    )
    thread.start()

    return True


def _executar_coleta(app: Flask):
    try:
        with app.app_context():
            resultado = ColetaService().executar_coleta()
            app.logger.info(
                "Coleta concluída: %s",
                resultado,
            )
    except Exception:
        app.logger.exception(
            "Erro durante coleta em segundo plano."
        )
    finally:
        _lock_coleta.release()
