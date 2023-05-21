---
{%- set p = salt.pillar.get("variable", "fails") %}
do something significant:
  test.show_notification:
    - text: Woohoo this {{ p }}

{%- if p == "fails" %}
fail miserably:
  test.fail_without_changes:
{%- endif -%}
