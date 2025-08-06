FROM python:3.12-slim

WORKDIR /app
COPY . /app
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 80
RUN ls -l /app
# Run Alembic migrations and then start the server
CMD ["/app/entrypoint.sh"]
