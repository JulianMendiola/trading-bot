"""Motor del bot: un escaneo completo de los 5 instrumentos.

Por cada instrumento:
  1. Descarga velas del timeframe de su estrategia.
  2. Si hay posición abierta: revisa stop / take profit.
  3. Si no hay posición: evalúa la señal de entrada,
     pasa el filtro de correlación y dimensiona por ATR.
"""

import time
import traceback

import config
from bot import data, risk
from bot.portfolio import Portfolio
from bot.strategies import ESTRATEGIAS


def escanear(portfolio: Portfolio | None = None) -> Portfolio:
    pf = portfolio or Portfolio()
    precios_actuales: dict[str, float] = {}

    simbolos = list(config.INSTRUMENTOS)
    try:
        diarios = data.precios_diarios(simbolos)
    except Exception:
        diarios = None
        print("  Aviso: no se pudieron bajar precios diarios (filtro de correlación desactivado)")

    for simbolo, info in config.INSTRUMENTOS.items():
        nombre, nombre_estrategia = info["nombre"], info["estrategia"]
        funcion, params = ESTRATEGIAS[nombre_estrategia]
        try:
            df = data.obtener_ohlc(simbolo, params["intervalo"], params["periodo_datos"])
        except Exception as e:
            print(f"  {nombre}: error de datos — {e}")
            continue

        precio_actual = float(df["Close"].iloc[-1])
        precios_actuales[simbolo] = precio_actual

        pos = next((p for p in pf.posiciones if p["simbolo"] == simbolo), None)
        if pos:
            _gestionar_posicion(pf, pos, df)
            continue

        if len(pf.posiciones) >= config.MAX_POSICIONES:
            continue

        try:
            senal = funcion(df)
        except Exception:
            print(f"  {nombre}: error evaluando estrategia")
            traceback.print_exc()
            continue

        if not senal:
            continue

        if diarios is not None:
            conflicto = risk.correlacion_excesiva(simbolo, senal["direccion"], pf.posiciones, diarios)
            if conflicto:
                pf.registrar_evento(
                    f"SEÑAL OMITIDA {senal['direccion'].upper()} {nombre}: "
                    f"correlación alta con {conflicto}"
                )
                continue

        equity = pf.equity(precios_actuales)
        try:
            dimension = risk.calcular_posicion(equity, senal["precio"], senal["atr"], senal["direccion"])
        except ValueError as e:
            print(f"  {nombre}: {e}")
            continue
        pf.abrir(simbolo, nombre, nombre_estrategia, senal, dimension)

    pf.guardar(precios_actuales)
    return pf


def _gestionar_posicion(pf: Portfolio, pos: dict, df):
    """Revisa stop y take profit contra el rango de la última vela cerrada."""
    i = -2 if len(df) >= 2 else -1
    maximo = float(df["High"].iloc[i])
    minimo = float(df["Low"].iloc[i])

    if pos["direccion"] == "long":
        if minimo <= pos["stop"]:
            pf.cerrar(pos, pos["stop"], "stop loss")
        elif maximo >= pos["take_profit"]:
            pf.cerrar(pos, pos["take_profit"], "take profit")
    else:
        if maximo >= pos["stop"]:
            pf.cerrar(pos, pos["stop"], "stop loss")
        elif minimo <= pos["take_profit"]:
            pf.cerrar(pos, pos["take_profit"], "take profit")


def loop_en_vivo():
    print(f"Bot en vivo — escaneo cada {config.INTERVALO_LOOP // 60} minutos. Ctrl+C para frenar.")
    while True:
        print(f"\n=== Escaneo {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        try:
            pf = escanear()
            print(f"  Posiciones abiertas: {len(pf.posiciones)} | Capital: {pf.capital:,.2f} USD")
        except Exception:
            traceback.print_exc()
        time.sleep(config.INTERVALO_LOOP)
