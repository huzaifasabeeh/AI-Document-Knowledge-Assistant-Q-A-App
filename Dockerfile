FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements-lock.txt requirements.txt ./
RUN python -m pip install -r requirements-lock.txt
RUN useradd --create-home --uid 10001 appuser
COPY --chown=appuser:appuser app.py ./
COPY --chown=appuser:appuser src ./src
COPY --chown=appuser:appuser scripts/preflight.py ./scripts/preflight.py
USER appuser
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=4)" || exit 1
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", "--browser.gatherUsageStats=false"]
