FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar ca-certificates y curl, luego instalar UV y limpiar todo en UNA SOLA CAPA
# Se mueve uv a /usr/local/bin para que esté automáticamente en el PATH
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && apt-get purge -y --auto-remove ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* /root/.local/bin

# Copiar archivos de dependencias
COPY pyproject.toml uv.lock ./

RUN uv sync --no-dev

COPY ./app ./app
COPY ./app.py . 

# Etapa de runtime
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1
ENV FLASK_CONTEXT=production
ENV VIRTUAL_ENV=/opt/venv
ENV PATH=$VIRTUAL_ENV/bin:$PATH

# Crear usuario no root y su directorio HOME
RUN useradd --create-home --home-dir /home/sysacad sysacad

WORKDIR /home/sysacad/app

COPY --from=builder /app/.venv $VIRTUAL_ENV
RUN chown -R sysacad:sysacad $VIRTUAL_ENV
    
COPY --from=builder --chown=sysacad:sysacad /app/app ./app
COPY --from=builder --chown=sysacad:sysacad /app/app.py .

USER sysacad

EXPOSE 5000

# Ejecutar Gunicorn a través del intérprete del venv
CMD ["/opt/venv/bin/python", "-m", "gunicorn", "-b", "0.0.0.0:5000", "app.wsgi:app"]