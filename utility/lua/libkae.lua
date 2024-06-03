--[[ Common functions for interactive Lua experimentation

-- STRUCTURE ----------------------------------------------------------

kae
  .range(start, stop, step) -> iterable of number
  .formatter(format_string, ...static_values) -> function(...) -> string
  .sort
    .type_order[type_name] -> number
    .self_comparable(type_name) -> boolean
    .cmp3(value1, value2) -> number
    .cmp3_name(entry1, entry2) -> number
    .cmp3_type(entry1, entry2) -> number
    .cmp3_value(entry1, entry2) -> number
    .get3(cmp3_func_name) -> cmp3_func
    .chain3(cmp3_func...) -> cmp3_func
    .reverse3(cmp3_func) -> cmp3_func
    .cmp_name(entry1, entry2) -> boolean
    .cmp_type(entry1, entry2) -> boolean
    .cmp_value(entry1, entry2) -> boolean
    .get(cmp_func_name) -> cmp_func
    .chain(cmp_func...) -> cmp_func
    .reverse(cmp_func) -> cmp_func
    .from_cmp3(cmp3_function) -> cmp_func
  .table
    .unpack(table) -> object...
    .pack(object...) -> table
    .merge(table1, table2) -> table
    .update(table1, table2) -> table
    .count(table) -> number
    .has(table, key) -> boolean
    .iter(table, cmp_func=kae.sort.cmp3_name) -> iterable of key, value
    .print(table, config={})
    .p = .print
    .tostring(table, config={}) -> string
    .s = .tostring
  .array
    .count(table) -> number
    .has(table, value) -> boolean
    .concat(table1, table2) -> table
    .extend(table1, table2) -> table
    .join(table, sep_string=",", value_format="%s") -> string
    .print(table, config={})
  .string
    .keywords[index] -> string
    .is_keyword(keyword) -> boolean
    .at(string, index) -> char
    .each(string, as_byte=false) -> iterable of index, char
    .escape(string, quote='"') -> string
    .quote(string, quote='"') -> string
    .isprint(string) -> boolean
  .op
    table of "oper": { n = #, names = {}, func = function }
  .operator
    .lookup(opname)
    .get(opname)

Set _G.libkae_terse = true to enable several "terse" shorthands:
  _G.k = kae
  _G.k.t = kae.table
  _G.k.a = kae.array
  _G.k.s = kae.string
  _G.k.o = kae.op
So you can do something like `k.t.merge(table1, table2)`.

Set _G.libkae_do_test = true to invoke this module's self-test
functions.

-- NUMERIC UTILITIES --------------------------------------------------

kae.range(start = 1, stop, step = 1)
  Generate a sequence of numbers from start to stop, inclusive. Acts
  similarly to Python's range() function, except that values start at
  one instead of zero and both endpoints are inclusive.

  The resulting sequence is empty if the start and stop are improperly
  ordered with respect to step:
    range(1, -2)      yields nothing
    range(-2)         equivalent to above; yields nothing
    range(10, 1)      yields nothing
    range(1, 10, -1)  yields nothing

  An error is raised if #args == 0 or #args > 3.
  An error is raised if step is 0.

  Usage:
    for idx in kae.range(10) do ... end

  kae.range(stop)         === kae.range(1, stop, 1)
  kae.range(start, stop)  === kae.range(start, stop, 1)

  kae.range(10)         -> 1 2 3 4 5 6 7 8 9 10
  kae.range(1, 10)      -> 1 2 3 4 5 6 7 8 9 10
  kae.range(1, 10, 1)   -> 1 2 3 4 5 6 7 8 9 10
  kae.range(1, 10, 2)   -> 1 3 5 7 9
  kae.range(10, 1, -1)  -> 10 9 8 7 6 5 4 3 2 1
  kae.range(10, 1, -2)  -> 10 8 6 4 2
  kae.range(-10, 1)     -> -10 -9 -8 -7 -6 -5 -4 -3 -2 -1 0 1

-- VALUE HELPERS ------------------------------------------------------

kae.formatter(format_string, ...static_values)
  Create a function that formats values using a previously-specified
  format string.

  fmtfunc = kae.formatter("%s.%s = %s", "varname")
  fmtfunc("key", "value") -> "varname.key = value"

-- SORTING OPERATIONS -------------------------------------------------

kae.sort.type_order
  Table specifying the collation order for the known Lua datatypes.
  This table can be modified if desired and new types can be added if
  necessary.

kae.sort.self_comparable(type_name)
  True if the given type (as a string) is self-comparable (basically,
  it's either a number or a string).

kae.sort.cmp3(value1, value2)
  Compare two values, allowing for nil. For simplicity, nil is assumed
  to be less than everything but equal to itself. The collation order
  is ascending and roughly as follows:
  1. if types are the same and the type is self-comparable, then just
     compare the two values and return -1, 0, or 1 for LT, EQ, and GT.
  2. if the types are different, use the collation order given by
     kae.sort.type_order.
  3. nil values collate after non-nil values
  4. values of unknown types collate last

kae.sort.cmp3_name(entry1, entry2)
  cmp3(entry1.name, entry2.name)

kae.sort.cmp3_type(entry1, entry2)
  cmp3(entry1.type, entry2.type)

kae.sort.cmp3_value(entry1, entry2)
  cmp3(entry1.value, entry2.value)

kae.sort.chain3(cmp3_functions...)
  Chain two or more three-way-comparison functions

kae.sort.get3(cmp3_func)
  Get a three-way comparison function by name, or just ensure the
  cmp3_func argument is a function. Returns nil on unknown cmp3_func.

kae.sort.reverse3(cmp3_func)
  Get a three-way comparison function that is the inverse of the one
  given (-1 -> 1, 1 -> -1, 0 -> 0).

kae.sort.cmp_name(entry1, entry2)
  return entry1.name < entry2.name

kae.sort.cmp_type(entry1, entry2)
  return entry1.type < entry2.type

kae.sort.cmp_value(entry1, entry2)
  return entry1.value < entry2.value

kae.sort.get(cmp_func)
  Behaves identically to kae.sort.get3.

kae.sort.chain(cmp_functions...)
  Get a binary comparison function that tests a sequence of binary
  comparison functions and returns the first non-equal result. This
  allows for collation first by type, then by key, etc.

kae.sort.from_cmp3(cmp3_function)
  Convert a cmp3 function to something table.sort understands

kae.sort.reverse(sort_function)
  Build a sorting function that's the reverse of the one given
  (false -> true, true -> false).

-- TABLE OPERATIONS ---------------------------------------------------

kae.table contains functions that operate on tables. These functions
prefer pairs() over ipairs().

kae.table.merge(table1, table2) -> table
  Create a table with the entries from both table1 and table2.
  Duplicate keys will have their table2 value.

kae.table.update(table1, table2) -> table
  Merge entries from table2 into table1, in-place. Overwrites
  any keys in common.

kae.table.count(table) -> number
  Count the number of fields defined in the table.

kae.table.iter(table, cmp_func=kae.sort.cmp_name)
  Iterate over the table in ascending order. The optional cmp_func is a
  binary comparison operator `function(left, right) -> boolean`:
    cmp_func = function(first, second)
      return first < second
    end
  Assuming `table[key]=value`, `first` and `second` are tables with the
  following entries:
    {
      ["name"]=key,           entry key
      ["type"]=type(value),   entry value's type
      ["value"]=value         entry value
    }
  The following comparison functions are available for convenience:
    kae.sort.cmp_name         sort by key
    kae.sort.cmp_type         sort by value's type
    kae.sort.cmp_value        sort by value
  However, any binary function returning a boolean can be used. The
  default sort function is kae.sort.cmp_name.

  To group entries by their type, use
    function (entry1, entry2)
      if entry1.type == entry2.type then
        return entry1.key < entry2.key
      end
      return entry1.type < entry2.type
    end

kae.table.print(table[, config={}])
  Format and print a table. The following configuration options are
  available:
    KEY       TYPE        DEFAULT
    --------- ----------- ---------------------------------------------
    name      string      "table"
    iprint    boolean     false
    printfunc function    print
    sort      boolean     true
    reverse   boolean     false
    sortfunc  function    sort by type, then by name
    format    function    ("%s.%s = %s"):format(name, key, value)
    table     boolean     false
    type      string      nil

    TODO: NOT YET IMPLEMENTED
    recurse   boolean     false
    maxdepth  number      0; negative -> infinite
    omit      table       values to omit; used for recursive tables
    omit_str  string      "..."

  config.type filters results to those having type(val) == config.type
  config.table is shorthand for config.type = "table"

kae.table.tostring(table[, config={}])
  Format a table as a string. The following configuration options are
  available:
    KEY       TYPE        DEFAULT
    indent    string      ""
    sep       string      ","
    prefix    string      "{"
    suffix    string      "}"
    linesep   string      " "; set to "\n" for multi-line result
    sep_last  boolean     false; set to true to add sep to last entry

  As this function is implemented in terms of kae.table.print, all
  configuration values used by kae.table.print are also supported, with
  the exception of printfunc, which is ignored.

-- ARRAY OPERATIONS ---------------------------------------------------

kae.array contains functions that operate on "array-like" tables.
These functions prefer ipairs() over pairs().

kae.array.count(table)
  Count the number of elements in the array-like table.

kae.array.concat(table1, table2)
  Create a new array-like table by concatinating table2 to table1.

kae.array.extend(table1, table2)
  Append the entries of table2 to table1, in-place.

kae.array.join(table, sep_string=",", value_format=kae.formatter("%s"))
  Concatenate an array into a single string using the given separator
  character and the value formatting function.

  value_format can be nil to use "%s", a string, a function taking one
  argument, or a table with the "call" metamethod defined. Any other
  type will raise an error.

kae.array.print(table, config={})
  Call kae.table.print() with the following implicit configuration:
    config.iprint = true
    config.format = function(varname, index, value)
      return string.format("%s[%s] = %s", varname, index, value)
    end

-- STRING OPERATIONS --------------------------------------------------

kae.string contains functions that operate on strings or otherwise
assist string operations.

kae.string.at(string, index)
  Get the character at the given index, starting at 1. Values
  outside the interval [1, #string] give nil.

kae.string.each(string, as_byte = false)
  Iterate over the string, character-by-character. Returns numeric
  character values if as_byte is true. Example usage:
    for i, c in kae.string.each("abc") do print(i, c) end
    1       a
    2       b
    3       c
    for i, c in kae.string.each("abc", true) do print(i, c) end
    1       97
    2       98
    3       99

kae.string.escape(string, quote = '"')
  Escape non-printing characters in a string. Note that this is NOT
  indented to be sufficient for sanitizing user input. Replaces the
  characters in the interval [0, 31] with their hexadecimal escape
  sequence "\x00" .. "\x1f" with the following exceptions:
    \a \b \f \n \r \t \v
  Additionally, the following replacements are also made:
    " becomes \" (if quote == '"')
    ' becomes \' (if quote == "'")
    \ becomes \\
  If quote is not "'" and not '"', quote marks are left as-is. The
  resulting string is not quoted; use kae.string.quote for that.

kae.string.quote(string, quote = '"')
  Invoke kae.string.escape(string, quote) and surround the result
  with the given quote marks.

kae.string.isprint(string)
  True if the string contains only printable characters (or is a
  printable character).

-- OPERATOR TABLE AND FUNCTIONS ---------------------------------------

TODO

-- TESTING UTILITIES --------------------------------------------------

TODO

--]]

kae = {

  config = {
    printfunc = print,
    table_format = function(varname, key, value)
      return ("%s.%s = %s"):format(varname, key, value)
    end,
    array_format = function(varname, index, value)
      return ("%s[%d] = %s"):format(varname, index, value)
    end,
  },

  --[[ Apply configuration that alters default behavior below ]]
  configure = function (name, value)
    kae.config[name] = value
  end,

  --[[ Generate a range of numbers from start..stop by step, inclusive ]]
  range = function (...)
    local args = kae.table.pack(...)
    local tbl = { start = 1, stop = 0, step = 1 }
    if #args == 1 then
      tbl.stop = args[1]
    elseif #args == 2 then
      tbl.start = args[1]
      tbl.stop = args[2]
    elseif #args == 3 then
      tbl.start = args[1]
      tbl.stop = args[2]
      tbl.step = args[3]
      if tbl.step == 0 then
        error("range(...) step must not be zero")
      end
    elseif #args > 3 then
      error("too many arguments to range(...)")
    else
      error("too few arguments to range(...)")
    end

    local function next_func(itable, curr)
      if itable.step > 0 then
        if itable.start > itable.stop then return nil end
        if curr == nil then return itable.start end
        if curr + itable.step > itable.stop then return nil end
      end
      if itable.step < 0 then
        if itable.start < itable.stop then return nil end
        if curr == nil then return itable.start end
        if curr + itable.step < itable.stop then return nil end
      end
      return curr + itable.step
    end
    return next_func, tbl, nil
  end,

  --[[ Create a string formatter function that allows curried arguments ]]
  formatter = function (format_string, ...)
    local static_args = kae.table.pack(...)
    return function(...)
      local full_args = kae.array.concat(static_args, kae.table.pack(...))
      return string.format(format_string, kae.table.unpack(full_args))
    end
  end,

  --[[ Sorting functions ]]
  sort = {

    -- Types collate according to the following order. This table can
    -- be modified if desired (and/or if a Lua implementation defines
    -- more types). Types not listed will use "max".
    type_order = {
      ["number"] = 10,
      ["string"] = 20,
      ["table"] = 30,
      ["function"] = 40,
      ["userdata"] = 50,
      ["nil"] = 60,       -- nil collates last
      max = 100,          -- for unknown types
    },

    -- True if the type is less-than-comparable with itself
    self_comparable = function(type_name)
      if type_name == "number" then return true end
      if type_name == "string" then return true end
      if type_name == "table" then return false end
      if type_name == "function" then return false end
      if type_name == "userdata" then return false end
      if type_name == "nil" then return false end
      return false
    end,

    -- Three-way compare two values, with nil collating last
    cmp3 = function(value1, value2)
      -- all types support identity
      if value1 == value2 then return 0 end

      -- not-nil < nill
      if value1 == nil and value2 == nil then return 0 end
      if value1 == nil and value2 ~= nil then return 1 end
      if value1 ~= nil and value2 == nil then return -1 end

      -- not all types are comparable; see if we need special logic
      local type1, type2 = type(value1), type(value2)
      if type1 == type2 then
        if not kae.sort.self_comparable(type1) then
          -- same type, not comparable: compare their string values
          value1 = tostring(value1)
          value2 = tostring(value2)
        end
        if value1 == value2 then return 0 end
        if value1 < value2 then return -1 end
        return 1
      end

      -- two different types; use collation order
      local coll1 = kae.sort.type_order[type1] or kae.sort.type_order.max
      local coll2 = kae.sort.type_order[type2] or kae.sort.type_order.max
      if coll1 == nil then coll1 = 100 end
      if coll2 == nil then coll2 = 100 end
      if coll1 < coll2 then return -1 end
      return 1
    end,

    -- Three-way compare two labelled entries by name
    cmp3_name = function(entry1, entry2)
      return kae.sort.cmp3(entry1.name, entry2.name)
    end,

    -- Three-way compare two labelled entries by type
    cmp3_type = function(entry1, entry2)
      return kae.sort.cmp3(entry1.type, entry2.type)
    end,

    -- Three-way compare two labelled entries by value
    cmp3_value = function(entry1, entry2)
      return kae.sort.cmp3(entry1.value, entry2.value)
    end,

    -- Get the associated three-way comparison function
    get3 = function(func)
      if type(func) == "function" then return func end
      if func == "name" then return kae.sort.cmp3_name end
      if func == "type" then return kae.sort.cmp3_type end
      if func == "value" then return kae.sort.cmp3_value end
      return nil
    end,

    -- Chain two or more three-way compare functions
    chain3 = function(...)
      local cmps = {}
      for _, func in ipairs(kae.table.pack(...)) do
        table.insert(cmps, kae.sort.get3(func))
      end
      return function(left, right)
        for _, func in ipairs(cmps) do
          local result = func(left, right)
          if result ~= 0 then return result end
        end
        return 0
      end
    end,

    -- Create a sort3 function with reversed ordering
    reverse3 = function(cmp3_func)
      return function(...)
        return -cmp3_func(...)
      end
    end,

    -- As above, but as a binary comparison operator
    cmp_name = function(entry1, entry2)
      return entry1.name < entry2.name
    end,

    -- As above, but as a binary comparison operator
    cmp_type = function(entry1, entry2)
      return entry1.type < entry2.type
    end,

    -- As above, but as a binary comparison operator
    cmp_value = function(entry1, entry2)
      return entry1.value < entry2.value
    end,

    -- Get the associated binary comparison function
    get = function(func)
      if type(func) == "function" then return func end
      if func == "name" then return kae.sort.cmp_name end
      if func == "type" then return kae.sort.cmp_type end
      if func == "value" then return kae.sort.cmp_value end
      return nil
    end,

    -- Chain two or more binary comparison functions
    chain = function(...)
      local cmps = {}
      for _, func in ipairs(kae.table.pack(...)) do
        table.insert(cmps, kae.sort.get(func))
      end
      return function(left, right)
        for _, func in ipairs(cmps) do
          -- We need a three-way comparison in order to chain these
          local result1 = func(left, right)
          local result2 = func(right, left)
          -- Chain continues if result1 and result2 are both false
          if result1 or result2 then
            return result1
          end
        end
        -- Values are equal, which fails less-than
        return false
      end
    end,

    -- Create a sort function that is the inverse of another sort function
    reverse = function(cmp_func)
      return function(...)
        return not cmp_func(...)
      end
    end,

    -- Convert a sort3 function to a normal Lua table.sort function
    from_cmp3 = function(cmp3_func)
      return function(left, right)
        return cmp3_func(left, right) < 0
      end
    end,

  },

  --[[ Table functions ]]
  table = {

    -- Portable version of table.unpack for LuaJIT
    unpack = function(tbl)
      if table.unpack then
        return table.unpack(tbl)
      end
      return unpack(tbl)
    end,

    -- Portable version of table.pack for LuaJIT
    pack = function(...)
      if table.pack then
        return table.pack(...)
      end
      return {...}
    end,

    -- Create a new table with entries from tbl1 and tbl2
    merge = function(tbl1, tbl2)
      local tbl = {}
      for key, val in pairs(tbl1) do
        tbl[key] = val
      end
      for key, val in pairs(tbl2) do
        tbl[key] = val
      end
      return tbl
    end,

    -- Merge tbl2 into tbl1, in-place
    update = function(tbl1, tbl2)
      for key, val in pairs(tbl2) do
        tbl1[key] = val
      end
      return tbl1
    end,

    -- Count the number of fields in the given table
    count = function(tbl)
      local n = 0
      for key, val in pairs(tbl) do
        n = n + 1
      end
      return n
    end,

    -- True if the table contains the given key, regardless of value
    has = function(tbl, key)
      for table_key, _ in pairs(tbl) do
        if table_key == key then
          return true
        end
      end
      return false
    end,

    -- Iterate over a table in ascending order
    iter = function(tbl, func)
      local temp = {}
      for key, val in pairs(tbl) do
        table.insert(temp, {key=key, type=type(val), val=val})
      end
      local sort_func = func or kae.sort.from_cmp3(kae.sort.cmp3_name)
      table.sort(temp, sort_func)

      for idx, entry in ipairs(temp) do
        temp[entry.key] = idx
        entry.index = idx
      end

      local function next_func(ptable, pkey)
        if pkey and ptable[pkey] then
          local idx = ptable[pkey] + 1
          if idx <= #ptable then
            return ptable[idx].key, ptable[idx].val
          end
          return nil, nil
        end
        return ptable[1].key, ptable[1].val
      end

      return next_func, temp, nil
    end,

    -- Print a table
    print = function(tbl, config)
      local conf = config or {}
      local name = conf.name or "table"
      local pairfunc = conf.iprint and ipairs or pairs
      local printfunc = conf.printfunc or kae.config.printfunc
      local formatfunc = conf.format or kae.config.table_format
      local temp = {}
      for key, val in pairfunc(tbl) do
        table.insert(temp, {name=key, type=type(val), value=val})
      end
      if conf.sort ~= false then
        local sortfunc = conf.sortfunc
        if not conf.sortfunc then
          sortfunc = kae.sort.from_cmp3(kae.sort.chain3("type", "name"))
        end
        if conf.reverse then
          sortfunc = kae.sort.reverse(sortfunc)
        end
        table.sort(temp, sortfunc)
      end
      for idx, entry in pairs(temp) do
        local vtype = entry.type
        local key = entry.name
        local val = entry.value
        if conf.recurse and vtype == "table" then
          val = ("[%s]"):format(kae.table.tostring(val, conf))
        end
        local show = true
        if conf.table and vtype ~= "table" then show = false end
        if conf.type and vtype ~= conf.type then show = false end
        if show then
          printfunc(formatfunc(name, key, val))
        end
      end
    end,

    -- Convenience wrapper to kae.table.print
    p = function(args)
      if #args == 0 then error("missing required arguments") end
      local tbl = args[1]
      local conf = {}
      for key, val in pairs(args) do conf[key] = val end
      return kae.table.print(tbl, conf)
    end,

    -- Convert a table to a string
    tostring = function(tbl, config)
      local conf = config or {}
      local entries = {}

      -- Invoke kae.table.print to handle the actual logic
      kae.table.print(tbl, kae.table.merge(conf, {
        printfunc = function(entry)
          table.insert(entries, entry)
        end,
        format = function(name, key, val)
          return {name, key, val}
        end
      }))

      local formatfunc = conf.format or function(name, key, value)
        local valstr = tostring(value)
        if type(value) == "string" then
          valstr = ("%q"):format(value)
        end
        return ("%s = %s"):format(key, valstr)
      end

      -- Determine per-line formatting values
      local indent = conf.indent or ""
      local sep = conf.sep or ","
      local linesep = conf.linesep or " "

      -- Build an array of lines
      local lines = {}
      for enr, entry in ipairs(entries) do
        local varname = entry[1]
        local tkey = entry[2]
        local tvalue = entry[3]
        local curr_sep = sep
        if enr == #entries and not conf.sep_last then
          curr_sep = ""
        end
        local line = ("%s%s%s"):format(
          indent,
          formatfunc(varname, tkey, tvalue),
          curr_sep
        )
        table.insert(lines, line)
      end

      -- Build a final string
      local afix_sep = conf.linesep or ""
      return ("%s%s%s%s%s"):format(
        conf.prefix or "{",
        afix_sep,
        table.concat(lines, conf.linesep or " "),
        afix_sep,
        conf.suffix or "}")
    end,

    -- Convenience wrapper to kae.table.tostring
    s = function(args)
      if #args == 0 then error("missing required arguments") end
      local tbl = args[1]
      local conf = {}
      for key, val in pairs(args) do conf[key] = val end
      return kae.table.tostring(tbl, conf)
    end,
  },

  --[[ Table functions for operating on array-like tables ]]
  array = {
    -- Count the number of fields in an array-like table
    count = function(tbl)
      local n = 0
      for index, value in ipairs(tbl) do
        n = n + 1
      end
      return n
    end,

    -- True if the array contains the item
    has = function(tbl, item)
      for _, entry in ipairs(tbl) do
        if entry == item then
          return true
        end
      end
      return false
    end,

    -- Concatenate two array-like tables and return the result
    concat = function(tbl1, tbl2)
      local tbl = {}
      kae.array.extend(tbl, tbl1)
      kae.array.extend(tbl, tbl2)
      return tbl
    end,

    -- Merge one array-like table into another, in-place
    extend = function(tbl1, tbl2)
      for index, value in ipairs(tbl2) do
        table.insert(tbl1, value)
      end
      return tbl1
    end,

    -- Join an array-like table of strings into a single string
    join = function(tbl, sep_string, value_format)
      local sep = sep_string or ","
      local vformat = kae.formatter("%s")
      if type(value_format) == "string" then
        vformat = kae.formatter(value_format)
      elseif type(value_format) == "function" then
        vformat = value_format
      elseif type(value_format) == "table" then
        vformat = function(...) return value_format(...) end
      elseif value_format ~= nil then
        error(("invalid value_format type %s"):format(type(value_format)))
      end

      local result = ""
      for idx, value in ipairs(tbl) do
        if idx ~= 1 then
          result = result .. sep
        end
        result = result .. vformat(value)
      end
      return result
    end,

    -- Print an array-like table
    print = function(tbl, conf)
      local iconf = {}
      if conf then kae.table.merge(iconf, conf) end
      iconf.iprint = true
      iconf.format = function(varname, index, val)
        return string.format("%s[%s] = %s", varname, index, val)
      end
      kae.table.print(tbl, iconf)
    end,

    -- Convert an array-like table of values to a single string
    tostring = function(tbl, conf)
      if not conf then conf = {} end
      local iconf = {}
      kae.table.merge(iconf, conf)
      local entries = {}
      iconf.iprint = true
      iconf.printfunc = function(entry) table.insert(entries, entry) end
      iconf.format = function(varname, index, val)
        return {varname, index, val}
      end
      iconf.sortfunc = function(val1, val2)
        return val1.name < val2.name
      end

      kae.table.print(tbl, iconf)

      local formatfunc = conf.format or function(name, key, value)
        local valstr = tostring(value)
        if type(value) == "string" then
          valstr = ("%q"):format(value)
        end
        return valstr
      end

      local indent = conf.indent or ""
      local sep = conf.sep or ","

      local lines = {}
      for enr, entry in ipairs(entries) do
        local varname = entry[1]
        local tkey = entry[2]
        local tvalue = entry[3]
        local curr_sep = sep
        if enr == #entries and not conf.sep_last then
          curr_sep = ""
        end
        local line = ("%s%s%s"):format(
          indent,
          formatfunc(varname, tkey, tvalue),
          curr_sep
        )
        table.insert(lines, line)
      end

      local afix_sep = conf.linesep or ""
      return ("%s%s%s%s%s"):format(
        conf.prefix or "{",
        afix_sep,
        table.concat(lines, conf.linesep or " "),
        afix_sep,
        conf.suffix or "}")
    end,
  },

  -- [[ True if tbl is an array (lacks holes, lacks named keys) ]]
  is_array = function(tbl)
    local tsize = #tbl
    local tcount = kae.table.count(tbl)
    local acount = kae.array.count(tbl)
    return tsize == tcount and tcount == acount
  end,

  --[[ Functions that operate on (or assist with) strings ]]
  string = {

    keywords = {
      "and", "break", "do", "else", "elseif", "end", "false", "for",
      "function", "if", "in", "local", "nil", "not", "or", "repeat",
      "return", "then", "true", "until", "while",
    },

    -- True if the string is a keyword (and should be escaped)
    is_keyword = function(value)
      for _, keyword in pairs(kae.string.keywords) do
        if value == keyword then
          return true
        end
      end
      return false
    end,

    -- Get a specific index of a string
    at = function(value, index)
      if index > 0 and index < #value then
        return string.char((value):byte(index))
      end
      return nil
    end,

    -- Iterate over a string, character-by-character
    each = function(value, as_byte)
      return function(str, index)
        if index == nil or str == nil then return nil, nil end
        if index >= #str then return nil, nil end
        index = index + 1
        result = str:byte(index)
        if not as_byte then result = string.char(result) end
        return index, result
      end, value, 0
    end,

    -- Escape a string
    escape = function(value, quote)
      if quote == nil then quote = '"' end
      if kae.string.is_keyword(value) then
        return ("%s%s%s"):format(quote, value, quote)
      end
      local escaped_chars = {}
      for idx, byte in kae.string.each(value, true) do
        local char = string.char(byte)
        if char == "\a" then char = "\\a"
        elseif char == "\b" then char = "\\b"
        elseif char == "\f" then char = "\\f"
        elseif char == "\n" then char = "\\n"
        elseif char == "\r" then char = "\\r"
        elseif char == "\t" then char = "\\t"
        elseif char == "\v" then char = "\\v"
        elseif char == "\\" then char = "\\\\"
        elseif char == quote then char = "\\" .. quote
        elseif byte < 0x32 or byte >= 0x7f then
          char = ("\\x%02x"):format(byte)
        end
        table.insert(escaped_chars, char)
      end
      return table.concat(escaped_chars)
    end,

    -- Quote a string
    quote = function(value, quote)
      if quote == nil then quote = '"' end
      return quote .. kae.string.escape(value, quote) .. quote
    end,

    -- True if the string contains only printable characters
    isprint = function(value)
      local result = true
      for index, byte in kae.string.each(value, true) do
        if byte < 0x32 or byte >= 0x7f then
          result = false
        end
      end
      return result
    end,

  },

  --[[ Debugging utilities (WIP) ]]
  debug = setmetatable({
    enable = false,

    target = io.stderr,

    getframe = function(adjust) -- TODO
    end,

    stackframes = function() -- TODO
    end,

    parse_frame = function(line)
      local file_line, func = line:match("^[%s]+(.*): in (.*)")
      if file_line and func then
        local file, linenr = file_line:match("(.*):([%d]+)")
        file = file or file_line
        linenr = linenr or ""
        return {file, linenr, func}
      end
      return nil
    end,

    parse_traceback = function(traceback)
      local tb = traceback or debug.traceback()
      local errors, frames = {}, {}
      local block = 0
      for line in tb:gmatch("[^\n]+") do
        if block == 0 then
          if line:gmatch("stack traceback:") then
            block = 1
          else -- error message
            local file, line_nr, msg = line:match("([^:]+):([%d]+): (.*)")
            table.insert(errors, {file, line_nr, msg})
          end
        else -- stack frame
          table.insert(frames, kae.debug.parse_frame(line))
        end
      end
      -- if we generated our own traceback, purge the first entry
      if not traceback then
        table.remove(frames, 1)
      end
      return errors, frames
    end,

    print = function(value)
      local out = kae.debug.target or print
      if type(out) == "function" then
        out(value)
      elseif io.type(out) == "file" then
        out:write(value)
        out:write(kae.debug.eol or "\n")
      else
        print(("error: unexpected kae.debug.target %s"):format(out))
        print(value)
      end
    end,
  },
  {
    __call = function(self, msg, ...) -- TODO
      if self.enable then
        print(msg)
      end
    end
  }),

  --[[ Operator table (WIP) ]]
  op = {
    eq = { n = 2, names = {"=="}, func = function(a, b) return a == b end },
    ne = { n = 2, names = {"~="}, func = function(a, b) return a ~= b end },
    ge = { n = 2, names = {">="}, func = function(a, b) return a >= b end },
    gt = { n = 2, names = {">"}, func = function(a, b) return a > b end },
    le = { n = 2, names = {"<="}, func = function(a, b) return a <= b end },
    lt = { n = 2, names = {"<"}, func = function(a, b) return a < b end },
    is = { n = 1, names = {"true"}, func = function(a)
      if a then return true else return false end
    end},
    isnot = { n = 1, names = {"false"}, func = function(a)
      if not a then return true else return false end
    end},
    neg = { n = 1, names = {"not"}, func = function(a) return not a end },
    istrue = { n = 1, func = function(a) return a == true end },
    isfalse = { n = 1, func = function(a) return a == false end },
    isnil = { n = 1, func = function(a) return a == nil end },
  },

  --[[ Operator functions (WIP) ]]
  operator = {
    -- Lookup an operator by key or by name. Returns an operator definition.
    lookup = function(opname)
      if kae.op[opname] ~= nil then
        return kae.op[opname]
      end
      for opid, opdef in pairs(kae.op) do
        if opdef.names and kae.array.has(opdef.names, opname) then
          return opdef
        end
      end
      error(("Failed to find operator %s"):format(opname))
    end,

    -- Get an operator and return something that can be called
    get = function(opname)
      local opdef = kae.operator.lookup(opname)
      return setmetatable({
        n = opdef.n,
        names = opdef.names or {},
        func = opdef.func
      }, { __call = function(self, ...) return self.func(...) end })
    end
  },

  --[[ Alias to kae.operator.get ]]
  get_op = function(opname)
    return kae.operator.get(opname)
  end,

  --[[ Testing functions (WIP) ]]
  test = {
    assert = function(operator, value1, value2)
      local op = kae.get_op(operator)
    end
  }
}

-- If terse mode is enabled, then set some shorthand variables
if rawget(_G, "libkae_terse") then
  _G.k = {}
  _G.k.t = kae.table
  _G.k.a = kae.array
  _G.k.s = kae.string
  _G.k.o = kae.op
end

-- Run the test suite if testing is enabled (TODO) {{{0
if rawget(_G, "libkae_do_test") then
  local log_asserts = rawget(_G, "libkae_log") or false

  local function test_log(msg)
    if rawget(_G, "libkae_test_log") then
      print(string.format("assert(%s) passed", msg))
    end
  end

  function assert1(cond, value)
  end

  function assert2(cond, value1, value2)
  end

  function assert_size(thing, size)
  end

  function assert_num_indexes(thing, num_indexes)
  end

  function assert_num_keys(thing, num_keys)
  end

  local test = {
    assert1 = function(cond, value)
      local func = kae.get_op(cond)
      local msg = string.format("%s %s", cond, value)
      assert(func(value), msg)
      test_log(msg)
    end,
    assert = function(cond, value1, value2)
      local func = kae.get_op(cond)
      local msg = string.format("%s %s %s", value1, cond, value2)
      assert(func(value1, value2), msg)
      test_log(msg)
    end,
  }

  test.eq = function(value1, value2) test.assert("eq", value1, value2) end
  test.ne = function(value1, value2) test.assert("ne", value1, value2) end
  test.gt = function(value1, value2) test.assert("gt", value1, value2) end
  test.ge = function(value1, value2) test.assert("ge", value1, value2) end
  test.lt = function(value1, value2) test.assert("lt", value1, value2) end
  test.le = function(value1, value2) test.assert("le", value1, value2) end
  test.istrue = function(value) test.assert1("true", value) end
  test.isfalse = function(value) test.assert1("false", value) end

  function libkae_test_table()
  end

  function libkae_test_array()
  end

  function libkae_test_string()
  end

  function libkae_test_op()
  end

  function libkae_test()
    local saved_log = false
    if rawget(_G, "libkae_test_log") then
      saved_log = true
    end
    local save_log = rawget(_G, "libkae_test_log")
    test.eq(1, 1)
    test.ne(1, 0)
    test.gt(1, 0)
    test.ge(1, 1); test.ge(1, 0)
    test.lt(0, 1)
    test.le(1, 1); test.le(0, 1)
    test.istrue(true)
    test.isfalse(false)
    local tbl1 = {foo=1, bar=2, baz=5, qux=3}
    local tbl2 = {abc=4, def=2, ghi=1, jkl=3}

    local arr1 = {"foo", "bar", "baz"}
    local arr2 = {"qux", "cat", "dog"}

    test.eq(kae.table.count(tbl1), 4)
    test.eq(kae.table.count(tbl2), 4)
    test.eq(kae.array.count(arr1), 3)
    test.eq(kae.array.count(arr2), 3)

    local tbl3 = kae.table.merge(tbl1, tbl2)
    test.eq(kae.table.count(tbl1), 4)
    test.eq(kae.table.count(tbl2), 4)
    test.eq(kae.table.count(tbl3), 8)

    kae.table.update(tbl3, tbl1)
    test.eq(kae.table.count(tbl3), 8)
    kae.table.update(tbl3, tbl2)
    test.eq(kae.table.count(tbl3), 8)
    kae.table.update(tbl1, tbl2)
    test.eq(kae.table.count(tbl1), 8)
    test.eq(kae.table.count(tbl2), 4)

    test.eq(3, 3)
  end

end -- End test suite 0}}}

return kae

