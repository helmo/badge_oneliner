import ugfx, wifi, badge, deepsleep
from . import urequests_pmenke as requests
from time import sleep

ugfx.init()
ugfx.input_init()
# Make sure WiFi is connected
wifi.init()

def set_message(text):
  ugfx.clear(ugfx.WHITE);
  ugfx.string(10,10,text,"Roboto_Regular12", 0)
  ugfx.flush()
  badge.eink_busy_wait()

set_message("Phonebook is loading. Please be patient")

debug_enabled = badge.nvs_get_str("oneliner", "debug") == "True"

def debug(message):
  if debug_enabled:
    set_message(message)

limit = 5
offset= 1

def load_entries(limit, offset):
  debug("Waiting for wifi...")

  # Wait for WiFi connection
  while not wifi.sta_if.isconnected():
    sleep(0.1)
    pass

  debug("Got wifi. Loading data.")

  data=None
  try:
    url = "http://83.137.144.16/api/oneliner"
    r = requests.get(url, headers={"Host": "defeest.nl"}, host_override="defeest.nl")
    data = r.text
    r.close()
  except Exception as e:
    set_message("Unexpected error: "+str(e))
    sleep(10)
    deepsleep.reboot()
  try:
    entries = []
    for entry in data.split('\n'):
      if entry == "":
        continue
      #extension = entry.split(',')[0]
      name = (entry.split(',')[0]).replace('"', '')
      entries.append((extension,name))
    debug("Loaded "+str(len(entries))+" entries")
    return entries
  except Exception as e:
    set_message("Parsing error: "+str(e))
    sleep(10)

def draw(entries):
  debug("Will now draw")
  y = 10
  ugfx.clear(ugfx.WHITE)
  for entry in entries:
    extension = entry[0]
    name = entry[1]
    ugfx.string(10, y, extension + " -> " + name, "Roboto_Regular12", 0)
    y += 20
  ugfx.flush()
  badge.eink_busy_wait()

up_state   = False
down_state = False
def up_pressed(pressed):
  global up_state, offset
  if up_state and not pressed:
    offset += 1
    draw(load_entries(limit, offset))
  up_state = pressed

def down_pressed(pressed):
  global down_state, offset
  if down_state and not pressed and offset > 1:
    offset -= 1
    draw(load_entries(limit, offset))
  down_state = pressed

def set_debug(pressed):
  if not pressed:
    if debug_enabled:
      set_message("Debug disabled")
      badge.nvs_set_str("oneliner", "debug", "False")
    else:
      set_message("Debug enabled")
      badge.nvs_set_str("oneliner", "debug", "True")

try:
  draw(load_entries(limit, offset))
except Exception as e:
  set_message("Error: "+str(e))
  sleep(10)
  deepsleep.reboot()

ugfx.input_attach(ugfx.JOY_UP, up_pressed)
ugfx.input_attach(ugfx.JOY_DOWN, down_pressed)
ugfx.input_attach(ugfx.BTN_SELECT, lambda pressed: deepsleep.reboot())
ugfx.input_attach(ugfx.BTN_START, set_debug)

while True:
  sleep(0.1)

