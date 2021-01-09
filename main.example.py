from src.mauenv import Mauenv

env = Mauenv("D:\\work\\mauenv")

data = env.get("HOLA")
print(data)

env.write("ME_LLAMO", "Maubg")

env.read()

input()