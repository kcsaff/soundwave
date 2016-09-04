import re


SYMBOL = '[\U0001F300-\U0001F64F\U0001F680-\U0001F6FF\u2600-\u26FF\u2700-\u27BF]'
# http://stackoverflow.com/a/26568779


class ParseError(Exception):
    line = 0


def _re_compile(regex):
    return re.compile(regex.replace(r'[\w]', SYMBOL), re.U)


class Rhythm(object):
    def __init__(self, beats):
        self.beats = beats


class Instrument(object):
    def __init__(self):
        pass


class Parser(object):
    def __init__(self):
        self.objects = dict()

    def define(self, name, kind, data):
        if name in self.objects:
            raise ParseError('`{}` is already defined'.format(name))
        else:
            object = getattr(self, kind)(data.split('#', 1)[0].strip().split())
            self.objects[name] = object

    def comment(self, *args):
        pass

    def parse(self, lines):
        for i, line in enumerate(lines, 1):
            for regex, fun in self.definitions:
                match = regex.match(line)
                if match:
                    try:
                        fun(self, *match.groups())
                    except ParseError as err:
                        err.line = line
                        raise
                    break
            else:
                err = ParseError('Could not parse line {}'.format(line))
                err.line = line
                raise err

    def rhythm(self, *beats):
        return Rhythm(beats)

Parser.definitions = [
    (_re_compile('^([\w]+)\s*:\s*(\w+)\s+(\S.*\S)\s*$'), Parser.define),
    (_re_compile('^\s*#.*$'), Parser.comment)
]
