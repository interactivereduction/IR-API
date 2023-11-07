FROM python:3.12-slim

WORKDIR /ir_api

# Install ir_api to the container
COPY . /ir_api
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir .

CMD ["uvicorn", "ir_api.ir_api:app", "--host", "0.0.0.0", "--port", "80"]