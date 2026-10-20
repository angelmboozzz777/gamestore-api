"""Arranca la API con un solo comando:

    python -m app

Es lo mismo que
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pero sin el mensaje "Uvicorn running on http://0.0.0.0:8000".
Esa direccion no se puede abrir en el navegador (da ERR_ADDRESS_INVALID):
0.0.0.0 solo significa "escuchar en todas las redes", para que el
emulador y el celular tambien puedan conectarse. En su lugar se muestran
las direcciones que si funcionan (localhost, 10.0.2.2 y la IP de la PC).
"""
import copy
import logging
import sys

import uvicorn
from uvicorn.config import LOGGING_CONFIG

PUERTO = 8000


class OcultarDireccion0000(logging.Filter):
    """Quita el aviso de uvicorn que muestra http://0.0.0.0:..."""

    def filter(self, record: logging.LogRecord) -> bool:
        return not str(record.msg).startswith("Uvicorn running on")


def configuracion_de_logs() -> dict:
    config = copy.deepcopy(LOGGING_CONFIG)
    config["filters"] = {"ocultar_0000": {"()": "app.__main__.OcultarDireccion0000"}}
    config["handlers"]["default"]["filters"] = ["ocultar_0000"]
    return config


def main() -> None:
    # Permite cambiar el puerto: python -m app 8001
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else PUERTO

    # main.py lee el puerto de sys.argv para mostrar las direcciones.
    sys.argv = [sys.argv[0], "--port", str(puerto)]

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=puerto,
        reload=True,
        log_config=configuracion_de_logs(),
    )


if __name__ == "__main__":
    main()
