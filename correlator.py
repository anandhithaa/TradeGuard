def correlate_incidents(sys_metrics, trade_metrics):
    """
    Looks at combined alerts across OS + Trading services to deduce
    the likely underlying root cause instead of spamming separate alerts.
    """
    incidents = []

    # Rule 1: Host resource exhaustion affecting trading performance
    if sys_metrics["alerts"] and (trade_metrics["strategy_breach"] or trade_metrics["feed_breach"]):
        incidents.append({
            "severity": "CRITICAL",
            "component": "Host Infrastructure & Trading Engine",
            "issue": "System resource bottleneck degrading trading pipeline",
            "observations": sys_metrics["alerts"] + [
                f"Feed delay: {trade_metrics['feed_delay_ms']} ms",
                f"Strategy latency: {trade_metrics['strategy_latency_ms']} ms"
            ],
            "investigation": [
                "Run 'top' or 'ps aux --sort=-%cpu' to identify runaway processes.",
                "Check 'free -h' and 'df -h' for memory leaks or full disks.",
                "Isolate or restart non-critical background jobs."
            ]
        })
        return incidents

    # Rule 2: Upstream Market Data Feed degradation causing downstream cascade
    if trade_metrics["feed_breach"] and (trade_metrics["strategy_breach"] or trade_metrics["gateway_breach"]):
        incidents.append({
            "severity": "CRITICAL",
            "component": "Market Data Feed",
            "issue": f"Market data feed is stale ({trade_metrics['feed_delay_ms']} ms delay)",
            "observations": [
                f"Strategy latency increased to {trade_metrics['strategy_latency_ms']} ms.",
                f"Order rejections spiked to {trade_metrics['order_rejections']}."
            ],
            "investigation": [
                "Check latest received tick timestamp from exchange feed.",
                "Inspect network/multicast feed connectivity.",
                "Review feed handler error logs using 'grep ERROR logs/tradeguard.log'.",
                "Verify feed recovery before resuming dependent strategy engines."
            ]
        })
        return incidents

    # Rule 3: Isolated Order Gateway issue
    if trade_metrics["gateway_breach"] and not trade_metrics["feed_breach"]:
        incidents.append({
            "severity": "WARNING",
            "component": "Order Gateway",
            "issue": f"Elevated order rejections ({trade_metrics['order_rejections']} rejected)",
            "observations": [
                f"Market data feed normal ({trade_metrics['feed_delay_ms']} ms).",
                f"Strategy latency normal ({trade_metrics['strategy_latency_ms']} ms)."
            ],
            "investigation": [
                "Check FIX session connectivity with the exchange.",
                "Inspect risk-check limits and margin thresholds.",
                "Review order gateway rejection codes in logs."
            ]
        })

    # Rule 4: Standalone OS alert when trading pipeline is still healthy
    if sys_metrics["alerts"] and not incidents:
        incidents.append({
            "severity": "WARNING",
            "component": "Linux Host Server",
            "issue": "System resource threshold exceeded",
            "observations": sys_metrics["alerts"],
            "investigation": [
                "Run 'top' to inspect high-resource processes.",
                "Check disk space with 'df -h' and clean old logs if needed."
            ]
        })

    return incidents
