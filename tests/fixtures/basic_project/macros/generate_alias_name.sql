{# Generate an alias for a model based on its name and materialization #}
{% macro generate_alias_name(custom_alias_name=none, node=none) -%}
    {%- if custom_alias_name is none -%}
        {{ node.name }}
    {%- else -%}
        {{ custom_alias_name | trim }}
    {%- endif -%}
{%- endmacro %}


{# A custom macro for tests #}
{% macro cents_to_dollars(column_name) -%}
    ({{ column_name }} / 100.0)
{%- endmacro %}
