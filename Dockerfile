FROM python:3.13-alpine
LABEL MAINTAINER="Jonathan Villanueva <me@jevillanueva.dev>"
RUN apk update && apk add --no-cache python3-dev \
    gcc \
    libc-dev \
    libffi-dev
WORKDIR /app/
COPY requirements.txt /app/
RUN pip install  --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--workers", "2", "--host", "0.0.0.0" ]
