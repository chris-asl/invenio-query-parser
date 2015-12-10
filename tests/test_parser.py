# -*- coding: utf-8 -*-
#
# This file is part of Invenio-Query-Parser.
# Copyright (C) 2014, 2015 CERN.
#
# Invenio-Query-Parser is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio-Query-Parser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Unit tests for the search engine query parsers."""

from __future__ import unicode_literals

from invenio_query_parser.ast import (
    AndOp,
    DoubleQuotedValue,
    EmptyQuery,
    GreaterEqualOp,
    GreaterOp,
    Keyword,
    KeywordOp,
    LowerEqualOp,
    LowerOp,
    NotOp,
    OrOp,
    RangeOp,
    RegexValue,
    SingleQuotedValue,
    Value,
    ValueQuery)

from invenio_query_parser.contrib.spires.ast import SpiresOp

from pytest import generate_tests


def generate_parser_test(query, expected):
    def func(self):
        from invenio_query_parser.walkers import repr_printer
        tree = self.parser.parse_query(query)
        printer = repr_printer.TreeRepr()
        assert tree == expected, "parsed tree: %s\nexpected tree: %s" % (
            tree.accept(printer), expected.accept(printer))
    return func


@generate_tests(generate_parser_test)  # pylint: disable=R0903
class TestParser(object):
    """Test parser functionality"""

    @classmethod
    def setup_class(cls):
        from invenio_query_parser.contrib.spires import converter
        cls.parser = converter.SpiresToInvenioSyntaxConverter()

    queries = (
        ("",
         EmptyQuery('')),
        ("    \t",
         EmptyQuery('    \t')),
        ("bar",
         ValueQuery(Value('bar'))),
        ("2004",
         ValueQuery(Value('2004'))),
        ("'bar'",
         ValueQuery(SingleQuotedValue('bar'))),
        ("\"bar\"",
         ValueQuery(DoubleQuotedValue('bar'))),
        ("J. Ellis",
         AndOp(ValueQuery(Value('J.')), ValueQuery(Value('Ellis')))),
        ("$e^{+}e^{-}$",
         ValueQuery(Value('$e^{+}e^{-}$'))),

        # Basic keyword:value
        ("author:bar",
         KeywordOp(Keyword('author'), Value('bar'))),
        ("author: bar",
         KeywordOp(Keyword('author'), Value('bar'))),
        ("author: 2004",
         KeywordOp(Keyword('author'), Value('2004'))),
        ("999: bar",
         KeywordOp(Keyword('999'), Value('bar'))),
        ("999C5: bar",
         KeywordOp(Keyword('999C5'), Value('bar'))),
        ("999__u: bar",
         KeywordOp(Keyword('999__u'), Value('bar'))),
        ("author: bar",
         KeywordOp(Keyword('author'), Value('bar'))),
        ("  author  :  bar  ",
         KeywordOp(Keyword('author'), Value('bar'))),

        # Quoted strings
        ("author: 'bar'",
         KeywordOp(Keyword('author'), SingleQuotedValue('bar'))),
        ("author: \"bar\"",
         KeywordOp(Keyword('author'), DoubleQuotedValue('bar'))),
        ("author: /bar/",
         KeywordOp(Keyword('author'), RegexValue('bar'))),
        ("author: \"'bar'\"",
         KeywordOp(Keyword('author'), DoubleQuotedValue("'bar'"))),
        ('author:"Ellis, J"',
         KeywordOp(Keyword('author'), DoubleQuotedValue("Ellis, J"))),

        # Weird values
        ("author: \"bar",
         KeywordOp(Keyword('author'), Value('"bar'))),
        ("author: 'bar",
         KeywordOp(Keyword('author'), Value("'bar"))),

        # Range queries
        ("year: 2000->2012",
         KeywordOp(Keyword('year'), RangeOp(Value('2000'), Value('2012')))),
        ("year: 2000-10->2012-09",
         KeywordOp(Keyword('year'), RangeOp(Value('2000-10'),
                                            Value('2012-09')))),
        ("cited: 3->30",
         KeywordOp(Keyword('cited'), RangeOp(Value('3'), Value('30')))),
        ('author: Albert->John',
         KeywordOp(Keyword('author'), RangeOp(Value('Albert'),
                                              Value('John')))),
        ('author: "Albert"->John',
         KeywordOp(Keyword('author'), RangeOp(DoubleQuotedValue('Albert'),
                                              Value('John')))),
        ('author: Albert->"John"',
         KeywordOp(Keyword('author'), RangeOp(Value('Albert'),
                                              DoubleQuotedValue('John')))),
        ('author: "Albert"->"John"',
         KeywordOp(Keyword('author'), RangeOp(DoubleQuotedValue('Albert'),
                                              DoubleQuotedValue('John')))),

        # Star patterns
        ("bar*",
         ValueQuery(Value('bar*'))),
        ("author: hello*",
         KeywordOp(Keyword('author'), Value('hello*'))),
        ("author: 'hello*'",
         KeywordOp(Keyword('author'), SingleQuotedValue('hello*'))),
        ("author: \"hello*\"",
         KeywordOp(Keyword('author'), DoubleQuotedValue('hello*'))),
        ("author: he*o",
         KeywordOp(Keyword('author'), Value('he*o'))),
        ("author: he*lo*",
         KeywordOp(Keyword('author'), Value('he*lo*'))),
        ("author: *hello",
         KeywordOp(Keyword('author'), Value('*hello'))),

        # Special characters in keyword:value
        ("author: O'Shea",
         KeywordOp(Keyword('author'), Value("O'Shea"))),
        ("author: e(-)",
         KeywordOp(Keyword('author'), Value('e(-)'))),
        ("author: e(+)e(-)",
         KeywordOp(Keyword('author'), Value('e(+)e(-)'))),
        ("title: Si-28(p(pol.),n(pol.))",
         KeywordOp(Keyword('title'), Value('Si-28(p(pol.),n(pol.))'))),

        # Unicode characters
        ("author: пушкин",
         KeywordOp(Keyword('author'), Value("пушкин"))),
        ("author: Lemaître",
         KeywordOp(Keyword('author'), Value("Lemaître"))),
        ('author: "Lemaître"',
         KeywordOp(Keyword('author'), DoubleQuotedValue("Lemaître"))),
        ("refersto:hep-th/0201100",
         KeywordOp(Keyword('refersto'), Value("hep-th/0201100"))),

        # Combined queries
        ("author:bar author:bar",
         AndOp(KeywordOp(Keyword('author'), Value('bar')),
               KeywordOp(Keyword('author'), Value('bar')))),
        ("author:bar and author:bar",
         AndOp(KeywordOp(Keyword('author'), Value('bar')),
               KeywordOp(Keyword('author'), Value('bar')))),
        ("author:bar AND author:bar",
         AndOp(KeywordOp(Keyword('author'), Value('bar')),
               KeywordOp(Keyword('author'), Value('bar')))),
        ("author and bar",
         AndOp(ValueQuery(Value('author')), ValueQuery(Value('bar')))),
        ("author:bar or author:bar",
         OrOp(KeywordOp(Keyword('author'), Value('bar')),
              KeywordOp(Keyword('author'), Value('bar')))),
        ("author:bar | author:bar",
         OrOp(KeywordOp(Keyword('author'), Value('bar')),
              KeywordOp(Keyword('author'), Value('bar')))),
        ("author:bar not author:bar",
         AndOp(KeywordOp(Keyword('author'), Value('bar')),
               NotOp(KeywordOp(Keyword('author'), Value('bar'))))),
        ("author:bar and not author:bar",
         AndOp(KeywordOp(Keyword('author'), Value('bar')),
               NotOp(KeywordOp(Keyword('author'), Value('bar'))))),
        ("author:bar -author:bar",
         AndOp(KeywordOp(Keyword('author'), Value('bar')),
               NotOp(KeywordOp(Keyword('author'), Value('bar'))))),
        ("author:bar- author:bar",
         AndOp(KeywordOp(Keyword('author'), Value('bar-')),
               KeywordOp(Keyword('author'), Value('bar')))),
        ("(author:bar)",
         KeywordOp(Keyword('author'), Value('bar'))),
        ("((author:bar))",
         KeywordOp(Keyword('author'), Value('bar'))),
        ("(((author:bar)))",
         KeywordOp(Keyword('author'), Value('bar'))),
        ("(author:bar) or author:bar",
         OrOp(KeywordOp(Keyword('author'), Value('bar')),
              KeywordOp(Keyword('author'), Value('bar')))),
        ("author:bar or (author:bar)",
         OrOp(KeywordOp(Keyword('author'), Value('bar')),
              KeywordOp(Keyword('author'), Value('bar')))),
        ("(author:bar) or (author:bar)",
         OrOp(KeywordOp(Keyword('author'), Value('bar')),
              KeywordOp(Keyword('author'), Value('bar')))),
        ("(author:bar)or(author:bar)",
         OrOp(KeywordOp(Keyword('author'), Value('bar')),
              KeywordOp(Keyword('author'), Value('bar')))),
        ("(author:bar)|(author:bar)",
         OrOp(KeywordOp(Keyword('author'), Value('bar')),
              KeywordOp(Keyword('author'), Value('bar')))),
        ("(author:bar)| (author:bar)",
         OrOp(KeywordOp(Keyword('author'), Value('bar')),
              KeywordOp(Keyword('author'), Value('bar')))),
        ("( author:bar) or ( author:bar)",
         OrOp(KeywordOp(Keyword('author'), Value('bar')),
              KeywordOp(Keyword('author'), Value('bar')))),
        ("(author:bar) or (author:bar )",
         OrOp(KeywordOp(Keyword('author'), Value('bar')),
              KeywordOp(Keyword('author'), Value('bar')))),
        ("(author:bar1 or a:bar2) and (title:bar3 or t:bar4)",
         AndOp(OrOp(KeywordOp(Keyword('author'), Value('bar1')),
                    KeywordOp(Keyword('a'), Value('bar2'))),
               OrOp(KeywordOp(Keyword('title'), Value('bar3')),
                    KeywordOp(Keyword('t'), Value('bar4'))))),
        ("author:bar and author:bar and author:bar",
            AndOp(AndOp(KeywordOp(Keyword('author'), Value('bar')),
                        KeywordOp(Keyword('author'), Value('bar'))),
                  KeywordOp(Keyword('author'), Value('bar')))),
        ("aaa +bbb -ccc +ddd",
         AndOp(AndOp(AndOp(ValueQuery(Value('aaa')),
                           ValueQuery(Value('bbb'))),
                     NotOp(ValueQuery(Value('ccc')))),
               ValueQuery(Value('ddd')))),
        ("author:bar not author:bar",
            AndOp(
                KeywordOp(Keyword('author'), Value('bar')),
                NotOp(KeywordOp(Keyword('author'), Value('bar'))))),
        ("author:bar and -author:bar",
            AndOp(
                KeywordOp(Keyword('author'), Value('bar')),
                NotOp(KeywordOp(Keyword('author'), Value('bar'))))),
        ("-author:bar",
            NotOp(KeywordOp(Keyword('author'), Value('bar')))),
        ("-author",
            NotOp(ValueQuery(Value('author')))),
        ("author:bar or -author:bar",
            OrOp(
                KeywordOp(Keyword('author'), Value('bar')),
                NotOp(KeywordOp(Keyword('author'), Value('bar'))))),
        ("author:bar or not author:bar",
            OrOp(
                KeywordOp(Keyword('author'), Value('bar')),
                NotOp(KeywordOp(Keyword('author'), Value('bar'))))),
        ("bar + (not a:\"Ba, r\")",
            AndOp(
                ValueQuery(Value('bar')),
                NotOp(KeywordOp(Keyword('a'), DoubleQuotedValue('Ba, r'))))),
        ("bar | -author:bar",
            OrOp(
                ValueQuery(Value('bar')),
                NotOp(KeywordOp(Keyword('author'), Value('bar'))))),


        # Nested searches
        # FIXME: These two tests should be restored when
        # we implement nested keywords functionality on labs.
        # ("refersto:author:Ellis",
        #  KeywordOp(Keyword('refersto'), KeywordOp(Keyword('author'),
        #                                           Value('Ellis')))),
        # ("refersto:refersto:author:Ellis",
        #  KeywordOp(Keyword('refersto'),
        #            KeywordOp(Keyword('refersto'),
        #                      KeywordOp(Keyword('author'), Value('Ellis'))))),
        # Keyword-like values
        ("auzor:me",
         AndOp(Value('auzor:'), ValueQuery(Value('me')))),
        ("high-energies: annual",
         AndOp(Value('high-energies:'), ValueQuery(Value('annual')))),
        ("au-thor me:",
         AndOp(ValueQuery(Value('au-thor')), Value('me:'))),


        # Spires syntax #

        # Simple query
        ("find t quark",
         SpiresOp(Keyword('t'), Value('quark'))),
        ("find a:richter",
         SpiresOp(Keyword('a'), Value('richter'))),
        ("find a:\"richter, b\"",
         SpiresOp(Keyword('a'), DoubleQuotedValue('richter, b'))),

        # Simple query with non-obvious values
        ("find a richter, b",
         SpiresOp(Keyword('a'), Value('richter, b'))),
        ("find texkey Allison:1980vw",
         SpiresOp(Keyword('texkey'), Value('Allison:1980vw'))),
        ("find title bbb:ccc ddd:eee",
         SpiresOp(Keyword('title'), Value('bbb:ccc ddd:eee'))),
        ("find da today-2",
         SpiresOp(Keyword('da'), Value('today-2'))),
        ("find da today - 2",
         SpiresOp(Keyword('da'), Value('today - 2'))),
        ("find da 2012-01-01",
         SpiresOp(Keyword('da'), Value('2012-01-01'))),
        ("find t quark andorinword",
         SpiresOp(Keyword('t'), Value('quark andorinword'))),

        # Simple query with spaces
        ("find t quark   ",
         SpiresOp(Keyword('t'), Value('quark'))),
        ("   find t quark   ",
         SpiresOp(Keyword('t'), Value('quark'))),
        ("find t quark ellis  ",
         SpiresOp(Keyword('t'), Value('quark ellis'))),

        # Combined queries
        ("find t quark and a ellis",
         AndOp(SpiresOp(Keyword('t'), Value('quark')),
               SpiresOp(Keyword('a'), Value('ellis')))),
        ("find t quark or a ellis",
         OrOp(SpiresOp(Keyword('t'), Value('quark')),
              SpiresOp(Keyword('a'), Value('ellis')))),
        ("find (t aaa or t bbb or t ccc)or t ddd",
         OrOp(OrOp(OrOp(SpiresOp(Keyword('t'), Value('aaa')),
                        SpiresOp(Keyword('t'), Value('bbb'))),
                   SpiresOp(Keyword('t'), Value('ccc'))),
              SpiresOp(Keyword('t'), Value('ddd')))),
        ("find a:richter and t quark",
         AndOp(SpiresOp(Keyword('a'), Value('richter')),
               SpiresOp(Keyword('t'), Value('quark')))),
        ("find (t quark) or (a ellis)",
         OrOp(SpiresOp(Keyword('t'), Value('quark')),
              SpiresOp(Keyword('a'), Value('ellis')))),
        ("find (t quark or a ellis)",
         OrOp(SpiresOp(Keyword('t'), Value('quark')),
              SpiresOp(Keyword('a'), Value('ellis')))),
        ("find ((t quark) or (a ellis))",
         OrOp(SpiresOp(Keyword('t'), Value('quark')),
              SpiresOp(Keyword('a'), Value('ellis')))),
        ("find (( t quark )or( a ellis ))",
         OrOp(SpiresOp(Keyword('t'), Value('quark')),
              SpiresOp(Keyword('a'), Value('ellis')))),
        ("find (( t quark )or( a:ellis ))",
         OrOp(SpiresOp(Keyword('t'), Value('quark')),
              SpiresOp(Keyword('a'), Value('ellis')))),
        ("find collaboration LIGO and a whiting, b f and a Weiss, r",
         AndOp(
             AndOp(
                 SpiresOp(Keyword('collaboration'), Value('LIGO')),
                 SpiresOp(Keyword('a'), Value('whiting, b f'))),
             SpiresOp(Keyword('a'), Value('Weiss, r')))),
        ("find (collaboration LIGO and a whiting, b f) and a Weiss, r",
         AndOp(
             AndOp(
                 SpiresOp(Keyword('collaboration'), Value('LIGO')),
                 SpiresOp(Keyword('a'), Value('whiting, b f'))),
             SpiresOp(Keyword('a'), Value('Weiss, r')))),
        ("find collaboration LIGO and (a whiting, b f and a Weiss, r)",
         AndOp(
             SpiresOp(Keyword('collaboration'), Value('LIGO')),
             AndOp(
                 SpiresOp(Keyword('a'), Value('whiting, b f')),
                 SpiresOp(Keyword('a'), Value('Weiss, r'))))),
        ("find (aff IMPERIAL and d <1989 and a ELLISON) or"
         "(a ELLISON and aff RIVERSIDE and tc P)",
         OrOp(
             AndOp(
                 AndOp(
                     SpiresOp(Keyword('aff'), Value('IMPERIAL')),
                     SpiresOp(Keyword('d'), LowerOp(Value('1989')))),
                 SpiresOp(Keyword('a'), Value('ELLISON'))),
             AndOp(
                 AndOp(
                     SpiresOp(Keyword('a'), Value('ELLISON')),
                     SpiresOp(Keyword('aff'), Value('RIVERSIDE'))),
                 SpiresOp(Keyword('tc'), Value('P'))))
         ),
        ("find (a ELLISON and aff RIVERSIDE and tc P) or"
         "(aff IMPERIAL and d <1989 and a ELLISON)",
         OrOp(
             AndOp(
                 AndOp(
                     SpiresOp(Keyword('a'), Value('ELLISON')),
                     SpiresOp(Keyword('aff'), Value('RIVERSIDE'))),
                 SpiresOp(Keyword('tc'), Value('P'))),
             AndOp(
                 AndOp(
                     SpiresOp(Keyword('aff'), Value('IMPERIAL')),
                     SpiresOp(Keyword('d'), LowerOp(Value('1989')))),
                 SpiresOp(Keyword('a'), Value('ELLISON'))))
         ),

        # Implicit keyword
        ("find a john and ellis",
         AndOp(SpiresOp(Keyword('a'), Value('john')),
               SpiresOp(Keyword('a'), Value('ellis')))),
        ("find a john and (ellis or albert)",
         AndOp(SpiresOp(Keyword('a'), Value('john')),
               OrOp(ValueQuery(Value('ellis')),
                    ValueQuery(Value('albert'))))),
        ("find a john and t quark or higgs",
         OrOp(AndOp(SpiresOp(Keyword('a'), Value('john')),
                    SpiresOp(Keyword('t'), Value('quark'))),
              SpiresOp(Keyword('t'), Value('higgs')))),
        ("find john and t quark or higgs",
         OrOp(AndOp(ValueQuery(Value('john')),
                    SpiresOp(Keyword('t'), Value('quark'))),
              SpiresOp(Keyword('t'), Value('higgs')))),
        ("find a l everett or t light higgs and j phys.rev.lett. and "
         "primarch hep-ph",
         AndOp(AndOp(OrOp(SpiresOp(Keyword('a'), Value('l everett')),
                          SpiresOp(Keyword('t'), Value('light higgs'))),
                     SpiresOp(Keyword('j'), Value('phys.rev.lett.'))),
               SpiresOp(Keyword('primarch'), Value('hep-ph')))),
        ("find a l everett or t light higgs and j phys.rev.lett. and monkey",
         AndOp(AndOp(OrOp(SpiresOp(Keyword('a'), Value('l everett')),
                          SpiresOp(Keyword('t'), Value('light higgs'))),
                     SpiresOp(Keyword('j'), Value('phys.rev.lett.'))),
               SpiresOp(Keyword('j'), Value('monkey')))),

        # Nested searches
        ("find refersto a ellis",
         SpiresOp(Keyword('refersto'), SpiresOp(Keyword('a'),
                                                Value('ellis')))),
        ("find refersto j Phys.Rev.Lett.",
         SpiresOp(Keyword('refersto'), SpiresOp(Keyword('j'),
                                                Value('Phys.Rev.Lett.')))),
        ("find refersto a ellis, j",
         SpiresOp(Keyword('refersto'), SpiresOp(Keyword('a'),
                                                Value('ellis, j')))),
        ("find refersto ellis, j",
         SpiresOp(Keyword('refersto'), ValueQuery(Value('ellis, j')))),
        ("find a parke, s j and refersto author witten",
         AndOp(SpiresOp(Keyword('a'), Value("parke, s j")),
               SpiresOp(Keyword('refersto'), SpiresOp(Keyword('author'),
                                                      Value('witten'))))),
        ("fin af oxford u. and refersto title muon*",
         AndOp(SpiresOp(Keyword('af'), Value("oxford u.")),
               SpiresOp(Keyword('refersto'),
                        SpiresOp(Keyword('title'), Value('muon*'))))),
        ("find refersto a parke or refersto a lykken and a witten",
         AndOp(OrOp(SpiresOp(Keyword('refersto'),
                             SpiresOp(Keyword('a'), Value("parke"))),
                    SpiresOp(Keyword('refersto'),
                             SpiresOp(Keyword('a'), Value('lykken')))),
               SpiresOp(Keyword('a'), Value('witten')))),
        ("find refersto:refersto:author:maldacena",
         SpiresOp(Keyword('refersto'),
                  SpiresOp(Keyword('refersto'),
                           SpiresOp(Keyword('author'),
                                    Value('maldacena'))))),
        ("find refersto hep-th/9711200 and t nucl*",
         AndOp(SpiresOp(Keyword('refersto'),
                        ValueQuery(Value("hep-th/9711200"))),
               SpiresOp(Keyword('t'), Value('nucl*')))),
        ("find refersto:a ellis",
         SpiresOp(Keyword('refersto'), SpiresOp(Keyword('a'),
                                                Value('ellis')))),
        ("find refersto: a ellis",
         SpiresOp(Keyword('refersto'), SpiresOp(Keyword('a'),
                                                Value('ellis')))),

        # Greater, Lower Ops
        ("find date > 1984",
         SpiresOp(Keyword('date'), GreaterOp(Value('1984')))),
        ("find ac > 5",
         SpiresOp(Keyword('ac'), GreaterOp(Value('5')))),
        ("find date after 1984",
         SpiresOp(Keyword('date'), GreaterOp(Value('1984')))),
        ("find date < 1984",
         SpiresOp(Keyword('date'), LowerOp(Value('1984')))),
        ("find ac < 5",
         SpiresOp(Keyword('ac'), LowerOp(Value('5')))),
        ("find date before 1984",
         SpiresOp(Keyword('date'), LowerOp(Value('1984')))),
        ("find date >= 1984",
         SpiresOp(Keyword('date'), GreaterEqualOp(Value('1984')))),
        ("find date <= 2014-10-01",
         SpiresOp(Keyword('date'), LowerEqualOp(Value('2014-10-01')))),
        ("find du > today-2",
         SpiresOp(Keyword('du'), GreaterOp(Value('today-2')))),
        ("find du > today - 2",
         SpiresOp(Keyword('du'), GreaterOp(Value('today - 2')))),
        ("find topcite 200+",
         SpiresOp(Keyword('topcite'), GreaterEqualOp(Value('200')))),
        ("find topcite 200-",
         SpiresOp(Keyword('topcite'), LowerEqualOp(Value('200')))),

        # Journal searches with whitespaces
        ("find j Phys.Rev.,D41,2330",
         SpiresOp(Keyword('j'), Value('Phys.Rev.,D41,2330'))),
        ("find j Phys.Rev.,D41, 2330",
         SpiresOp(Keyword('j'), Value('Phys.Rev.,D41, 2330'))),

        # Popular queries
        ("arXiv:1004.0648",
         KeywordOp(Keyword('arXiv'), Value("1004.0648"))),
        ("find ea chowdhury, borun d",
         SpiresOp(Keyword('ea'), Value("chowdhury, borun d"))),
        ("(author:'Hiroshi Okada' OR (author:'H Okada' hep-ph) OR "
         "title: 'Dark matter in supersymmetric U(1(B-L) model' OR "
         "title: 'Non-Abelian discrete symmetry for flavors')",
         OrOp(OrOp(OrOp(KeywordOp(Keyword('author'),
                                  SingleQuotedValue('Hiroshi Okada')),
                        AndOp(KeywordOp(Keyword('author'),
                                        SingleQuotedValue('H Okada')),
                              ValueQuery(Value('hep-ph')))),
                   KeywordOp(Keyword('title'),
                             SingleQuotedValue('Dark matter in supersymmetric '
                                               'U(1(B-L) model'))),
              KeywordOp(Keyword('title'), SingleQuotedValue(
                  'Non-Abelian discrete symmetry for flavors')))),
        ("f a Oleg Antipin",
         SpiresOp(Keyword('a'), Value('Oleg Antipin'))),
        ("FIND a Oleg Antipin",
         SpiresOp(Keyword('a'), Value('Oleg Antipin'))),
        ("f a rodrigo,g and not rodrigo,j",
         AndOp(SpiresOp(Keyword('a'), Value('rodrigo,g')),
               NotOp(SpiresOp(Keyword('a'), Value('rodrigo,j'))))),

        # Dotable keys
        # FIXME: These will return when we have the full keyword List
        # that includes "doted" keywords
        # ("foo.bar:baz",
        #  KeywordOp(Keyword('foo.bar'), Value('baz'))),
        # ("a.b.c.d.f:bar",
        #  KeywordOp(Keyword('a.b.c.d.f'), Value('bar'))),
    )
