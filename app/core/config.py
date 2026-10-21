"""Módulo de configuración central del microservicio de IA.

Utiliza Pydantic Settings para cargar variables de entorno y definir
parámetros operativos de la aplicación con validación estricta de tipos.
"""


from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuraciones globales de la aplicación."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Microservicio IA - ERP Gimnasio"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")

    # Seguridad y Criptografía
    SECRET_KEY: str = Field(
        default="clave_secreta_para_desarrollo_local_minimo_32_caracteres_12345"
    )
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    ALLOWED_CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )


    # Almacenamiento Local
    STORAGE_LOCAL_PATH: str = Field(default="./storage")
    MAX_UPLOAD_IMAGE_SIZE_MB: int = Field(default=10)
    MAX_UPLOAD_VIDEO_SIZE_MB: int = Field(default=50)

    # Parámetros Biomecánicos
    POSE_MODEL_PATH: str = Field(default="models/pose_landmarker_lite.task")
    MIN_LANDMARK_VISIBILITY_CONFIDENCE: float = Field(default=0.65)


settings = Settings()
