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
PARSER
=======

Parser is used for parsing the data/conversations from Reddit datasets.
This data is then cleaned using "cleaner.py" and "refiner.py" files.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from bz2 import BZ2File
from datetime import datetime
import os
import re
import sys
import json

import alice_config as alice

start_time = datetime.now()


class Parser(object):
    """Parse relevant data from Reddit datasets."""

    def __init__(self):
        """
        Creates an instance of the class.

        Arguments:
            self: An instance of the class.

        """
        pparams_file = alice.pparams_file
        with open(pparams_file, 'r') as params_file:
            config_file = json.load(params_file)

        self.report_file = alice.subreddits_file
        self.output_path = alice.parsed_dir
        self.output_file = alice.cassiopeia_output_file
        self.conversation_line_cache_size = config_file['conversation_line_cache_size']
        self.output_file_size = config_file['output_file_size']
        self.print_every = config_file['print_every']

        self.subreddit_blacklist = set(config_file['subreddit_blacklist'])
        self.subreddit_whitelist = set(config_file['subreddit_whitelist'])
        self.substring_blacklist = set(config_file['substring_blacklist'])

    def parse(self):
        """
        Parse the Reddit data into a "./parsed/" folder.

        Arguments:
            self: An instance of the class.

        """
        if os.path.isfile(self.output_path):
            print('# File with same name already exists in the output folder.')
            return

        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)

        subreddit_dict = {}
        conversation_line_dict = {}
        cache_count = 0
        raw_data = self.get_raw_data_enumerator()
        output_handler = OutputHandler(os.path.join(
            self.output_path, self.output_file), self.output_file_size)

        for count_lines, line in enumerate(raw_data):
            line = line.decode('utf-8')
            if len(line) > 1 and (line[-1] == '}' or line[-2] == '}'):
                conversation_line = json.loads(line)
                if self.post_qualifies(conversation_line):
                    sub = conversation_line['subreddit']
                    if sub in subreddit_dict:
                        subreddit_dict[sub] += 1
                    else:
                        subreddit_dict[sub] = 1
                    conversation_line_dict[conversation_line['name']] = RedditConversationLine(
                        conversation_line)
                    cache_count += 1
                    if cache_count % self.print_every == 0:
                        end_time = datetime.now()
                        elapsed_time = (end_time - start_time)
                        print('\r# {:,} lines cached in {}.'.format(
                            cache_count, str(elapsed_time).split('.')[0]), end='')
                        sys.stdout.flush()
                    if cache_count > self.conversation_line_cache_size:
                        print()
                        self.process_cached_conversation_lines(
                            conversation_line_dict)
                        self.write_cached_conversation_lines(
                            conversation_line_dict, output_handler)
                        self.generate_subreddit_report(
                            subreddit_dict)
                        conversation_line_dict.clear()
                        cache_count = 0
                    end_time = datetime.now()
                    elapsed_time = (end_time - start_time)

        self.process_cached_conversation_lines(conversation_line_dict)
        self.write_cached_conversation_lines(
            conversation_line_dict, output_handler)
        self.generate_subreddit_report(subreddit_dict)

    def get_raw_data_enumerator(self):
        for input_file in os.listdir(alice.datasets_dir):
            if input_file.endswith(alice.bz2_file):
                loading_start_time = datetime.now()
                current_input_file = os.path.join(
                    alice.datasets_dir, input_file)
                self.input_file = current_input_file
                print('\n# Loading "{}" file in memory at {}.'.format(
                    input_file, loading_start_time.strftime('%I:%M %p')))
                with BZ2File(self.input_file, 'r') as raw_data:
                    for line in raw_data:
                        yield line

    def post_qualifies(self, json_object):
        """
        Checks if the post was relevant OR good in the datasets.

        Arguments:
            self: An instance of the class.
            json_object: Instantiate json object.

        """
        body = json_object['body'].encode('ascii', 'ignore').strip()
        body = body.decode('utf-8')

        post_length = len(body)
        if post_length < 8 or post_length > 240:
            return False

        subreddit = json_object['subreddit']

        # Filter posts based on the configured whitelist and blacklist
        if len(self.subreddit_whitelist) > 0 and subreddit not in self.subreddit_whitelist:
            return False
        if len(self.subreddit_blacklist) > 0 and subreddit in self.subreddit_blacklist:
            return False
        if len(self.substring_blacklist) > 0:
            for substring in self.substring_blacklist:
                if body.find(substring) >= 0:
                    return False

        # Preprocess the conversation lines text
        body = re.sub('[ \t\n]+', ' ', body)  # Strip whitespace with space.
        body = re.sub('\^', '', body)  # Strip out carets.
        body = re.sub('\\\\', '', body)  # Strip out backslashes.
        body = re.sub('&lt;', '<', body)  # Replace '&lt;' with '<'
        body = re.sub('&gt;', '>', body)  # Replace '&gt;' with '>'
        body = re.sub('&amp;', '&', body)  # Replace '&amp;' with '&'

        post_length = len(body)
        if post_length < 8 or post_length > 240:
            return False

        json_object['body'] = body  # Save changes

        return True

    def process_cached_conversation_lines(self, conversation_line_dict):
        """
        Process conversations.

        Arguments:
            self: An instance of the class.
            conversation_line_dict: Dictionary of json object.

        """
        counter_index = 0
        for my_id, my_conversation_line in conversation_line_dict.items():
            counter_index += 1
            if counter_index % self.print_every == 0:
                end_time = datetime.now()
                elapsed_time = (end_time - start_time)
                print('\r# {:,} lines processed in {}.'.format(
                    counter_index, str(elapsed_time).split('.')[0]), end='')
                sys.stdout.flush()

            if my_conversation_line.parent_id is not None:
                if my_conversation_line.parent_id in conversation_line_dict:
                    parent = conversation_line_dict[my_conversation_line.parent_id]
                    if parent.child_id is None:
                        parent.child_id = my_id
                    else:
                        parent_previous_child = conversation_line_dict[parent.child_id]
                        if parent.parent_id in conversation_line_dict:
                            grandparent = conversation_line_dict[parent.parent_id]
                            if my_conversation_line.author == grandparent.author:
                                parent.child_id = my_id
                            elif (parent_previous_child.author != grandparent.author and my_conversation_line.score > parent_previous_child.score):
                                parent.child_id = my_id
                        elif my_conversation_line.score > parent_previous_child.score:
                            parent.child_id = my_id
                else:
                    my_conversation_line.parent_id = None

    def write_cached_conversation_lines(self, conversation_line_dict, output_handler):
        """
        Writes conversations in memory.

        Arguments:
            self: An instance of the class.
            conversation_line_dict: Dictionary of json object.

        """
        counter_index = 0
        prev_print_count = 0
        for k, v in conversation_line_dict.items():
            if v.parent_id is None and v.child_id is not None:
                conversation_line = v
                depth = 0
                output_string = ''
                while conversation_line is not None:
                    depth += 1
                    if depth % 2 == 1:
                        output_string += 'X: '
                    else:
                        output_string += 'A: '
                    output_string += conversation_line.body + '\n'
                    if conversation_line.child_id in conversation_line_dict:
                        conversation_line = conversation_line_dict[conversation_line.child_id]
                    else:
                        conversation_line = None
                        if depth % 2 == 0:
                            output_handler.write(output_string + '===\n')
                            counter_index += depth
                            if counter_index > prev_print_count + self.print_every:
                                end_time = datetime.now()
                                elapsed_time = (end_time - start_time)
                                prev_print_count = counter_index
                                print('\r# {:,} lines wrote in memory in {}.'.format(
                                    counter_index, str(elapsed_time).split('.')[0]), end='')
                                sys.stdout.flush()
        print()

    def generate_subreddit_report(self, subreddit_dict):
        """
        Creates subreddit file.

        Arguments:
            self: An instance of the class.
            subreddit_dict: Subreddit dictionary from json object.

        """
        out_report_file = os.path.join(self.output_path, self.report_file)
        print('# Updating subreddit report file at {}.'.format(
            datetime.now().strftime('%H:%M %p')))
        subreddit_list = sorted(subreddit_dict.items(), key=lambda x: -x[1])
        with open(out_report_file, 'w') as file:
            for item in subreddit_list:
                file.write('{}: {}\n'.format(*item))
        print('# {} subreddit file created.'.format(
            alice.file_size(self.report_file)))


