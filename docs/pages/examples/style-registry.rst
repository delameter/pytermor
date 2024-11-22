.. _examples.style-registry:

.. currentmodule:: pytermor.style

#######################
    Style Registry
#######################

This page describes an example user-defined :class:`.Style` registry class,
which purpose is to keep all the formats defined for some field of
application.

The class below is based on a real registry from my other project.

.. code-block::

    import pytermor as pt

    class Styles(pt.Styles):
        self.INDEX = pt.FrozenStyle(fg=pt.cv.GRAY_50, bg=pt.cv.BLACK)
        self.INDEX_ZEROS = pt.FrozenStyle(fg=pt.cv.GRAY_23, bg=pt.cv.BLACK)
        self.INDEX_PREFIX = pt.FrozenStyle(fg=pt.cv.GRAY_30, bg=pt.cv.BLACK)
        self.CPNUM_PREFIX = pt.FrozenStyle(fg=pt.cv.GRAY_30)
        self.RAW_PREFIX = self.INDEX_PREFIX
        self.RAW = self.INDEX
        self.CHAR = pt.FrozenStyle(fg=0xFFFFFF, bg=0)
        self.INVALID = pt.FrozenStyle(fg=pt.cv.GRAY_30)
        self.PLAIN = pt.FrozenStyle(fg=pt.cv.GRAY_50)
        self.TOTALS = pt.FrozenStyle(overlined=True)

-----------------------------------
Immutability
-----------------------------------

...

.. _examples.style-merging:

-----------------------------------
Style merging example
-----------------------------------

Style merging allows to build complex style conditions, e.g. take a look into
`Highlighter.colorize()` method::

    int_st = merge_styles(st, fallbacks=[Style(bold=True)])

Instead of using ``Style(st, bold=True)`` the merging algorithm is invoked.
This changes the logic of "bold" attribute application -- if there is a
necessity to explicitly forbid bold text at origin/parent level, one could write::

    STYLE_NUL = Style(STYLE_DEFAULT, cv.GRAY, bold=False)
    STYLE_PRC = Style(STYLE_DEFAULT, cv.MAGENTA)
    STYLE_KIL = Style(STYLE_DEFAULT, cv.BLUE)
    ...

Resulting ``int_st`` will be bold for all styles except ``STYLE_NUL``:

    >>> from pytermor import merge_styles, Style, cv
    >>> merge_styles(Style(fg=cv.BLUE), fallbacks=[Style(bold=True)])
    <Style[blue +BOLD]>

    >>> merge_styles(Style(fg=cv.GRAY, bold=False), fallbacks=[Style(bold=True)])
    <Style[gray -BOLD]>

-----------------------------------
Attaching logic
-----------------------------------

.. code-block::

    class VarTableStyles(pt.Styles):
        def __init__(self):
            self.VARIABLE_KEY_FMT = FrozenStyle(fg=pt.cvr.AIR_SUPERIORITY_BLUE, bold=True)
            self.VARIABLE_PUNCT_FMT = FrozenStyle(fg=pt.cvr.ATOMIC_TANGERINE)
            self.VARIABLES_FMT = {
                str: FrozenStyle(fg=pt.cvr.YOUNG_BAMBOO),
                int: FrozenStyle(fg=pt.cvr.CELESTIAL_BLUE),
                float: FrozenStyle(fg=pt.cvr.CELESTIAL_BLUE),
                bool: FrozenStyle(fg=pt.cvr.ICATHIAN_YELLOW),
            }

        def format_variable(self, v: any) -> pt.Fragment:
            if type(vc := v) in self.VARIABLES_FMT.keys():
                if isinstance(v, float):
                    vc = f"{v:.2f}"
                elif isinstance(v, bool) or isinstance(v, int):
                    vc = str(v)
                return pt.Fragment(vc, self.VARIABLES_FMT.get(type(v)))
            return self.format_variable(str(v))
