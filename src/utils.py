from abc import ABCMeta
from src.variables import Atom, Variable, Literal, parse_variables

import os
import sys
import re

_posix_variable = re.compile(
    r"""
    \$\{
        (?P<name>[^\}:]*)
        (?::-
            (?P<default>[^\}]*)
        )?
    \}
    """,
    re.VERBOSE,
)

class pyv:
    PY2 = sys.version_info[0] == 2

if pyv().PY2:
    from StringIO import StringIO 
else:
    from io import StringIO

class utils:

    def __init__(self):
        pass

    def _walk_to_root(self, path):
        if not os.path.exists(path):
            raise IOError('Ruta de inicio no encontrada')

        if os.path.isfile(path):
            path = os.path.dirname(path)

        last_dir = None
        current_dir = os.path.abspath(path)
        while last_dir != current_dir:
            yield current_dir
            parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
            last_dir, current_dir = current_dir, parent_dir

    def find_dotenv(self, filename='.env', raise_error_if_not_found=False, usecwd=False):
        
        def _es_interactivo():
            main = __import__('__main__', None, None, fromlist=['__file__'])
            return not hasattr(main, '__file__')

        if usecwd or _es_interactivo() or getattr(sys, 'frozen', False):
            path = os.getcwd()
        else:
            frame = sys._getframe()

            if pyv.PY2 and not __file__.endswith('.py'):
                
                current_file = __file__.rsplit('.', 1)[0] + '.py'
            else:
                current_file = __file__

            while frame.f_code.co_filename == current_file:
                assert frame.f_back is not None
                frame = frame.f_back
            frame_filename = frame.f_code.co_filename
            path = os.path.dirname(os.path.abspath(frame_filename))

        for dirname in self._walk_to_root(path):
            check_path = os.path.join(dirname, filename)
            if os.path.isfile(check_path):
                return check_path

        if raise_error_if_not_found:
            raise IOError('No se encontro ningun archivo')

        return ''

    def parse_variables(self, value):
        cursor = 0

        for match in _posix_variable.finditer(value):
            (start, end) = match.span()
            name = match.groupdict()["name"]
            default = match.groupdict()["default"]

            if start > cursor:
                yield Literal(value=value[cursor:start])

            yield Variable(name=name, default=default)
            cursor = end

        length = len(value)
        if cursor < length:
            yield Literal(value=value[cursor:length])

    def resolve_variables(self, values, override):

        new_values = {} 

        for (name, value) in values:
            if value is None:
                result = None
            else:
                atoms = parse_variables(value)
                env = {} 
                if override:
                    env.update(os.environ) 
                    env.update(new_values)
                else:
                    env.update(new_values)
                    env.update(os.environ)  
                result = "".join(atom.resolve(env) for atom in atoms)

            new_values[name] = result

        return new_values

class Position:
    def __init__(self, chars, line):
        # type: (int, int) -> None
        self.chars = chars
        self.line = line

    @classmethod
    def start(cls):
        # type: () -> Position
        return cls(chars=0, line=1)

    def set(self, other):
        # type: (Position) -> None
        self.chars = other.chars
        self.line = other.line

    def advance(self, string):
        # type: (Text) -> None
        self.chars += len(string)
        self.line += len(re.findall(re.compile(r"(\r\n|\n|\r)", re.UNICODE), string))


def to_env(text):
    if pyv.PY2:
        return text.encode(sys.getfilesystemencoding() or "utf-8")
    else:
        return text