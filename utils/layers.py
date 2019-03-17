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
LAYERS
=======

Layers are used during the inference when the user wants to have conversation
about something specific like a story OR a joke.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import alice_config as alice


class Layers:
    """Class loads Layers."""

    def __init__(self):
        """
        Creates an instance of the class.

        Arguments:
            self: An instance of the class.

        """
        self.dict = {}
        self.stories = {}
        self.jokes = []

    def load_layers(self, layers_dir):
        """
        Configuring the layers directory.

        Arguments:
            self: An instance of the class.
            layers_dir: Folder for storing memory based data.
        """

        dict_xa_file = alice.dict_file
        with open(dict_xa_file, 'r') as dict_file:
            for line in dict_file:
                ln = line.strip()
                if not ln or ln.startswith('#'):
                    continue
                cap_words = ln.split(',')
                for cap_word in cap_words:
                    tmp = cap_word.strip()
                    self.dict[tmp.lower()] = tmp

        stories_xa_file = alice.stories_file
        with open(stories_xa_file, 'r') as stories_file:
            story_name, story_content = '', ''
            for line in stories_file:
                ln = line.strip()
                if not ln or ln.startswith('#'):
                    continue
                if ln.startswith('_NAME:'):
                    if story_name != '' and story_content != '':
                        self.stories[story_name] = story_content
                        story_name, story_content = '', ''
                    story_name = ln[6:].strip().lower()
                elif ln.startswith('_CONTENT:'):
                    story_content = ln[9:].strip()
                else:
                    story_content += ' ' + ln.strip()

            if story_name != '' and story_content != '':
                self.stories[story_name] = story_content

        jokes_xa_file = alice.jokes_file
        with open(jokes_xa_file, 'r') as jokes_file:
            for line in jokes_file:
                ln = line.strip()
                if not ln or ln.startswith('#'):
                    continue
                self.jokes.append(ln)
