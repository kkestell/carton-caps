FROM python:3.13-slim-bookworm

RUN useradd -m -u 1000 mulder

WORKDIR /app
COPY . .

RUN chown -R mulder:mulder /app
USER mulder

RUN python -m venv .venv
RUN .venv/bin/pip install -r requirements.txt
RUN .venv/bin/pip install -e .

RUN chmod +x /app/entrypoint.sh

ENV QUART_APP=src.carton_caps.app:create_app
EXPOSE 5000

CMD ["/app/entrypoint.sh"]
