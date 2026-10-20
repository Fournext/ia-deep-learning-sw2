# Reglas de Seguridad y Privacidad de Datos Biométricos

Normativa ineludible para la protección de datos sensibles e infraestructura.

## 1. Gestión de Credenciales y Secretos
- Cero secretos en código fuente ni en el historial de Git.
- Todos los valores de configuración sensibles se gestionan mediante variables de entorno y se declaran con valores ficticios en `.env.example`.
- Verificación automática en CI mediante `bandit` y reglas de escaneo de secretos.

## 2. Protección y Retención de Material Audiovisual
- Las fotografías y videos subidos por los usuarios para análisis postural contienen datos biométricos sensibles sujetos a leyes de privacidad (GDPR / legislaciones locales).
- Procesamiento efímero: una vez que los landmarks y medidas articulares son extraídos y almacenados numéricamente, los archivos de imagen/video deben ser eliminados del almacenamiento temporal local o anonimizados según la directiva configurada.
- No almacenar imágenes crudas en bases de datos relacionales ni exponer rutas de archivos accesibles públicamente sin autenticación previa.

## 3. Seguridad de Endpoints y Carga de Archivos
- Validar tipos MIME reales (mediante inspección de magic bytes en cabeceras de archivo, no solo extensión).
- Limitar el tamaño máximo de archivo (ej. 10MB para imágenes, 100MB para videos).
- Proteger rutas contra ataques de Path Traversal (`os.path.basename` o nombres de archivo generados como UUIDv4).
