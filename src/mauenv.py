from src.cojer import cojer
from src.trabajo import Trabajo

class Mauenv:

    def __init__(self, directorio = None):
        self.dir = directorio
        if not self.dir:
            print("No se ha puesto ningun directorio")
        
        self.letras = "q,w,e,r,t,y,u,i,o,p,a,s,d,f,g,h,j,k,l,z,x,c,v,b,n,m".upper().split(",")
        self.under = "_"

        self.env = cojer(self.dir)

        # print(self.env)

        if self.env[0] == False:
            print("No se encontro un .mauenv")
            exit(1)

    def get(self, nombre):
        nombre = nombre.upper()
        data = Trabajo().get(nombre, self.env[1])
        if data is not None:
            return data
        

    def _chequeo(self, val):
        for letra in val:
            if str(letra).upper() not in self.letras and str(letra) not in ["{", "}"]:
                print("Letra invalida :: " + str(letra))
                exit(1)

    def _validar(self, nombre, value):
        nombre, value = nombre.strip(), value.strip()
        self._chequeo(nombre)
        self._chequeo(value)


    def write(self, nombre: str, value: str):
        self._validar(str(nombre), str(value))
        data = Trabajo().write(nombre, value, self.env[2])

    def read(self):
        return open(self.env[2], "r").read()