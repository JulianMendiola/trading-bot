"""Gestión de riesgo: tamaño de posición por ATR, stops y filtro de correlación."""

import pandas as pd

import config


def calcular_posicion(capital: float, precio: float, atr: float, direccion: str) -> dict:
    """Dimensiona la posición arriesgando exactamente RIESGO_POR_TRADE del capital.

    El stop se coloca a ATR_MULT_STOP * ATR del precio de entrada; la cantidad
    de unidades se ajusta para que tocar el stop pierda el 1% del capital.
    """
    riesgo_usd = capital * config.RIESGO_POR_TRADE
    distancia_stop = config.ATR_MULT_STOP * atr
    if distancia_stop <= 0:
        raise ValueError("ATR inválido, no se puede dimensionar la posición")

    unidades = riesgo_usd / distancia_stop
    if direccion == "long":
        stop = precio - distancia_stop
        take_profit = precio + distancia_stop * config.RATIO_TAKE_PROFIT
    else:
        stop = precio + distancia_stop
        take_profit = precio - distancia_stop * config.RATIO_TAKE_PROFIT

    return {
        "unidades": unidades,
        "stop": stop,
        "take_profit": take_profit,
        "riesgo_usd": riesgo_usd,
    }


def correlacion_excesiva(
    simbolo: str,
    direccion: str,
    posiciones_abiertas: list[dict],
    precios_diarios: pd.DataFrame,
) -> str | None:
    """Devuelve el símbolo conflictivo si la señal duplicaría exposición.

    Compara retornos diarios del candidato contra cada posición abierta en la
    misma dirección; si |correlación| supera el umbral, la señal se descarta.
    """
    if simbolo not in precios_diarios.columns:
        return None
    retornos = precios_diarios.pct_change(fill_method=None).dropna(how="all")

    for pos in posiciones_abiertas:
        if pos["direccion"] != direccion:
            continue
        otro = pos["simbolo"]
        if otro == simbolo or otro not in retornos.columns:
            continue
        par = retornos[[simbolo, otro]].dropna()
        if len(par) < 10:
            continue
        corr = par[simbolo].corr(par[otro])
        if abs(corr) > config.CORRELACION_MAXIMA:
            return f"{otro} (corr {corr:.2f})"
    return None
