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
TOKENIZED
========

Tokenized is used for creating tokenized data from the dataset.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from collections import namedtuple
import os
import codecs

from tensorflow.python.ops import lookup_ops
import tensorflow as tf

from hparams import HParams
import alice_config as alice


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class TokenizedData:
    """Creates tokenized data."""

    def __init__(
            self,
            core_dir,
            hparams=None,
            training=True,
            buffer_size=8192):
        """
        Creating instance of the class.

        Arguments:
            self: An instance of the class.
            core_dir: Folder for storing data for training.
            hparams: Object containing hyper parameters.
            training: Whether to use this object for training.
            buffer_size: Buffer size used for mapping process during data
                         processing.
        """
        if hparams is None:
            self.hparams = HParams(core_dir).hparams
        else:
            self.hparams = hparams

        self.src_max_len = alice.hparams_len
        self.tgt_max_len = alice.hparams_len

        self.training = training
        self.text_set = None
        self.id_set = None

        vocab_file = alice.vocab_file
        self.vocab_size, _ = check_vocab(vocab_file)
        self.vocab_table = lookup_ops.index_table_from_file(
            vocab_file, default_value=self.hparams.unk_id)

        if training:
            self.case_table = prepare_case_table()
            self.reverse_vocab_table = None
            self._load_core(core_dir)
            self._convert_to_tokens(buffer_size)
        else:
            self.case_table = None
            self.reverse_vocab_table = \
                lookup_ops.index_to_string_table_from_file(vocab_file,
                                                           default_value=self.hparams.unk_token)

    def get_training_batch(self, num_threads=4):
        assert self.training

        buffer_size = self.hparams.batch_size * 400
        train_set = self.id_set.shuffle(buffer_size=buffer_size)

        # Create a target input prefixed with BOS and a target output
        # suffixed with EOS. After this mapping, each element in the train_set
        # contains 3 columns/items.
        train_set = train_set.map(lambda src, tgt:
                                  (src, tf.concat(([self.hparams.bos_id],
                                                   tgt), 0),
                                   tf.concat((tgt, [self.hparams.eos_id]), 0)),
                                  num_parallel_calls=num_threads).prefetch(
            buffer_size)

        # Add in sequence lengths.
        train_set = train_set.map(lambda src, tgt_in, tgt_out:
                                  (src, tgt_in, tgt_out, tf.size(
                                      src), tf.size(tgt_in)),
                                  num_parallel_calls=num_threads).prefetch(
            buffer_size)

        def batching_func(xa):
            return xa.padded_batch(
                self.hparams.batch_size,
                # The first three entries are the source and target line rows,
                # these have unknown-length vectors. The last two entries are
                # the source and target row sizes, which are scalars.
                padded_shapes=(tf.TensorShape([None]),  # src
                               tf.TensorShape([None]),  # tgt_input
                               tf.TensorShape([None]),  # tgt_output
                               tf.TensorShape([]),      # src_len
                               tf.TensorShape([])),     # tgt_len
                # Pad the source and target sequences with eos tokens.
                # Though we don't generally need to do this since later on we
                # will be masking out calculations past the true sequence.
                padding_values=(self.hparams.eos_id,  # src
                                self.hparams.eos_id,  # tgt_input
                                self.hparams.eos_id,  # tgt_output
                                0,       # src_len -- unused
                                0))      # tgt_len -- unused

        if self.hparams.num_buckets > 1:
            bucket_width = (
                self.src_max_len + self.hparams.num_buckets - 1) // self.hparams.num_buckets

            # Parameters match the columns in each element of the dataset.
            def key_func(unused_1, unused_2, unused_3, src_len, tgt_len):
                # Calculate bucket_width by maximum source sequence length.
                # Pairs with length [0, bucket_width) go to bucket 0, length
                # [bucket_width, 2 * bucket_width) go to bucket 1, etc.
                # Pairs with length over ((num_bucket-1) * bucket_width) words
                # all go into the last bucket. Bucket sentence pairs by the
                # length of their source sentence and target sentence.
                bucket_id = tf.maximum(
                    src_len // bucket_width, tgt_len // bucket_width)
                return tf.to_int64(tf.minimum(self.hparams.num_buckets, bucket_id))

            # No key to filter the dataset. Therefore the key is unused.
            def reduce_func(unused_key, windowed_data):
                return batching_func(windowed_data)

            batched_dataset = train_set.apply(
                tf.contrib.data.group_by_window(key_func=key_func,
                                                reduce_func=reduce_func,
                                                window_size=self.hparams.batch_size))
        else:
            batched_dataset = batching_func(train_set)

        batched_iter = batched_dataset.make_initializable_iterator()
        (src_ids, tgt_input_ids, tgt_output_ids,
         src_seq_len, tgt_seq_len) = (batched_iter.get_next())

        return BatchedInput(initializer=batched_iter.initializer,
                            source=src_ids,
                            target_input=tgt_input_ids,
                            target_output=tgt_output_ids,
                            source_sequence_length=src_seq_len,
                            target_sequence_length=tgt_seq_len)

    def get_inference_batch(self, src_dataset):
        text_dataset = src_dataset.map(
            lambda src: tf.string_split([src]).values)

        if self.hparams.src_max_len_infer:
            text_dataset = text_dataset.map(
                lambda src: src[:self.hparams.src_max_len_infer])

        # Convert the word strings to ids
        id_dataset = text_dataset.map(lambda src: tf.cast(
            self.vocab_table.lookup(src), tf.int32))
        if self.hparams.source_reverse:
            id_dataset = id_dataset.map(lambda src: tf.reverse(src, axis=[0]))

        # Add in the word counts.
        id_dataset = id_dataset.map(lambda src: (src, tf.size(src)))

        def batching_func(xa):
            return xa.padded_batch(
                self.hparams.batch_size_infer,
                # The entry is the source line rows; this has unknown-length
                # vectors. The last entry is the source row size; this is a
                # scalar.
                padded_shapes=(tf.TensorShape([None]),  # src
                               tf.TensorShape([])),     # src_len
                # Pad the source sequences with eos tokens. Though notice we
                # don't generally need to do this since later on we will be
                # masking out calculations past the true sequence.
                padding_values=(self.hparams.eos_id,  # src
                                0))                   # src_len -- unused

        id_dataset = batching_func(id_dataset)

        infer_iter = id_dataset.make_initializable_iterator()
        (src_ids, src_seq_len) = infer_iter.get_next()

        return BatchedInput(initializer=infer_iter.initializer,
                            source=src_ids,
                            target_input=None,
                            target_output=None,
                            source_sequence_length=src_seq_len,
                            target_sequence_length=None)

    def _load_core(self, core_dir):
        for file_core in range(2, 0, -1):
            file_list = []
            learn_1 = 'assistance'
            learn_2 = 'character'
            if file_core == 1:
                file_dir = os.path.join(core_dir, learn_1)
            else:
                file_dir = os.path.join(core_dir, learn_2)

            for data_file in sorted(os.listdir(file_dir)):
                full_path_name = os.path.join(file_dir, data_file)
                if os.path.isfile(full_path_name) and data_file.lower().endswith('.xames3'):
                    file_list.append(full_path_name)

            assert len(file_list) > 0
            dataset = tf.data.TextLineDataset(file_list)

            src_dataset = dataset.filter(lambda line:
                                         tf.logical_and(tf.size(line) > 0,
                                                        tf.equal(tf.substr(line, 0, 2), tf.constant('X:'))))
            src_dataset = src_dataset.map(lambda line:
                                          tf.substr(line, 2, alice.max_len)).prefetch(4096)
            tgt_dataset = dataset.filter(lambda line:
                                         tf.logical_and(tf.size(line) > 0,
                                                        tf.equal(tf.substr(line, 0, 2), tf.constant('A:'))))
            tgt_dataset = tgt_dataset.map(lambda line:
                                          tf.substr(line, 2, alice.max_len)).prefetch(4096)

            src_tgt_dataset = tf.data.Dataset.zip((src_dataset, tgt_dataset))
            if file_core == 1:
                src_tgt_dataset = src_tgt_dataset.repeat(
                    self.hparams.learn_1_repeat_times)
            elif file_core == 2:
                src_tgt_dataset = src_tgt_dataset.repeat(
                    self.hparams.learn_2_repeat_times)

            if self.text_set is None:
                self.text_set = src_tgt_dataset
            else:
                self.text_set = self.text_set.concatenate(src_tgt_dataset)

    def _convert_to_tokens(self, buffer_size):
        # The following 3 steps act as a python String lower() function
        # Split to characters
        self.text_set = self.text_set.map(lambda src, tgt:
                                          (tf.string_split([src], delimiter='').values,
                                           tf.string_split([tgt], delimiter='').values)
                                          ).prefetch(buffer_size)

        # Convert all upper case characters to lower case characters
        self.text_set = self.text_set.map(lambda src, tgt:
                                          (self.case_table.lookup(src),
                                           self.case_table.lookup(tgt))
                                          ).prefetch(buffer_size)

        # Join characters back to strings
        self.text_set = self.text_set.map(lambda src, tgt:
                                          (tf.reduce_join([src]),
                                           tf.reduce_join([tgt]))
                                          ).prefetch(buffer_size)

        # Split to word tokens
        self.text_set = self.text_set.map(lambda src, tgt:
                                          (tf.string_split([src]).values, tf.string_split(
                                              [tgt]).values)
                                          ).prefetch(buffer_size)

        # Remove sentences longer than the model allows
        self.text_set = self.text_set.map(lambda src, tgt:
                                          (src[:self.src_max_len],
                                           tgt[:self.tgt_max_len])
                                          ).prefetch(buffer_size)

        # Reverse the source sentence if applicable
        if self.hparams.source_reverse:
            self.text_set = self.text_set.map(lambda src, tgt:
                                              (tf.reverse(src, axis=[0]), tgt)
                                              ).prefetch(buffer_size)

        # Convert the word strings to ids.
        # Word strings that are not in the vocab get the lookup table's
        # default_value integer.
        self.id_set = self.text_set.map(lambda src, tgt:
                                        (tf.cast(self.vocab_table.lookup(src), tf.int32),
                                         tf.cast(self.vocab_table.lookup(tgt), tf.int32))
                                        ).prefetch(buffer_size)


def check_vocab(vocab_file):
    """
    Check if vocab file exists.

    Arguments:
        vocab_file: Path to the vocab file.
    """
    if tf.gfile.Exists(vocab_file):
        vocab_list = []
        with codecs.getreader('utf-8')(tf.gfile.GFile(vocab_file, 'rb')) as file:
            for word in file:
                vocab_list.append(word.strip())
    else:
        raise ValueError(
            '# The vocab_file does not exist. Please run "vocab_generator.py" script to create it.')

    return len(vocab_list), vocab_list


def prepare_case_table():
    keys = tf.constant([chr(i) for i in range(32, 127)])

    l1 = [chr(i) for i in range(32, 65)]
    l2 = [chr(i) for i in range(97, 123)]
    l3 = [chr(i) for i in range(91, 127)]
    values = tf.constant(l1 + l2 + l3)

    return tf.contrib.lookup.HashTable(
        tf.contrib.lookup.KeyValueTensorInitializer(keys, values), ' ')


class BatchedInput(namedtuple('BatchedInput',
                              ['initializer',
                               'source',
                               'target_input',
                               'target_output',
                               'source_sequence_length',
                               'target_sequence_length'])):
    pass
