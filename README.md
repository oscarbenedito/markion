# Markion
Markion is a Python script to allow writing literate programs using Markdown. Markion retrieves the tangled code in a file and written it to the specified files in the output directory. This README file is an example of a file that Markion can process, indeed, this file will give you Markion itself!

## Using Markion

### Creating the input file
To use Markion, create a Mardown file normally, and insert code snippets as you would typically with Markdown. If you want to use that code for your output files, you should use the following syntax:

<pre>
```[language] block|file blockid|filename
code snippet
```
</pre>

Specifing the language is optional (but you should put a space between the <code>```</code> and either "block" or "file"). The next word specifies wether the code is a block or it is the content of a file, and the last word represents the block ID (to include it in other snippets) or the output file name (where the code will be written) respectively. You may add comments if desired at the end of the line, both Markdown and Markion will ignore them.

### Prerequisites
In order to run the program, you will need Python version 3.6 or later.

### Running the program
To run the program, execute the file `markion.py` followed by the input file.

```
python3 markion.py file
```

There is an addition option `--output-directory` (or `-d`) to specify an output directory and you can also run the program with `--help` (or `-h`) to get help about the program's usage.

## Explanation of the program
First of all, we will make it executable, we'll write the license notice and import all the required libraries.
```python file markion.py
#!/usr/bin/env python3
[[ include license ]]
import os, sys, re, argparse
```

### Program arguments
We will use Python's `argparse` package to deal with our program's arguments. We initialize the parser with a brief description of the program's utility.
```python file markion.py
parser = argparse.ArgumentParser(description='Markion is a simple scripts that retrieves tangled code from Markdown.')
```
One of the arguments is the name of the input file:
```python file markion.py
parser.add_argument('file', metavar='file', type=str, nargs=1, help='Input file.')
```
Another optional argument lets the user specify the output directory.
```python file markion.py
parser.add_argument('-d', '--output-directory', dest='out_dir', type=str, default=os.getcwd(), help='Change the output directory.')
```
The other argument is also optional and it lets the program automatically detect the output directory (based on the file's directory). This option will override the `--output-directory` option.
```python file markion.py
parser.add_argument('-D', '--auto-directory', dest='auto_dir', action='store_true', help='Auto detect output directory.')
```
To calculate the directory automatically, we simply check the input file's directory.
```python block auto_dir
if args.auto_dir:
    args.out_dir = os.path.dirname(args.file[0])
```
Finally we assign the arguments' values to the `args` variable to use it later on.
```python file markion.py
args = parser.parse_args()
```

### Reading the input file
We read the input file and copy the contents to a variable `inp`.
```python file markion.py
with open(args.file[0], 'r') as f:
    inp = f.read()
```

### Extracting the tangled code
We extract the important pieces of code from the `inp` variable. To do so there are two regular expressions, one that matches the blocks and one that matches the content to output in the files. We get all the snippets and save them into the variables `blocks` and `files`.
```python file markion.py
r_block = '```[\w\-.]*\s+block\s+([\w.-]+).*?\n(.*?)\n```\s*?\n'
r_file = '```[\w\-.]*\s+file\s+([\w.-]+).*?\n(.*?\n)```\s*?\n'
blocks = re.findall(r_block, inp, flags = re.DOTALL)
files = re.findall(r_file, inp, flags = re.DOTALL)
```

### Resolving includes in the tangled code
For each file specified in the input, we resolve all the blocks that are included (recursively). To do so we use the function `resolve`.
```python file markion.py
[[ include resolve ]]
block_content = { b[0] : [False, b[1]] for b in blocks }
file_content = dict()
for f in files:
    if f[0] not in file_content:
        file_content[f[0]] = ''
    file_content[f[0]] += resolve(f[1], block_content)
```
The following code is the function resolve included in the last code fragment, it won't be directly written on the file, but be included when the `[[ include resolve ]]` is called. As you can see it indents the whole block.
```python block resolve
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
```

### Writing the output to the corresponding files
Finally, if there weren't any errors, we write the output code into the respective files. To do so, we assign the directory automatically if the option has been delcared, otherwise, we create the output directory if not already created:
```python file markion.py
[[ include auto_dir ]]
if not os.path.exists(args.out_dir):
    os.mkdirs(args.out_dir)
```
And we write the output.
```python file markion.py
for fn, fc in file_content.items():
    with open(args.out_dir + '/' + fn, 'w') as f:
        f.write(fc)
```

## License
The program is licensed under the GNU General Public License version 3 (available [here](https://www.gnu.org/licenses/gpl-3.0.html)).

In order to make sure there is no missunderstanding, we will include the following license notice on our file.
```python block license
# Copyright (C) 2019 Oscar Benedito
#
# This file is part of Markion.
#
# Markion is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Markion is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Markion.  If not, see <https://www.gnu.org/licenses/>.
```

## Author

- **Oscar Benedito** - oscar@oscarbenedito.com
