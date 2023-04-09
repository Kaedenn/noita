
function get_settings()
  local i = 0
  local setting = ModSettingGetAtIndex(i)
  local results = {}
  while setting ~= nil do
    table.insert(results, {setting, ModSettingGet(setting)})
    i = i + 1
    setting = ModSettingGetAtIndex(i)
  end
  return results
end