class RedditConversationLine(object):
    """Class to read through reddit json file."""

    def __init__(self, json_object):
        """
        Creates an instance of class which reads through reddit json file.

        Arguments:
            self: An instance of the class.
            json_object: An instance of json object.

        """
        self.body = json_object['body']
        self.score = json_object['ups'] - json_object['downs']
        self.author = json_object['author']
        self.parent_id = json_object['parent_id']
        self.child_id = None


class OutputHandler(object):
    """Output loading class."""

    def __init__(self, path, output_file_size):
        """
        Creates an instance of the class.

        Arguments:
            self: An instance of the class.
            path: Folder where the output file will be created.
            output_file_size: Size of the output file created.

        """
        if path.endswith(alice.bz2_file):
            path = path[:-len(alice.bz2_file)]
        self.base_path = path
        self.output_file_size = output_file_size
        self.file_reference = None

    def write(self, data):
        """
        Writes data.

        Arguments:
            self: An instance of the class.
            data: Data read through json object.

        """
        if self.file_reference is None:
            self._get_current_path()
        self.file_reference.write(data.encode('ascii', 'ignore'))
        self.current_file_size += len(data)
        if self.current_file_size >= self.output_file_size:
            self.file_reference.close()
            self.file_reference = None

    def _get_current_path(self):
        """
        Checks if the path for loading ".bz2" file exists or not.

        Arguments:
            self: An instance of the class.

        """
        counter_index = 1
        while True:
            path = '{}_{}{}'.format(
                self.base_path, counter_index, alice.bz2_file)
            if not os.path.exists(path):
                break
            counter_index += 1
        self.current_path = path
        self.current_file_size = 0
        self.file_reference = BZ2File(self.current_path, 'w')


