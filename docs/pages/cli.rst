.. _cli:

#####################
CLI usage
#####################

Commands like the ones below can be used for quick experimenting without loading the IDE:

 - One-liner for system-wide installation :comment:`(which is not recommended)`:

   .. code-block:: console
      :class: highlight-adjacent

      $ python -c "import pytermor as pt; pt.echo('RED', 'red')"

   .. raw:: html

      <div class="highlight-adjacent">
         <div class="highlight">
            <pre><span style="color: red">red text</span></pre>
         </div>
      </div>

   .. todo :: Find a solution for embedding colored text into PDF (as SVG -> PNG maybe?)

 - One-liner for virtual environment (`venv`) with `pytermor` pre-installed (see `install`_)
   :comment:`(note that the library source code root folder should be used as current working directory)`:

   .. code-block:: console
      :class: highlight-adjacent

      $ PYTHONPATH=. venv/bin/python -c "import pytermor as pt; pt.echo('GREEN', 'green')"

   .. raw:: html

      <div class="highlight-adjacent">
         <div class="highlight">
            <pre><span style="color: green;">green text</span></pre>
         </div>
      </div>

 - Interactive mode for virtual environment with `pytermor` pre-installed
   :comment:`(again, current working directory should be sources root dir)`:

   .. code-block:: console
      :class: highlight-adjacent

      $ PYTHONSTARTUP=.run-startup.py PYTHONPATH=. venv/bin/python -qi

   .. code-block:: python
      :class: highlight-adjacent

      python 3.8.10
      pytermor 2.41.1-dev1
      >>> pt.echo("This is warning, be warned", pt.Styles.WARNING)

   .. raw:: html

      <div class="highlight-adjacent">
         <div class="highlight">
            <pre><span style="color: orange;">This is warning, be warned</span></pre>
         </div>
      </div>
