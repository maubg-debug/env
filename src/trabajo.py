import random


class Trabajo:

    def parse(self, cosa, envy):
        if "{{" in cosa:
            if "}}" in cosa:
                exN = []
                for i, chars in enumerate(cosa):
                    try:
                        if chars == "{" and cosa[int(i) + 1] == "{":
                            exN.append(i)
                        elif chars == "}" and cosa[int(i) + 1] == "}":
                            exN.append(i + 2)    
                        else:
                            continue
                    except IndexError:
                        continue
                
                if len(exN) == 2:
                    string = str(cosa[exN[0]:exN[1]]).replace(" ", "")

                    if "random" in string:
                        frString = string[9:-3].split(",")
                        res = random.randint(int(frString[0]), int(frString[1]))
                    cosa = cosa.replace(" ", "").replace(string, str(res))
                    return cosa
                else:
                    print("Sintaxis invalida")
                    exit(1)

            print("Sintaxis invalida")
            exit(1)
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
            return None

    def write(self, nombre: str, value: str, archivo: str):
        if archivo is not None:
            dataEx = open(archivo, "r").read()
            if not dataEx.endswith("\n"):
                dataEx = str(dataEx) + "\n"
            data = open(archivo, "w")

            data.write(f"{dataEx}{nombre}: {value}\n")
            data.close()

            return