if __name__ == '__main__':
    dirs_to_create = [alice.model_dir, alice.parsed_dir]
    for dir in dirs_to_create:
        alice.create_dir(dir)

    Parser().parse()

    line_count = 0

    for input_file in os.listdir(alice.parsed_dir):
        if input_file.endswith(alice.bz2_file):
            loading_start_time = datetime.now()
            current_input_file = os.path.join(
                alice.parsed_dir, input_file)
            print('\n# Loading compressed "{}" file in memory at {}.'.format(
                input_file, loading_start_time.strftime('%I:%M %p')), end='')
            sys.stdout.flush()
            with BZ2File(current_input_file, 'r') as raw_data:
                for line in raw_data:
                    lnstrp = line.strip()
                    if not lnstrp:
                        continue
                    if lnstrp.startswith(b'X:'):
                        line_count += 1

    end_time = datetime.now()
    elapsed_time = (end_time - start_time)
    print('\n# Total {:,} conversations logged in {}.'.format(
        line_count, str(elapsed_time).split('.')[0]))

    end_time = datetime.now()
    elapsed_time = (end_time - start_time)
    total_data_memory = 0
    for input_file in os.listdir(alice.parsed_dir):
        if input_file.endswith(alice.bz2_file):
            current_input_file = os.path.join(alice.parsed_dir, input_file)
            total_data_memory = total_data_memory + \
                float(alice.file_size(current_input_file)[:-3])
    print('# Compressed "cassiopeia" files created. Memory used {} MB on disk.'.format(
        total_data_memory))

    for input_file in os.listdir(alice.parsed_dir):
        loading_start_time = datetime.now()
        current_input_file = os.path.join(
            alice.parsed_dir, input_file)
        print('\n# Loading compressed "{}" file in memory at {}.'.format(
            input_file, loading_start_time.strftime('%I:%M %p')), end='')
        sys.stdout.flush()
        if input_file.endswith(alice.bz2_file):
            current_input_file = os.path.join(alice.parsed_dir, input_file)
            zipfile = BZ2File(current_input_file)
            data = zipfile.read()
            open(alice.cassiopeia_file, 'a+b').write(data)

    end_time = datetime.now()
    elapsed_time = (end_time - start_time)
    print('\r# Uncompressing file in same directory. Total time took {}.\n'.format(
        str(elapsed_time).split('.')[0]), end='')
    sys.stdout.flush()
    print('# Uncompressed data is of {}'.format(
        alice.file_size(alice.cassiopeia_file)))
    print('# Run .\\cleaner.py file to continue.')
