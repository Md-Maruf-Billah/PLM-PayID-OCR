-- Reference snippet: copy into ~/.hammerspoon/init.lua (or require it from
-- there) and reload Hammerspoon's config. Binds F8 to run one scan.
--
-- Update PYTHON_PATH and SCRIPT_PATH for your machine, e.g.:
--   PYTHON_PATH = "/Users/cashier/Documents/playlive-payid-ocr/.venv/bin/python"
--   SCRIPT_PATH = "/Users/cashier/Documents/playlive-payid-ocr/src/main.py"

local PYTHON_PATH = "/path/to/playlive-payid-ocr/.venv/bin/python"
local SCRIPT_PATH = "/path/to/playlive-payid-ocr/src/main.py"

hs.hotkey.bind({}, "F8", function()
    hs.task.new(PYTHON_PATH, nil, { SCRIPT_PATH }):start()
end)
