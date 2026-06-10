"""Cartera simulada (paper trading) con persistencia en JSON y CSV de trades."""

import csv
import json
import os
from datetime import datetime, timezone

import config


def _ahora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


class Portfolio:
    def __init__(self):
        self.capital = config.CAPITAL_INICIAL
        self.posiciones: list[dict] = []
        self.historial_equity: list[dict] = []
        self.eventos: list[dict] = []
        self.cargar()

    # ---------- persistencia ----------

    def cargar(self):
        if os.path.exists(config.ARCHIVO_ESTADO):
            with open(config.ARCHIVO_ESTADO, encoding="utf-8") as f:
                estado = json.load(f)
            self.capital = estado["capital"]
            self.posiciones = estado["posiciones"]
            self.historial_equity = estado.get("historial_equity", [])
            self.eventos = estado.get("eventos", [])

    def guardar(self, precios_actuales: dict | None = None):
        equity = self.equity(precios_actuales or {})
        self.historial_equity.append({"fecha": _ahora(), "equity": round(equity, 2)})
        self.historial_equity = self.historial_equity[-2000:]
        self.eventos = self.eventos[-200:]
        estado = {
            "capital": self.capital,
            "posiciones": self.posiciones,
            "historial_equity": self.historial_equity,
            "eventos": self.eventos,
            "precios": precios_actuales or {},
            "actualizado": _ahora(),
        }
        os.makedirs(os.path.dirname(config.ARCHIVO_ESTADO), exist_ok=True)
        with open(config.ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)

    def registrar_evento(self, texto: str):
        self.eventos.append({"fecha": _ahora(), "texto": texto})
        print(f"  [{_ahora()}] {texto}")

    # ---------- operaciones ----------

    def abrir(self, simbolo: str, nombre: str, estrategia: str, senal: dict, dimension: dict):
        pos = {
            "simbolo": simbolo,
            "nombre": nombre,
            "estrategia": estrategia,
            "direccion": senal["direccion"],
            "entrada": senal["precio"],
            "unidades": dimension["unidades"],
            "stop": dimension["stop"],
            "take_profit": dimension["take_profit"],
            "riesgo_usd": dimension["riesgo_usd"],
            "motivo": senal["motivo"],
            "abierta": _ahora(),
        }
        self.posiciones.append(pos)
        self.registrar_evento(
            f"ABIERTA {senal['direccion'].upper()} {nombre} @ {senal['precio']:.2f} "
            f"(stop {dimension['stop']:.2f}, TP {dimension['take_profit']:.2f}) — {senal['motivo']}"
        )

    def cerrar(self, pos: dict, precio_salida: float, motivo: str):
        signo = 1 if pos["direccion"] == "long" else -1
        pnl = signo * (precio_salida - pos["entrada"]) * pos["unidades"]
        self.capital += pnl
        self.posiciones.remove(pos)
        self._registrar_trade(pos, precio_salida, pnl, motivo)
        self.registrar_evento(
            f"CERRADA {pos['direccion'].upper()} {pos['nombre']} @ {precio_salida:.2f} "
            f"→ PnL {pnl:+.2f} USD ({motivo})"
        )

    def _registrar_trade(self, pos: dict, salida: float, pnl: float, motivo: str):
        existe = os.path.exists(config.ARCHIVO_TRADES)
        os.makedirs(os.path.dirname(config.ARCHIVO_TRADES), exist_ok=True)
        with open(config.ARCHIVO_TRADES, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if not existe:
                w.writerow(["abierta", "cerrada", "simbolo", "nombre", "estrategia",
                            "direccion", "entrada", "salida", "unidades", "pnl_usd", "motivo_cierre"])
            w.writerow([pos["abierta"], _ahora(), pos["simbolo"], pos["nombre"],
                        pos["estrategia"], pos["direccion"], f"{pos['entrada']:.4f}",
                        f"{salida:.4f}", f"{pos['unidades']:.6f}", f"{pnl:.2f}", motivo])

    # ---------- métricas ----------

    def equity(self, precios_actuales: dict) -> float:
        flotante = 0.0
        for pos in self.posiciones:
            precio = precios_actuales.get(pos["simbolo"])
            if precio is None:
                continue
            signo = 1 if pos["direccion"] == "long" else -1
            flotante += signo * (precio - pos["entrada"]) * pos["unidades"]
        return self.capital + flotante

    def tiene_posicion(self, simbolo: str) -> bool:
        return any(p["simbolo"] == simbolo for p in self.posiciones)
