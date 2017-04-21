import difflib

import pytest

from diffhtml.ndiff import (
    format_tag, ndiff,
    BlockDiffContext, InlineDiffContext,
)


def test_format_tag():
    result = format_tag(('<div>', '</div>'), '<br>')
    assert result == '<div>&lt;br&gt;</div>'


inline_examples = [
    ('<foo><bark><buz>', '<food><bar><rex>'),
]


@pytest.mark.parametrize(('a', 'b'), inline_examples)
def test_inline_equal(a, b):
    ctx = InlineDiffContext(a, b, 5, 9, 6, 10)
    assert ctx.dump_equal() == ('&lt;bar', '&lt;bar')


@pytest.mark.parametrize(('a', 'b'), inline_examples)
def test_inline_delete(a, b):
    ctx = InlineDiffContext(a, b, 11, 16, None, None)
    assert ctx.dump_delete() == ('<del>&lt;buz&gt;</del>', '')


@pytest.mark.parametrize(('a', 'b'), inline_examples)
def test_inline_insert(a, b):
    ctx = InlineDiffContext(a, b, None, None, 11, 16)
    assert ctx.dump_insert() == ('', '<ins>&lt;rex&gt;</ins>')


@pytest.mark.parametrize(('a', 'b'), inline_examples)
def test_inline_replace(a, b):
    ctx = InlineDiffContext(a, b, 11, 16, 11, 16)
    result = ctx.dump_replace()
    assert result == ('<del>&lt;buz&gt;</del>', '<ins>&lt;rex&gt;</ins>')


@pytest.mark.parametrize(('a', 'b'), inline_examples)
def test_inline_crunch(a, b):
    cruncher = difflib.SequenceMatcher(difflib.IS_CHARACTER_JUNK)
    result = list(InlineDiffContext.crunch(cruncher, a, b))
    assert result == [
        ('&lt;foo',) * 2,
        ('', '<ins>d</ins>'),   # Insertion.
        ('&gt;&lt;bar',) * 2,
        ('<del>k</del>', ''),   # Deletion.
        ('&gt;&lt;',) * 2,
        ('<del>buz</del>', '<ins>rex</ins>'),   # Replace.
        ('&gt;',) * 2,
    ]


block_examples = [
    (
        ['<foo>', '<buz>', '<rex>', '<mos>', '<nod>', '<doy>'],
        ['<foo>', '<bar>', '<buz>', '<mos>', '<rod>', '<dug>'],
    ),
]


@pytest.mark.parametrize(('a', 'b'), block_examples)
def test_block_equal(a, b):
    ctx = BlockDiffContext(a, b, 0, 1, 0, 1)
    assert list(ctx.dump_equal()) == ['&lt;foo&gt;']


@pytest.mark.parametrize(('a', 'b'), block_examples)
def test_block_delete(a, b):
    ctx = BlockDiffContext(a, b, 2, 3, None, None)
    assert list(ctx.dump_delete()) == ['<del>&lt;rex&gt;</del>']


@pytest.mark.parametrize(('a', 'b'), block_examples)
def test_block_insert(a, b):
    ctx = BlockDiffContext(a, b, None, None, 1, 2)
    assert list(ctx.dump_insert()) == ['<ins>&lt;bar&gt;</ins>']


@pytest.mark.parametrize(('a', 'b'), block_examples)
def test_block_replace(a, b):
    ctx = BlockDiffContext(a, b, 3, 6, 3, 6, cutoff=0.8)
    assert list(ctx.dump_replace()) == [
        # Identical.
        '&lt;mos&gt;',

        # Similar enough to trigger inline diff.
        '<del>&lt;<del>n</del>od&gt;</del>',
        '<ins>&lt;<ins>r</ins>od&gt;</ins>',

        # Not similar enough.
        '<del>&lt;doy&gt;</del>',
        '<ins>&lt;dug&gt;</ins>',
    ]


@pytest.mark.parametrize(('a', 'b'), block_examples)
def test_ndiff(a, b):
    assert list(ndiff(a, b)) == [
        '&lt;foo&gt;',
        '<ins>&lt;bar&gt;</ins>',
        '&lt;buz&gt;',
        '<del>&lt;rex&gt;</del>',
        '&lt;mos&gt;',
        '<del>&lt;<del>n</del>od&gt;</del>',
        '<ins>&lt;<ins>r</ins>od&gt;</ins>',
        '<del>&lt;doy&gt;</del>',
        '<ins>&lt;dug&gt;</ins>',
    ]
