from src.mauenv import Mauenv

string = ""

env = Mauenv("D:\\work\\mauenv")

data = env.get("HOLA")

print(data)

input()