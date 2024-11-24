-- Emulate some functions implemented by Noita

io = require 'io'
os = require 'os'

DEV_ROOT = os.getenv("HOME") .. "/Programming/Noita"
DATA_PREFIX = DEV_ROOT .. "/ref/"
MODS_PREFIX = DEV_ROOT .. "/mods/"

mod_setting_cache = {}
globals_cache = {
  ["ORB_MAP_STRING"] = "8,1 1,-3 -9,7 -8,19 -18,28 -20,5 -1,31 20,31 19,5 6,3 19,-3",
  ["NEW_GAME_PLUS_COUNT"] = "0",
}

session_numbers = {
  ["world_seed"] = 0,
  ["NEW_GAME_PLUS_COUNT"] = 0,
}

local function _repr(value)
  if type(value) == "nil" then return tostring(value) end
  if type(value) == "boolean" then return tostring(value) end
  if type(value) == "function" then return tostring(value) end
  if type(value) == "number" then return tostring(value) end
  if type(value) == "string" then return ("%q"):format(value) end
  if type(value) == "userdata" then return tostring(value) end
  if type(value) == "table" then
    local count = 0
    for _ in pairs(value) do count = count + 1 end
    return ("table[%d]{%d}"):format(#value, count)
  end

  return ("unknown[%s] %q"):format(type(value), tostring(value))
end

function print_error(message)
  io.stderr:write(("ERROR: %s\n"):format(message))
  io.stderr:write(debug.traceback() .. "\n")
end

function GamePrint(message)
  io.stderr:write(("GamePrint: %s\n"):format(message))
end

function GamePrintImportant(title, description, ui_custom_decoration_file)
  io.stderr:write(("!! GamePrint: %s\n"):format(title))
  if description then
    io.stderr:write(("!! GamePrint: %s\n"):format(description))
  end
end

function ModSettingGet(conf_var)
  local value = mod_setting_cache[conf_var]
  GamePrint(("ModSettingGet(%q) => %s"):format(conf_var, _repr(value)))
  return value
end

--[[function ModSettingGetAtIndex(index) TODO
  for idx, name in ipairs(mod_setting_cache) do
    if idx = index then
      return {}
    end
  end
end]]

function ModSettingGetCount() return #mod_setting_cache end

ModSettingGetNextValue = ModSettingGet

function ModSettingSet(conf_var, value)
  GamePrint(("ModSettingSet(%q, %s)"):format(conf_var, _repr(value)))
  mod_setting_cache[conf_var] = value
end

function ModSettingSetNextValue(conf_var, value, is_default)
  GamePrint(("ModSettingSetNextValue(%q, %s, default=%s)"):format(
    conf_var, _repr(value), _repr(is_default)))
  mod_setting_cache[conf_var] = value
end

function GlobalsSetValue(key, value)
  globals_cache[key] = tostring(value)
end

function GlobalsGetValue(key, default)
  if globals_cache[key] == nil then GamePrint(("GlobalsGetValue(%q): not defined"):format(key)) end
  return globals_cache[key] or (default or "")
end

function ModTextFileGetContent(filepath)
  local finalpath = filepath
  if filepath:match("^data/") then
    finalpath = DATA_PREFIX .. filepath
  elseif filepath:match("^mods/") then
    finalpath = MODS_PREFIX .. filepath
  end
  if finalpath ~= filepath then
    GamePrint(("Rewrote %q to %q"):format(filepath, finalpath))
  end
  local fobj, err, errno = io.open(finalpath, "r")
  if fobj == nil then
    GamePrintImportant(("Error opening %q: error %d: %s"):format(finalpath, errno, err))
    return nil
  end
  local data = fobj:read("*all")
  fobj:close()
  return data
end

function ModDoesFileExist(filepath)
  local finalpath = filepath
  if filepath:match("^data/") then
    finalpath = DATA_PREFIX .. filepath
  elseif filepath:match("^mods/") then
    finalpath = MODS_PREFIX .. filepath
  end
  if finalpath ~= filepath then
    GamePrint(("Rewrote %q to %q"):format(filepath, finalpath))
  end
  local fobj, err, errno = io.open(finalpath, "r")
  if fobj == nil then
    return false
  end
  fobj:close()
  return true
end

function BiomeMapGetSize()
  local newgame_n = tonumber(GlobalsGetValue("NEW_GAME_PLUS_COUNT"))
  if newgame_n == 0 then
    return 70, 48
  end
  return 64, 48
end

function GameTextGet(text, param0, param1, param2) -- TODO
  -- luacheck: globals I18N
  if not I18N.initialized then
    I18N:init()
  end
  return I18N:get(text)
end

function GameTextGetTranslatedOrNot(text)
  print(("GameTextGetTranslatedOrNot(%q) -- STUB"):format(text))
  return GameTextGet(text)
end

function load_imgui(vinfo)
  if not vinfo then vinfo = {} end
  if type(vinfo) == "string" then vinfo = {mod=vinfo} end
  local version = vinfo.version or "unknown"
  local mod = vinfo.mod or "unknown"
  print(("load_imgui(version=%q, mod=%q)"):format(version, mod))
  return {}
end

--[[ STUBS ]]
function SessionNumbersGetValue(varname)
  local value = session_numbers[varname]
  if value then
    return value
  end
  print(("SessionNumbersGetValue(%q) -- STUB"):format(varname))
  return 0
end

function ModTextFileSetContent(filepath, content)
  print(("ModTextFileSetContent(%q, %d) -- STUB"):format(filepath, content.length))
end

function BiomeMapGetName(biome_x, biome_y)
  print(("BiomeMapGetName(%d, %d) -- STUB"):format(biome_x, biome_y))
  return "_EMPTY_"
end

function GameGetOrbCollectedThisRun(orb_id)
  print(("GameGetOrbCollectedThisRun(%d) -- STUB"):format(orb_id))
  return false
end

function BiomeGetValue(biome_name, key)
  print(("BiomeGetValue(%q, %q) -- STUB"):format(biome_name, key))
  return ""
end

setmetatable(_G, {
  __index = function(self, key)
    if not key:match("^_") then
      io.stderr:write(("_G[%s] not defined\n"):format(_repr(key)))
    end
    return nil
  end
})

