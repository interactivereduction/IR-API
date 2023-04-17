# IR-API
The interactive reduction ReST API.
![License: GPL-3.0](https://img.shields.io/github/license/InteractiveReduction/run-detection)
![Build: passing](https://img.shields.io/github/actions/workflow/status/interactivereduction/IR-API/tests.yml?branch=main)
[![codecov](https://codecov.io/gh/interactivereduction/IR-API/branch/main/graph/badge.svg?token=XRJ1F7TEIT)](https://codecov.io/gh/interactivereduction/IR-API)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)

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


## API Documentation
Once deployed the auto generated api documentation is available at `/docs`. These can be used to inspect the API, and
can be used to try out each endpoint, which is useful for some manual testing and verification.

## Integration and end-to-end Testing
To run the integration and e2e tests, a postgres database is expected at localhost:5432 with user: postgres 
password:password

## Transforms Overview

Transforms are used to apply modifications to instrument scripts based on reduction input parameters. They enable you to
dynamically adapt the script depending on specific requirements, such as changing configuration settings, altering input
data, or modifying the processing flow.

### Adding New Transforms

To add a new transform for a different instrument, follow these steps:
  - Create a new class that inherits from the Transform abstract base class, and implement the apply method. This method
takes a PreScript object and a Reduction entity as arguments, and modifies the script as needed. 

For example:

```python
class YourInstrumentTransform(Transform):
    def apply(self, script: PreScript, reduction: Reduction) -> None:
        # Your script modification logic here e.g.
        script.value = f"print('hello {reduction.reduction_inputs.get('user', 'world')}')"
```
  - Update the get_transform_for_instrument factory function to return an instance of your new transform class when the 
appropriate instrument is provided as input by adding a new case for your instrument in the match statement:

```python
def get_transform_for_instrument(instrument: str) -> Transform:
    match instrument.lower():
        case "mari":
            return MariTransform()
        case "your_instrument":
            return YourInstrumentTransform()
        case _:
            raise MissingTransformError(f"No transform for instrument {instrument}")
```

## Data Access Pattern
The api is implementing a trimmed down version of the repository pattern. It is trimmed down in that, there is no data
mapper pattern being used, and therefore the seperation of business and data layers is not complete as there is no
separation of domain entities and database models. It also does not implement generalised search criteria and the api 
depends directly on `LambdaElement` criteria.
However, this trimmed down implementation does offer the other benefits of the pattern while reducing some of the 
drawbacks. It provides a unified data access api, which significantly reduces complexity in querying data and testing
while mocking data access. By being trimmed down, the increased complexity that can arise from the implementation of 
model mappers/transformers is reduced.  

