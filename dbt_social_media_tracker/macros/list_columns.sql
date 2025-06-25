{% macro list_columns(table_name, schema_name) %}
  {% set columns = adapter.get_columns_in_relation(adapter.get_relation(
      database=target.database,
      schema=schema_name,
      identifier=table_name
  )) %}
  {% for column in columns %}
    {{ column.name }}{% if not loop.last %},{% endif %}
  {% endfor %}
{% endmacro %}
