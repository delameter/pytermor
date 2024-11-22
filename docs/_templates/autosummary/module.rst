{{ fullname | escape | underline}}

{% set cd_ref = ('class_diagram', 'sitemap') %}
{% set refs_cd = ['ansi', 'color', 'filter', 'numfmt', 'renderer', 'text'] %}
{% set refs_extra = {'color': [('transitions', 'retweet')] } %}

{% set refs = [] %}
{% if name in refs_cd %} {% set refs = refs + [cd_ref] %} {% endif %}
{% set refs = refs + refs_extra.get(name, []) %}

{% if refs %}

.. only:: html

    .. sidebar::
        :class: seamless-sidebar

        {% for ref in refs %}

        .. button-ref:: guide.{{ name }}_{{ ref[0] }}
            :color: primary
            :class: fa-{{ ref[1].replace('_', '-') }} sidebar-button sd-text-nowrap
            :outline:

        {%- endfor %}

.. only:: latex

    {% for ref in refs %}

    :fas:`{{ ref[1] }}` `guide.{{ name }}_{{ ref[0] }}`

    {%- endfor %}

{% endif %}

.. automodule:: {{ fullname }}

   {% block attributes %}
   {% if attributes %}
   .. rubric:: {{ _('Module Attributes') }}

   .. autosummary::
   {% for item in attributes %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block functions %}
   {% if functions %}
   .. rubric:: {{ _('Functions') }}

   .. autosummary::
   {% for item in functions %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block classes %}
   {% if classes %}
   .. rubric:: {{ _('Classes') }}

   .. autosummary::
   {% for item in classes %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block exceptions %}
   {% if exceptions %}
   .. rubric:: {{ _('Exceptions') }}

   .. autosummary::
   {% for item in exceptions %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

{% block modules %}
{% if modules %}
.. rubric:: Modules

.. autosummary::
   :toctree:
   :recursive:
{% for item in modules %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}
