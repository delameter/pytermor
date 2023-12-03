#################
   Rendering
#################

The library can be split into two domains, the first one being "**high**\ -level"
domain, which includes templating, style abstractions, text implementations
which support aligning, wrapping, padding, etc., as well as number formatting
helpers and a registry of preset colors.

The second one is "**low**\ -level", containing colors and color spaces
definitions, helpers for composing various terminal escape sequences, the escape
sequence abstractions themselves, as well as a large set of filters for
chain-like application.


.. _rendering-high-level:

-----------------------------------
High-level
-----------------------------------

Imagine we want to colorize ``git --help`` output *manually*, i.e., we will not
pipe an output of ``git`` and apply filters to do the job (yet), instead we
copy-paste the output to python source code files as string literals and will try
to add a formatting using all primary approaches.

.. code-block:: plain
   :caption: Part of the input

    These are common Git commands used in various situations:

    start a working area (see also: git help tutorial)
       clone             Clone a repository into a new directory
       init              Create an empty Git repository or reinitialize an existing one
       [..]

.. container:: code-block-caption outputcaption

    Part of the output

.. container:: highlight highlight-manual highlight-adjacent output

    | These are common Git commands used in various situations:
    |
    | :yellow:`start a working area` (see also: :lime:`git help tutorial`)
    | |nbspt3|\ :lime:`clone`\ |nbspt13|\ Clone a repository into a new directory
    | |nbspt3|\ :lime:`init`\ |nbspt14|\ Create an empty Git repository or reinitialize an existing one
    | |nbspt3|\ [..]


The examples in this part are sorted from simple ones at the beginning to
complicated ones at the end.

Isolated pre-rendering
================================
.. highlight:: python
   :linenothreshold: 5

Use `render()` method to apply a :term:`style` to a string part individually for
each of them::

    import pytermor as pt

    subtitle = pt.render("start a working area", pt.Style(fg=pt.cv.YELLOW, bold=True))
    subtitle += " (see also: "
    subtitle += pt.render("git help tutorial", pt.cv.GREEN)
    subtitle += ")"

    pt.echo(subtitle)

.. container:: highlight highlight-manual highlight-adjacent output

    :yellow:`start a working area` (see also: :lime:`git help tutorial`)


`render()` method uses `SgrRenderer` by default, which is set up automatically
depending on output device characteristics and environment setup.

Note that ``render()`` accepts `FT` as format argument, which can be `Style` or
`Color` or *str* or *int* (there are a few ways to define a color).

Fragments
====================
`Fragment` is a basic class implementing `IRenderable` interface and contains a
text string along with a `Style` instance and that's it.

``Fragment`` instances can be safely concatenated with a regular *str* (but not
with another `Fragment`) from the left side as well as from the right side
(highlighted line). If you attempt to add one ``Fragment`` to another
``Fragment``, you'll end
up with a `Text` instance (see the example after next).

.. code-block::
   :emphasize-lines: 12

    from collections.abc import Iterable
    import pytermor as pt

    data = [
        ("clone", "Clone a repository into a new directory"),
        ("init", "Create an empty Git repository or reinitialize an existing one"),
    ]

    st = pt.Style(fg=pt.cv.GREEN)
    for name, desc in data:
        frag = pt.Fragment(name.ljust(16), st)
        pt.echo('  ' + frag + desc)

.. container:: highlight highlight-manual highlight-adjacent output

    | |nbspt3|\ :lime:`clone`\ |nbspt13|\ Clone a repository into a new directory
    | |nbspt3|\ :lime:`init`\ |nbspt14|\ Create an empty Git repository or reinitialize an existing one

Fragments in f-strings
======================
Another approach to align a formatted text is to combine Python's *f-strings*
with `Fragment` instances::

    import pytermor as pt

    data = [
        ("bisect", "Use binary search to find the commit that introduced a bug"),
        ("diff", "Show changes between commits, commit and working tree, etc"),
        ("grep", "Print lines matching a pattern"),
    ]

    st = pt.Style(fg=pt.cv.GREEN)
    for name, desc in data:
        frag = pt.Fragment(name, st)
        pt.echo(f"  {frag:<16s}    {desc}")

.. container:: highlight highlight-manual highlight-adjacent output

    | |nbspt3|\ :lime:`bisect`\ |nbspt12|\ Use binary search to find the commit that introduced a bug
    | |nbspt3|\ :lime:`diff`\ |nbspt14|\ Show changes between commits, commit and working tree, etc
    | |nbspt3|\ :lime:`grep`\ |nbspt14|\ Print lines matching a pattern

Texts & FrozenTexts
====================
`Text` is a general-purpose composite `IRenderable` implementation, which can
contain any amount of strings linked with styles (i.e. `Fragment` instances).

