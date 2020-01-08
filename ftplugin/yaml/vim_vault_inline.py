#  Copyright 2018 Adam Harwell
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from distutils import spawn
import os
import re
import subprocess

import vim

MODE_ENCRYPT = 'encrypt'
MODE_DECRYPT = 'decrypt'
PATTERN_VAULT_OR_PIPE = r':\s*(!vault)?\s*\|'


def get_indent_level(line):
    tabstop = int(vim.eval("&tabstop"))
    line = line.expandtabs(tabstop)
    indent = 0 if line.isspace() else len(line) - len(line.lstrip())
    return indent


def prev_line(line_num):
    # Don't go off the end of the buffer
    if line_num < 0:
        return None, line_num
    return vim.current.buffer[line_num], line_num - 1


def next_line(line_num):
    # Don't go off the end of the buffer
    if not line_num < len(vim.current.buffer):
        return None, line_num + 1
    return vim.current.buffer[line_num], line_num + 1


def vault_subshell(string, mode):
    pass_fn = os.getenv("VAULT_PASSWORD_FILE")
    if pass_fn:
        pass_fn = os.path.expanduser(pass_fn)
        if not spawn.find_executable("ansible-vault"):
            print("Cannot find `ansible-vault` in PATH!")
            return

        vault_command = (
            'ansible-vault', mode, '-',
            '--vault-password-file', pass_fn
        )
        vault = subprocess.Popen(vault_command,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE)
        out, _ = vault.communicate(input=string)
        if out:
            out = out.decode('UTF-8')
            return out.strip()
        else:
            print("Could not encrypt value.")
    else:
        print("Please set 'VAULT_PASSWORD_FILE' in your environment.")


class VaultHandler(object):
    _attempted = False
    _data = None
    _lines = None
    _indent_string = ""
    _encrypted_data = None

    @property
    def text(self):
        if not self._attempted:
            self._attempted = True
            data = self._read_data_block()
            if data:
                self._data = vault_subshell(
                    data.encode('UTF-8'),
                    mode=(MODE_DECRYPT if self._encrypted_data else
                          MODE_ENCRYPT)
                )
        return self._data

    @property
    def lines(self):
        str(self.text)
        return self._lines

    @property
    def indent_string(self):
        str(self.text)
        return self._indent_string

    def _read_data_block(self):
        # Grab the current cursor position from vim
        curr_line = vim.current.window.cursor[0]
        # The cursor position is one-indexed, but the buffer is zero-indexed
        curr_line -= 1

        # Find the definition line of the current block
        start_line = vim.current.buffer[curr_line]
        if re.search(PATTERN_VAULT_OR_PIPE, start_line):
            # We're already at the definition line
            pass
        else:
            indent_level = get_indent_level(start_line)
            line, curr_line = prev_line(curr_line)
            while line and get_indent_level(line) == indent_level:
                line, curr_line = prev_line(curr_line)
            curr_line += 1
        header_line_num = curr_line

        # Get the first line
        line, curr_line = next_line(curr_line)

        # Check if there is actually a secret starting here
        if not re.search(PATTERN_VAULT_OR_PIPE, line):
            print("Line is not the start of a vault secret!")
            return

        # Now get the first line of the actual secret
        line, curr_line = next_line(curr_line)

        # Save indentation data
        self._indent_string = re.search(r'^\s+', line).group(0)
        indent_level = get_indent_level(line)

        # Our data starts with this line
        data = line.strip(' \t')

        # Is the data already encrypted or not?
        if '$ANSIBLE_VAULT;' in data:
            self._encrypted_data = True
            # Need a newline after the encrypted data's header
            data += '\n'
        else:
            self._encrypted_data = False

        # The data continues with the following lines appended, until the
        # indentation level changes.
        line, curr_line = next_line(curr_line)
        while line and get_indent_level(line) == indent_level:
            # Preserve newlines for non-encrypted data
            if not self._encrypted_data:
                data += '\n'
            data += line.strip(' \t')
            line, curr_line = next_line(curr_line)

        self._lines = (header_line_num, curr_line - 1)

        return data

    def replace_block(self):
        if self.text:
            start = self.lines[0]
            end = self.lines[1]

            # Set up the starting line
            start_line_tokens = vim.current.buffer[start].split(':')
            start_line = start_line_tokens[0]
            # We know the encryption state of the old data, so do the opposite
            if self._encrypted_data:
                start_line += ": |"
            else:
                start_line += ": !vault |"
            vim.current.buffer[start] = start_line

            # Delete all the old data lines
            del vim.current.buffer[start+1:end]

            # Replace them with the new lines
            lines = ["{indent}{line}".format(indent=self.indent_string, line=l)
                     for l in self.text.split('\n')]
            vim.current.buffer.append(lines, start + 1)
