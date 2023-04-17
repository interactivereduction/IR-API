# IR-API
The interactive reduction ReST API.

## Local Install
`pip install .[all]`
You may need to escape the square brackets e.g. \[all\]

## Running Directly for development

```shell
uvicorn ir_api.ir_api:app --reload  
```

The reload option will reload the api on code changes.

## How to container

Build using this command in the root of this repository:

```shell
docker build . -f ./container/ir_api.D -t ghcr.io/interactivereduction/ir-api
```

Run on port 8080, by binding port 80 to port 8080 with a built container:
```shell
docker run -p 8080:80 ghcr.io/interactivereduction/ir-api
```