import csv
import os
from datetime import datetime
import config

def log_message(level, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {message}\n"
    with open(config.LOG_FILE, "a") as f:
        f.write(line)

def get_next_incident_id():
    if not os.path.exists(config.INCIDENT_CSV):
        return 1
    with open(config.INCIDENT_CSV, "r") as f:
        rows = list(csv.reader(f))
        return max(1, len(rows))

def report_incidents(incidents):
    if not incidents:
        print("STATUS: OK — All infrastructure and trading services operating normally.")
        log_message("INFO", "Health check passed. All systems nominal.")
        return

    file_exists = os.path.exists(config.INCIDENT_CSV)
    with open(config.INCIDENT_CSV, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Incident_ID", "Timestamp", "Severity", "Component", "Issue", "Observations"])

        for inc in incidents:
            inc_id = f"INC-{get_next_incident_id():03d}"
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Print formatted alert to terminal
            print("\n" + "=" * 55)
            print(f"{inc_id} | {inc['severity']}")
            print(f"Issue: {inc['issue']}")
            print(f"Detection time: {now_str}")
            print(f"Affected component: {inc['component']}")
            print("Related observations:")
            for obs in inc["observations"]:
                print(f"  - {obs}")
            print("Suggested investigation:")
            for idx, step in enumerate(inc["investigation"], 1):
                print(f"  {idx}. {step}")
            print("=" * 55 + "\n")

            # Write to application log and CSV
            log_message("ERROR", f"{inc_id} [{inc['severity']}] {inc['component']}: {inc['issue']}")
            writer.writerow([
                inc_id,
                now_str,
                inc["severity"],
                inc["component"],
                inc["issue"],
                " | ".join(inc["observations"])
            ])
