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
ALICE
========

Alice is the inference script which invokes the precognition via console.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import re
import sys
import random

import pyttsx3

import tensorflow as tf


utils_dir = os.path.join(os.path.dirname(os.getcwd()), 'utils\\')
os.chdir(utils_dir)
sys.path.insert(0, os.getcwd())

from precognition import AlicePrecognition
import alice_config as alice

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def cognition():
    """Opens console for taking text based input from user."""

    engine = pyttsx3.init()

    engine.setProperty('rate', 160)
    engine.setProperty('volume', 1.0)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)

    with tf.Session() as sess:
        precognition = AlicePrecognition(
            session=sess,
            core_dir=alice.core_dir,
            layers_dir=alice.layers_dir,
            model_dir=alice.model_dir,
            model_name=alice.codename)

        # Current Command UI supports only one chat session
        session_id = precognition.session_data.add_session()
        initial_greeting = random.choice(
            ['Oh hello!', 'Hi!', 'Hello!', 'Hey there!', 'Hey!'])

        alice_greeting = '{}'.format(initial_greeting)
        engine.say('{}'.format(initial_greeting))
        print('AL: ' + alice_greeting)
        engine.runAndWait()
        engine.stop()

        # Ask questions
        sys.stdout.write('XA: ')
        sys.stdout.flush()
        question = sys.stdin.readline()
        while question:
            exit_condition = (question.strip() == 'bye' or question.strip(
            ) == 'exit' or question.strip() == 'close' or question.strip() == 'goodbye')
            if exit_condition:
                engine.say('Goodbye.')
                print('AL: Goodbye.')
                engine.runAndWait()
                engine.stop()
                break

            alice_response = '{}'.format(re.sub(r'_nl_|_np_', '\n', precognition.precognition(
                session_id, question)).strip())
            engine.say(alice_response)
            print('AL: ' + alice_response)
            engine.runAndWait()
            engine.stop()
            print('XA: ', end='')
            sys.stdout.flush()
            question = sys.stdin.readline()


if __name__ == '__main__':
    cognition()
