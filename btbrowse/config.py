import os
import shutil
import pytoml

app_name = 'btbrowse'


# define filesystem paths

from xdg import BaseDirectory
package_dir = os.path.dirname(os.path.realpath(__file__))
config_dir = BaseDirectory.save_config_path(app_name)
#data_dir = BaseDirectory.save_data_path(app_name)
cache_dir = BaseDirectory.save_cache_path(app_name)
#runtime_dir = BaseDirectory.get_runtime_dir(app_name)


# load config file

config_file = os.path.join(config_dir, 'config.toml')

if not os.path.isfile(config_file):
    shutil.copyfile(os.path.join(package_dir, 'examples', 'config.toml'), config_file)

with open(config_file) as config_file_object:
    settings = pytoml.load(config_file_object)


# load config settings or defaults

try:
    torrent_dir = settings['torrent_dir']
except KeyError:
    torrent_dir = cache_dir

try:
    browse_only = settings['browse_only']
except KeyError:
    browse_only = False

try:
    hours_to_live = settings['hours_to_live']
except KeyError:
    hours_to_live = 12


# copy version number to settings

from version import __version__
settings['version'] = __version__

