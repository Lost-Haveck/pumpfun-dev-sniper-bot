# Pump.fun Dev Sniper Bot (Python)

A Python automation that listens to **Pump.fun** account trade events via WebSocket and automatically:
1) Buys a detected mint using your wallet/public key and configured slippage/amount  
2) Waits a short period  
3) Sells 100% back out

All settings are configurable via `.env`. Intended for educational/demo purposes.

---

## ⚠️ Disclaimer
This code is for **educational purposes only**. Trading tokens is risky. Use at your own risk. Keep private keys and RPC URLs secure and never commit secrets to GitHub.

---

## Features
- WebSocket subscription to `subscribeAccountTrade`
- Auto buy → delay → sell flow
- Configurable: buy amount (SOL), slippage, priority fee, pool
- .env-based configuration and simple logging
- Auto-reconnect loop for the websocket

---

## Requirements
- Python 3.9+
- A Solana RPC endpoint
- A funded wallet (if you intend to live trade)

Install deps:
```bash
pip install -r requirements.txt
