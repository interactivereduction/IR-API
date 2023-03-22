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