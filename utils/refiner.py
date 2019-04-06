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
REFINER
========

Refiner assets back the conversation delimiters and removes any still
remaining underlying spaces.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from datetime import datetime
import sys

import alice_config as alice

start_time = datetime.now()


def refiner():
    """Removes unwanted spaces and adds delimiters."""

    exception_list = []

    # Add more words to exception file
    with open(alice.exception_file, 'r') as exception_file:
        for line in exception_file:
            lnstrp = line.strip()
            if not lnstrp:
                continue
            exception_list.append(lnstrp)

    conversations = []

    # Correct the conversation endings
    with open(alice.cassiopeia_cleaned_file, 'r') as input_file:
        samples = []
        for num, line in enumerate(input_file):
            end_time = datetime.now()
            elapsed_time = (end_time - start_time)
            print('\r# {:,} lines cached in {}.'.format(
                num, str(elapsed_time).split('.')[0]), end='')
            sys.stdout.flush()
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

    # Add back the delimiters
    print('\n# {:,} conversations logged.'.format(len(conversations)))
    with open(alice.cassiopeia_file, 'a') as output_file:
        count = 0
        for conversation in conversations:
            written = False
            for counter_index in range(0, len(conversation) - 1, 2):
                src_line = conversation[counter_index]['text'].strip()
                tgt_line = conversation[counter_index + 1]['text'].strip()
                assert src_line.startswith('X:') and tgt_line.startswith('A:')

                skip = False

                tokens = (src_line[2:] + ' ' + tgt_line[2:]).split(' ')
                for token in tokens:
                    if len(token) and token != ' ':
                        t = token.lower()
                        if t in exception_list:
                            skip = True
                            count += 1
                            if count % 1000 == 0:
                                end_time = datetime.now()
                                elapsed_time = (end_time - start_time)
                                print('\r# {:,} conversations skipped in {}.'.format(
                                    count, str(elapsed_time).split('.')[0]), end='')
                                sys.stdout.flush()
                            break

                if not skip:
                    output_file.write('{}\n'.format(src_line))
                    output_file.write('{}\n'.format(tgt_line))
                    written = True

            if written:
                output_file.write('===\n')


if __name__ == '__main__':
    refiner()
    print('\n# Cassiopeia file created of {}.'.format(
        alice.file_size(alice.cassiopeia_file)))
    print('# Run .\\vocab.py file to continue.')
