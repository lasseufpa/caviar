import re

from .errors import FormatError

def look_next_line(infile):
    now = infile.tell()
    line = infile.readline()
    infile.seek(now)
    return line


def match_or_error(exp, infile):
    line = infile.readline()
    match = re.match(exp, line)
    if match:
        return match
    else:
        raise FormatError(
            'Expected "{}", found "{}"'.format(exp, line))