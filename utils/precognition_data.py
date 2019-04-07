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
PRECOGNITION DATA
==================

Precognition Data makes Alice perform some activities.

## The current supported activities are:
    * Stating date and time.
    * Stating what's the day today, yesterday and tomorrow's.
    * Basic arithmetic like Addition, Subtraction, Multiplication and Division.
    * Can tell a story OR a joke.
    * Have general conversations like asking your name and saving in session.
    * Can google something.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import time
import random
import datetime as dt
import calendar as cal
import webbrowser as wb

import alice_config as alice


class PrecognitionData:
    """Precogniton Class for predicting and asserting insights."""

    def __init__(self, layers, conversation_session):
        """
        Creates an instance of a class for predicting.

        Arguments:
            self: An instance of the class.
            layers: Data in Layers directory needed for prediction.
            conversation_session: Conversating session with Alice.
        """

        self.layers = layers
        self.conversation_session = conversation_session

    # Date and time rules
    @staticmethod
    def current_date_time():
        return time.strftime('%Y-%m-%d %H:%M')

    @staticmethod
    def current_time():
        return time.strftime('%I:%M %p')

    @staticmethod
    def whats_today():
        return '{:%B %d, %Y}'.format(dt.date.today())

    @staticmethod
    def whats_today_date():
        return '{:%d %B, %Y}'.format(dt.date.today())

    @staticmethod
    def whats_today_day():
        return '{:%A}'.format(dt.date.today())

    @staticmethod
    def whats_today_month():
        return '{:%B}'.format(dt.date.today())

    @staticmethod
    def whats_today_year():
        return '{:%Y}'.format(dt.date.today())

    @staticmethod
    def weekday_status(day_delta):
        now = dt.datetime.now()
        if day_delta == 'd_2':
            day_time = now - dt.timedelta(days=2)
        elif day_delta == 'd_1':
            day_time = now - dt.timedelta(days=1)
        elif day_delta == 'd1':
            day_time = now + dt.timedelta(days=1)
        elif day_delta == 'd2':
            day_time = now + dt.timedelta(days=2)
        else:
            day_time = now
        weekday = cal.day_name[day_time.weekday()]
        return '{}, {:%B %d, %Y}'.format(weekday, day_time)

    # Basic Arithmetics
    @staticmethod
    def basic_addition(num1, num2):
        res = num1 + num2
        desc = random.choice(PrecognitionData.simple_list)
        return '{}{:,}'.format(desc, res)

    @staticmethod
    def basic_subtraction(num1, num2):
        res = num1 - num2
        desc = random.choice(PrecognitionData.simple_list)
        return '{}{:,}'.format(desc, res)

    @staticmethod
    def basic_multiplication(num1, num2):
        res = num1 * num2
        if num1 > 100 and num2 > 100 and num1 % 2 == 1 and num2 % 2 == 1:
            desc = random.choice(PrecognitionData.difficult_list)
        else:
            desc = random.choice(PrecognitionData.simple_list)
        return '{}{:,}'.format(desc, res)

    @staticmethod
    def basic_division(num1, num2):
        if num2 == 0:
            desc = random.choice(PrecognitionData.divide_by_zero_list)
            return '{}'.format(desc)
        else:
            res = num1 / num2
            if isinstance(res, int):
                if 50 < num1 != num2 > 50:
                    desc = random.choice(PrecognitionData.difficult_list)
                else:
                    desc = random.choice(PrecognitionData.difficult_list)
                return '{}{:,}'.format(desc, res)
            else:
                if num1 > 20 and num2 > 20:
                    desc = random.choice(PrecognitionData.difficult_list)
                else:
                    desc = random.choice(PrecognitionData.simple_list)
                return '{}{:.2f}'.format(desc, res)

    # Stories, jokes and previous topic
    def tell_a_story(self):
        self.conversation_session.previous_topic = 'STORY'
        self.conversation_session.continue_topic = True

        stories = self.layers.stories
        _, content = random.choice(list(stories.items()))
        return content

    def tell_story_name(self, story_name):
        self.conversation_session.previous_topic = 'STORY'
        self.conversation_session.continue_topic = True

        stories = self.layers.stories
        content = stories[story_name]
        return content

    def tell_a_joke(self):
        self.conversation_session.previous_topic = 'JOKE'
        self.conversation_session.continue_topic = True

        jokes = self.layers.jokes
        content = random.choice(jokes)
        return content

    def continue_previous_topic(self):
        if self.conversation_session.previous_topic == 'STORY':
            self.conversation_session.continue_topic = True
            return self.tell_a_story()
        elif self.conversation_session.previous_topic == 'JOKE':
            self.conversation_session.continue_topic = True
            return self.tell_a_joke()
        else:
            return 'Sorry, what topic would you prefer?'

    # General communication
    def ask_how_are_you_if_not_yet(self):
        how_are_you_asked = self.conversation_session.how_are_you_asked
        if how_are_you_asked:
            return ''
        else:
            self.conversation_session.how_are_you_asked = True
            return random.choice(PrecognitionData.ask_how_are_you_list)

    def ask_name_if_not_yet(self):
        username = self.conversation_session.username
        call_me = self.conversation_session.call_me
        if username or call_me:
            return random.choice([f'Sure, My name is {alice.shortname} - {alice.fullname}.', f'I\'m {alice.shortname} - {alice.fullname}.', f'I\'m {alice.shortname}.'])
        else:
            return random.choice(PrecognitionData.ask_name_list)

    def ask_username_and_reply(self):
        username = self.conversation_session.username
        if username and username.strip() != '':
            return random.choice([f'{username}.', f'I think you said it\'s {username}.', f'I know you. You\'re {username}.'])
        else:
            return random.choice(['I\'m so sorry. I don\'t remember your name.', 'I\'m sorry, I think I forgot to save your name in my memory.', 'Uhh... I\'m so sorry, I don\'t remember you.', 'I\'ve got a terrible memory for names. Can you tell me yours again?', 'Forgive me. Your name completely slipped out of my mind.', 'I\'m so sorry. I remember meeting you, but I just can\'t remember your name.', 'I\'m really embarrassed. I\'ve forgotten your name.', 'I\'m terrible with names. Can you please tell me your name again?', 'I apologize. Your name just flew right out of my mind.', 'You have me at a disadvantage now, I\'m sorry. I forgot your name.', 'How awkward! Have we met? Please tell me your name again.'])

    def ask_call_me(self, punc_type):
        call_me = self.conversation_session.call_me
        username = self.conversation_session.username

        if call_me and call_me.strip() != '':
            if punc_type == 'comma0':
                return ', {}'.format(call_me)
            else:
                return call_me
        elif username and username.strip() != '':
            if punc_type == 'comma0':
                return ', {}'.format(username)
            else:
                return username
        else:
            return ''

    def read_previous_question(self):
        self.conversation_session.update_pair = False
        previous_question = self.conversation_session.previous_question
        if previous_question is None or previous_question.strip() == '':
            return random.choice(['You did not say anything.', 'Forgive me. But did you say anything?', 'I\'m sorry, I didn\'t quite catch that.', 'Could you say that again?'])
        else:
            return random.choice([f'You said, {previous_question}', f'Well... I think you said, {previous_question}', f'This, {previous_question}'])

    def answer_previous_question(self):
        self.conversation_session.update_pair = False
        previous_answer = self.conversation_session.previous_answer
        if previous_answer is None or previous_answer.strip() == '':
            return random.choice(['I did not say anything.', 'Nothing.', 'I did\'nt say anything.', 'Nothing from me...'])
        else:
            return random.choice([f'I answered, {previous_answer}', f'I said, {previous_answer}'])

    def update_username(self, new_username):
        return self.update_username_and_call_me(new_username=new_username)

    def update_call_me(self, new_call):
        return self.update_username_and_call_me(new_call=new_call)

    def update_username_and_call_me(self, new_username=None, new_call=None):
        username = self.conversation_session.username
        call_me = self.conversation_session.call_me

        if username and new_username and new_username.strip() != '':
            if new_username.lower() != username.lower():
                self.conversation_session.update_pending_action(
                    'update_username_confirmed', None, new_username)
                return random.choice(['I\'m confused. I have saved your name as {}. Did I get it wrong?'.format(
                    username),
                    'I\'m sorry I think I have saved your name as {}. Isn\'t is correct?'.format(username)])
            else:
                return random.choice(['Oh... I remember you, thanks for reassuring.', 'I know you.', 'I know your name.', 'Okay got it, thanks {}.'.format(username)])

        if call_me and new_call and new_call.strip() == '':
            if new_call.lower() != call_me.lower():
                self.conversation_session.update_pending_action(
                    'update_call_me_confirmed', new_call, None)
                return 'You wanted me to call you {} previously. Would you like me to call you {} now?'.format(call_me, new_call)
            else:
                return 'Got it! will call you {}.'.format(call_me)

        if new_call and new_call.strip() != '':
            if new_username and new_username.strip() != '':
                self.conversation_session.username = new_username

            self.conversation_session.call_me = new_call
            return random.choice(['Thanks, I shall address you as {} from now.'.format(new_call), 'Thanks, I shall call you as {} from now.'.format(new_call), 'Thanks, I will remember you as {}.'.format(new_call),
                                  'Thanks, {} for telling me your name.'.format(
                                      new_call),
                                  'From now, I\'ll call you {}.'.format(new_call)])
        elif new_username and new_username.strip() != '':
            self.conversation_session.username = new_username
            return random.choice(['Thanks, {} for telling me your name.'.format(new_username), 'Thanks, I shall call you as {} from now.'.format(new_username), 'Thanks, I shall address you as {} from now.'.format(new_username), 'Thanks, I will remember you as {}.'.format(new_username),
                                  'Thanks, I\'ll address you as {} from now.'.format(
                                      new_username),
                                  'From now, I\'ll call you {}.'.format(new_username)])
        return 'Sorry, I\'m confused. I could\'nt figure out what you meant.'

    def update_username_enforced(self, new_username):
        if new_username and new_username.strip() != '':
            self.conversation_session.username = new_username
            return random.choice(['Okay, thanks {}.'.format(new_username),
                                  'Thank you, {}.'.format(new_username),
                                  'Got it, {}.'.format(new_username)])
        else:
            self.conversation_session.username = None
            return 'Sorry, I\'m lost.'

    def update_call_me_enforced(self, new_call):
        if new_call and new_call.strip() != '':
            self.conversation_session.call_me = new_call
            return random.choice(['Okay got it, thanks {}.'.format(new_call),
                                  'Thanks, {}.'.format(new_call)])
        else:
            self.conversation_session.call_me = None
            return 'Sorry, I\'m totally lost.'

    def update_username_and_reply_alice(self, new_username):
        username = self.conversation_session.username

        if new_username and new_username.strip() == '':
            if username:
                if new_username.lower() != username.lower():
                    self.conversation_session.update_pending_action(
                        'update_username_confirmed', None, new_username)
                    return 'I\'m confused. I have saved your name as {} in my \
                    memory. Did I get it correctly or I missed \
                    something?'.format(username)
                else:
                    return 'Thanks {}. My name is {}.'.format(username, alice.shortname)
            else:
                self.conversation_session.username = new_username
                return 'Thanks {}. By the way I\'m {} - {}. Nice to meet you.'.format(new_username, alice.shortname, alice.fullname)
        else:
            return 'My name is {} - {}.'.format(alice.shortname, alice.fullname)

    def correct_username(self, new_username):
        if new_username and new_username.strip() != '':
            self.conversation_session.username = new_username
            return 'Thank you, {}.'.format(new_username)
        else:
            self.conversation_session.username = None
            self.conversation_session.call_me = None
            return 'I\'m totally lost.'

    def clear_username_and_call_me(self):
        self.conversation_session.username = None
        self.conversation_session.call_me = None

    def execute_pending_action_and_reply(self, answer):
        precog = self.conversation_session.pending_action['Precog']
        if precog == 'update_username_confirmed':
            if answer == 'yes':
                reply = 'Thanks for confirming this {}'.format(
                    self.conversation_session.username)
            else:
                new_username = self.conversation_session.pending_action['No']
                self.conversation_session.username = new_username
                reply = random.choice(['Thanks {} for correcting me.'.format(
                    new_username), 'Thanks {} for correcting on this one.'.format(new_username), 'Got it {}'.format(new_username)])
        elif precog == 'update_call_me_confirmed':
            if answer.lower() == 'yes':
                new_call = self.conversation_session.pending_action['Yes']
                self.conversation_session.call_me = new_call
                reply = random.choice(['Thanks {} for correcting me.'.format(
                    new_call), 'Thanks {} for correcting on this one.'.format(new_call), 'Got it {}'.format(new_call)])
            else:
                reply = 'Thank you. I will call you {}.'.format(
                    self.conversation_session.call_me)
        else:
            # Most standard reply suitable for most of the situations
            reply = random.choice(['Okay, thanks!', 'Ok, thank you.'])

        self.conversation_session.clear_pending_action()
        return reply

    # Functions with Alice
    def whats_your_age():
        current_age = alice.current_age
        return random.choice([f'I\'m {current_age} days old.', f'{current_age} days old.', f'Technically, I don\'t have a birth date as such but it\'s been about {current_age} days into my existence.'])

    def whats_your_gender():
        gender = alice.gender
        return random.choice([f'I\'m a program. I\'m without form. But my creator programmed me to be a {gender}.', f'I\'m a program. I\'m without form. But I do have feminine personality.', f'What can I say, {alice.creator_name} programmed me to be his female assistant.'])

    def whens_your_birthday():
        birthday = alice.created_date
        return random.choice[f'It\'s on {birthday}.', f'On {birthday}.']

    def whos_your_creator():
        creator_name = alice.creator_name
        return creator_name

    def whats_creator_gender():
        creator_gender = alice.creator_gender
        return f'He\'s a {creator_gender}.'

    def where_you_from_city():
        location_city = alice.location_details('city')
        return location_city

    def where_you_from_country():
        location_country_name = alice.location_details('country_name')
        return location_country_name

    @staticmethod
    def google_this(google):
        wb.open(f'https://google.com/search?q={google}')
        return random.choice(['Here you go.', 'Okay...'])

    simple_list = [
        ' ',
        'Here you go, ',
        'Easy, it\'s ',
        'That\'s easy, ',
        'That was easy, ',
        'Piece of cake, ',
        'I know, it\'s ',
        'It is '
    ]
    difficult_list = [
        'Umm... ',
        'Here you go, ',
        'That was a little difficult, ',
        'That was a toughie, ',
        'That was a tough one I had to use a calculator, ',
        'That was a little difficult to my current situations but I\'m programmed to assist you. Here\'s the result, ',
        'This took me sometime to figure out, here you go, ',
        'This was a toughie but I knew how to solve this, here you go, '
    ]
    ask_how_are_you_list = [
        'And you?',
        'You?',
        'How are you?',
        'How about you?',
        'How are you holding up these days?'
    ]
    ask_name_list = [
        'And you?',
        'May I have your name, please?',
        'May I ask your name.',
        'And, how should I call you?',
        'And, how should I address you?',
        'What do you want me to call you?',
        'What is your name?',
        'How may I address you?',
        'What is your name?, if you don\'t mind me asking.'
    ]
    divide_by_zero_list = [
        'You got be kidding. Nothing divides by 0',
        'Undefined.',
        'Very big number which is way out of my comprehension.',
        'Infinity?!*'
    ]


