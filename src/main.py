from contextlib import contextmanager
from collections import OrderedDict

from src.utils import utils, StringIO, pyv, Position, to_env
from src.variables import parse_variables

import os
import io
import logging
import sys
import re
import codecs


logger = logging.getLogger(__name__)
utils = utils()

def to_text(string):
    if pyv.PY2:
        return string.decode("utf-8")
    else:
        return string

def make_regex(string, extra_flags=0):
    return re.compile(to_text(string), re.UNICODE | extra_flags)


_newline = make_regex(r"(\r\n|\n|\r)")
_multiline_whitespace = make_regex(r"\s*", extra_flags=re.MULTILINE)
_whitespace = make_regex(r"[^\S\r\n]*")
_export = make_regex(r"(?:export[^\S\r\n]+)?")
_single_quoted_key = make_regex(r"'([^']+)'")
_unquoted_key = make_regex(r"([^=\#\s]+)")
_equal_sign = make_regex(r"(=[^\S\r\n]*)")
_single_quoted_value = make_regex(r"'((?:\\'|[^'])*)'")
_double_quoted_value = make_regex(r'"((?:\\"|[^"])*)"')
_unquoted_value = make_regex(r"([^\r\n]*)")
_comment = make_regex(r"(?:[^\S\r\n]*#[^\r\n]*)?")
_end_of_line = make_regex(r"[^\S\r\n]*(?:\r\n|\n|\r|$)")
_rest_of_line = make_regex(r"[^\r\n]*(?:\r|\n|\r\n)?")
_double_quote_escapes = make_regex(r"\\[\\'\"abfnrtv]")
_single_quote_escapes = make_regex(r"\\[\\']")

try:
    import typing

    Original = typing.NamedTuple(
        "Original",
        [
            ("string", typing.Text),
            ("line", int),
        ],
    )

    Binding = typing.NamedTuple(
        "Binding",
        [
            ("key", typing.Optional[typing.Text]),
            ("value", typing.Optional[typing.Text]),
            ("original", Original),
            ("error", bool),
        ],
    )
except (ImportError, AttributeError):
    from collections import namedtuple
    Original = namedtuple(
        "Original",
        [
            "string",
            "line",
        ],
    )
    Binding = namedtuple( 
        "Binding",
        [
            "key",
            "value",
            "original",
            "error",
        ],
    )

def with_warn_for_invalid_lines(mappings):
    for mapping in mappings:
        if mapping.error:
            logger.warning(
                "No pudo analizar la declaración que comienza en la línea %s",
                mapping.original.line,
            )
        yield mapping

class Reader:
    def __init__(self, stream):
        self.string = stream.read()
        self.position = Position.start()
        self.mark = Position.start()

    def has_next(self):
        return self.position.chars < len(self.string)

    def set_mark(self):
        self.mark.set(self.position)

    def get_marked(self):
        return Original(
            string=self.string[self.mark.chars:self.position.chars],
            line=self.mark.line,
        )

    def peek(self, count):
        return self.string[self.position.chars:self.position.chars + count]

    def read(self, count):
        result = self.string[self.position.chars:self.position.chars + count]
        if len(result) < count:
            raise Error("leer: Fin de cadena")
        self.position.advance(result)
        return result

    def read_regex(self, regex):
        match = regex.match(self.string, self.position.chars)
        if match is None:
            raise Error("leer_regex: Patrón no encontrado")
        self.position.advance(self.string[match.start():match.end()])
        return match.groups()

class Error(Exception):
    pass

def parse_binding(reader):
    reader.set_mark()
    try:
        reader.read_regex(_multiline_whitespace)
        if not reader.has_next():
            return Binding(
                key=None,
                value=None,
                original=reader.get_marked(),
                error=False,
            )
        reader.read_regex(_export)
        key = parse_key(reader)
        reader.read_regex(_whitespace)
        if reader.peek(1) == "=":
            reader.read_regex(_equal_sign)
            value = parse_value(reader)
        else:
            value = None
        reader.read_regex(_comment)
        reader.read_regex(_end_of_line)
        return Binding(
            key=key,
            value=value,
            original=reader.get_marked(),
            error=False,
        )
    except Error:
        reader.read_regex(_rest_of_line)
        return Binding(
            key=None,
            value=None,
            original=reader.get_marked(),
            error=True,
        )

def parse_key(reader):
    char = reader.peek(1)
    if char == "#":
        return None
    elif char == "'":
        (key,) = reader.read_regex(_single_quoted_key)
    else:
        (key,) = reader.read_regex(_unquoted_key)
    return key


def parse_unquoted_value(reader):
    # type: (Reader) -> Text
    (part,) = reader.read_regex(_unquoted_value)
    return re.sub(r"\s+#.*", "", part).rstrip()

def decode_escapes(regex, string):
    # type: (Pattern[Text], Text) -> Text
    def decode_match(match):
        # type: (Match[Text]) -> Text
        return codecs.decode(match.group(0), 'unicode-escape')  # type: ignore

    return regex.sub(decode_match, string)


def parse_value(reader):
    # type: (Reader) -> Text
    char = reader.peek(1)
    if char == u"'":
        (value,) = reader.read_regex(_single_quoted_value)
        return decode_escapes(_single_quote_escapes, value)
    elif char == u'"':
        (value,) = reader.read_regex(_double_quoted_value)
        return decode_escapes(_double_quote_escapes, value)
    elif char in (u"", u"\n", u"\r"):
        return u""
    else:
        return parse_unquoted_value(reader)

def parse_stream(stream):
    # type: (IO[Text]) -> Iterator[Binding]
    reader = Reader(stream)
    while reader.has_next():
        yield parse_binding(reader)

class DotEnv:
    
    def __init__(self, path: str = None, encoding='utf-8', verbose: bool = None, interpolate=True, override=True, **kwargs):
        self.dotenv_path = path
        self.encoding = encoding
        self.verbose = verbose
        self._dict = None
        self.interpolate = interpolate
        self.override = override

        for key, value in kwargs:
            setattr(self, key, value)

    @contextmanager
    def _get_stream(self):
        if isinstance(self.dotenv_path, StringIO):
            yield self.dotenv_path
        elif os.path.isfile(self.dotenv_path):
            with io.open(self.dotenv_path, encoding=self.encoding) as stream:
                yield stream
        else:
            if self.verbose:
                logger.info("No se pudo encontrar archivo de configuracion o %s.", self.dotenv_path or '.env')
            yield StringIO('')

    def dict(self):
        if self._dict:
            return self._dict

        raw_values = self.parse()

        if self.interpolate:
            self._dict = OrderedDict(utils.resolve_variables(raw_values, override=self.override))
        else:
            self._dict = OrderedDict(raw_values)

        return self._dict

    def parse(self):
        with self._get_stream() as stream:
            for mapping in with_warn_for_invalid_lines(parse_stream(stream)):
                if mapping.key is not None:
                    yield mapping.key, mapping.value

    def set_as_environment_variables(self):
        for k, v in self.dict().items():
            print(k)
            print(v)
            if k in os.environ and not self.override:
                continue
            if v is not None:
                os.environ[to_env(k)] = to_env(v)

        return True

    def get(self, key):
        data = self.dict()

        if key in data:
            return data[key]

        if self.verbose:
            logger.warning("Key %s not found in %s.", key, self.dotenv_path)

        return None

def load_env(path: str = None, stream: str = None, verbose: bool = None, **kwargs):
    
    error = True if kwargs.get("error") else False

    f = path or stream or utils.find_dotenv(raise_error_if_not_found=error)
    DotEnv(path=f, verbose=verbose, **kwargs).set_as_environment_variables()