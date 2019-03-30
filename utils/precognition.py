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
PRECOGNITION
=============

Precognition is used for predicting the answers for the asked questions during
inference.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import random
import string

import nltk

import tensorflow as tf

from session import SessionData
from creator import CognitionModelCreator
from precognition_data import invoke_precognition
from tokenized import TokenizedData
from layers import Layers
from recognizer import check_patterns_and_replace
import alice_config as alice

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class AlicePrecognition(object):
    """Object Class to use the base inference script which will answer the questions after understanding the underlying question pattern"""

    def __init__(self,
                 session,
                 core_dir,
                 layers_dir,
                 model_dir,
                 model_name):
        """
        Creates an instance of a class for predicting.

        Arguments:
            self: Creates an instance of the class.
            session: Initialize TensorFlow session.
            core_dir: Folder storing training and vocab data.
            layers_dir: Folder storing data files for the fun.
            model_dir: Folder containing the trained model files.
            model_name: Name of the trained model [Codename: cassiopeia].
        """

        self.session = session

        # Preparing source dataset and constructing hparams
        print('\n')
        print(f'{alice.print_alice}'.center(os.get_terminal_size().columns))
        tokenized = TokenizedData(
            core_dir=core_dir, training=False)

        self.layers = Layers()
        self.layers.load_layers(layers_dir)

        self.session_data = SessionData()

        self.hparams = tokenized.hparams
        self.src_placeholder = tf.placeholder(shape=[None], dtype=tf.string)
        src_dataset = tf.data.Dataset.from_tensor_slices(self.src_placeholder)
        self.inference_batch = tokenized.get_inference_batch(src_dataset)

        # Preparing inference model
        self.model = CognitionModelCreator(training=False,
                                           tokenized=tokenized,
                                           batch_input=self.inference_batch)

        # Overide trained model weights
        self.model.saver.restore(session, os.path.join(model_dir, model_name))
        self.session.run(tf.tables_initializer())

    def precognition(self, session_id, question):
        """
        Prediction using the dataset.

        Arguments:
            self: Instance of the class.
            session_id: Conversation Session ID.
            question: Question asked during inference.

        """
        conversation_session = self.session_data.get_session(session_id)
        conversation_session.before_precognition()

        if question.strip() == '':
            answer = random.choice(['Don\'t you want to ask anything?',
                                    'Don\'t you want to say something?',
                                    'Do you want to ask something?',
                                    'You were saying something...',
                                    'Umm... what?',
                                    'Hmm... what?',
                                    'I think you missed saying something.'])
            conversation_session.after_precognition(question, answer)
            return answer

        pattern_matched, new_question, queue_list = check_patterns_and_replace(
            question)

        for previous_question in range(2):
            tokens = nltk.word_tokenize(new_question.lower())
            tmp_sentence = [' '.join(tokens[:]).strip()]

            self.session.run(self.inference_batch.initializer,
                             feed_dict={self.src_placeholder: tmp_sentence})

            outputs, _ = self.model.infer(self.session)

            if self.hparams.beam_width > 0:
                outputs = outputs[0]

            eos_token = self.hparams.eos_token.encode('utf-8')
            outputs = outputs.tolist()[0]

            if eos_token in outputs:
                outputs = outputs[:outputs.index(eos_token)]

            if pattern_matched and previous_question == 0:
                output_sentence, if_xa_taught_value = self.get_final_output(
                    outputs, conversation_session, queue_list=queue_list)

                if if_xa_taught_value:
                    conversation_session.after_precognition(
                        question, output_sentence)
                    return output_sentence
                else:
                    new_question = question
            else:
                output_sentence, _ = self.get_final_output(
                    outputs, conversation_session)
                conversation_session.after_precognition(
                    question, output_sentence)
                return output_sentence

    def get_final_output(self,
                         sentence,
                         conversation_session,
                         queue_list=None):
        """
        Return value if found answer.

        Arguments:
            self: Creates an instance of the class.
            sentence: Result from precognition.
            conversation_session: Conversation Session.
            queue_list: List of input hotwords in queue.

        """
        sentence = b' '.join(sentence).decode('utf-8')
        if sentence == '':
            return random.choice(['I don\'t know what to say.',
                                  'What do you expect me to say now?',
                                  'I\'m sorry. I don\'t know what to say',
                                  'Uh...']), False

        if_xa_taught_value = False
        last_word = None
        word_list = []
        for word in sentence.split(' '):
            word = word.strip()
            if not word:
                continue

            if word.startswith('_xa_taught_value_'):
                if_xa_taught_value = True
                word = invoke_precognition(
                    word[17:], layers=self.layers,
                    conversation_session=conversation_session,
                    queue_list=queue_list)
                if word is None or word == '':
                    continue
            else:
                if word in self.layers.dict:
                    word = self.layers.dict[word]

                if (last_word is None or last_word in ['.', '!', '?']) and not word[0].isupper():
                    word = word.capitalize()

            if not word.startswith('\'') and \
                word != 'n\'t' and \
                (word[0] not in string.punctuation or word in [
                 '(', '[', '{', '``', '$']) and \
                    last_word not in ['(', '[', '{', '``', '$']:
                word = ' ' + word

            word_list.append(word)
            last_word = word

        return ''.join(word_list).strip(), if_xa_taught_value
