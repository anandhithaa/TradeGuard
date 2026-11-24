import socket
import json
import threading
import time
from system_monitor import check_system_health
from correlator import correlate_incidents
from reporter import report_incidents, log_message
import config

latest_metrics = {
    "feed_delay_ms": 0.0,
    "strategy_latency_ms": 0.0,
    "order_rejections": 0,
    "pids": {}
}
lock = threading.Lock()

def telemetry_listener():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 9003))
    srv.listen(10)
    while True:
        conn, _ = srv.accept()
        with conn:
            for line in conn.makefile():
                data = json.loads(line.strip())
                with lock:
                    svc = data.get("service")
                    if svc == "strategy":
                        latest_metrics["feed_delay_ms"] = data["feed_delay_ms"]
                        latest_metrics["strategy_latency_ms"] = data["strategy_latency_ms"]
                        latest_metrics["pids"]["Strategy"] = data["pid"]
                    elif svc == "gateway":
                        latest_metrics["order_rejections"] += data["rejected"]
                        latest_metrics["pids"]["Gateway"] = data["pid"]
                    elif svc == "feed_down":
                        latest_metrics["feed_delay_ms"] = 999.0

def main():
    threading.Thread(target=telemetry_listener, daemon=True).start()
    print("TradeGuard Live Monitor started (Press Ctrl+C to stop)...\n")
    active_issue = None

    try:
        while True:
            sys_metrics = check_system_health()
            with lock:
                trade_metrics = {
                    "feed_delay_ms": latest_metrics["feed_delay_ms"],
                    "strategy_latency_ms": latest_metrics["strategy_latency_ms"],
                    "order_rejections": latest_metrics["order_rejections"],
                    "feed_breach": latest_metrics["feed_delay_ms"] > config.FEED_DELAY_THRESHOLD,
                    "strategy_breach": latest_metrics["strategy_latency_ms"] > config.STRATEGY_LATENCY_THRESHOLD,
                    "gateway_breach": latest_metrics["order_rejections"] > config.ORDER_REJECTION_THRESHOLD,
                }
                pids = dict(latest_metrics["pids"])
                latest_metrics["order_rejections"] = 0  # Reset per-window rejection counter

            print(f"[HOST] CPU:{sys_metrics['cpu']}% RAM:{sys_metrics['ram']}% | "
                  f"[IPC] Feed:{trade_metrics['feed_delay_ms']}ms "
                  f"Strat:{trade_metrics['strategy_latency_ms']}ms "
                  f"Rej:{trade_metrics['order_rejections']} | PIDs:{pids}")

            incidents = correlate_incidents(sys_metrics, trade_metrics)
            if incidents:
                issue_key = incidents[0]["issue"]
                if issue_key != active_issue:  # Deduplicate ongoing alerts
                    report_incidents(incidents)
                    active_issue = issue_key
            else:
                if active_issue is not None:
                    print("RESOLVED: Pipeline latency and rejection rates returned to normal.\n")
                    log_message("INFO", f"RESOLVED: {active_issue}")
                    active_issue = None

            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down TradeGuard cleanly.")

if __name__ == "__main__":
    main()
