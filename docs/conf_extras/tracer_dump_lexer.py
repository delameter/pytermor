# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import Name, Number, String, Punctuation, Whitespace, Text, Keyword, Operator


__all__ = ['TracerDumpLexer']

class TracerDumpLexer(RegexLexer):
    name = 'PtTracerDump'
    aliases = ['pttd']

    hd = r'[0-9A-Fa-f]+'
    s0 = r'\s*?'
    s1 = r'\s+?'

    tokens = {
        'root': [
            (r'\n', Whitespace),
            (fr'^({s0})(0x)?({hd})', bygroups(Whitespace, Name.Entity, Operator)),
            (fr'({s1})(\|)(U\+)?({s1})', bygroups(Whitespace, Punctuation, Name.Builtin, Whitespace)),
            (fr'(\.\.\.)$', Punctuation),
            (fr'([^|]+?)$', Number.Hex),
            (fr"([^|]+?)({s1})(\|)(.+?)$", bygroups(Number.Hex, Whitespace, Punctuation, String)),
        ],
    }


from sphinx.highlighting import lexers
lexers[TracerDumpLexer.name] = TracerDumpLexer()
