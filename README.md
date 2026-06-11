# TradingBot 🤖📈

Bot de trading **paper trading** (dinero simulado, datos reales) que monitorea 5 instrumentos con 3 estrategias, inspirado en el video de @adiix_official.

> ⚠️ Esto es una simulación educativa. No opera con dinero real y nada de esto es consejo financiero.

## Qué hace

| Instrumento | Estrategia | Timeframe |
|---|---|---|
| S&P 500 (ES=F) | Reversión a la media (Bollinger + RSI) | 15 min |
| Nasdaq (NQ=F) | Reversión a la media (Bollinger + RSI) | 15 min |
| Bitcoin (BTC-USD) | Ruptura de momentum (canal Donchian 20) | 1 hora |
| Oro (GC=F) | Seguimiento de tendencia (cruce EMA 20/50) | 4 horas |
| Petróleo (CL=F) | Seguimiento de tendencia (cruce EMA 20/50) | 4 horas |

**Gestión de riesgo:**
- Tamaño de posición por ATR: cada trade arriesga exactamente el **1% del capital**
- Stop loss duro a 2×ATR, take profit a 2× el riesgo
- **Filtro de correlación**: no abre una posición si correlaciona >0.7 con otra abierta en la misma dirección
- Máximo 5 posiciones simultáneas

Datos de Yahoo Finance (gratis, sin API key).

## Instalación

```
pip install -r requirements.txt
```

## Uso

```
python main.py scan      # un escaneo: revisa posiciones y busca señales
python main.py live      # loop continuo, escanea cada 15 minutos
python main.py report    # reporte diario por consola
python main.py backtest  # prueba las estrategias sobre el histórico
python main.py reset     # reinicia la cuenta simulada a 10.000 USD
```

## Modo 24/7 (GitHub Actions)

El workflow [.github/workflows/bot.yml](.github/workflows/bot.yml) ejecuta `python main.py scan` cada 15 minutos en GitHub Actions y commitea el estado (`data/`) al repo. El bot corre aunque tu compu esté apagada. También se puede disparar a mano desde la pestaña **Actions** del repo.

> Si corrés el bot local (`live`), pausá el workflow antes para no pisar el estado.

## Dashboard

```
python dashboard.py
```

Abrí http://localhost:8800 — equity, posiciones abiertas, historial de trades y actividad del bot, con refresco automático cada 30 s. Hace `git pull` cada 3 minutos para traer lo que el bot hizo en la nube. `iniciar_bot.bat` abre todo con doble click.

## Configuración

Todo en [config.py](config.py): capital inicial, % de riesgo, instrumentos, parámetros de cada estrategia.
