"""Backtest simple: reproduce cada estrategia sobre el histórico disponible.

No comparte estado con el paper trading; sirve para ver si las reglas
tienen sentido antes de dejar el bot corriendo.
"""

import config
from bot import data, risk
from bot.strategies import ESTRATEGIAS


def backtest_instrumento(simbolo: str) -> dict:
    info = config.INSTRUMENTOS[simbolo]
    funcion, params = ESTRATEGIAS[info["estrategia"]]
    df = data.obtener_ohlc(simbolo, params["intervalo"], params["periodo_datos"])

    capital = config.CAPITAL_INICIAL
    posicion = None
    trades = []
    minimo_velas = 60  # margen para que los indicadores se estabilicen

    for i in range(minimo_velas, len(df)):
        ventana = df.iloc[: i + 1]
        vela = df.iloc[i]

        if posicion:
            if posicion["direccion"] == "long":
                if vela["Low"] <= posicion["stop"]:
                    salida, motivo = posicion["stop"], "stop"
                elif vela["High"] >= posicion["take_profit"]:
                    salida, motivo = posicion["take_profit"], "take profit"
                else:
                    continue
            else:
                if vela["High"] >= posicion["stop"]:
                    salida, motivo = posicion["stop"], "stop"
                elif vela["Low"] <= posicion["take_profit"]:
                    salida, motivo = posicion["take_profit"], "take profit"
                else:
                    continue
            signo = 1 if posicion["direccion"] == "long" else -1
            pnl = signo * (salida - posicion["entrada"]) * posicion["unidades"]
            capital += pnl
            trades.append(pnl)
            posicion = None
            continue

        senal = funcion(ventana)
        if senal:
            try:
                dim = risk.calcular_posicion(capital, senal["precio"], senal["atr"], senal["direccion"])
            except ValueError:
                continue
            posicion = {
                "direccion": senal["direccion"],
                "entrada": senal["precio"],
                "unidades": dim["unidades"],
                "stop": dim["stop"],
                "take_profit": dim["take_profit"],
            }

    ganadores = [t for t in trades if t > 0]
    return {
        "nombre": info["nombre"],
        "estrategia": info["estrategia"],
        "velas": len(df),
        "trades": len(trades),
        "ganadores": len(ganadores),
        "pnl": sum(trades),
        "capital_final": capital,
    }


def backtest_todos():
    print(f"\nBacktest sobre el histórico disponible (capital inicial {config.CAPITAL_INICIAL:,.0f} USD por instrumento)\n")
    print(f"{'Instrumento':12} {'Estrategia':18} {'Velas':>6} {'Trades':>7} {'Ganados':>8} {'PnL USD':>10}")
    print("-" * 66)
    for simbolo in config.INSTRUMENTOS:
        try:
            r = backtest_instrumento(simbolo)
        except Exception as e:
            print(f"{config.INSTRUMENTOS[simbolo]['nombre']:12} error: {e}")
            continue
        tasa = f"{r['ganadores']}/{r['trades']}" if r["trades"] else "-"
        print(f"{r['nombre']:12} {r['estrategia']:18} {r['velas']:>6} {r['trades']:>7} "
              f"{tasa:>8} {r['pnl']:>+10.2f}")
    print("\nOjo: el histórico intradía de Yahoo es corto (días/semanas); es una prueba de sanidad, no una validación seria.")
