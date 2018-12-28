# -*- coding: utf-8 -*-
# hypua2jamo: Convert Hanyang-PUA code to unicode Hangul Jamo
# Copyright (C) 2012  mete0r
#
# This file is part of hypua2jamo.
#
# hypua2jamo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# hypua2jamo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hypua2jamo.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
import io


def parse_line(line):
    comment = line.find('%%%')
    if comment != -1:
        line = line[:comment]

    if line.startswith('U+'):
        pua = int(line[2:6], 16)
        jamo = line[10:].strip()
        if jamo != '':
            jamo = jamo.split(' ')
            jamo = u''.join(unichr(int(code[2:6], 16)) for code in jamo)
        else:
            jamo = u''
        return pua, jamo
    else:
        return None, None


def parse_lines(lines):
    for line in lines:
        pua, jamo = parse_line(line)
        if pua:
            yield pua, jamo


def test_parse(self):
    lines = ['U+E0BC => U+115F U+1161 U+11AE',
             'U+E0C6 => U+115F U+11A3',
             'U+E230 => U+1102 U+117A %%% <= U+1102 U+117C',
             'U+F86A =>']

    pua, jamo = parse_line(lines[0])
    self.assertEquals(0xE0BC, pua)
    self.assertEquals(unichr(0x115F)+unichr(0x1161)+unichr(0x11AE), jamo)

    pua, jamo = parse_line(lines[2])
    self.assertEquals(0xE230, pua)
    self.assertEquals(unichr(0x1102)+unichr(0x117A), jamo)

    pua, jamo = parse_line(lines[3])
    self.assertEquals(0xF86A, pua)
    self.assertEquals(u'', jamo)


def codepoint(code):
    return '\\u%x' % code


def parse_datafile_into_table(f):
    if isinstance(f, basestring):
        with file(f) as f:
            return parse_datafile_into_table(f)
    return dict(parse_lines(f))


def table_to_c(table, fp):
    pua_groups = make_groups(sorted(table.keys()))

    fp.write('#include "codepoints_typedef.h"\n')

    for pua_start, pua_end in pua_groups:
        for pua_code in range(pua_start, pua_end + 1):
            jamo = table[pua_code]

            codepoints = ', '.join(
                ['0x{:04X}'.format(len(jamo))] +
                ['0x{:04x}'.format(ord(uch)) for uch in jamo]
            )
            fp.write(
                'static codepoint_t pua2jamo_{:04X}[] = {{ {} }};\n'.format(
                    pua_code, codepoints
                )
            )

        fp.write(
            'static codepoint_t *pua2jamo_group_{:04X}[] = {{\n'.format(
                pua_start,
            )
        )
        for pua_code in range(pua_start, pua_end + 1):
            fp.write('\tpua2jamo_{:04X},\n'.format(pua_code))
        fp.write('};\n')

    lookup = ':\\\n'.join(
        '\t(0x{start:04X} <= code && code <= 0x{end:04X})?'
        '(pua2jamo_group_{start:04X}[code - 0x{start:04X}])'.format(
            start=pua_start,
            end=pua_end
        )
        for pua_start, pua_end in pua_groups
    )
    lookup_macro = '#define lookup(code) \\\n' + lookup + ':\\\n\t' + 'NULL\n'
    fp.write(lookup_macro)


def make_groups(codes):
    groups = []
    current_group = None
    for code in codes:
        if current_group is None:
            current_group = [code, code]
        elif current_group[-1] + 1 == code:
            current_group[-1] = code
        else:
            groups.append(current_group)
            current_group = [code, code]

    if current_group is not None:
        groups.append(current_group)

    return groups


if __name__ == '__main__':
    composed = parse_datafile_into_table('data/hypua2jamocomposed.txt')
    with io.open('codepoints_p2j.h', 'wb') as fp:
        table_to_c(composed, fp)

    # decomposed = parse_datafile_into_table('data/hypua2jamodecomposed.txt')
    # table_to_c(decomposed, 'src/hypua2jamo/decomposed.c')