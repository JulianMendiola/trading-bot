"""Descarga de datos de mercado vía Yahoo Finance (gratis, sin API key)."""

import pandas as pd
import yfinance as yf


def obtener_ohlc(simbolo: str, intervalo: str, periodo: str) -> pd.DataFrame:
    """Descarga velas OHLC. Para 4h descarga 1h y resamplea."""
    intervalo_descarga = "1h" if intervalo == "4h" else intervalo
    df = yf.download(
        simbolo,
        interval=intervalo_descarga,
        period=periodo,
        progress=False,
        auto_adjust=True,
        multi_level_index=False,
    )
    if df is None or df.empty:
        raise RuntimeError(f"Sin datos para {simbolo} ({intervalo})")

    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

    if intervalo == "4h":
        df = (
            df.resample("4h")
            .agg({"Open": "first", "High": "max", "Low": "min",
                  "Close": "last", "Volume": "sum"})
            .dropna()
        )
    return df


def precios_diarios(simbolos: list[str], periodo: str = "60d") -> pd.DataFrame:
    """Cierres diarios de varios símbolos, para el filtro de correlación."""
    df = yf.download(
        simbolos, interval="1d", period=periodo,
        progress=False, auto_adjust=True,
    )["Close"]
    if isinstance(df, pd.Series):
        df = df.to_frame(simbolos[0])
    return df.dropna(how="all")