``Text`` also supports aligning, padding with specified chars to specified width,
but most importantly it supports :def:`fargs` syntax (for the details see `guide.fargs`),
which allows to compose formatted text parts much faster and keeps the code compact. Generally
speaking, the basic input parameter is either a tuple of string and `Style` or `Color`,
which then will be applied to preceeding string, or a standalone string. Usually
explicit definition of a tuple is not neccessary, but there are cases, when it is::

    import pytermor as pt

    subtitle_st = pt.Style(fg=pt.cv.YELLOW, bold=True)
    command_st = pt.Style(fg=pt.cv.GREEN)
    text = pt.FrozenText(
        ("work on the current change ", subtitle_st),
        "(see also: ",
        "git help everyday", command_st,
        ")"
    )
    pt.echo(text)

.. container:: highlight highlight-manual highlight-adjacent output

    :yellow:`work on the current change` (see also: :lime:`git help everyday`\ )

`FrozenText` is an immutable version of `Text` (to be precise, its quite the
opposite: ``Text`` is a child of ``FrozenText``).

We will utilize aligning capabilities of ``FrozenText`` class in a following
code fragment:

.. code-block::
   :emphasize-lines: 11

    import pytermor as pt

    data = [
        ("add", "Add file contents to the index"),
        ("mv", "Move or rename a file, a directory, or a symlink"),
        ("restore", "Restore working tree files"),
    ]
    st = pt.Style(fg=pt.cv.GREEN)

    for name, desc in data:
        pt.echo([pt.FrozenText("  ", name, st, width=18, pad=4), desc])

.. container:: highlight highlight-manual highlight-adjacent output

    | |nbspt3|\ :lime:`add`\ |nbspt15|\ Add file contents to the index
    | |nbspt3|\ :lime:`mv`\ |nbspt15| Move or rename a file, a directory, or a symlink
    | |nbspt3|\ :lime:`restore`\ |nbspt11|\ Restore working tree files

At highlighted line we compose a `FrozenText` instance with command
name and set up desired width (18=16+2 for right margin), and explicitly set up
left padding with ``pad`` argument. Padding chars and regular spaces originating
from the alignment process are always applied to the opposite sides of text.

Note that although `text.echo()` accepts a single `RT` as a first argument,
it also accepts a sequence of them, which allows us to call ``echo`` just
once. `common.RT` is a type var including *str* type and all `IRenderable`
implementations.

Template tags
========================
There is a support of library's internal tag format, which allows to inline
formatting into the original string, and get the final result by calling just
one method::

    import pytermor as pt

    s = """@st:[fg=yellow bold] @cmd:[fg=green]
    :[st]grow, mark and tweak your common history:[-]
       :[cmd]branch:[-]            List, create, or delete branches
       :[cmd]commit:[-]            Record changes to the repository
       :[cmd]merge:[-]             Join two or more development histories together
    """
    pt.echo(pt.TemplateEngine().substitute(s))

.. container:: highlight highlight-manual highlight-adjacent output

    | |nbspt3|\ :lime:`branch`\ |nbspt12|\ List, create, or delete branches
    | |nbspt3|\ :lime:`commit`\ |nbspt12|\ Record changes to the repository
    | |nbspt3|\ :lime:`merge`\ |nbspt13|\ Join two or more development histories together

Here ``"@st:[fg=yellow bold]"`` is a definition of a custom user style named *"st"*,
``":[st]"`` is a opening tag for that style, and ``":[-]"`` is a closing tag matching
the most recently opened one. See `guide.templates` for the details.

  .. Template postprocessing
  .. ========================
  .. .. currently as es7s midddleware
  .. .. todo :: @TODO

Regexp group substitution
=========================
A little bit artificial example, but this method can be applied to
solve real tasks nevertheless. The trick is to apply the desired style
to a string containing special characters like ``r"\1"``, which
will represent regexp group 1 after passing it into ``re.sub()``. The actual
string being passed as 2nd argument will be ``" ESC [ 32m \1 ESC [ m"``. Regexp
substitution function will replace all ``"\1"`` with a matching group in every
line of the input, therefore the match will end up being surrounded with
(already rendered) SGRs responsible for green text color, ???, PROFIT::

    import re
    import pytermor as pt

    s = """
       fetch             Download objects and refs from another repository
       pull              Fetch from and integrate with another repository or a local branch
       push              Update remote refs along with associated objects
    """

    regex = re.compile(r"^(\s+)(\S+)(.+)$")
    for line in s.splitlines():
        pt.echo(
            regex.sub(
                pt.render(r"\1" + pt.Fragment(r"\2", pt.cv.GREEN) + r"\3"),
                line,
            )
        )

