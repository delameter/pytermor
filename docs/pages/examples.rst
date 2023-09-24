.. _examples:

#################
    Examples
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
Rendering · High-level
-----------------------------------

Imagine we want to colorize ``git --help`` output *manually*, i.e., we will not
pipe an output of ``git`` and apply filters to do the job (yet), instead we
copy-paste the output to python source code files as string literals and will try
to add a formatting using all primary approaches.

.. literalinclude:: /demo/examples/input.txt
   :language: plain
   :caption: Part of the input

.. include:: /demo/examples/output.rst

The examples in this part are sorted from simple ones at the beginning to
complicated ones at the end.

Separated pre-rendering
================================
Use `render()` method to apply a :term:`style` to a string part individually for
each of them.

.. literalinclude:: /demo/examples/prerender.py
   :linenos:

.. include:: /demo/examples/prerender.rst

`render()` method uses `SgrRenderer` by default, which is set up automatically
depending on output device characteristics and environment setup.

Note that ``render()`` accepts `FT` as format argument, which can be `Style` or
`Color` or *str* or *int* (there is a few methods to define a color).

Fragments
====================
`Fragment` is a basic class implementing `IRenderable` interface and contains a
text string along with a `Style` instance and that's it.

``Fragment`` instances can be safely concatenated with a regular *str* (but not
with another `Fragment`) from the left side as well as from the right side (line
#15). If you attempt to add one ``Fragment`` to another ``Fragment``, you'll end
up with a `Text` instance (see the example after next).

.. literalinclude:: /demo/examples/fragments.py
   :linenos:

.. include:: /demo/examples/fragments.rst

Fragments in f-strings
======================
Another approach to align a formatted text is to combine Python's *f-strings*
with `Fragment` instances.

.. literalinclude:: /demo/examples.fragments-fstrings.py
   :linenos:

.. only:: html

   .. raw:: html
       :file: ../demo/examples.fragments-fstrings.html

.. only:: latex

   .. figure:: /demo/examples.fragments-fstrings.svg
      :align: center

Texts & FrozenTexts
====================
`Text` is a general-purpose composite `IRenderable` implementation, which can
contain any amount of strings linked with styles (i.e. `Fragment` instances).

``Text`` also supports aligning, padding with specified chars to specified width,
but most importantly it supports :def:`fargs` syntax (for the details see `guide.fargs`),
which allows to compose formatted text parts much faster and keeps the code compact. Generally
speaking, the basic input parameter is either a tuple of string and `Style` or `Color`,
which then will be applied to preceeding string, or a standalone string. Usually
explicit definition of a tuple is not neccessary, but there are cases, when it is.

.. literalinclude:: /demo/examples.texts.py
   :linenos:

.. only:: html

   .. raw:: html
       :file: ../demo/examples.texts.html

.. only:: latex

   .. figure:: /demo/examples.texts.svg
      :align: center

`FrozenText` is immutable version of `Text` (to be precise, its quite the
opposite: ``Text`` is a child of ``FrozenText``).

We will utilize aligning capabilities of ``FrozenText`` class in a following
code fragment:

.. literalinclude:: /demo/examples.frozentexts.py
   :linenos:

.. only:: html

   .. raw:: html
       :file: ../demo/examples.frozentexts.html

.. only:: latex

   .. figure:: /demo/examples.frozentexts.svg
      :align: center

At line #13 we compose a `FrozenText` instance with command name and set up
desired width (18=16+2 for left padding), and explicitly set up right padding
with ``pad`` argument. Padding chars will be applied to the left, right or both
sides depending on ``align`` argument.

Note that although `echo()` accepts a single `RT` as a first argument,
it also accepts a sequence of them, which allows us to call ``echo`` just
once. `RT` is a type var including *str* type and all `IRenderable`
implementations.

Templates
========================
There is a support of library's internal tag format, which allows to inline
formatting into the original string, and get the final result by calling just
one method:

.. literalinclude:: /demo/examples.templates.py
   :linenos:

.. only:: html

   .. raw:: html
       :file: ../demo/examples.templates.html

.. only:: latex

   .. figure:: /demo/examples.templates.svg
      :align: center

Here ``@st:[fg=yellow bold]`` is a definition of a custom user style named ``st``,
``:[st]`` is a opening tag for that style, and ``:[-]`` is a closing tag matching
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
string being passed as 2nd argument will be ``ESC [ 32m \1 ESC [ m``. Regexp
substitution function will replace all ``\1`` with a matching group in every
line of the input, therefore the match will end up being surrounded with
(already rendered) SGRs responsible for green text color, ???, PROFIT:

.. literalinclude:: /demo/examples.regexp-group-rendering.py
   :linenos:
   :end-before: [extra-1-start]

.. only:: html

   .. raw:: html
       :file: ../demo/examples.regexp-group-rendering.html

.. only:: latex

   .. figure:: /demo/examples.regexp-group-rendering.svg
      :align: center

For more complex logic it's usually better to extract it into separate function:

.. literalinclude:: /demo/examples.regexp-group-rendering.py
   :linenos:
   :start-after: [extra-1-start]
   :end-before: [extra-1-end]

Another approach:

.. literalinclude:: /demo/examples.regexp-group-rendering.py
   :linenos:
   :start-after: [extra-2-start]
   :end-before: [extra-2-end]

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

.. literalinclude:: /demo/examples.refilters.py
   :linenos:

.. only:: html

   .. raw:: html
       :file: ../demo/examples.refilters.html

.. only:: latex

   .. figure:: /demo/examples.refilters.svg
      :align: center

.. _rendering-low-level:

-----------------------------------
Rendering · Low-level
-----------------------------------

The examples in this part are sorted from simple (for the developer) ones at the beginning to
complicated (for the developer) ones at the end. But after you change the point of view, the
results are reversed: first ones are most complicated for the interpreter to run, while the
ones at the end are simplest (roughly one robust method per instance is invoked). Therefore,
the answer to the question "which method is most suitable" should always be evaluated on the
individual basis.

Preset compositions
====================================
Preset composition methods produce sequence instances or already rendered
sequence bytes as if they were rendered by `SgrRenderer`. Methods with
names starting with ``make_`` return seq. instances, and methods named
``compose_*`` return *str*, which means that more than one sequence were
involved.

In the next example we create an SGR which colors text to black, and bg to
:hex:`0xffaf00` (line #3), then compose a sequence chain which includes:

    - :abbr:`CUP (Cursor Position)` instruction: ``ESC [1;1H``;
    - SGR instruction with our prev. defined colors: ``ESC [30;48;5;214m``;
    - :abbr:`EL (Erase in Line)` instruction: ``ESC [0K``.

Effectively this results in a whole terminal line colored with colors specified,
and note that we did not fill the line with spaces or something like that --
this method is (in theory) faster, because the tty needs to process only ~10-20
characters of input instead of 120+ (average terminal width).

.. literalinclude:: /demo/examples/preset-compositons.py
   :linenos:

.. include:: /demo/examples/preset-compositons.rst

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
while there we pick and insert a closing sequence manually.

.. literalinclude:: /demo/examples.auto-wrap.py
   :linenos:

.. only:: html

   .. raw:: html
       :file: ../demo/examples.auto-wrap.html

.. only:: latex

   .. figure:: /demo/examples.auto-wrap.svg
      :align: center

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
directly without any modifications.

.. literalinclude:: /demo/examples.manual-wrap.py
   :linenos:

.. only:: html

   .. raw:: html
       :file: ../demo/examples.manual-wrap.html

.. only:: latex

   .. figure:: /demo/examples.manual-wrap.svg
      :align: center

Manual instantiating
====================================
In case of necessity of some non-standard sequence types or "illegal" parameter
values there is also a possibility to build the sequence from the scratch,
instantiating one of the base sequence classes and providing required parameters
values.

If your case is covered with an existing helper method in `term` package, use it
instead of making new instance directly. This approach will make it easier to
maintain the code, if something in internal logic of sequence base classes changes
in the future.

.. code:: python

   print(pt.SequenceCSI("J", 2).assemble(), end="")
   # equivalent to
   print(pt.make_erase_in_display(2).assemble(), end="")

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

Even if it seems OK for a while:

.. code-block:: python

    print('\x1b[41m', end="(；¬＿¬)")
    print('\x1b[41m\x1b[2J\x1b[1;1H', end="(O∆O)")

...things get worse pretty fast:

.. code-block:: python
   :emphasize-lines: 1

   print('\x1b[38;2;232;232;22m\x1b[1;41m\x1b[2J\x1b[1;1H', end="(╯°□°)╯")

Compare with the next fragment, which does literally the same as the *highlighted line*
from the example above, but is much easier to read thanks to low-level abstractions:

.. code-block:: python

    print(pt.make_color_rgb(232, 232, 22), end="")
    print(pt.ansi.SeqIndex.BOLD + pt.ansi.SeqIndex.BG_RED, end="")
    print(pt.make_erase_in_display(2).assemble(), end="")
    print(pt.make_reset_cursor().assemble(), end="(°~°)")

Or after adding some high-level abstractions as well:

.. code-block:: python

    st = pt.Style(fg=0xe8e816, bg='red', bold=True)
    fill = pt.compose_clear_line_fill_bg(st.fg.to_sgr())
    pt.echo(fill + "(°v°♡)", st)

.. an empty comment that prevents pycharm from eating up
   two consecutive newlines at the end, which are required
   when the article ends with a code block
