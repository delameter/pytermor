====================
Use cases
====================

.. code-block:: python

   from pytermor import span
   print(span.blue('Use'), span.cyan('cases'))


`Span` is a combination of two control sequences; it wraps specified string with pre-defined leading and trailing SGR definitions.


Nested formats
-----------------

Preset spans can safely overlap with each other (as long as they require different `breaker` sequences to reset).

.. code-block:: python

   from pytermor import span

   print(span.blue(span.underlined('Nested') + span.bold(' formats')))

.. image:: https://user-images.githubusercontent.com/50381946/161387692-4374edcb-c1fe-438f-96f1-dae3c5ad4088.png
   :align: center


Content-aware nesting
------------------------

Compose text spans with automatic content-aware format termination.

.. code-block:: python

   from pytermor import autocomplete

   span1 = autocomplete('hi_cyan', 'bold')
   span2 = autocomplete('bg_black', 'inversed', 'underlined', 'italic')

   msg = span1(f'Content{span2("-aware format")} nesting')
   print(msg)

.. image:: https://user-images.githubusercontent.com/50381946/161387711-23746520-419b-4917-9401-257854ff2d8a.png
   :align: center


Flexible sequence builder
----------------------------

Create your own `SGR sequences` with ``build()`` method, which accepts color/attribute keys, integer codes and even existing `SGR`-s, in any amount and in any order. Key resolving is case-insensitive.

.. code-block:: python

   from pytermor import sequence, build

   seq1 = build('red', 1)  # keys or integer codes
   seq2 = build(seq1, sequence.ITALIC)  # existing SGRs as part of a new one
   seq3 = build('underlined', 'YELLOW')  # case-insensitive

   msg = f'{seq1}Flexible{sequence.RESET} ' + \
         f'{seq2}sequence{sequence.RESET} ' + \
         str(seq3) + 'builder' + str(sequence.RESET)
   print(msg)

.. image:: https://user-images.githubusercontent.com/50381946/161387734-677d5b10-15c1-4926-933f-b1144b0ce5cb.png
   :align: center


256 colors support
------------------------------------

Use ``color_indexed()`` to set foreground/background color to any of `↗ xterm-256 colors <https://www.ditig.com/256-colors-cheat-sheet>`_.

.. code-block:: python

   from pytermor import color_indexed, sequence, autocomplete

   txt = '256 colors support'
   start_color = 41
   msg = ''
   for idx, c in enumerate(range(start_color, start_color+(36*6), 36)):
       msg += f'{color_indexed(c)}{txt[idx*3:(idx+1)*3]}{sequence.COLOR_OFF}'

   print(autocomplete(sequence.BOLD).wrap(msg))

.. image:: https://user-images.githubusercontent.com/50381946/161387746-0a94e3d2-8295-478c-828c-333e99e5d50a.png
   :align: center


True Color support
---------------------

Support for 16M-color mode (or True Color) — with ``color_rgb()`` wrapper method.

.. code-block:: python

   from pytermor import color_rgb, sequence, span

   txt = 'True color support'
   msg = ''
   for idx, c in enumerate(range(0, 256, 256//18)):
       r = max(0, 255-c)
       g = max(0, min(255, 127-(c*2)))
       b = c
       msg += f'{color_rgb(r, g, b)}{txt[idx:(idx+1)]}{sequence.COLOR_OFF}'

   print(span.bold(msg))

.. image:: https://user-images.githubusercontent.com/50381946/161411577-743b9a81-eac3-47c0-9b59-82b289cc0f45.png
   :align: center
