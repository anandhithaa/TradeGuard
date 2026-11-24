# TradeGuard — Low-Latency Trading Infrastructure Telemetry & Automated Incident Correlation Engine

**TradeGuard** is a Linux-native production monitoring, fault-injection, and root-cause correlation framework designed for high-frequency trading (HFT) and latency-sensitive distributed environments. It continuously tracks multi-process TCP trading pipelines alongside OS-level resource metrics, detects nanosecond-scale latency anomalies in real time, and automatically classifies whether an incident stems from application stalls or underlying host contention.

---

## Key Capabilities

* **Real-Time Multi-Process TCP Telemetry:** Simulates and monitors an end-to-end electronic trading pipeline—tracking heartbeat health, message round-trip latency (nanosecond precision), and socket responsiveness across isolated worker processes (`services.py`, `trading_sim.py`).
* **Linux Host & Process Resource Profiling:** Collects live OS-level metrics including per-process CPU utilization, resident memory footprint, thread states, and system load averages (`system_monitor.py`) to maintain continuous visibility into host health.
* **Automated Root-Cause Correlation Engine:** Cross-references application latency spikes against system-level resource anomalies (`correlator.py`) to immediately distinguish process-level execution freezes from hardware/CPU bottlenecks—reducing mean time to diagnosis (MTTD) during live production incidents.
* **Structured Incident Auditing & Alert Reporting:** Automatically generates timestamped, machine-readable post-mortem records (`logs/incidents.csv`) alongside verbose operational execution logs (`logs/tradeguard.log`) via `reporter.py`.
* **Production Automation & Cron Orchestration:** Managed via a hardened POSIX shell wrapper (`run_tradeguard.sh`) supporting automated background health checks, environment isolation, and scheduled execution (`logs/cron.log`).
* **Deterministic POSIX Fault Injection:** Validated under simulated production outages using kernel-level process suspension (`kill -STOP` / `kill -CONT`), verifying sub-second anomaly detection, automated incident escalation, and clean recovery tracking.

---

## System Architecture

```text
+-----------------------------------------------------------------------+
|                     TradeGuard Orchestrator (main.py)                 |
+-----------------------------------+-----------------------------------+
                                    |
          +-------------------------+-------------------------+
          v                                                   v
+-----------------------------+               +-------------------------------+
|  Trading Pipeline Telemetry |               |   Linux Host & Process Agent  |
|  (services.py / trading_sim)|               |      (system_monitor.py)      |
|  - Multi-process TCP sockets|               |  - Per-PID CPU / RSS memory   |
|  - Nanosecond RTT probes    |               |  - Process state & load stats |
+--------------+--------------+               +---------------+---------------+
               |                                              |
               +----------------------+-----------------------+
                                      v
                    +-----------------------------------+
                    |   Root-Cause Correlation Engine   |
                    |          (correlator.py)          |
                    |  - Threshold & anomaly detection  |
                    |  - App stall vs. host contention  |
                    +-----------------+-----------------+
                                      |
                                      v
                    +-----------------------------------+
                    |  Incident Reporter & Audit Logs   |
                    |           (reporter.py)           |
                    |  - logs/incidents.csv (structured)|
                    |  - logs/tradeguard.log (runtime)  |
                    +-----------------------------------+



**REPOSITORY STRUCTURE**

tradeguard/
├── main.py               # Central monitoring loop, CLI flags, and graceful signal handling
├── config.py             # Centralized latency thresholds, polling intervals, and port mappings
├── services.py           # TCP service definitions, socket health probes, and latency timers
├── trading_sim.py        # Multi-process order/market-data simulator for realistic load testing
├── system_monitor.py     # Linux process & system telemetry collector (CPU, memory, PID state)
├── correlator.py         # Real-time anomaly correlation logic for automated root-cause classification
├── reporter.py           # Structured CSV incident logger and operational console/file formatter
├── run_tradeguard.sh     # Bash automation script for environment setup, execution, and cron runs
└── logs/
    ├── incidents.csv     # Structured post-mortem incident ledger (timestamp, PID, latency, cause)
    ├── tradeguard.log    # Detailed runtime telemetry and state-transition audit trail
    └── cron.log          # Automated scheduled execution logs
