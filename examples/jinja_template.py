"""Example of Jinja2 Template
* https://changhsinlee.com/pyderpuffgirls-ep5/
* https://multithreaded.stitchfix.com/blog/2017/07/06/one-weird-trick/
"""

from jinja2 import Template
import plac


@plac.annotations(
)
def main():
    # Initialize client object
    flag_columns = [
        {'key': 'thriller', 'value': 1},
        {'key': 'film_noir', 'value': 2},
        {'key': 'western', 'value': 3}]

    where_clause = '''
    WHERE {% for column in columns %}{% if not loop.first %} AND {% endif %}{{ column['key'] }} = {{ column['value'] }}{% endfor %}
    '''

    print(Template(where_clause).render(columns=flag_columns))


if __name__ == "__main__":
    plac.call(main)
