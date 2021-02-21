import os
import tempfile


#/* (technician use only)
# * List of default search filenames.
# */
CONFIGS_DIR = os.path.realpath(
    os.path.dirname(__file__)
)

PROGRAM_DIR = os.path.realpath(
    os.path.join(CONFIGS_DIR, os.pardir)
)


TEMP_DIR = os.path.realpath(
    tempfile.gettempdir()
)

DEFAULT_RSNAPSHOT_CONFIG_FILE = os.path.realpath(
    os.path.join(CONFIGS_DIR, 'rsnapshot.cfg')
)

DEFAULT_PLC_SETTINGS_FILE = os.path.realpath(
    os.path.join(CONFIGS_DIR, 'plc_settings.update_from_git')
)

DEFAULT_EMAIL_SETTINGS_FILE = os.path.realpath(
    os.path.join(CONFIGS_DIR, 'email_settings.update_from_git')
)

DEFAULT_OTHER_SETTINGS_FILE = os.path.realpath(
    os.path.join(CONFIGS_DIR, 'other_settings.update_from_git')
)


DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE = os.path.realpath(
    os.path.join(TEMP_DIR, 'plc_rsnapshot_output.log')
)

DEFAULT_RSNAPSHOT_INTERMEDIATE_ERROR_FILE = os.path.realpath(
    os.path.join(TEMP_DIR, 'plc_rsnapshot_error.log')
)



DEFAULT_DISK_CHECKING_LOCKFILE = os.path.realpath(
    os.path.join(TEMP_DIR, 'plc_disk_checking.pid')
)

DEFAULT_DISK_ERROR_LOCKFILE = os.path.realpath(
    os.path.join(TEMP_DIR, 'plc_disk_error.pid')
)

#/* important: set the current pomeep program version here */
CURRENT_VERSION = "v2622b"

