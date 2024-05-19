import json
import inspect

from libtado.api import Tado

from tests.api import utils


def generate_jsonschema_file(filename: str, data: object):
    from genson import SchemaBuilder
    builder = SchemaBuilder()
    builder.add_object(data)
    schema = builder.to_schema()
    with open(f"schemas/{filename}.json", "w") as file:
        file.write(json.dumps(schema, indent=2))
    return schema


tado_methods = inspect.getmembers(utils.TestApi, predicate=inspect.isfunction)
tado_methods = [method[0] for method in tado_methods if method[0].startswith('get_')]

for method in tado_methods:
    print(f"Calling {method}")
    res = eval(f'utils.TestApi.{method}()')
    print(f"Generating schema for {method}")
    schema = generate_jsonschema_file(f"{method}", res)

print()
print("End of generating schemas.")
