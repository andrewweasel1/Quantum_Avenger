"""Container liveness probe: print the health report, exit 1 when degraded."""

import json
import sys

from new_pipeline.monitoring.health import HealthCheck

if __name__ == "__main__":
    status = HealthCheck().status()
    print(json.dumps(status, indent=2))
    sys.exit(0 if status["status"] == "healthy" else 1)
