# .mauenv
 Un .env personalizado (Sigue en progreso y hay cosas feas en el codigo como "hardcode")


# Como funciona (Y sintaxis)

* `.mauenv` tiene que estar en la ruta padre del directorio en el que tu eligas
    ```python
    from src.mauenv import Mauenv

    env = Mauenv("D:\\work\\mauenv") # Ruta
    ```

    Entonces las carpetas serian asi

    ```
    work/
      | .mauenv
      |- carpeta/
      | main.py
    ```

* Luego la sintaxis iria asi
    
    ```
    COSA: cosas_xd
    COSA_2      : awd
    // Comentario (no pueden ir en la misma linea)
    NUM: {{ random[2, 10] }}
    VAR: {{ $NUM }}
    ```

* Funciones

    ```python
    from src.mauenv import Mauenv

    env = Mauenv("D:\\work\\mauenv") # Ruta

    data = env.get("COSA")
    print(data) # Recojes el valor de "COSA"

    env.write("ALGO", "XD") # Escribes algo caracteres validos ([a-z], [A-Z], _)

    env.read() # Mirar todo el archivo .env
    ```

# TODO 
- [x] Hacer que se puedan usar variables
- [ ] Mas cosas como la de `{ random[num1, num2] }`
- [ ] Mejorar todo
- [ ] hacer que no se vea como una \*\*\*\*\*\*
