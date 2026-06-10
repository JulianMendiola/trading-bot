"""Reporte diario por consola: equity, posiciones abiertas y trades cerrados."""

import csv
import json
import os
from datetime import datetime, timezone

import config


def reporte_diario():
    if not os.path.exists(config.ARCHIVO_ESTADO):
        print("Todavía no hay estado. Corré primero: python main.py scan")
        return

    with open(config.ARCHIVO_ESTADO, encoding="utf-8") as f:
        estado = json.load(f)

    hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    capital = estado["capital"]
    precios = estado.get("precios", {})

    print(f"\n========== REPORTE DIARIO — {hoy} ==========")
    rendimiento = (capital / config.CAPITAL_INICIAL - 1) * 100
    print(f"Capital realizado: {capital:,.2f} USD ({rendimiento:+.2f}% desde el inicio)")

    print(f"\nPosiciones abiertas: {len(estado['posiciones'])}")
    for p in estado["posiciones"]:
        precio = precios.get(p["simbolo"])
        flotante = ""
        if precio:
            signo = 1 if p["direccion"] == "long" else -1
            pnl = signo * (precio - p["entrada"]) * p["unidades"]
            flotante = f" | PnL flotante {pnl:+.2f} USD"
        print(f"  {p['direccion'].upper():5} {p['nombre']:10} entrada {p['entrada']:.2f} "
              f"stop {p['stop']:.2f} TP {p['take_profit']:.2f}{flotante}")

    trades_hoy = []
    if os.path.exists(config.ARCHIVO_TRADES):
        with open(config.ARCHIVO_TRADES, encoding="utf-8") as f:
            trades_hoy = [t for t in csv.DictReader(f) if t["cerrada"].startswith(hoy)]

    print(f"\nTrades cerrados hoy: {len(trades_hoy)}")
    total = 0.0
    for t in trades_hoy:
        pnl = float(t["pnl_usd"])
        total += pnl
        print(f"  {t['direccion'].upper():5} {t['nombre']:10} {t['entrada']} → {t['salida']} "
              f"= {pnl:+.2f} USD ({t['motivo_cierre']})")
    if trades_hoy:
        print(f"  PnL del día: {total:+.2f} USD")
    print("=" * 47)
