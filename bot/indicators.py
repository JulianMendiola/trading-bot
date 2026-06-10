"""Indicadores técnicos calculados sobre DataFrames de OHLC."""

import pandas as pd


def ema(series: pd.Series, periodo: int) -> pd.Series:
    return series.ewm(span=periodo, adjust=False).mean()


def rsi(series: pd.Series, periodo: int = 14) -> pd.Series:
    delta = series.diff()
    ganancia = delta.clip(lower=0).ewm(alpha=1 / periodo, adjust=False).mean()
    perdida = (-delta.clip(upper=0)).ewm(alpha=1 / periodo, adjust=False).mean()
    rs = ganancia / perdida.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


def atr(df: pd.DataFrame, periodo: int = 14) -> pd.Series:
    """Average True Range. Requiere columnas High, Low, Close."""
    h, l, c_prev = df["High"], df["Low"], df["Close"].shift(1)
    tr = pd.concat([h - l, (h - c_prev).abs(), (l - c_prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / periodo, adjust=False).mean()


def bollinger(series: pd.Series, periodo: int = 20, desvios: float = 2.0):
    """Devuelve (banda_inferior, media, banda_superior)."""
    media = series.rolling(periodo).mean()
    std = series.rolling(periodo).std()
    return media - desvios * std, media, media + desvios * std


def donchian(df: pd.DataFrame, periodo: int = 20):
    """Canal de Donchian sobre las velas ANTERIORES (excluye la actual).

    Devuelve (techo, piso): máximos y mínimos de las últimas `periodo` velas.
    """
    techo = df["High"].rolling(periodo).max().shift(1)
    piso = df["Low"].rolling(periodo).min().shift(1)
    return techo, piso
