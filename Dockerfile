# Multi-stage Dockerfile para Microservicio de IA para ERP de Gimnasio
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

COPY pyproject.toml .

# Crear virtualenv y construir dependencias (ruedas precompiladas manylinux)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.30.0" \
    "pydantic>=2.8.0" \
    "pydantic-settings>=2.4.0" \
    "python-multipart>=0.0.9" \
    "opencv-python-headless>=4.10.0" \
    "mediapipe>=0.10.14,<1.0.0" \
    "numpy>=1.26.4,<2.0.0" \
    "pandas>=2.2.0" \
    "scikit-learn>=1.5.0" \
    "torch>=2.2.0" \
    "httpx>=0.27.0"

# --- Runtime Stage ---
FROM python:3.12-slim-bookworm AS runner

WORKDIR /app

# Forzar HTTPS en repositorios Debian para evitar caídas en puerto 80 del host
# Librerías dinámicas necesarias para OpenCV y MediaPipe (incluyendo libgl1, libegl1 y libgles2 para mediapipe_c_bindings)
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install --no-install-recommends -y \
    libgl1 \
    libegl1 \
    libgles2 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Copiar código del microservicio, datasets y modelos
COPY app /app/app
COPY ml /app/ml
COPY models /app/models

# Crear directorio de almacenamiento local seguro
RUN mkdir -p /app/storage

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health/live || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
