# vim-vault-inline

## Installation

Use your plugin manager of choice.

- [Pathogen](https://github.com/tpope/vim-pathogen)
  - `git clone https://github.com/rm-you/vim-vault-inline ~/.vim/bundle/vim-vault-inline`
- [Vundle](https://github.com/gmarik/vundle)
  - Add `Bundle 'https://github.com/rm-you/vim-vault-inline'` to .vimrc
  - Run `:BundleInstall`
- [NeoBundle](https://github.com/Shougo/neobundle.vim)
  - Add `NeoBundle 'https://github.com/rm-you/vim-vault-inline'` to .vimrc
  - Run `:NeoBundleInstall`
- [vim-plug](https://github.com/junegunn/vim-plug)
  - Add `Plug 'https://github.com/rm-you/vim-vault-inline'` to .vimrc
  - Run `:PlugInstall`

## Usage

Set the variable `VAULT_PASSWORD_FILE` in your environment to the absolute
path of your ansible-vault password file.

Use the command :VaultEncryptionToggle when the cursor is inside a multi-line
yaml block. The author recommends adding a binding to your vimrc, like:

`nmap ,v :VaultEncryptionToggle<CR>`

## Todo

1. Write tests
2. Write documentation
