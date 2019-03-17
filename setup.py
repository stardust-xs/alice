# Copyright 2019 XA. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.
#
# =============================================================================
#
#                           A . L . I . C . E
#                A Logically Interacting Computing Entity
#
# =============================================================================

"""
SETUP
======

Setup file makes sure various things.

## Setup file checks:
    * Curremt Python version.
    * Installed Tensorflow version.
    * If all folders are present in place.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import sys
import pip
import ctypes

utils_dir = os.path.join(os.getcwd(), 'utils\\')
os.chdir(utils_dir)
sys.path.insert(0, os.getcwd())

import alice_config as alice

if sys.version_info < (3, 6, 0, 'final', 0):
    ctypes.windll.user32.MessageBoxW(
        0, 'Python 3.6 or later is required!', 'Warning', 16)
    raise SystemExit()
else:
    def install(package):
        pip.main(['install', package])

    try:
        print('# Checking tensorflow version.')
        import tensorflow as tf
        print(f'# Current tensorflow version installed is {tf.__version__}.')
    except ImportError:
        print('# Tensorflow is not installed. Installing now...')
        install('tensorflow==1.5.0')

    null_folders = [alice.engine_dir,
                    alice.core_dir,
                    alice.files_dir,
                    alice.json_dir,
                    alice.legacy_dir,
                    alice.layers_dir,
                    alice.logs_dir,
                    alice.model_dir,
                    alice.assistance_dir,
                    alice.character_dir,
                    alice.datasets_dir,
                    alice.parsed_dir]

    print('# Checking folders and creating if not exists.')
    for dir_to_create in null_folders:
        alice.create_dir(dir_to_create)

    print('# Done.')
