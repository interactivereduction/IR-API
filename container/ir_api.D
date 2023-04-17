FROM python:3.10

WORKDIR /ir_api

# Install ir_api to the container
COPY . /ir_api
RUN python -m pip install --no-cache-dir .

CMD ["uvicorn", "ir_api.ir_api:app", "--host", "0.0.0.0", "--port", "80"]