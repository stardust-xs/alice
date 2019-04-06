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
TRAIN
======

Train trains the actual model, checkpoint and meta files and stores them in
models directory.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import math
import time

import tensorflow as tf

from creator import CognitionModelCreator
from tokenized import TokenizedData
import alice_config as alice

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class Trainer(object):
    """Class for initiating the training."""

    def __init__(self, core_dir):
        """
        Creates an instance for training the model.

        Arguments:
            self: An instance of the class.
            core_dir: Folder with training related data.
        """
        self.graph = tf.Graph()
        with self.graph.as_default():
            tokenized = TokenizedData(core_dir=core_dir)

            self.hparams = tokenized.hparams
            self.train_batch = tokenized.get_training_batch()
            self.model = CognitionModelCreator(training=True,
                                               tokenized=tokenized,
                                               batch_input=self.train_batch)

    def train_model(self, model_dir, target='', last_end_file=None, last_end_epoch=0, last_end_learning_rate=8e-4):
        """
        Train a seq2seq model.

        Arguments:
            self: An instance of the class.
            model_dir: Where to create model.
            target: Leave blank*.
            last_end_file: Checkpoint for last trained file.
            last_end_epoch: Checkpoint for last trained epoch number.
            last_end_learning_rate: Checkpoint for last learning rate.
        """
        summary_name = 'alice_training_logs'
        summary_writer = tf.summary.FileWriter(os.path.join(
            alice.model_dir, summary_name), self.graph)

        log_device_placement = self.hparams.log_device_placement
        num_epochs = self.hparams.num_epochs

        config_proto = tf.ConfigProto(
            log_device_placement=log_device_placement,
            allow_soft_placement=True)
        config_proto.gpu_options.allow_growth = True

        with tf.Session(target=target,
                        config=config_proto,
                        graph=self.graph) as sess:
            sess.run(tf.global_variables_initializer())
            if last_end_file:
                print('# Restoring model weights from last time...')
                self.model.saver.restore(
                    sess, os.path.join(model_dir, last_end_file))

            sess.run(tf.tables_initializer())
            global_step = self.model.global_step.eval(session=sess)

            # Initialize all starting iterators
            sess.run(self.train_batch.initializer)

            # Initialize the statistic variables
            ckpt_loss, ckpt_precog_count = 0.0, 0.0
            train_ppl, last_recorded_ppl = 2000.0, 2.0
            train_epoch = last_end_epoch
            learning_rate = pre_learning_rate = last_end_learning_rate

            print('\n# Initiated training on {} at {}'.format(
                time.strftime('%d-%m-%Y'), time.strftime('%I:%M %p')))

            # Start time of the first epoch
            epoch_start_time = time.time()
            while train_epoch < num_epochs:
                # One complete execution of this While Loop will be 1 training # step. Multiple time/steps will trigger 'train_epoch' to be
                # increased.
                try:
                    step_result = self.model.train_step(
                        sess, learning_rate=learning_rate)
                    (_, step_loss, step_precog_count, step_summary,
                     global_step, step_word_count, batch_size) = step_result

                    # Write step summary
                    summary_writer.add_summary(step_summary, global_step)

                    # Update statistics
                    ckpt_loss += (step_loss * batch_size)
                    ckpt_precog_count += step_precog_count

                except tf.errors.OutOfRangeError:
                    # Completed going through the training dataset.
                    # Going onto the next epoch.
                    train_epoch += 1

                    mean_loss = ckpt_loss / ckpt_precog_count
                    train_ppl = math.exp(
                        float(mean_loss)) if mean_loss < 300 else math.inf

                    elapsed_epoch = time.time() - epoch_start_time
                    print('# Finished epoch {:2d} on step {:5d} at {}. In the executed epoch learning rate was {:.6f}, mean loss was {:.4f}, perplexity calculated was {:8.4f}, and {:.2f} seconds elapsed.'.format(
                        train_epoch, global_step, time.strftime('%d-%m-%Y %H:%M:%S'), learning_rate, mean_loss, train_ppl, round(elapsed_epoch, 2)))

                    # Start time of the next epoch
                    epoch_start_time = time.time()

                    summary = tf.Summary(value=[tf.Summary.Value(
                        tag='train_ppl', simple_value=train_ppl)])
                    summary_writer.add_summary(summary, global_step)

                    # Saving checkpoint
                    if train_ppl < last_recorded_ppl:
                        self.model.saver.save(sess, os.path.join(
                            model_dir, alice.codename),
                            global_step=global_step)
                        last_recorded_ppl = train_ppl

                    ckpt_loss, ckpt_precog_count = 0.0, 0.0

                    learning_rate = self._get_learning_rate(
                        train_ppl, pre_learning_rate, train_epoch)
                    pre_learning_rate = learning_rate

                    sess.run(self.model.batch_input.initializer)
                    continue

            # Done Training
            self.model.saver.save(sess, os.path.join(
                model_dir, alice.codename), global_step=global_step)
            summary_writer.close()

    @staticmethod
    def _get_learning_rate(ppl, pre_learning_rate, train_epoch):
        new_learning_rate = round(pre_learning_rate * 0.96, 6)
        if train_epoch >= 55:
            return 9.6e-5
        elif train_epoch >= 50:
            return 1e-4
        elif ppl <= 16.0:
            return max(min(new_learning_rate, 4e-4), 1e-4)
        elif ppl <= 32.0:
            return max(min(new_learning_rate, 6e-4), 4e-4)
        else:
            return max(min(new_learning_rate, 8e-4), 6e-4)


if __name__ == '__main__':
    precognition_training = Trainer(alice.core_dir)
    precognition_training.train_model(alice.model_dir)
