from new_pipeline.monitoring.health import HealthCheck

if __name__ == "__main__":
    status = HealthCheck().status()
    print(status)
