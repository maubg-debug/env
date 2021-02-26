from src.main import load_env, get_env
from os import environ

data = get_env()
print(data)

load_env()
print(environ["HOLA_MUNDO"])