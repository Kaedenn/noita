--[[ Naively encode an XML file as JSON
--
-- Usage:
--  lua xml_to_json.lua data/materials.xml > materials.json
--
--]]

nxml = dofile("utility/lua/nxml.lua")
dofile("utility/lua/json.lua")
if not JSON or not JSON.encode then error("failed to load JSON") end

function read_file(filename)
  local lines = {}
  for line in io.open(filename):lines() do
    table.insert(lines, line)
  end
  return table.concat(lines, "\n")
end

function write_file(filename, text)
  local close = false
  local fileobj = io.stdout
  if type(filename) == "string" then
    fileobj = io.open(filename, "w")
    close = true
  elseif io.type(filename) == "file" then
    fileobj = filename
  elseif filename ~= nil then
    error(("invalid argument %s '%s'"):format(type(filename), filename))
  end

  fileobj:write(text)
  if close then fileobj:close() end
end

function main(argv)
  local ifile = nil
  local ofile = nil

  ifile = argv[1] or error("missing input file")
  ofile = argv[2] or io.stdout

  local lines_in = read_file(ifile)
  local xml_data = nxml.parse(lines_in)
  local json_text = JSON:encode(xml_data)
  write_file(ofile, json_text)
end

main(arg)

os.exit()

