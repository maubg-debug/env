# .env

.env lee pares clave-valor de un archivo `.env` y puede establecerlos como entorno
variables. Ayuda en el desarrollo de aplicaciones siguiendo las

## Como empezar

Si su aplicación toma su configuración de variables de entorno, como un factor de 12
aplicación, lanzarla en desarrollo no es muy práctico porque tienes que configurar
esas variables de entorno usted mismo.

Para ayudarlo con eso, puede agregar env a su aplicación para que cargue el
configuración de un archivo `.env` cuando está presente (por ejemplo, en desarrollo) mientras permanece
configurable a través del entorno:

```python
from src.main import load_env

load_dotenv()  # tomar variables de entorno de .env.

# Código de su aplicación, que usa variables de entorno (por ejemplo, de `os.environ` o
# `os.getenv`) como si vinieran del entorno real.
```

```python
from src.main import get_env

data = get_env()  # Recibir -> dict
print(data)
```

La sintaxis de los archivos `.env` admitidos por env es similar a la de Bash:

```bash
# Comentario
DOMINIO=example.org
ADMIN_EMAIL=admin@${DOMINIO}
ROOT_URL=${DOMINIO}/app
```
Si usa variables en valores, asegúrese de que estén rodeadas por `{` y `}`, como
`${DOMINIO}`, ya que las variables básicas como `$DOMINIO` no se expanden.

Probablemente desee agregar `.env` a su`.gitignore`, especialmente si contiene
secretos como una contraseña.

Consulte la sección "Formato de archivo" a continuación para obtener más información sobre lo que puede escribir en un
Archivo `.env`.

