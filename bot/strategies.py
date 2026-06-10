"""Las tres estrategias del bot.

Cada estrategia recibe un DataFrame OHLC y devuelve un dict señal o None:
  {"direccion": "long"|"short", "motivo": str, "atr": float, "precio": float}
La señal se evalúa sobre la ÚLTIMA VELA CERRADA (iloc[-2]) para no operar
con una vela todavía en formación.
"""

import pandas as pd

import config
from bot import indicators as ind


def _vela_cerrada(df: pd.DataFrame) -> int:
    return -2 if len(df) >= 2 else -1


def mean_reversion(df: pd.DataFrame) -> dict | None:
    """Reversión a la media en 15m: Bollinger + RSI (S&P 500 / Nasdaq)."""
    p = config.MEAN_REVERSION
    inf, media, sup = ind.bollinger(df["Close"], p["bb_periodo"], p["bb_desvios"])
    rsi = ind.rsi(df["Close"], p["rsi_periodo"])
    atr = ind.atr(df)
    i = _vela_cerrada(df)
    cierre = float(df["Close"].iloc[i])

    if cierre < float(inf.iloc[i]) and float(rsi.iloc[i]) < p["rsi_sobreventa"]:
        return {"direccion": "long", "atr": float(atr.iloc[i]), "precio": cierre,
                "motivo": f"Cierre bajo banda inferior, RSI {rsi.iloc[i]:.0f}"}
    if cierre > float(sup.iloc[i]) and float(rsi.iloc[i]) > p["rsi_sobrecompra"]:
        return {"direccion": "short", "atr": float(atr.iloc[i]), "precio": cierre,
                "motivo": f"Cierre sobre banda superior, RSI {rsi.iloc[i]:.0f}"}
    return None


def momentum_breakout(df: pd.DataFrame) -> dict | None:
    """Ruptura de canal Donchian en 1h (Bitcoin)."""
    p = config.MOMENTUM_BREAKOUT
    techo, piso = ind.donchian(df, p["donchian_periodo"])
    atr = ind.atr(df)
    i = _vela_cerrada(df)
    cierre = float(df["Close"].iloc[i])

    if cierre > float(techo.iloc[i]):
        return {"direccion": "long", "atr": float(atr.iloc[i]), "precio": cierre,
                "motivo": f"Ruptura del máximo de {p['donchian_periodo']} velas"}
    if cierre < float(piso.iloc[i]):
        return {"direccion": "short", "atr": float(atr.iloc[i]), "precio": cierre,
                "motivo": f"Ruptura del mínimo de {p['donchian_periodo']} velas"}
    return None


def trend_following(df: pd.DataFrame) -> dict | None:
    """Seguimiento de tendencia en 4h: cruce de EMAs (Oro / Petróleo).

    Señal solo cuando el cruce ocurre en la última vela cerrada,
    para no entrar tarde a una tendencia ya extendida.
    """
    p = config.TREND_FOLLOWING
    rapida = ind.ema(df["Close"], p["ema_rapida"])
    lenta = ind.ema(df["Close"], p["ema_lenta"])
    atr = ind.atr(df)
    i = _vela_cerrada(df)
    cierre = float(df["Close"].iloc[i])

    cruce_alcista = rapida.iloc[i] > lenta.iloc[i] and rapida.iloc[i - 1] <= lenta.iloc[i - 1]
    cruce_bajista = rapida.iloc[i] < lenta.iloc[i] and rapida.iloc[i - 1] >= lenta.iloc[i - 1]

    if cruce_alcista:
        return {"direccion": "long", "atr": float(atr.iloc[i]), "precio": cierre,
                "motivo": f"EMA{p['ema_rapida']} cruzó sobre EMA{p['ema_lenta']}"}
    if cruce_bajista:
        return {"direccion": "short", "atr": float(atr.iloc[i]), "precio": cierre,
                "motivo": f"EMA{p['ema_rapida']} cruzó bajo EMA{p['ema_lenta']}"}
    return None


ESTRATEGIAS = {
    "mean_reversion": (mean_reversion, config.MEAN_REVERSION),
    "momentum_breakout": (momentum_breakout, config.MOMENTUM_BREAKOUT),
    "trend_following": (trend_following, config.TREND_FOLLOWING),
}