.. container:: highlight highlight-manual highlight-adjacent output

    | |nbspt3|\ :lime:`fetch`\ |nbspt13|\ Download objects and refs from another repository
    | |nbspt3|\ :lime:`pull`\ |nbspt14|\ Fetch from and integrate with another repository or a local branch
    | |nbspt3|\ :lime:`push`\ |nbspt14|\ Update remote refs along with associated objects

For more complex logic it's usually better to extract it into separate function::

    def replace_expand(m: re.Match) -> str:
        tpl = pt.render(r"\1" + pt.Fragment(r"\2", pt.cv.GREEN) + r"\3")
        return m.expand(tpl)
    regex.sub(replace_expand, "...")

Another approach::

    def replace_manual(m: re.Match) -> str:
        return pt.render(m.group(1) + pt.Fragment(m.group(2), pt.cv.GREEN) + m.group(3))
    regex.sub(replace_manual, "...")

Refilters
========================
Refilters (**Re**\ ndering **filter**\ s) are usually applied in sequences, where
each of those matches one or two named regexp groups and applies the specified
styles accordingly.

In the example below we first (#10-12) implement ``_render()`` method in a new
class inherited from `AbstractNamedGroupsRefilter`, then (#14-16) the refilter
is created (note regexp group name ``'cmd'`` and matching dictionary key, which
value is a `FT`), then (#19) the refilter is applied and result is printed.

.. note ::

   Although filters in general are classified as **low**\ -level, this example
   is placed into **high**\ -level group, because no manipulation at byte level
   or at color channel level is performed.

::

    import re
    import pytermor as pt

    s = """
       reset             Reset current HEAD to the specified state
       switch            Switch branches
       tag               Create, list, delete or verify a tag object signed with GPG
    """

    class SgrNamedGroupsRefilter(pt.AbstractNamedGroupsRefilter):
        def _render(self, v: pt.IT, st: pt.FT) -> str:
            return pt.render(v, st, pt.SgrRenderer)

    f = SgrNamedGroupsRefilter(
        re.compile(r"(\s+)(?P<cmd>\S+)(.+)"),
        {"cmd": pt.cv.GREEN},
    )

    pt.echo(pt.apply_filters(s, f))

.. container:: highlight highlight-manual highlight-adjacent output

    | |nbspt3|\ :lime:`reset`\ |nbspt13|\ Reset current HEAD to the specified state
    | |nbspt3|\ :lime:`switch`\ |nbspt12|\ Switch branches
    | |nbspt3|\ :lime:`tag`\ |nbspt15|\ Create, list, delete or verify a tag object signed with GPG


.. _rendering-low-level:

-----------------------------------
Low-level
-----------------------------------

The examples in this part are sorted from simple (for the developer) ones at the beginning to
complicated (for the developer) ones at the end. But after you change the point of view, the
results are reversed: first ones are most complicated for the interpreter to run, while the
ones at the end are simplest (roughly one robust method per instance is invoked). Therefore,
the answer to the question "which method is most suitable" should always be evaluated on the
individual basis.

Preset compositions
====================================
Preset composition methods produce sequence instances or ready-to-print
strings as if they were rendered by `SgrRenderer`. Methods with
names starting with ``make_`` return single sequence instance each, while
methods named ``compose_*`` return *str*\ ings which are several sequences
rendered and concatenated.

In the next example we create an SGR which sets background color to
:bgteal:`@`\ :hex:`#008787` (highlighted line) by specifying :term:`xterm-256`
code 30 (see `guide.xterm-256-palette`), then compose a string which includes:

    - :abbr:`CUP (Cursor Position)` instruction: ``ESC [1;1H``;
    - SGR instruction with our color: ``ESC [48;5;30m``;
    - :abbr:`EL (Erase in Line)` instruction: ``ESC [0K``.

Effectively this results in a whole terminal line colored with a specified color,
and note that we did not fill the line with spaces or something like that --
this method is (in theory) faster, because the tty needs to process only ~10-20
characters of input instead of 120+ (average terminal width).

.. code-block::
   :emphasize-lines: 3

    import pytermor as pt

    col_sgr = pt.make_color_256(30, pt.ColorTarget.BG)
    seq = pt.compose_clear_line_fill_bg(col_sgr)
    pt.echo(seq + 'AAAA    BBBB')

.. container:: highlight highlight-manual highlight-adjacent output

    :bgtealline:`AAA    BBBB`

.. note ::

  ``compose_*`` methods do not belong to any `renderer`, so the decision of using
  or not using these depending on a terminal settings should be made by the developer
  on a higher level. The suggested implementation of conditional composite sequences
  would be to request current renderer setup and ensure `is_format_allowed` returns
  *True*, in which case it's ok to write composite sequences (as the default renderer
  already uses them)::

     seq = ""
     if pt.RendererManager.get_default().is_format_allowed:
       seq = pt.compose_clear_line_fill_bg(pt.cv.NAVY_BLUE)
     pt.echo(seq + 'AAAA    BBBB')

.. todo ::

  More consistent way of working with composite sequences would be to merge
  classes from `ansi` module with classes from `text` module, i.e. make
  `ISequence` children also inherit `IRenderable` interface and therefore be
  rendered using the same mechanism as for `Text` or `Fragment`, but that would
  require quite a bit of refactoring and, considering relatively rare usage of
  pre-rendered composites, was deferred for a time.

Assisted wrapping
====================================
Similar to the next one, but here we call helper method `ansi.enclose()`, which
automatically builds the closing sequence complement to specified opening one,
while there we pick and insert a closing sequence manually::

    import pytermor as pt

    pt.echo(pt.enclose(pt.SeqIndex.CYAN, "imported") + " rich.inspect")

.. container:: highlight highlight-manual highlight-adjacent output

    :cyan:`imported` rich.inspect

Manual wrapping
====================================
Pretty straightforward wrapping of target string into a format which, for
example, colors the text with a specified color, can be performed with
f-stings. All inheritors of `ISequence` class implement ``__str__()`` method,
which ensures that they can be safely evaluated in f-strings even without
format specifying.

:def:`Resetter`, of closing sequence, in this case can vary; for example, it can
be "hard-reset" sequence, which resets the terminal format stack completely (``ESC
[m``), or it can be text color reset sequence (``ESC [39m``), or even more exotic
ones.

`SeqIndex` class contains prepared sequences which can be inserted into f-string
directly without any modifications::

    import pytermor as pt

    print(f"{pt.SeqIndex.CYAN}imported{pt.SeqIndex.RESET} rich.inspect", end="")

.. container:: highlight highlight-manual highlight-adjacent output

    :cyan:`imported` rich.inspect

Manual instantiating
====================================
In case of necessity of some non-standard sequence types or "illegal" parameter
values there is also a possibility to build the sequence from the scratch,
instantiating one of the base sequence classes and providing required parameters
values::

    import pytermor as pt

    print(pt.SequenceCSI("J", 2).assemble(), end="")
    # which is equivalent to:
    print(pt.make_erase_in_display(2).assemble(), end="")

If your case is covered with an existing helper method in `term` package, use it
instead of making new instance directly. This approach will make it easier to
maintain the code, if something in internal logic of sequence base classes changes
in the future.

Manual assembling :sup:`(don't do this)`
========================================
The last resort method which works in 100% is to assemble the sequence char by char
manually, contain it as a string in source code and just print it when there is a
necessity to do that. The only problem with this approach is an empirical rule,
which says:

.. highlights::

  Each raw ANSI escape sequence in the source code reduces
  the readability of the whole file by 50%.

This means that even 2 SGRs would give 25% readability of the original, while 4
SGRs give ≈6% :comment:`(this rule is a joke I made up just now, but the key
idea should be true)`.

In short:
    - they are hard to modify,
    - they are hard to maintain,
    - they are hard to debug.

Even if it seems OK for a while::

    print('\x1b[41m', end="(；¬＿¬)")
    print('\x1b[1;1H\x1b[41m\x1b[0K', end="(O∆O)")

...things get worse pretty fast::

    print('\x1b[1;1H\x1b[38;2;232;232;22m\x1b[1;41m\x1b[0K', end="(╯°□°)╯")

Compare with the next fragment, which does literally the same as the line
from the example above, but is much easier to read thanks to low-level abstractions::

    import pytermor as pt
    print(
        pt.make_reset_cursor(),
        pt.make_color_rgb(232, 232, 22),
        pt.ansi.SeqIndex.BOLD,
        pt.ansi.SeqIndex.BG_RED,
        pt.make_erase_in_line(),
        sep="", end="(°~°)",
    )

Or doing the same with high-level abstractions instead::

    import pytermor as pt
    st = pt.Style(fg=0xe8e816, bg='red', bold=True)
    fill = pt.compose_clear_line_fill_bg(st.fg.to_sgr())
    pt.echo(fill + "(°v°♡)", st)

.. container:: highlight highlight-manual highlight-adjacent output

    :yellowonredline:`(°v°♡)`

.. note ::

    The last example also automatically resets the terminal back to normal
    state, so that the text that is printed afterwards doesn't have any formatting,
    in contrast with other examples requiring to assemble and print `SeqIndex.COLOR_OFF`
    and `SeqIndex.BG_COLOR_OFF` (or just `SeqIndex.RESET`) at the end (which is omitted).
