import socket
import time
import json
import os
import sys

FEED_PORT = 9001
STRATEGY_PORT = 9002
TELEMETRY_PORT = 9003

def send_telemetry(payload):
    try:
        with socket.create_connection(("127.0.0.1", TELEMETRY_PORT), timeout=0.2) as s:
            s.sendall((json.dumps(payload) + "\n").encode())
    except OSError:
        pass

def run_order_gateway():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", STRATEGY_PORT))
    srv.listen(5)
    print(f"[OrderGateway] PID={os.getpid()} listening on :{STRATEGY_PORT}", flush=True)

    while True:
        conn, _ = srv.accept()
        with conn:
            data = conn.recv(1024).decode().strip()
            if not data:
                continue
            msg = json.loads(data)
            now_ns = time.perf_counter_ns()
            end_to_end_ms = (now_ns - msg["tick_ns"]) / 1_000_000.0
            rejected = 1 if end_to_end_ms > 50.0 else 0
            send_telemetry({
                "service": "gateway",
                "pid": os.getpid(),
                "e2e_ms": round(end_to_end_ms, 2),
                "rejected": rejected
            })

def run_strategy_engine():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", FEED_PORT))
    srv.listen(5)
    print(f"[StrategyEngine] PID={os.getpid()} listening on :{FEED_PORT}", flush=True)

    while True:
        conn, _ = srv.accept()
        with conn:
            data = conn.recv(1024).decode().strip()
            if not data:
                continue
            msg = json.loads(data)
            recv_ns = time.perf_counter_ns()
            feed_delay_ms = (recv_ns - msg["tick_ns"]) / 1_000_000.0

            _ = sum(i * i for i in range(5000))
            proc_ms = (time.perf_counter_ns() - recv_ns) / 1_000_000.0

            send_telemetry({
                "service": "strategy",
                "pid": os.getpid(),
                "feed_delay_ms": round(feed_delay_ms, 2),
                "strategy_latency_ms": round(proc_ms, 2)
            })

            try:
                with socket.create_connection(("127.0.0.1", STRATEGY_PORT), timeout=0.5) as gw:
                    gw.sendall((json.dumps(msg) + "\n").encode())
            except OSError:
                send_telemetry({"service": "gateway", "pid": -1, "e2e_ms": 999.0, "rejected": 1})

def run_market_feed():
    print(f"[MarketFeed] PID={os.getpid()} streaming ticks every 0.5s...", flush=True)
    seq = 0
    while True:
        seq += 1
        tick = {"seq": seq, "symbol": "NIFTY", "price": 24500.5, "tick_ns": time.perf_counter_ns()}
        try:
            with socket.create_connection(("127.0.0.1", FEED_PORT), timeout=0.5) as s:
                s.sendall((json.dumps(tick) + "\n").encode())
        except OSError:
            send_telemetry({"service": "feed_down", "pid": os.getpid()})
        time.sleep(0.5)

if __name__ == "__main__":
    role = sys.argv[1]
    if role == "gateway":
        run_order_gateway()
    elif role == "strategy":
        run_strategy_engine()
    elif role == "feed":
        run_market_feed()
