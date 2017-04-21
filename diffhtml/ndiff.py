"""Implements a differ that outputs HTML context diff.
"""

import collections
import difflib

import markupsafe


DUMP_HANDLERS = {
    'equal': 'dump_equal',
    'delete': 'dump_delete',
    'insert': 'dump_insert',
    'replace': 'dump_replace',
}


def format_tag(tag, content):
    content = markupsafe.escape(content)
    return markupsafe.Markup('{0}{content}{1}'.format(*tag, content=content))


DiffContext = collections.namedtuple('DiffContext', 'a b loa hia lob hib')


class InlineDiffContext(DiffContext):
    """Context of a inline diff operation.
    """
    insert_tag = ('<ins>', '</ins>')
    delete_tag = ('<del>', '</del>')

    @classmethod
    def crunch(cls, cruncher, a, b):
        cruncher.set_seqs(a, b)
        for tag, ai1, ai2, bi1, bi2 in cruncher.get_opcodes():
            subcontext = cls(a, b, ai1, ai2, bi1, bi2)
            yield getattr(subcontext, DUMP_HANDLERS[tag])()

    def dump_equal(self):
        return (
            markupsafe.escape(self.a[self.loa:self.hia]),
            markupsafe.escape(self.b[self.lob:self.hib]),
        )

    def dump_delete(self):
        return (format_tag(self.delete_tag, self.a[self.loa:self.hia]), '')

    def dump_insert(self):
        return ('', format_tag(self.insert_tag, self.b[self.lob:self.hib]))

    def dump_replace(self):
        return (self.dump_delete()[0], self.dump_insert()[1])


class BlockDiffContext(DiffContext):
    """Context of a diff operation.
    """
    insert_tag = ('<ins>', '</ins>')
    delete_tag = ('<del>', '</del>')

    def __new__(cls, *args, cutoff=0.75, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self.cutoff = cutoff
        return self

    @classmethod
    def crunch(cls, cruncher, a, b):
        for tag, loa, hia, lob, hib in cruncher.get_opcodes():
            context = cls(a, b, loa, hia, lob, hib)
            yield from getattr(context, DUMP_HANDLERS[tag])()

    def dump_equal(self):
        for line in self.a[self.loa:self.hia]:
            yield markupsafe.escape(line)

    def dump_delete(self):
        for line in self.a[self.loa:self.hia]:
            yield format_tag(self.delete_tag, line)

    def dump_insert(self):
        for line in self.b[self.lob:self.hib]:
            yield format_tag(self.insert_tag, line)

    def _dump_replace_lines(self):
        if self.loa < self.hia:
            if self.lob < self.hib:
                yield from self.dump_replace()
            else:
                yield from self.dump_delete()
        elif self.lob < self.hib:
            yield from self.dump_insert()

    def dump_replace(self):
        # Based on `difflib.Differ._fancy_replace`.
        # When replacing one block of lines with another, search the blocks
        # for *similar* lines; the best-matching pair (if any) is used as a
        # sync point, and intraline difference marking is done on the
        # similar pair. Lots of work, but often worth it.
        best_ratio = 0
        cruncher = difflib.SequenceMatcher(difflib.IS_CHARACTER_JUNK)

        eq = None       # Indexes of the identical line.
        best = None     # Indexes of the best non-identical line.
        for bi, bline in enumerate(self.b[self.lob:self.hib], self.lob):
            cruncher.set_seq2(bline)
            for ai, aline in enumerate(self.a[self.loa:self.hia], self.loa):
                if aline == bline:
                    if not eq:
                        eq = (ai, bi)
                    continue
                cruncher.set_seq1(aline)

                # Ratio calculation is expensive; this raduces the computation
                # as much as possible.
                if (cruncher.real_quick_ratio() > best_ratio and
                        cruncher.quick_ratio() > best_ratio):
                    ratio = cruncher.ratio()
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best = (ai, bi)

        if best_ratio < self.cutoff:    # No "pretty close" pair.
            if not eq:  # No identical pair either. Just dump the lines.
                yield from self.dump_delete()
                yield from self.dump_insert()
                return
            # There's an identical line. Use it.
            best_ratio = 1.0
            best = eq
        else:
            eq = None

        # Dump lines up to the best pair.
        subcontext = self._replace(hia=best[0], hib=best[1])
        subcontext.cutoff = self.cutoff
        yield from subcontext._dump_replace_lines()

        # Intraline marking.
        if eq:  # Identical lines are simple.
            yield markupsafe.escape(self.a[eq[0]])
        else:
            pairs = InlineDiffContext.crunch(
                cruncher, self.a[best[0]], self.b[best[1]],
            )
            a, b = map(lambda x: markupsafe.Markup('').join(x), zip(*pairs))
            yield format_tag(self.delete_tag, a)
            yield format_tag(self.insert_tag, b)

        # Dump lines after the best pair.
        subcontext = self._replace(loa=best[0] + 1, lob=best[1] + 1)
        subcontext.cutoff = self.cutoff
        yield from subcontext._dump_replace_lines()


def ndiff(a, b):
    cruncher = difflib.SequenceMatcher(None, a, b)
    yield from BlockDiffContext.crunch(cruncher, a, b)
