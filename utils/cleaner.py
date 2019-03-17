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
CLEANER
========

Cleaner makes a temporary file called "cassiopeia_temp.xames3" which has
less unappropriate punctuations and curse words. Additionally, this file is
stripped off the conversation delimiters (X: and A:).
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from datetime import datetime
import os
import re
import sys

import nltk

import alice_config as alice

start_time = datetime.now()


class Cleaner():
    """Cleans unwanted punctuations in data."""

    def __init__(self, core_dir):
        """
        Creates a new cleaning instance for each file.

        Arguments:
            self: An instance of the class.
            core_dir: Directory for training files.

        """
        self.conversations = []

        # Looping through all files that end with ".xames3" in directory
        for data_file in sorted(os.listdir(core_dir)):
            full_path_name = os.path.join(core_dir, data_file)
            if os.path.isfile(full_path_name) and data_file.lower().endswith(alice.xames3_file):
                loading_start_time = datetime.now()
                print('\r# Loading "{}" file in memory at {}.'.format(
                    data_file, loading_start_time.strftime('%H:%M %p')))
                with open(full_path_name, 'r', encoding='iso-8859-1') as file:
                    samples = []
                    for line in file:
                        lnstrp = line.strip()
                        if not lnstrp:
                            continue
                        if lnstrp == '===':
                            if len(samples):
                                self.conversations.append(samples)
                            samples = []
                        else:
                            lnstrp = lnstrp[2:].strip()
                            samples.append({'text': lnstrp})

                    if len(samples):
                        self.conversations.append(samples)

    def write_cleaned_conversations(self, cleaned_file):
        """
        Writes "cleaned" conversations.

        Arguments:
            self: An instance of the method.
            cleaned_file: Cleaned file.

        """
        pattern_curse = re.compile(
            r'\b(ass|asshole|bastard|bitch|child-fucker|damn|fuck|fucking|motherfucker|motherfucking|'
            r'nigger|shit|shitass)\b',
            re.IGNORECASE)
        special_chars = [34, 35, 36, 37, 38, 40, 41, 42, 43, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57,
                         60, 61, 62, 64, 91, 92, 93, 94, 95, 96]

        with open(cleaned_file, 'a') as output_file:
            counter_index = 0
            for conversation in self.conversations:
                written = False

                # Iterate over all the samples of the conversation to get pairs
                for conv_id in range(0, len(conversation) - 1, 2):
                    input_line = conversation[conv_id]['text'].strip()
                    target_line = conversation[conv_id + 1]['text'].strip()

                    if all(ord(char) < 123 and ord(char) not in special_chars for char in input_line) and \
                            all(ord(char) < 123 and ord(char) not in special_chars for char in target_line):
                        input_line = self.get_formatted_line(input_line)
                        target_line = self.get_formatted_line(target_line)

                        # Discard conversations where answer has curse words
                        if re.search(pattern_curse, target_line):
                            continue

                        # Discard sentences starting with a dot
                        if input_line.startswith('.') or target_line.startswith('.'):
                            continue

                        # Discard sentences starting with a dash
                        if input_line.startswith('-') or target_line.startswith('-'):
                            continue

                        # This is to speed up the parsing below
                        if len(input_line) > 180 or len(target_line) > 180:
                            continue

                        in_tokens = nltk.word_tokenize(input_line)
                        tg_tokens = nltk.word_tokenize(target_line)
                        if 8 <= len(in_tokens) <= 32 and 8 <= len(tg_tokens) <= 32:
                            output_file.write('{}\n'.format(input_line))
                            output_file.write('{}\n'.format(target_line))
                            written = True

                if written:
                    output_file.write('===\n')
                    counter_index += 1
                    end_time = datetime.now()
                    elapsed_time = (end_time - start_time)
                    print('\r# {:,} conversations wrote temporarily in {}.'.format(
                        counter_index, str(elapsed_time).split('.')[0]), end='')
                    sys.stdout.flush()

    @staticmethod
    def get_formatted_line(line):
        pattern_dot = re.compile(r'\.\s+\.')
        pattern_dash = re.compile(r'-\s+-')
        pattern_html = re.compile(r'<.*?>')

        # Use formal ellipsis and dashes
        while re.search(pattern_dot, line):
            line = re.sub(pattern_dot, '..', line)

        while re.search(pattern_dash, line):
            line = re.sub(pattern_dash, '--', line)

        line = re.sub('\.{3,}', '... ', line)
        line = re.sub('-{2,}', ' -- ', line)

        # Use formal apostrophe
        line = line.replace(' \' ', '\'')

        # Remove extra spaces
        line = re.sub('\s+', ' ', line).strip()
        line = line.replace(' .', '.').replace(' ?', '?').replace(' !', '!')

        # Remove HTML tags
        line = re.sub(pattern_html, '', line)

        # Remove extra punctuations and m's
        line = re.sub('\?{2,}', '?', line)
        line = re.sub('!{2,}', '!', line)
        line = re.sub('m{3,}', 'mm', line)

        return line


if __name__ == '__main__':
    if os.path.isfile(alice.cassiopeia_output_file):
        os.remove(alice.cassiopeia_output_file)
    else:
        print('\r# Error: "{}" file not found'.format(
            alice.cassiopeia_output_file))

    cleaned_file = Cleaner(alice.parsed_dir)
    end_time = datetime.now()
    elapsed_time = (end_time - start_time)
    print('\r# {:,} decent conversations to be considered.'.format(
        len(cleaned_file.conversations)))
    cleaned_file.write_cleaned_conversations(alice.cassiopeia_temp_file)
    print('\n# {} temporary file created.'.format(
        alice.file_size(alice.cassiopeia_temp_file)))
