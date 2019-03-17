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
HPARAMS
========

Hparams is used for accessing the defined hyperparameters which are used
during training the data.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import json
import codecs

import tensorflow as tf

import alice_config as alice


class HParams:
    """Load and access hyperparameters."""

    def __init__(self, hparams_dir):
        """
        Creates a new cleaning instance for each file.

        Arguments:
            self: An instance of the class.
            hparams_dir: Directory storing hparams file.

        """
        self.hparams = self.load_hparams(hparams_dir)

    @staticmethod
    def load_hparams(hparams_dir):
        """
        Load hparams from an existing directory.

        Arguments:
            hparams_dir: Directory storing hparams file.
        """
        hparams_file = alice.hparams_file
        if tf.gfile.Exists(hparams_file):
            with codecs.getreader('utf-8')(tf.gfile.GFile(hparams_file, 'rb')) as file:
                try:
                    hparams_values = json.load(file)
                    hparams = tf.contrib.training.HParams(**hparams_values)
                except ValueError:
                    print('# Error loading hparams file.')
                    return None
            return hparams
        else:
            return None
