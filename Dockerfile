FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH
WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl \
 && curl -LsSf https://astral.sh/uv/install.sh | sh \
 && apt-get purge -y curl \
 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
# Crea .venv (predeterminado de uv) y sincroniza deps usando Python 3.12 del sistema
RUN uv sync --no-dev

COPY ./app ./app
COPY ./app.py .

FROM python:3.12-slim AS runtime

ENV FLASK_CONTEXT=production
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH=$VIRTUAL_ENV/bin:$PATH

WORKDIR /home/sysacad
RUN useradd --create-home --home-dir /home/sysacad sysacad

# Copiar el entorno creado en .venv (builder) a /opt/venv (runtime)
COPY --from=builder /app/.venv /opt/venv
COPY --from=builder /app/app ./app
COPY --from=builder /app/app.py .

USER sysacad

EXPOSE 5000

CMD [ "python", "./app.py" ]