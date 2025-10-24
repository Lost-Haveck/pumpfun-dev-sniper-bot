import json
import time
import threading
import requests
import os
from dotenv import load_dotenv
from websocket import WebSocketApp

# === Global Config (defaults) ===
BUY_AMOUNT_SOL = 0.0005
SLIPPAGE = 25
PRIORITY_FEE_SOL = 0.00005
POOL = "pump"

# Loaded from .env
RPC_ENDPOINT = None
WALLET_PUBLIC_KEY = None
WALLET_PRIVATE_KEY = None  # (not used here, but loaded for future signing)


def load_env():
    """Load environment variables from .env"""
    global RPC_ENDPOINT, WALLET_PUBLIC_KEY, WALLET_PRIVATE_KEY
    load_dotenv()
    RPC_ENDPOINT = os.getenv("rpc_endpoint_chainstack")
    WALLET_PUBLIC_KEY = os.getenv("wallet_public_key")
    WALLET_PRIVATE_KEY = os.getenv("wallet_private_key")
    if not (RPC_ENDPOINT and WALLET_PUBLIC_KEY and WALLET_PRIVATE_KEY):
        raise RuntimeError("Missing one or more required env vars")


def send_trade_request(url: str, data: dict) -> str:
    """Send POST trade request to PumpPortal"""
    try:
        resp = requests.post(url, json=data)
        if resp.status_code != 200:
            return f"HTTP error: {resp.status_code}"
        result = resp.json()
        return str(result.get("result", "no result in response"))
    except Exception as e:
        return f"Request failed: {e}"


def bot_trading_logic(mint_address: str):
    """Buy then sell logic for a given mint"""
    print(f"[+] Processing mint address: {mint_address}")

    # --- BUY ---
    buy_data = {
        "publicKey": WALLET_PUBLIC_KEY,
        "action": "buy",
        "mint": mint_address,
        "amount": str(BUY_AMOUNT_SOL),
        "denominatedInSol": "true",
        "slippage": SLIPPAGE,
        "priorityFee": str(PRIORITY_FEE_SOL),
        "pool": POOL,
    }
    buy_resp = send_trade_request("https://pumpportal.fun/api/trade-local", buy_data)
    print(f"[BUY] Transaction Sent: {buy_resp}")

    # --- Wait before selling ---
    time.sleep(10)

    # --- SELL ---
    sell_data = {
        "publicKey": WALLET_PUBLIC_KEY,
        "action": "sell",
        "mint": mint_address,
        "amount": "100%",
        "denominatedInSol": "false",
        "slippage": SLIPPAGE,
        "priorityFee": str(PRIORITY_FEE_SOL),
        "pool": POOL,
    }
    sell_resp = send_trade_request("https://pumpportal.fun/api/trade-local", sell_data)
    print(f"[SELL] Transaction Sent: {sell_resp}")


def on_open(ws: WebSocketApp):
    """Subscribe to account trades for chosen wallets"""
    payload = {
        "method": "subscribeAccountTrade",
        "keys": [
            # TODO: Replace with your own list of wallets to track
            "HV1KXxWFaSeriyFvXyx48FqG9BoFbfinB8njCJonqP7K"
        ],
    }
    ws.send(json.dumps(payload))
    print("[+] Subscribed to account trades.")


def on_message(ws: WebSocketApp, message: str):
    """Handle incoming websocket messages"""
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        return

    mint = data.get("mint")
    if mint:
        print(f"[WS] Received new token: {mint}")
        # Run trading logic in a background thread (non-blocking)
        threading.Thread(target=bot_trading_logic, args=(mint,), daemon=True).start()


def on_error(ws: WebSocketApp, error):
    print(f"[!] WebSocket error: {error}")


def on_close(ws: WebSocketApp, code, msg):
    print(f"[!] WebSocket closed: code={code}, msg={msg}")


def websocket_connect():
    """Persistent WebSocket connection with auto-reconnect"""
    uri = "wss://pumpportal.fun/api/data"
    while True:
        ws = WebSocketApp(
            uri,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        try:
            ws.run_forever(ping_interval=25, ping_timeout=10)
        except KeyboardInterrupt:
            print("[x] Stopping bot.")
            return
        except Exception as e:
            print(f"[!] Fatal error: {e}")
        print("[~] Reconnecting in 5s...")
        time.sleep(5)


def main():
    load_env()
    print("[+] Environment loaded. Starting bot…")
    websocket_connect()


if __name__ == "__main__":
    main()
