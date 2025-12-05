Proyecto de Microservicio de Gestión Academica

**Descripción**

Microservicio desarrollado en Flask para la gestión académica de la universidad. Proporciona APIs REST para administrar universidades, facultades y especialidades con persistencia en base de datos SQL y caché en Redis. Permite crear, editar, consultar y eliminar información sobre universidades, facultades y programas de estudio de manera rápida y eficiente.

**Características principales:**

- Acceso mediante una interfaz simple basada en solicitudes HTTP
- Los datos se guardan en una base de datos segura y confiable
- El sistema recuerda consultas frecuentes para ser más rápido
- Búsquedas y filtros avanzados para encontrar la información necesaria
- Compatible con múltiples universidades simultáneamente

**Requisitos previos**

- Python 3.12 o superior
- PostgreSQL instalado y funcionando
- Redis instalado (para caché)
- pip (gestor de paquetes de Python)

**Estructura del proyecto**

- `app/` - Código principal de la aplicación
- `app/models/` - Modelos de datos (Universidad, Facultad, Especialidad)
- `app/resources/` - Endpoints REST
- `app/services/` - Lógica de negocio
- `app/repositories/` - Acceso a datos
- `test/` - Tests unitarios e integración
- `migrations/` - Migraciones de base de datos

**Dependencias Principales**
Flask==3.0.2
flask-marshmallow==0.15.0
werkzeug>=3.0.1
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.40
psycopg2-binary==2.9.10
python-dotenv==1.0.1
Flask-Migrate==4.1.0
marshmallow==3.20.0
markupsafe==3.0.2
Flask-Hashids == 1.0.3
sqlalchemy-filters == 0.13.0
Flask-Filter == 0.1.2a3
requests==2.31.0
tenacity==8.2.3
Flask-Caching==2.1.0
redis==5.0.3

**Integrantes:**

Aguilera Sebastián

Aguilera Rocío

Gualpa Agostina

González Luciana

Pérez Jazmín

Choquevillca Celeste

Guzmán Dana

**Endpoints:**
https://backend.universidad.localhost/api/v1/universidad
https://backend.universidad.localhost/api/v1/facultad
https://backend.universidad.localhost/api/v1/especialidad

**Migracion DB:**

1. flask db init
2. flask db migrate -m "migracion"
3. flask db upgrade

**Configuracion Traefik:**
Entrypoint seguro "https"

### Antes de ejecutar configurar archivos .env
