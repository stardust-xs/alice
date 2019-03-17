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
ASSISTANT
==========

Assistant helps "model_creator.py" file by supporting some key functions.

Try not to modify this file.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import tensorflow as tf


def get_initializer(init_op, seed=None, init_weight=None):
    """
    Creates an initializer.

    Arguments:
        init_op: Mode of creation.
        seed: Should be set to None.
        init_weight: Should be set to None.

    """
    if init_op == 'uniform':
        assert init_weight
        return tf.random_uniform_initializer(
            -init_weight, init_weight, seed=seed)
    elif init_op == 'glorot_normal':
        return tf.contrib.keras.initializers.glorot_normal(seed=seed)
    elif init_op == 'glorot_uniform':
        return tf.contrib.keras.initializers.glorot_uniform(seed=seed)
    else:
        raise ValueError('Unknown init_op %s' % init_op)


def create_embbeding(vocab_size, embed_size, dtype=tf.float32, scope=None):
    """
    Creates an embedding matrix for both encoder and decoder.

    Arguments:
        vocab_size: Size of the vocab words in "vocab.xames3".
        embed_size: Projector embedding size.
        dtype: Datatype.
        scope: Scope of the model.

    """
    with tf.variable_scope(scope or 'embeddings', dtype=dtype):
        embedding = tf.get_variable(
            'embedding', [vocab_size, embed_size], dtype)
    return embedding


def _single_cell(num_units, keep_prob, device_str=None):
    """
    Creates an instance of a single RNN cell.

    Arguments:
        num_units: Number of units in matrix.
        keep_prob: Probability factor.
        device_str: Should be set to None.

    """
    single_cell = tf.contrib.rnn.GRUCell(num_units)
    if keep_prob < 1.0:
        single_cell = tf.contrib.rnn.DropoutWrapper(
            cell=single_cell, input_keep_prob=keep_prob)

    # Device Wrapper
    if device_str:
        single_cell = tf.contrib.rnn.DeviceWrapper(single_cell, device_str)
    return single_cell


def create_rnn_cell(num_units, num_layers, keep_prob):
    """
    Creates multi-layer RNN cell.

    Arguments:
        num_units: Number of units in matrix.
        num_layers: Number of layers in RNN.
        keep_prob: Probability factor.

    """
    cell_list = []
    for i in range(num_layers):
        single_cell = _single_cell(num_units=num_units, keep_prob=keep_prob)
        cell_list.append(single_cell)

    # If Single layer
    if len(cell_list) == 1:
        return cell_list[0]
    else:
        # Multi layered
        return tf.contrib.rnn.MultiRNNCell(cell_list)


def gradient_clip(gradients, max_gradient_norm):
    """
    Clipping gradients of the model.

    Arguments:
        gradient: Gradient value.
        max_gradient_norm: Maximum normalized gradient score.

    """
    clipped_gradients, gradient_norm = tf.clip_by_global_norm(
        gradients, max_gradient_norm)
    gradient_norm_summary = [tf.summary.scalar('grad_norm', gradient_norm)]
    gradient_norm_summary.append(
        tf.summary.scalar('clipped_gradient',
                          tf.global_norm(clipped_gradients)))
    return clipped_gradients, gradient_norm_summary
