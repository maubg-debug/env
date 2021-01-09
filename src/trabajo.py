import random


class Trabajo:

    def parse(self, cosa, envy):
        if "{" in cosa and "}" in cosa:
            exN = []
            for i, chars in enumerate(cosa):
                try:
                    if chars == "{":
                        exN.append(cosa.index(chars))
                    elif chars == "}":
                        exN.append(cosa.index(chars) + 1)    
                except IndexError:
                    pass
                if len(exN) == 2:
                    string = str(cosa[exN[0]:exN[1]]).replace(" ", "")
                    # print(cosa[exN[0]:exN[1]])
                    res = ""
                    if "random" in string:
                        frString = string[string.index("[") + 1:string.index("]")].split(",")
                        res = random.randint(int(frString[0]), int(frString[1]))
                        exN = []
                    elif string[2:-1] in envy:
                        if not "$" in string[1:-1]:
                            print("Sintaxis invalida")
                            exit(1)
                        res = self.get(string[2:-2].replace("$", ""), envy)
                        exN = []
                    cosa = cosa.replace(" ", "").replace(string, str(res))
            return cosa
        return cosa

    def get(self, nombre, envy):
            env = envy.split("\n")
            for cosa in env:
                if cosa.startswith("//"):
                    continue
                if nombre in cosa.split(":")[0]:
                    cosa = cosa.split(":")
                    cosa = self.parse(cosa[1], envy)
                    return cosa
            return

    def write(self, nombre: str, value: str, archivo: str):
        if archivo is not None:
            dataEx = open(archivo, "r").read()
            if not dataEx.endswith("\n"):
                dataEx = str(dataEx) + "\n"
            data = open(archivo, "w")

            data.write(f"{dataEx}{nombre}: {value}\n")
            data.close()

            return