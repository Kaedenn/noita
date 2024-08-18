--[[ Lua preloader
--
-- This script is invoked by the Lua wrapper script and implements dofile() and
-- dofile_once() capable of loading extracted Noita data files and/or Noita
-- mods.
--
-- ENVIRONMENT VARIABLES
--
-- DATA_ROOT    path to the directory containing the extracted `data` folder
-- MOD_ROOT     path to the directory containing the Noita mods
-- BASE         path to the directory containing the Lua wrapper script
-- LUA_DEBUG    if set, set _G.lualib_debug = true
--
-- EXTRA FEATURES
--
-- The following modules will always be preloaded (or attempted, anyway):
--    $BASE/../utility/lua/libkae.lua
--    $BASE/../utility/lua/functions.lua
-- Note that it's fine if these files don't exist; the errors aren't fatal.
--
-- The following special dofile() shorthands are also available:
--    dofile("inspect.lua") -- $BASE/../utility/lua/inspect.lua
--
-- EXTERNAL CONFIGURATION
--    _G.lualib_debug (boolean) if true, enable internal debugging
--
--]]

_G.lualib = true

if rawget(_G, "save_dofile") == nil then
  _G.save_dofile = _G.dofile
end

-- Configure global variables based on environment
local function _preconfig()
  local luadebug = os.getenv("LUA_DEBUG")
  _G.lualib_debug = false
  if luadebug ~= nil and luadebug ~= "" then
    _G.lualib_debug = true
  end
end
_preconfig()

local function lualib_debug(msg)
  if _G.lualib_debug then
    io.stderr:write(("DEBUG: %s\n"):format(msg))
  end
end

-- Return first non-nil result of values[1](value) for value in value[2:]
local function first_of(values)
  local func = values[1]
  for idx = 2, #values do
    local result = func(values[idx])
    if result ~= nil then
      return result
    end
  end
  return nil
end

-- Table of cached modules to support dofile_once()
MODULE_CACHE = {}

-- Table of dofile() path remap rules.
-- If env is not nil, then paths matching pattern will be prefixed with the
-- value of `os.getenv(env) .. "/"`. Otherwise, if prefix is not nil, then the
-- path will be prefixed with `prefix .. "/"`.
local PATH_REMAP = {
  { pattern = "^data/", env = "DATA_ROOT" },
  { pattern = "^mods/", env = "MOD_ROOT" },
  { pattern = "^utility/", prefix = os.getenv("BASE") .. "/.." },
  { pattern = "inspect.lua", prefix = os.getenv("BASE") .. "/../utility/lua" },
  { pattern = "^lualib/", env = "BASE" },
}

-- Table of modules that will always be loaded.
local PRELOAD_MODULES = {
  "utility/lua/libkae.lua",
  "utility/lua/functions.lua",
  "lualib/cell_factory.lua",
  "lualib/i18n.lua",
  "lualib/noitaemu.lua",
}

-- Add a remap path for the custom dofile() logic. At least one of `env` or
-- `prefix` must be supplied.
function add_path_remap(pattern, env, prefix)
  if env == nil and prefix == nil then
    error(("Failed to add remap '%s': path and/or env is nil"):format(pattern))
  end
  table.insert(PATH_REMAP, { pattern = pattern, env = env, prefix = prefix })
end

-- Define a custom dofile() function that allows loading files from one of the
-- PATH_REMAP entries above.
function dofile(path)
  local new_path = remap_path(path)
  if path ~= new_path then
    print(("dofile('%s') -- remap from '%s'"):format(new_path, path))
  else
    print(("dofile('%s') -- no remap"):format(new_path))
  end
  return _G.save_dofile(new_path)

  --[[ If we couldn't use the original dofile, we could do something like...
  local success, result = pcall(dofile_env, new_path, {})
  if not success then
    error(("%s: loading '%s' from '%s'"):format(result, new_path, path))
  end
  lualib_debug(("dofile('%s') -- via %s"):format(new_path, result, path))
  return result
  --]]
end

-- dofile with remapped path, but cache the result
function dofile_once(path)
  if MODULE_CACHE[path] ~= nil then
    return MODULE_CACHE[path]
  end
  lualib_debug(("Loading uncached module '%s'"):format(path))
  MODULE_CACHE[path] = dofile(path) or {}
  lualib_debug(("MODULE_CACHE[%q] = %s"):format(path, MODULE_CACHE[path]))
  return MODULE_CACHE[path]
end

-- Execute the module with remapped path, but using the given environment
function dofile_env(path, environment)
  local new_path = remap_path(path)
  local obj = loadfile(new_path)
  local set_f = setfenv(obj, setmetatable(environment, { __index = _G }));
  local status, result = pcall(set_f)
  if status == false then
    error(("dofile_env('%s') (as '%s') failed with '%s'"):format(
      path, new_path, result))
  end
  return environment
end

-- Remap a path given to dofile() to permit loading additional things, like the
-- data directory or various mods.
function remap_path(path)
  for idx, rule in pairs(PATH_REMAP) do
    local prefix = nil
    if rule.env ~= nil then
      prefix = os.getenv(rule.env)
    elseif rule.prefix ~= nil then
      prefix = rule.prefix
    end
    if prefix ~= nil and path:match(rule.pattern) then
      return ("%s/%s"):format(prefix, path)
    end
  end
  return path
end

for idx, path in pairs(PRELOAD_MODULES) do
  dofile(path)
end

return {}
