" --------------------------------
" Add our plugin to the path
" --------------------------------
python import sys
python import vim
python sys.path.append(vim.eval('expand("<sfile>:h")'))

" --------------------------------
"  Function(s)
" --------------------------------
function! HandleVaultLine()
python << endOfPython

import vim_vault_inline

vh = vim_vault_inline.VaultHandler()
vh.replace_block()

endOfPython
endfunction

" --------------------------------
"  Expose our commands to the user
" --------------------------------
command! VaultEncryptionToggle call HandleVaultLine()
