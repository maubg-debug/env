from abc import ABCMeta
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

class Atom():
    __metaclass__ = ABCMeta

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def resolve(self, env):
        raise NotImplementedError

class Variable(Atom):
    def __init__(self, name, default):
        self.name = name
        self.default = default

    def __repr__(self):
        return "Variable(name={}, default={})".format(self.name, self.default)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.name, self.default) == (other.name, other.default)

    def __hash__(self):
        return hash((self.__class__, self.name, self.default))

    def resolve(self, env):
        default = self.default if self.default is not None else ""
        result = env.get(self.name, default)
        return result if result is not None else ""

class Literal(Atom):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Literal(value={})".format(self.value)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value

    def __hash__(self):
        return hash((self.__class__, self.value))

    def resolve(self, env):
        return self.value

def parse_variables(value):
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