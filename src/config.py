import configparser

CONFIG_FILE = 'config.ini'

def get_config():
    """Reads the configuration from the .ini file."""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config

def get_setting(section, key, fallback=None):
    """Gets a specific setting from the config file."""
    config = get_config()
    return config.get(section, key, fallback=fallback)

def update_setting(section, key, value):
    """Updates a setting in the config file."""
    config = get_config()
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, key, str(value))
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

import os

if __name__ == '__main__':
    # --- Example Usage and Testing ---
    print("Running config module tests...")

    # Set up a known state for the config file for testing
    update_setting('Settings', 'scan_interval_seconds', '5')
    update_setting('Settings', 'test_setting', 'hello')

    # Test reading settings
    interval = get_setting('Settings', 'scan_interval_seconds', fallback='10')
    test_val = get_setting('Settings', 'test_setting', fallback='world')

    assert interval == '5'
    assert test_val == 'hello'
    print("Assertion passed: Correctly read initial settings.")

    # Test updating a setting
    update_setting('Settings', 'scan_interval_seconds', '15')
    interval = get_setting('Settings', 'scan_interval_seconds')
    assert interval == '15'
    print("Assertion passed: Correctly updated a setting.")

    # Reset to default
    update_setting('Settings', 'scan_interval_seconds', '5')

    print("Config module tests passed successfully.")