def invoke_precognition(
        precog_info,
        layers=None,
        conversation_session=None,
        queue_list=None):
    """
    Calls the precognition activities on demand.

    Arguments:
        precog_info: Question loaded during inference.
        layers = Data in Layers directory needed for prediction.
        conversation_session: Conversation Session.
        queue_list: List of input hotwords in queue.

    """

    precog_data = PrecognitionData(layers, conversation_session)

    precog_dict = {
        'current_date_time': PrecognitionData.current_date_time,
        'current_time': PrecognitionData.current_time,
        'whats_today': PrecognitionData.whats_today,
        'whats_today_date': PrecognitionData.whats_today_date,
        'whats_today_day': PrecognitionData.whats_today_day,
        'whats_today_month': PrecognitionData.whats_today_month,
        'whats_today_year': PrecognitionData.whats_today_year,
        'weekday_status': PrecognitionData.weekday_status,

        'basic_addition': PrecognitionData.basic_addition,
        'basic_subtraction': PrecognitionData.basic_subtraction,
        'basic_multiplication': PrecognitionData.basic_multiplication,
        'basic_division': PrecognitionData.basic_division,

        'whats_your_age': PrecognitionData.whats_your_age,
        'whats_your_gender': PrecognitionData.whats_your_gender,
        'whens_your_birthday': PrecognitionData.whens_your_birthday,
        'whos_your_creator': PrecognitionData.whos_your_creator,
        'whats_creator_gender': PrecognitionData.whats_creator_gender,
        'where_you_from_city': PrecognitionData.where_you_from_city,
        'where_you_from_country': PrecognitionData.where_you_from_country,

        'google_this': PrecognitionData.google_this,

        'ask_how_are_you_if_not_yet': precog_data.ask_how_are_you_if_not_yet,
        'ask_name_if_not_yet': precog_data.ask_name_if_not_yet,
        'ask_username_and_reply': precog_data.ask_username_and_reply,
        'ask_call_me': precog_data.ask_call_me,
        'read_previous_question': precog_data.read_previous_question,
        'answer_previous_question': precog_data.answer_previous_question,

        'update_username': precog_data.update_username,
        'update_call_me': precog_data.update_call_me,
        'update_username_and_call_me': precog_data.update_username_and_call_me,
        'update_username_enforced': precog_data.update_username_enforced,
        'update_call_me_enforced': precog_data.update_call_me_enforced,
        'update_username_and_reply_alice': precog_data.update_username_and_reply_alice,

        'correct_username': precog_data.correct_username,
        'clear_username_and_call_me': precog_data.clear_username_and_call_me,
        'execute_pending_action_and_reply': precog_data.execute_pending_action_and_reply

    }

    queue1_index = precog_info.find('_queue1_')
    queue2_index = precog_info.find('_queue2_')

    if queue1_index == -1:
        precog_name = precog_info
        if precog_name in precog_dict:
            return precog_dict[precog_name]()
    else:
        precog_name = precog_info[:queue1_index]
        if queue2_index == -1:
            precog_queue = precog_info[queue1_index + 8:]
            if precog_queue == '_name_' and queue_list is not None and len(queue_list) >= 1:
                return precog_dict[precog_name](queue_list[0])
            elif precog_queue == '_call_me_' and queue_list is not None and len(queue_list) >= 2:
                return precog_dict[precog_name](queue_list[1])
            elif precog_queue == '_google_' and queue_list is not None and len(queue_list) >= 1:
                return precog_dict[precog_name](queue_list[0])
            else:
                return precog_dict[precog_name](precog_queue)
        else:
            precog_queue1 = precog_info[queue1_index + 8:queue2_index]
            precog_queue2 = precog_info[queue2_index + 8:]
            if queue_list is not None and len(queue_list) >= 2:
                queue1_val = queue_list[0]
                queue2_val = queue_list[1]

                if precog_queue1 == '_num1_' and precog_queue2 == '_num2_':
                    return precog_dict[precog_name](queue1_val, queue2_val)
                elif precog_queue1 == '_num2_' and precog_queue2 == '_num1_':
                    return precog_dict[precog_name](queue2_val, queue1_val)
                elif precog_queue1 == '_name_' and precog_queue2 == '_call_me_':
                    return precog_dict[precog_name](queue1_val, queue2_val)

    return random.choice(['I\'m sorry. I don\'t know the answer...', 'I don\'t have answer to that one.', 'Sorry, I don\'t know.'])
