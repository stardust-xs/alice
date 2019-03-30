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
VOCAB
======

Vocab is used for creating a vocab file which will be used for prediction
during inference.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from datetime import datetime
import os
import sys

import alice_config as alice

start_time = datetime.now()


def generate_vocab_file(core_dir):
    """
    Creates "vocab.xames3" file for training and prediction.

    Arguments:
        core_dir: Core folder.
    """
    vocab_list = []

    # Special tokens, with IDs: 0, 1, 2.
    for t in ['_unk_', '_bos_', '_eos_']:
        vocab_list.append(t)

    # The word following this punctuation should be capitalized in the
    # prediction output.
    for t in ['.', '!', '?']:
        vocab_list.append(t)

    # The word following this punctuation should not precede with a space
    # in the prediction output.
    for t in ['(', '[', '{', '``', '$']:
        vocab_list.append(t)

    for file_core in range(2, 0, -1):
        learn_1 = 'assistance'
        learn_2 = 'character'
        if file_core == 1:
            file_dir = os.path.join(core_dir, learn_1)
        else:
            file_dir = os.path.join(core_dir, learn_2)

        for data_file in sorted(os.listdir(file_dir)):
            full_path_name = os.path.join(file_dir, data_file)
            if os.path.isfile(full_path_name) and data_file.lower().endswith('.xames3'):
                with open(full_path_name, 'r') as f:
                    for line in f:
                        lnstrp = line.strip()
                        if not lnstrp:
                            continue
                        if lnstrp.startswith('X:') or lnstrp.startswith('A:'):
                            tokens = lnstrp[2:].strip().split(' ')
                            for token in tokens:
                                if len(token) and token != ' ':
                                    t = token.lower()
                                    if t not in vocab_list:
                                        vocab_list.append(t)

    print('# {} vocabs created from the inbuilt data files.'.format(len(vocab_list)))

    temp_dict = {}
    cassiopeia_file = alice.cassiopeia_file
    if os.path.exists(cassiopeia_file):
        with open(cassiopeia_file, 'r') as raw_data:
            line_cnt = 0
            for line in raw_data:
                line_cnt += 1
                end_time = datetime.now()
                elapsed_time = (end_time - start_time)
                if line_cnt % 2000 == 0:
                    print('\r# {:,} lines read from the base file in {}.'.format(
                        line_cnt, str(elapsed_time).split('.')[0]), end='')
                    sys.stdout.flush()

                lnstrp = line.strip()
                if not lnstrp:
                    continue
                if lnstrp.startswith('X:') or lnstrp.startswith('A:'):
                    tokens = lnstrp[2:].strip().split(' ')
                    for token in tokens:
                        if len(token) and token != ' ':
                            t = token.lower()
                            if t not in vocab_list:
                                if lnstrp.startswith('A:'):
                                    vocab_list.append(t)
                                else:
                                    if t not in temp_dict:
                                        temp_dict[t] = 1
                                    else:
                                        temp_dict[t] += 1
                                        if temp_dict[t] >= 2:
                                            if t.startswith('.') or \
                                                t.startswith('-') or \
                                                t.startswith('!') or \
                                                t.startswith('@') or \
                                                t.startswith('$') or \
                                                t.startswith('%') or \
                                                t.startswith('"') or \
                                                t.startswith("'") or \
                                                t.startswith(':') or \
                                                t.startswith(';') or \
                                                t.startswith(',') or \
                                                t.endswith('..') or \
                                                t.endswith('-') or \
                                                t.endswith('@') or \
                                                    t.endswith('-'):
                                                continue

                                            vocab_list.append(t)

            print('\r')

    counter_index = 0
    with open(alice.vocab_file, 'a') as final_vocab_file:
        for v in vocab_list:
            final_vocab_file.write('{}\n'.format(v))
            counter_index += 1
            end_time = datetime.now()
            elapsed_time = (end_time - start_time)
            print('\r# {} vocabs generated. Total time took {}.'.format(
                counter_index, str(elapsed_time).split('.')[0]), end='')
            sys.stdout.flush()

    with open(alice.exception_file, 'a') as exception_file:
        for k, _ in temp_dict.items():
            if k not in vocab_list:
                exception_file.write('{}\n'.format(k))
    print('\n# Exception file created.')


if __name__ == '__main__':
    if os.path.isfile(alice.cassiopeia_cleaned_file):
        os.remove(alice.cassiopeia_cleaned_file)
    else:
        print('\r# Error: {} file not found'.format(
            alice.cassiopeia_cleaned_file))

    if os.path.isfile(alice.vocab_file):
        os.remove(alice.vocab_file)
    else:
        print('\r# Error: {} file not found'.format(alice.vocab_file))

    if os.path.isfile(alice.exception_file):
        os.remove(alice.exception_file)
    else:
        print('\r# Error: {} file not found'.format(alice.exception_file))
    generate_vocab_file(alice.core_dir)
    print('# Run .\\train.py file to continue.')
