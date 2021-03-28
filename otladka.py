import yaml
from pprint import pprint

with open('openapi.yaml') as f:
    templates = yaml.safe_load(f)

pprint(templates)