import pathlib

import diffhtml
import flask

from flask import request
from markupsafe import Markup


app = flask.Flask(
    'Diff-HTML Demo',
    template_folder=pathlib.Path(__file__).parent.joinpath('templates'),
)


DEFAULT_A = """
I am the very model of a modern Major-General,
I've information vegetable, animal, and mineral,
I know the kings of England, and I quote the fights historical,
From Marathon to Waterloo, in order categorical.
"""

DEFAULT_B = """
I am the very model of an anime individual,
I've information on comical, unusual, and moe girl,
I know the girls from galgames, and I quote the lines all chuunibyo,
From Neo Eva to SAO, down to the very last detail.
"""


@app.route('/ndiff', methods=['GET', 'POST'])
def ndiff():
    a = request.form.get('a', DEFAULT_A)
    b = request.form.get('b', DEFAULT_B)
    try:
        cutoff = float(request.form.get('cutoff', 0.6))
    except ValueError:
        cutoff = 0.6
    context = {
        'result': None,
        'cutoff': cutoff,
        'input': {'a': a, 'b': b},
    }
    if request.method == 'POST':
        context['result'] = Markup('<br>').join(diffhtml.ndiff(
            a.splitlines(), b.splitlines(), cutoff=cutoff,
        ))
    return flask.render_template('ndiff.html', **context)


@app.route('/')
def home():
    return flask.redirect(flask.url_for('ndiff'))


if __name__ == '__main__':
    app.run()
