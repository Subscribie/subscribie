import os
import sys
from strictyaml import load


"""
Given a Shop directory, this script will check for any missing
settings the shop not not have, and add those keys
and values by looking up the default values from
subscribie.settings
"""

# SUBSCRIBIE_SKIP_SETTINGS_LOAD is needed
# since Subscribie application loads settings eagerly,
# and if any keys are missing from it settings the app will
# refuse to start, which is intentional.
# in an operational setting however it's useful to
# overwrite that such as when adding those missing
# settings as this script does.
os.environ["SUBSCRIBIE_SKIP_SETTINGS_LOAD"] = "True"
from subscribie.settings import (  # noqa: E402
    SETTINGS,
    get_missing_setting_keys,
    load_raw_settings_string,
    schema,
)

"""
Update all shops to have at least the default/example value
for any new setting keys pre-existing shops do not have
"""

SHOPS_DIR = sys.argv[1]

path = (
    SHOPS_DIR
    if SHOPS_DIR.endswith((".yaml", ".example"))
    else f"{SHOPS_DIR}/settings.yaml"
)

missing_keys = get_missing_setting_keys(path)

if missing_keys:
    shop_settings = load(load_raw_settings_string(path))

    for key in missing_keys:
        example_value = SETTINGS[key].example
        print(f"Adding missing key {key}={example_value!r} to {path}")
        shop_settings[key] = example_value

    updated_yaml = shop_settings.as_yaml()
    # Validate updated YAML against schema before writing
    load(updated_yaml, schema)

    with open(path, "w") as fp:
        fp.write(updated_yaml)
