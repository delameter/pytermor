.. _examples:

###################
     Examples
###################

Most basic example:

.. code-block:: python
   :class: highlight-adjacent

    import pytermor as pt

    pt.force_ansi_rendering()
    pt.echo('RED', 'red')
    pt.echo('GREEN', pt.cv.GREEN)
    pt.echo("This is warning, be warned", pt.Styles.WARNING)

.. container:: highlight highlight-manual highlight-adjacent output

   | :red:`red text`
   | :lime:`green text`
   | :orange:`This is warning, be warned`

For more advanced ones proceed to the next section.

.. toctree::

   rendering
