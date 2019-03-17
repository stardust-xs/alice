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
SESSION
========

Session provides session during the Inference.
While in production environment, the SessionData needs to be maintained so
that the ConversationSession objects can expire and then be cleaned from the
memory.
"""


class SessionData:
    """Class which creates session during inference."""

    def __init__(self):
        """
        Creates an instance for creating session.

        Arguments:
            self: An instance of the class.
        """
        self.session_dict = {}

    def add_session(self):
        """
        Adds a session.

        Arguments:
            self: An instance of the class.
        """
        items = self.session_dict.items()
        if items:
            prev_id = max(k for k, v in items)
        else:
            prev_id = 0
        new_id = prev_id + 1

        self.session_dict[new_id] = ConversationSession(new_id)
        return new_id

    def get_session(self, session_id):
        return self.session_dict[session_id]


class ConversationSession:
    """Creates a conversation session."""

    def __init__(self, session_id):
        """
        Creates an instance for creating conversation session.

        Arguments:
            self: An instance of the class.
            session_id: Integer ID of the conversation session
        """
        self.session_id = session_id
        self.how_are_you_asked = False
        self.username = None
        self.call_me = None
        self.previous_question = None
        self.previous_answer = None
        self.update_pair = True
        self.previous_topic = None
        self.continue_topic = False

        # Will be storing the information of the pending action:
        # The action function name, the queuemeter for answer yes,
        # and the queuemeter for answer no.
        self.pending_action = {'Precog': None, 'Yes': None, 'No': None}

    def before_precognition(self):
        self.update_pair = True
        self.continue_topic = False

    def after_precognition(self, new_question, new_answer):
        self._update_previous_pair(new_question, new_answer)
        self._clear_previous_topic()

    def _update_previous_pair(self, new_question, new_answer):
        """Previous pair is updated after each prediction except in a few cases"""
        if self.update_pair:
            self.previous_question = new_question
            self.previous_answer = new_answer

    def _clear_previous_topic(self):
        """Previous topic is cleared after each prediction except in few cases"""
        if not self.continue_topic:
            self.previous_topic = None

    def update_pending_action(self, precog_name, yes_queue, no_queue):
        self.pending_action['Precog'] = precog_name
        self.pending_action['Yes'] = yes_queue
        self.pending_action['No'] = no_queue

    def clear_pending_action(self):
        """Pending action is, and only is, cleared at the end of function:
        execute_pending_action_and_reply"""
        self.pending_action['Precog'] = None
        self.pending_action['Yes'] = None
        self.pending_action['No'] = None
