# Quantum Avenger — pipeline / app image (Phase 7).
# Build from the repo root:
#   docker build -f new_pipeline/hardening/docker/Dockerfile.app -t quantum-avenger-app .
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY new_pipeline/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY new_pipeline ./new_pipeline

# Run as a non-root user.
RUN useradd --create-home --uid 10001 quant && chown -R quant /app
USER quant

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -m new_pipeline.scripts.check_health || exit 1

ENTRYPOINT ["python", "-m", "new_pipeline.main"]
CMD ["health"]
