import random
import config

def get_trading_metrics(scenario="normal"):
    """
    Simulates metrics for:
    1. Market Data Feed (delay in ms)
    2. Strategy Engine (latency in ms)
    3. Order Gateway (rejected orders count)
    """
    if scenario == "normal":
        feed_delay = random.randint(2, 15)
        strategy_latency = random.randint(8, 25)
        rejections = random.choice([0, 0, 1])

    elif scenario == "feed_lag":
        # Upstream market data degrades, causing downstream domino effects
        feed_delay = random.randint(150, 250)
        strategy_latency = random.randint(80, 140)
        rejections = random.randint(8, 18)

    elif scenario == "gateway_issue":
        # Feed and strategy are fine, but exchange/gateway rejects orders
        feed_delay = random.randint(4, 12)
        strategy_latency = random.randint(10, 20)
        rejections = random.randint(12, 25)

    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    return {
        "feed_delay_ms": feed_delay,
        "strategy_latency_ms": strategy_latency,
        "order_rejections": rejections,
        "feed_breach": feed_delay > config.FEED_DELAY_THRESHOLD,
        "strategy_breach": strategy_latency > config.STRATEGY_LATENCY_THRESHOLD,
        "gateway_breach": rejections > config.ORDER_REJECTION_THRESHOLD
    }
