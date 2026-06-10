"""Configuración del bot de trading (paper trading)."""

# Capital inicial simulado (USD)
CAPITAL_INICIAL = 10_000.0

# Riesgo máximo por operación: 1% del capital, sin excepciones
RIESGO_POR_TRADE = 0.01

# Stop de pérdida: distancia en múltiplos de ATR(14)
ATR_MULT_STOP = 2.0

# Take profit en múltiplos del riesgo (2 = relación 1:2)
RATIO_TAKE_PROFIT = 2.0

# Filtro de correlación: si un activo correlaciona más que esto
# con una posición abierta en la misma dirección, se omite la señal
CORRELACION_MAXIMA = 0.7

# Máximo de posiciones abiertas a la vez
MAX_POSICIONES = 5

# Instrumentos y estrategia asignada
# estrategia: mean_reversion (15m) | momentum_breakout (1h) | trend_following (4h)
INSTRUMENTOS = {
    "ES=F":    {"nombre": "S&P 500",  "estrategia": "mean_reversion"},
    "NQ=F":    {"nombre": "Nasdaq",   "estrategia": "mean_reversion"},
    "BTC-USD": {"nombre": "Bitcoin",  "estrategia": "momentum_breakout"},
    "GC=F":    {"nombre": "Oro",      "estrategia": "trend_following"},
    "CL=F":    {"nombre": "Petróleo", "estrategia": "trend_following"},
}

# Parámetros por estrategia
MEAN_REVERSION = {
    "intervalo": "15m",
    "periodo_datos": "5d",
    "bb_periodo": 20,
    "bb_desvios": 2.0,
    "rsi_periodo": 14,
    "rsi_sobreventa": 30,
    "rsi_sobrecompra": 70,
}

MOMENTUM_BREAKOUT = {
    "intervalo": "1h",
    "periodo_datos": "30d",
    "donchian_periodo": 20,
}

TREND_FOLLOWING = {
    "intervalo": "4h",  # se resamplea desde 1h
    "periodo_datos": "60d",
    "ema_rapida": 20,
    "ema_lenta": 50,
}

# Archivos de estado
ARCHIVO_ESTADO = "data/estado.json"
ARCHIVO_TRADES = "data/trades.csv"

# Intervalo del loop en vivo (segundos)
INTERVALO_LOOP = 15 * 60
