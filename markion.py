#!/usr/bin/env python3
# Markion
# Copyright (C) 2019-2020 Oscar Benedito <oscar@oscarbenedito.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import os, sys, re, argparse
parser = argparse.ArgumentParser(description='Markion is a simple scripts that retrieves tangled code from Markdown.')
parser.add_argument('file', metavar='file', type=str, nargs=1, help='Input file.')
parser.add_argument('-d', '--output-directory', dest='out_dir', type=str, default=os.getcwd(), help='Change the output directory.')
parser.add_argument('-D', '--auto-directory', dest='auto_dir', action='store_true', help='Auto detect output directory.')
args = parser.parse_args()
with open(args.file[0], 'r') as f:
    inp = f.read()
r_block = '```[\w\-.]*\s+block\s+([\w.-]+).*?\n(.*?)\n```\s*?\n'
r_file = '```[\w\-.]*\s+file\s+([\w.-]+).*?\n(.*?\n)```\s*?\n'
blocks = re.findall(r_block, inp, flags = re.DOTALL)
files = re.findall(r_file, inp, flags = re.DOTALL)
r_include = re.compile('([ \t]*)\[\[\s*include\s+([\w\-.]+)\s*\]\]', flags = re.DOTALL)
def resolve(content, blocks):
    it = r_include.finditer(content)
    for include in it:
        block_name = include[2]
        if blocks[block_name][0]:
            raise Exception('Circular dependency in block ' + block_name)
        blocks[block_name][0] = True
        s = resolve(blocks[block_name][1], blocks)
        blocks[block_name][0] = False
        blocks[block_name][1] = s
        s = include[1] + s.replace('\n', '\n' + include[1])
        content = r_include.sub(repr(s)[1:-1], content, count = 1)
    return content
block_content = { b[0] : [False, b[1]] for b in blocks }
file_content = dict()
for f in files:
    if f[0] not in file_content:
        file_content[f[0]] = ''
    file_content[f[0]] += resolve(f[1], block_content)
if args.auto_dir:
    args.out_dir = os.path.dirname(args.file[0])
if not os.path.exists(args.out_dir):
    os.mkdirs(args.out_dir)
for fn, fc in file_content.items():
    with open(args.out_dir + '/' + fn, 'w') as f:
        f.write(fc)
