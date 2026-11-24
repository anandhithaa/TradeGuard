# System Resource Thresholds (Part A)
CPU_THRESHOLD = 90.0             # Percentage
RAM_THRESHOLD = 90.0             # Percentage
DISK_THRESHOLD = 85.0            # Percentage

# Trading Pipeline Thresholds (Part B)
FEED_DELAY_THRESHOLD = 100       # Milliseconds
STRATEGY_LATENCY_THRESHOLD = 60  # Milliseconds
ORDER_REJECTION_THRESHOLD = 5    # Count per cycle

# Output Paths (Part D)
LOG_FILE = "logs/tradeguard.log"
INCIDENT_CSV = "logs/incidents.csv"
