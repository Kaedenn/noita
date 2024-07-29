" File: filenamematch.vim
" Author: Kaedenn (kaedenn AT gmail DOT com)
" Version: 1.0.0
"
" Usage:
"   let g:noita_data_dir = "path/to/extracted/data.wak/"
"   source "path/to/this/file.vim"
"
" Variables:
"   g:steam_root        path to the Steam root directory; defaults to reading
"                       ~/.steam/root and using the directory it links to
"   g:noita_mods_dir    path to the Noita mods directory
"                       if unset, uses g:noita_game_dir . "/mods"
"   g:noita_data_dir    path to the extracted data.wak directory
"                       if unset, loading data files via `gf` will not work
"   g:noita_game_dir    path to the directory containing noita.exe; defaults
"                       to "<steam-root>/steamapps/common/Noita"
"   g:noita_debug       if set, enables diagnostic messages
"   g:noita_silent      if set, disables all output other than errors
"
" Example:
"
" let g:noita_data_dir = expand("~/Noita/data")
" let g:noita_mods_dir = expand("~/Noita/mods")
" source utility/filenamematch.vim

unlet! g:noita_loaded
let s:have_data = 0

let s:self_path = expand("<sfile>:p")
let s:util_path = fnamemodify(s:self_path, ":h")

if !exists("g:noita_data_dir")
  echomsg "g:noita_data_dir unset; loading data files disabled"
else
  let s:have_data = 1
endif

let s:resolve_util = s:util_path . "/pathresolve.py"
if !filereadable(s:resolve_util)
  throw printf("pathresolve.py not found in '%s'", s:util_path)
endif

function! <SID>DebugOn()
  if exists("g:noita_debug") && !exists("g:noita_silent")
    return 1
  endif
  return 0
endfunction

" Display a debugging message, if debugging is enabled
function! <SID>Debug(msg, ...)
  if <SID>DebugOn()
    echo "noita: debug: " . call(function('printf'), [a:msg] + a:000)
  endif
endfunction

" Display an informational message, unless disabled
function! <SID>Info(msg, ...)
  if !exists("g:noita_silent")
    echo call(function('printf'), [a:msg] + a:000)
  endif
endfunction

" Determine where the mods directory is
function! Noita_GetModsPath()
  if exists("g:noita_mods_dir")
    return g:noita_mods_dir
  endif
  if exists("g:noita_game_dir")
    return g:noita_game_dir . "/mods"
  endif
  return ""
endfunction

" Determine where the extracted data.wak directory is
function! Noita_GetDataPath()
  if exists("g:noita_data_dir")
    return g:noita_data_dir
  endif
  return ""
endfunction

" Build the command to resolve the given path
function! Noita_GetCommand(fpath)
  let l:base_arg = shellescape(expand("%:p:h"))
  let l:path_arg = shellescape(a:fpath)

  let l:mods_path = shellescape(Noita_GetModsPath())
  let l:data_path = shellescape(Noita_GetDataPath())
  let l:args = [ 'python', s:resolve_util, l:path_arg, '-p', l:base_arg, '-n' ]
  if l:mods_path != ""
    let l:args = l:args + [ "-m", l:mods_path ]
  endif
  if l:data_path != ""
    let l:args = l:args + [ "-d", l:data_path ]
  endif
  if exists("g:noita_silent")
    let l:args = l:args + [ '-q' ]
  endif
  let l:cmd = l:args->join()
  "if <SID>DebugOn()
  "  let l:cmd = l:cmd . " -v"
  "endif
  return l:cmd
endfunction

function! Noita_ResolveDataPath(fpath)
  let l:cmd = Noita_GetCommand(a:fpath)
  call <SID>Debug("Executing '%s'", l:cmd)
  let l:result = system(l:cmd)
  call <SID>Debug("Got '%s'", l:result)
  return l:result
endfunction

set includeexpr=Noita_ResolveDataPath(v:fname)

call <SID>Debug("Loaded Noita path support features")
call <SID>Debug("spath = '%s', upath = '%s'", s:self_path, s:util_path)

let g:noita_loaded = 1

