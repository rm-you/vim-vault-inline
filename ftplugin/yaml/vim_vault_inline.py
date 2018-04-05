import os
import re
import subprocess
from distutils import spawn

import vim

MODE_ENCRYPT = 'encrypt'
MODE_DECRYPT = 'decrypt'


def get_indent_level(line):
    tabstop = 4  # TODO: get this from vim variable
    line = line.expandtabs(tabstop)
    indent = 0 if line.isspace() else len(line) - len(line.lstrip())
    return indent


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
            'ansible-vault', mode, '/dev/stdin',
            '--output=/dev/stdout',
            '--vault-password-file', pass_fn
        )
        vault = subprocess.Popen(vault_command,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE)
        out, _ = vault.communicate(input=string)
        if out:
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

    def __init__(self, expect_encrypted):
        self._expect_encrypted = expect_encrypted

    @property
    def text(self):
        if not self._attempted:
            self._attempted = True
            data = self._read_data_block()
            if data:
                self._data = vault_subshell(
                    data,
                    mode=(MODE_DECRYPT if self._expect_encrypted else
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
        start_line = curr_line = vim.current.window.cursor[0]
        # The cursor position is one-indexed, but the buffer is zero-indexed
        curr_line -= 1

        # Grab the first line of the secret definition (with !vault)
        line, curr_line = next_line(curr_line)

        # Check that there is actually a secret starting here
        if '!vault' not in line:
            print("Line is not the start of a vault secret!")
            return

        # Now get the first line of the actual secret
        line, curr_line = next_line(curr_line)

        # Check that it's actually encrypted if it should be
        if self._expect_encrypted and '$ANSIBLE_VAULT' not in line:
            print("This is not an encrypted secret!")
            return
        # Or correctly unencrypted if it should be
        elif not self._expect_encrypted and '$ANSIBLE_VAULT' in line:
            print("This is secret is already encrypted!")
            return

        # Save indentation data
        self._indent_string = re.search(r'^\s+', line).group(0)
        indent_level = get_indent_level(line)

        # Our secret starts with this initial line and a newline
        secret = "{}\n".format(line.strip())

        # The secret continues with the following lines appended, until the
        # indentation level changes.
        line, curr_line = next_line(curr_line)
        while line and get_indent_level(line) == indent_level:
            secret += line.strip()
            line, curr_line = next_line(curr_line)

        self._lines = (start_line, curr_line - 1)

        return secret

    def replace_block(self):
        if self.text:
            start = self.lines[0]
            end = self.lines[1]
            del vim.current.buffer[start:end]
            lines = ["{indent}{line}".format(indent=self.indent_string, line=l)
                     for l in self.text.split('\n')]
            vim.current.buffer.append(lines, start)
