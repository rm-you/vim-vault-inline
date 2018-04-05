" --------------------------------
" Add our plugin to the path
" --------------------------------
python import sys
python import vim
python sys.path.append(vim.eval('expand("<sfile>:h")'))

" --------------------------------
"  Function(s)
" --------------------------------
function! DecryptVaultLine()
python << endOfPython

import vim_vault_inline

vh = vim_vault_inline.VaultHandler(expect_encrypted=True)
vh.replace_block()

endOfPython
endfunction

function! EncryptVaultLine()
python << endOfPython

import vim_vault_inline

vh = vim_vault_inline.VaultHandler(expect_encrypted=False)
vh.replace_block()

endOfPython
endfunction

" --------------------------------
"  Expose our commands to the user
" --------------------------------
command! Dc call DecryptVaultLine()
command! Ec call EncryptVaultLine()
