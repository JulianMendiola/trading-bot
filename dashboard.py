"""Dashboard web del bot. Corre con: python dashboard.py  →  http://localhost:8800

Sirve dashboard.html y expone /api/estado y /api/trades leyendo los archivos
que escribe el bot. No necesita dependencias extra.
"""

import csv
import json
import os
import subprocess
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

import config

PUERTO = int(os.environ.get("PORT", 8800))
CARPETA = os.path.dirname(os.path.abspath(__file__))


def sincronizar_con_github():
    """El bot corre en GitHub Actions y commitea su estado al repo;
    acá hacemos git pull cada 3 minutos para que el dashboard lo refleje."""
    while True:
        try:
            r = subprocess.run(
                ["git", "pull", "--ff-only"],
                cwd=CARPETA, capture_output=True, text=True, timeout=60,
            )
            if r.returncode == 0 and "Already up to date" not in r.stdout:
                print(f"  Estado sincronizado desde GitHub")
        except Exception:
            pass
        time.sleep(180)


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/estado"):
            self._json(self._estado())
        elif self.path.startswith("/api/trades"):
            self._json(self._trades())
        elif self.path in ("/", "/index.html"):
            self.path = "/dashboard.html"
            super().do_GET()
        else:
            super().do_GET()

    def _estado(self):
        if not os.path.exists(config.ARCHIVO_ESTADO):
            return {"capital": config.CAPITAL_INICIAL, "posiciones": [],
                    "historial_equity": [], "eventos": [], "precios": {},
                    "actualizado": None}
        with open(config.ARCHIVO_ESTADO, encoding="utf-8") as f:
            return json.load(f)

    def _trades(self):
        if not os.path.exists(config.ARCHIVO_TRADES):
            return []
        with open(config.ARCHIVO_TRADES, encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def _json(self, datos):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, *args):
        pass  # silenciar el log por request


if __name__ == "__main__":
    os.chdir(CARPETA)
    threading.Thread(target=sincronizar_con_github, daemon=True).start()
    print(f"Dashboard en http://localhost:{PUERTO} (sincroniza con GitHub cada 3 min)")
    HTTPServer(("127.0.0.1", PUERTO), Handler).serve_forever()
