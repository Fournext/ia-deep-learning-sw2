# Guía de Despliegue con Docker y Docker Compose

Este documento describe el procedimiento para desplegar el microservicio de IA en entornos locales, de staging y producción.

---

## 1. Requisitos Previos

- **Docker Engine:** Versión 24.0 o superior (compatible con Windows con WSL2 o Linux).
- **Docker Compose:** Versión v2.20 o superior.
- **Memoria RAM Mínima:** 4 GB (8 GB recomendado para inferencia simultánea de video y deep learning).
- **Soporte de Aceleración:** CPU (por defecto, no requiere GPU obligatoria). Detección automática de CUDA disponible si se cuenta con GPU Nvidia y `nvidia-container-toolkit`.

---

## 2. Variables de Entorno (`.env`)

Crea un archivo `.env` en la raíz del proyecto basándote en `.env.example`:

```bash
# Entorno
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Seguridad
SECRET_KEY=cambiar_en_produccion_por_un_hash_seguro_minimo_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_CORS_ORIGINS=["https://erp.gimnasio.com"]

# Almacenamiento seguro temporal
STORAGE_LOCAL_PATH=/app/storage
MAX_UPLOAD_IMAGE_SIZE_MB=10
MAX_UPLOAD_VIDEO_SIZE_MB=50
```

---

## 3. Puesta en Marcha con Docker Compose (Contenedor Único Stateless)

El microservicio se ejecuta como un contenedor autónomo y ligero sin base de datos:

```bash
# Construir y levantar el microservicio en segundo plano
docker compose up -d --build

# Verificar estado del contenedor
docker compose ps

# Visualizar logs en tiempo real
docker compose logs -f api
```

El servicio estará disponible en:
- API REST: `http://localhost:8000/api/v1`
- Documentación OpenAPI interactiva: `http://localhost:8000/docs`
- Healthcheck de liveness: `http://localhost:8000/health/live`
- Healthcheck de readiness: `http://localhost:8000/health/ready`

---

## 4. Comandos de Mantenimiento

```bash
# Ejecutar migraciones manualmente
docker compose exec api alembic upgrade head

# Ejecutar suite de pruebas dentro del contenedor
docker compose exec api pytest --cov=app tests/

# Detener los servicios
docker compose down
```
