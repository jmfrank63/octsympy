import sys
sys.ps1 = ""; sys.ps2 = ""
import sympy as sp
from sympy import *
#import dill as pickle


def dbout(l):
    sys.stderr.write("pydebug: " + str(l) + "\n")


def objectfilter(x):
    """Perform final fixes before passing objects back to Octave"""
    if isinstance(x, sp.Matrix) and x.shape == (1,1):
        #dbout("Note: replaced 1x1 mat with scalar")
        y = x[0,0]
    else:
        y = x
    return y


# Single quotes must be replaced with two copies, escape not enough
# FIXME: unicode strings probably do not have enough escaping
def octcmd(x):
    x = objectfilter(x)
    if isinstance(x, sp.Expr):
        # works on Octave where " is valid for enclosing strings
        #s = "sym(\\"" + str(x) + "\\", \\"" + sp.srepr(x) + "\\")"
        s = "sym('" +   sp.srepr(x).replace("'", "''")   + "'" + \
            ", [1 1]" + \
            ", '" +   str(x).replace("'", "''")   + "'" + \
            ", '" +   str(x).replace("'", "''")   + "'" + \
            ")"
        # possibly str(x).encode("string_escape")
    elif isinstance(x, sp.Matrix):
        _d = x.shape
        _pretty_ascii = sp.pretty(x,use_unicode=False).encode("string_escape")
        _pretty_unicode = \
            sp.pretty(x,use_unicode=True).encode("utf-8").replace("\n","\\n")

        s = "sym('" +   sp.srepr(x).replace("'", "''")   + "'" + \
            ", [" +   str(_d[0]) + ' ' + str(_d[1])   + ']' + \
            ", '" +   str(x).replace("'", "''")   + "'" + \
            ", sprintf('" +   _pretty_ascii.replace("'", "''")   + "')" + \
            ")"
    elif isinstance(x, bool) and x:
        s = "true"
    elif isinstance(x, bool) and not x:
        s = "false"
    elif isinstance(x, (list,tuple)):
        s = "{"
        for y in x:
            s = s + octcmd(y) + ",  "
        s = s + "}"
    elif isinstance(x, int):
        s = str(x)
    elif isinstance(x, float):
        s = str(x)
        # FIXME
    elif isinstance(x, str):
        s = "sprintf('" + x.encode("string_escape").replace("'", "''") + "')"
    elif isinstance(x, unicode):
        # not .encode("string_escape")
        s = "sprintf('" + \
          x.encode("utf-8").replace("\n","\\n").replace("'", "''") + "')"
    else:
        s = "error('python does not know how to export that')"
    return s

