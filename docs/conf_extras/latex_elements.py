from collections.abc import Iterable

from . import read_x

# fmt: off
def get() -> dict:
    return {
        # 'fontenc'              : r'\usepackage[X2,T1]{fontenc}',             # with language = "ru"
        "preamble"               : '\n'.join(_get_preamble()),
        # 'passoptionstopackages': r'\PassOptionsToPackage{svgnames}{xcolor}', #
        "papersize"              : "a4paper",                                  # letter,a4paper
        "pointsize"              : "10pt",                                     # 10,11,12
        "inputenc"               : "\\usepackage[utf8]",                       # ⎫
        "utf8extra"              : "",                                         # ⎭ both necessary for unicode in pdf
        "classoptions"           : ",openany,oneside",                         # remove blank pages
        "babel"                  : "\\usepackage[english]{babel}",             # quote symbols and more
        "pxunit"                 : "0.5bp",                                    # (dpi = 72*bp)           doesnt work btw
        "figure_align"           : "H",                                        # text wrapping
        "fncychap"               : read_x('latex_fncychap.sty'),               # chapter start pages
        #'fontpkg'                : '\\usepackage{amsmath,amsfonts,amssymb,amsthm}',
        # 'fontpkg'               : '\\usepackage[defaultsans]{lato}',        # eliminates bold monospace chars
        "printindex"             : r"\footnotesize\raggedright\printindex",    # decrease font for index
        # "releasename"            : "",  ## does not work
        'sphinxsetup'            : ', '.join(f'{k}={v}' for k, v in dict().items()),

    }

def _get_preamble() -> Iterable[str]:
    yield r'\setlength{\emergencystretch}{5em}'  # decrease "can't fit" warnings
    yield r'\DeclareUnicodeCharacter{2588}{~}'   # █
    yield read_x('latex_preamble.sty')
# fmt: on
