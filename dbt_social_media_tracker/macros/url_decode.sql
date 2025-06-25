-- URL decode macro for Japanese characters with key patterns (focusing on most common ones)
{% macro url_decode(column_name) %}
  CASE
    WHEN {{ column_name }} LIKE '%25%' OR {{ column_name }} LIKE '%E3%' OR {{ column_name }} LIKE '%e3%' THEN
      -- Essential Japanese characters for artist names (12 REPLACE functions)
      REPLACE(
        REPLACE(
          REPLACE(
            REPLACE(
              REPLACE(
                REPLACE(
                  REPLACE(
                    REPLACE(
                      REPLACE(
                        REPLACE(
                          REPLACE(
                            REPLACE(
                              {{ column_name }},
                              '%E3%83%9F', 'ミ'),  -- Mi uppercase
                            '%e3%83%9f', 'ミ'),  -- Mi lowercase
                          '%E3%82%BA', 'ズ'),    -- Zu uppercase
                        '%e3%82%ba', 'ズ'),    -- Zu lowercase
                      '%E3%83%8B', 'ニ'),      -- Ni uppercase
                    '%e3%83%8b', 'ニ'),      -- Ni lowercase
                  '%E3%82%A6', 'ウ'),        -- U uppercase
                '%e3%82%a6', 'ウ'),        -- U lowercase
              '%E3%82%AD', 'キ'),          -- Ki uppercase
            '%e3%82%ad', 'キ'),          -- Ki lowercase
          '%E3%82%AF', 'ク'),            -- Ku uppercase
        '%e3%82%af', 'ク')            -- Ku lowercase
    ELSE {{ column_name }}
  END
{% endmacro %}
