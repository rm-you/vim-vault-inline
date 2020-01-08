"  Copyright 2018 Adam Harwell
"
"  Licensed under the Apache License, Version 2.0 (the "License");
"  you may not use this file except in compliance with the License.
"  You may obtain a copy of the License at
"
"      http://www.apache.org/licenses/LICENSE-2.0
"
"  Unless required by applicable law or agreed to in writing, software
"  distributed under the License is distributed on an "AS IS" BASIS,
"  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"  See the License for the specific language governing permissions and
"  limitations under the License.

" --------------------------------
" Add our plugin to the path
" --------------------------------
py3 import sys
py3 import vim
py3 sys.path.append(vim.eval('expand("<sfile>:h")'))

" --------------------------------
"  Function(s)
" --------------------------------
function! HandleVaultLine()
py3 << endOfPython

import vim_vault_inline

vh = vim_vault_inline.VaultHandler()
vh.replace_block()

endOfPython
endfunction

" --------------------------------
"  Expose our commands to the user
" --------------------------------
command! VaultEncryptionToggle call HandleVaultLine()
