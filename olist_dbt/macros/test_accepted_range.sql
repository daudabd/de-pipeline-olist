{% test accepted_range(model, column_name, min_value=none, max_value=none, inclusive=true) %}

with validation as (

    select {{ column_name }} as test_value
    from {{ model }}

),

validation_errors as (

    select test_value
    from validation
    where
    {% if min_value is not none %}
        {% if inclusive %} test_value < {{ min_value }}
        {% else %} test_value <= {{ min_value }}
        {% endif %}
    {% endif %}
    {% if min_value is not none and max_value is not none %} or {% endif %}
    {% if max_value is not none %}
        {% if inclusive %} test_value > {{ max_value }}
        {% else %} test_value >= {{ max_value }}
        {% endif %}
    {% endif %}

)

select * from validation_errors

{% endtest %}
