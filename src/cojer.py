import os

def cojer(directorio):
    def ValidarArchivo(fl):
        directorio.replace("\\\\", "\\").replace("\\", "\\\\")
        if directorio.endswith("\\"):
            return f"{directorio}{fl}"
        return f"{directorio}\\{fl}"

    for archivo in os.listdir(directorio):
        if archivo.endswith(".mauenv"):
            return [True, str(open(ValidarArchivo(archivo), "r").read()), ValidarArchivo(archivo)]
    return [False, None]