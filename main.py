"""TradingBot — paper trading multi-instrumento.

Uso:
  python main.py scan      Un escaneo: revisa posiciones y busca señales
  python main.py live      Loop continuo (escanea cada 15 min)
  python main.py report    Reporte diario por consola
  python main.py backtest  Prueba las estrategias sobre el histórico
  python main.py reset     Borra el estado y arranca de cero
"""

import os
import sys

import config


def reset():
    for archivo in (config.ARCHIVO_ESTADO, config.ARCHIVO_TRADES):
        if os.path.exists(archivo):
            os.remove(archivo)
            print(f"Borrado {archivo}")
    print(f"Cuenta reiniciada a {config.CAPITAL_INICIAL:,.0f} USD simulados.")


def main():
    comando = sys.argv[1] if len(sys.argv) > 1 else "scan"

    if comando == "scan":
        from bot.engine import escanear
        pf = escanear()
        print(f"\nEscaneo completo. Posiciones abiertas: {len(pf.posiciones)} | "
              f"Capital realizado: {pf.capital:,.2f} USD")
    elif comando == "live":
        from bot.engine import loop_en_vivo
        loop_en_vivo()
    elif comando == "report":
        from bot.report import reporte_diario
        reporte_diario()
    elif comando == "backtest":
        from bot.backtest import backtest_todos
        backtest_todos()
    elif comando == "reset":
        reset()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
