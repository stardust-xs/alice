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
PREPROCESSING
========

Preprocessing is done to add back the lost delimiters (X: and A:) during the
cleaning process. Also, Preprocessing checks and maintain the conversation
endings.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from datetime import datetime
import os
import sys

import nltk

import alice_config as alice

start_time = datetime.now()


def core_preprocess(parsed_dir):
    """
    Converts "cassiopeia_temp.xames3" to "cassiopeia_cleaned.xames3" and
    preprocesses the training data so that it is ready to be handled by TensorFlow TextLineDataSet

    Arguments:
        parsed_dir: Folder containing "cassiopeia_temp.xames3" file.

    """
    for data_file in sorted(os.listdir(parsed_dir)):
        full_path_name = os.path.join(parsed_dir, data_file)
        if os.path.isfile(full_path_name) and data_file.lower().endswith('.xames3'):
            new_name = data_file.lower().replace('_temp.xames3', '_cleaned.xames3')
            full_new_name = os.path.join(parsed_dir, new_name)

            conversations = []
            with open(full_path_name, 'r') as file:
                samples = []
                for line in file:
                    lnstrp = line.strip()
                    if not lnstrp or lnstrp.startswith('#=='):
                        continue
                    if lnstrp == '===':
                        if len(samples):
                            conversations.append(samples)
                        samples = []
                    else:
                        samples.append({'text': lnstrp})

                if len(samples):
                    conversations.append(samples)

            with open(full_new_name, 'a') as output_file:
                counter_index = 0
                depth = 0
                for conversation in conversations:
                    counter_index += 1
                    step = 2
                    for counter_index in range(0, len(conversation) - 1, step):
                        source_tokens = nltk.word_tokenize(
                            conversation[counter_index]['text'])
                        target_tokens = nltk.word_tokenize(
                            conversation[counter_index + 1]['text'])

                        source_line = 'X: ' + \
                            ' '.join(source_tokens[:]).strip()
                        target_line = 'A: ' + \
                            ' '.join(target_tokens[:]).strip()

                        output_file.write('{}\n'.format(source_line))
                        output_file.write('{}\n'.format(target_line))

                    output_file.write('===\n')
                    depth += 1
                    end_time = datetime.now()
                    elapsed_time = (end_time - start_time)
                    print('\r# {:,} conversations processed in {}.'.format(
                        depth, str(elapsed_time).split('.')[0]), end='')
                    sys.stdout.flush()


if __name__ == '__main__':
    if os.path.isfile(alice.cassiopeia_file):
        os.remove(alice.cassiopeia_file)
    else:
        print('\r# Error: {} file not found'.format(alice.cassiopeia_file))
    core_preprocess(alice.parsed_dir)
    print('\n# {} processed file created.'.format(
        alice.file_size(alice.cassiopeia_cleaned_file)))
    print('# Run .\\temp_vocab.py file to continue.')
