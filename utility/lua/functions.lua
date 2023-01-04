-- Common functions for interactive lua5.3 experimentation

-- Use the following to debug Lua errors:
-- (11:32:26 AM) kakolainen[m]:
--    setmetatable(_G, {
--      __index = function(t,k)
--        debug.traceback();
--        error(tostring(k).." not in table");
--      end
--    });
--    print(_G[nil])
-- (11:33:54 AM) kakolainen[m]: easier way to catch all errors and print stacktrace with just
--    xpcall(f, debug.traceback)

function pdir(tbl, conf)
  if not conf then conf = {} end
  local vname = "tbl"
  if conf.name then
    vname = conf.name
  end
  for key, val in pairs(tbl) do
    local show = true
    if conf.table then
      if type(val) ~= "table" then
        show = false
      end
    end
    if conf.type and conf.type ~= type(val) then
      show = false
    end
    if show then
      print(string.format("%s.%s = %s", vname, key, tostring(val)))
    end
  end
end

function pvar(vname, conf)
  local pconf = {}
  if conf then
    for key, val in pairs(conf) do
      pconf[key] = val
    end
  end
  pconf.name = vname
  pdir(_G[vname], conf)
end

function dir(tbl)
  pdir(tbl, {})
end
