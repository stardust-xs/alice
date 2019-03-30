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
RECOGNIZER
===========

Recognizer is used for recognizing and understanding the patterns in the asked
questions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import re

import nltk


def check_patterns_and_replace(question):
    """
    Checks pattern and then replaces the hotword in the question.

    Arguments:
        question: Question asked during inference.
    """

    pattern_matched, new_sentence, queue_list = _check_arithmetic_pattern_and_replace(
        question)

    if not pattern_matched:
        pattern_matched, new_sentence, queue_list = _check_not_username_pattern_and_replace(
            new_sentence)

    if not pattern_matched:
        pattern_matched, new_sentence, queue_list = _check_username_call_me_pattern_and_replace(
            new_sentence)

    if not pattern_matched:
        pattern_matched, new_sentence, queue_list = _check_google_search_and_replace(
            new_sentence)

    if not pattern_matched:
        pattern_matched, new_sentence, queue_list = _check_wikipedia_search_and_replace(
            new_sentence)


def _check_arithmetic_pattern_and_replace(sentence):
    """
    Checks arithmetic pattern and then replaces the numbers in question.

    Arguments:
        sentence: A mMathematical statement.
    """
    pattern_matched, ind_list, num_list = _contains_arithmetic_pattern(
        sentence)
    if pattern_matched:
        s1, e1 = ind_list[0]
        s2, e2 = ind_list[1]
        # Leave spaces around the special tokens so that NLTK knows they are
        # separate tokens
        new_sentence = sentence[:s1] + ' _num1_ ' + \
            sentence[e1:s2] + ' _num2_ ' + sentence[e2:]
        return True, new_sentence, num_list
    else:
        return False, sentence, num_list


def _contains_arithmetic_pattern(sentence):
    """
    Checks maths related terms in question.

    Arguments:
        sentence: A mathematical statement.
    """
    numbers = [
        'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
        'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen',
        'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen',
        'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty',
        'ninety', 'hundred', 'thousand', 'lakh', 'crore', 'million', 'billion', 'trillion', 'quadrillion', 'pentallion']

    patt_op1 = re.compile(
        r'\s(plus|add|added|\+|minus|subtract|subtracted|-|times|multiply|multiplied|\*|divide|(divided\s+by)|/)\s',
        re.IGNORECASE)
    patt_op2 = re.compile(r'\s((sum\s+of)|(product\s+of))\s', re.IGNORECASE)
    patt_as = re.compile(r'((\bis\b)|=|(\bequals\b)|(\bget\b))', re.IGNORECASE)

    math_op1 = re.search(patt_op1, sentence)
    math_op2 = re.search(patt_op2, sentence)
    math_as = re.search(patt_as, sentence)
    if (math_op1 or math_op2) and math_as:
        # Contains an arithmetic operator and an assign operator.
        # Replace all occurrences of word 'and' with 3 whitespaces before
        # feeding to the pattern matcher.
        patt_and = re.compile(r'\band\b', re.IGNORECASE)
        if math_op1:
            tmp_sentence = patt_and.sub('   ', sentence)
        else:
            # Do not support word 'and' in the English numbers any more as
            # that can be ambiguous.
            tmp_sentence = patt_and.sub('_T_', sentence)

        num_regex = r'(?:{})'.format('|'.join(numbers))
        patt_num = re.compile(r'\b{0}(?:(?:\s+(?:and\s+)?|-){0})*\b|\d+'.format(num_regex),
                              re.IGNORECASE)
        ind_list = [(m.start(0), m.end(0))
                    for m in re.finditer(patt_num, tmp_sentence)]
        num_list = []
        if len(ind_list) == 2:
            # Contains exactly two numbers
            for start, end in ind_list:
                text = sentence[start:end]
                text_int = _text2int(text)
                if text_int == -1:
                    return False, [], []
                num_list.append(text_int)
            return True, ind_list, num_list
    return False, [], []


def _text2int(text):
    """
    Converts text based numbers into actual numbers.

    Arguments:
        text: Textual number.
    """
    if text.isdigit():
        return int(text)

    num_words = {}
    units = [
        'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
        'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',
        'sixteen', 'seventeen', 'eighteen', 'nineteen',
    ]
    tens = ['', '', 'twenty', 'thirty', 'forty',
            'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
    scales = ['hundred', 'thousand', 'million', 'billion',
              'trillion', 'quadrillion', 'pentallion']

    num_words['and'] = (1, 0)
    for idx, word in enumerate(units):
        num_words[word] = (1, idx)
    for idx, word in enumerate(tens):
        num_words[word] = (1, idx * 10)
    for idx, word in enumerate(scales):
        num_words[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in text.replace('-', ' ').lower().split():
        if word not in num_words:
            return -1

        scale, increment = num_words[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0
    return result + current


def _check_not_username_pattern_and_replace(sentence):
    """
    Checks if the wrong username is stored during inference.

    Arguments:
        sentence: Statement during inference.
    """
    tokens = nltk.word_tokenize(sentence)
    tmp_sentence = ' '.join(tokens[:]).strip()

    patt_not_but = re.compile(
        r'(\s|^)my\s+name\s+is\s+(not|n\'t)\s+(.+?)(\s\.|\s,|\s!)\s*but\s+(.+?)(\s\.|\s,|\s!|$)', re.IGNORECASE)
    patt_not = re.compile(
        r'(\s|^)my\s+name\s+is\s+(not|n\'t)\s+(.+?)(\s\.|\s,|\s!|$)', re.IGNORECASE)

    math_not_but = re.search(patt_not_but, tmp_sentence)
    math_not = re.search(patt_not, tmp_sentence)

    queue_list = []
    found = 0
    if math_not_but:
        wrong_name = math_not_but.group(3).strip()
        correct_name = math_not_but.group(5).strip()
        queue_list.append(correct_name)
        new_sentence = sentence.replace(
            wrong_name, ' _ignored_ ', 1).replace(correct_name, ' _name_ ', 1)
        found += 1
    elif math_not:
        wrong_name = math_not.group(3).strip()
        new_sentence = sentence.replace(wrong_name, ' _ignored_ ', 1)
        found += 1
    else:
        new_sentence = sentence

    if found >= 1:
        return True, new_sentence, queue_list
    else:
        return False, sentence, queue_list


def _check_username_call_me_pattern_and_replace(sentence):
    """
    Checks if the username is asked during inference.

    Arguments:
        sentence: Statement during inference.
    """
    tokens = nltk.word_tokenize(sentence)
    tmp_sentence = ' '.join(tokens[:]).strip()

    patt_name = re.compile(
        r'(\s|^)my\s+name\s+is\s+(.+?)(\s\.|\s,|\s!|$)', re.IGNORECASE)
    patt_call = re.compile(
        r'(\s|^)call\s+me\s+(.+?)(\s(please|pls))?(\s\.|\s,|\s!|$)', re.IGNORECASE)

    math_name = re.search(patt_name, tmp_sentence)
    math_call = re.search(patt_call, tmp_sentence)

    queue_list = []
    found = 0
    if math_name:
        user_name = math_name.group(2).strip()
        queue_list.append(user_name)
        new_sentence = sentence.replace(user_name, ' _name_ ', 1)
        found += 1
    else:
        queue_list.append('')
        new_sentence = sentence

    if math_call:
        call_me = math_call.group(2).strip()
        queue_list.append(call_me)
        new_sentence = new_sentence.replace(call_me, ' _call_me_ ')
        found += 1
    else:
        queue_list.append('')

    if found >= 1:
        return True, new_sentence, queue_list
    else:
        return False, sentence, queue_list


def _check_google_search_and_replace(sentence):
    """
    Checks if google search is asked during inference.

    Arguments:
        sentence: Statement during inference.
    """
    tokens = nltk.word_tokenize(sentence)
    tmp_sentence = ' '.join(tokens[:]).strip()

    patt_name_1 = re.compile(
        r'(\s|^)search\s+(.+?)\son+\s+((web|the\sweb)|(google)|(internet|the\sinternet)|(net|the\snet))', re.IGNORECASE)
    patt_name_2 = re.compile(
        r'(\s|^)search\s+for\s+(.+?)\son+\s+((web|the\sweb)|(google)|(internet|the\sinternet)|(net|the\snet))', re.IGNORECASE)

    google_search_1 = re.search(patt_name_1, tmp_sentence)
    google_search_2 = re.search(patt_name_2, tmp_sentence)
    queue_list = []

    found = 0

    if google_search_2:
        google_open = google_search_2.group(2).strip()
        queue_list.append(google_open)
        new_sentence = sentence.replace(google_open, ' _google_ ')
        found += 1
    else:
        if google_search_1:
            google_open = google_search_1.group(2).strip()
            queue_list.append(google_open)
            new_sentence = sentence.replace(google_open, ' _google_ ')
            found += 1
        else:
            queue_list.append('')
            new_sentence = sentence

    if found >= 1:
        return True, new_sentence, queue_list
    else:
        return False, sentence, queue_list


def _check_wikipedia_search_and_replace(sentence):
    """
    Checks if search on wikipedia is asked during inference.

    Arguments:
        sentence: Statement during inference.
    """
    pass
#     tokens = nltk.word_tokenize(sentence)
#     tmp_sentence = ' '.join(tokens[:]).strip()
#
#     patt_name_1 = re.compile(
#         r'(\s|^)search\s+(.+?)\son+\s+((wikipedia|the\swikipedia))', re.IGNORECASE)
#     patt_name_2 = re.compile(
#         r'(\s|^)search\s+for\s+(.+?)\son+\s+((wikipedia|the\swikipedia))', re.IGNORECASE)
#     patt_name_3 = re.compile(
#         r'(^)who\s+is\s+(([A-Za-z]+[,.]?[ ]?|[a-z]+[\'-]?)+)+($|\?)', re.IGNORECASE)
#
#     wikipedia_search_1 = re.search(patt_name_1, tmp_sentence)
#     wikipedia_search_2 = re.search(patt_name_2, tmp_sentence)
#     wikipedia_search_3 = re.search(patt_name_3, tmp_sentence)
#     queue_list = []
#
#     found = 0
#
#     if wikipedia_search_3:
#         wikipedia_open = wikipedia_search_3.group(2).strip()
#         queue_list.append(wikipedia_open)
#         new_sentence = sentence.replace(wikipedia_open, ' _wikipedia_ ')
#         found += 1
#     else:
#         if wikipedia_search_2:
#             wikipedia_open = wikipedia_search_2.group(2).strip()
#             queue_list.append(wikipedia_open)
#             new_sentence = sentence.replace(wikipedia_open, ' _wikipedia_ ')
#             found += 1
#         else:
#             if wikipedia_search_1:
#                 wikipedia_open = wikipedia_search_1.group(2).strip()
#                 queue_list.append(wikipedia_open)
#                 new_sentence = sentence.replace(
#                     wikipedia_open, ' _wikipedia_ ')
#                 found += 1
#             else:
#                 queue_list.append('')
#                 new_sentence = sentence
#
#     if found >= 1:
#         return True, new_sentence, queue_list
#     else:
#         return False, sentence, queue_list


# if __name__ == '__main__':
#
#     sentence = 'who is donald trump?'
#     print('# {}'.format(sentence))
#     pattern, ns, ql = _check_wikipedia_search_and_replace(sentence)
#     print(pattern, ns, ql)
#
#     sentence = 'My name is akshay mestry. Please call me Mr. XA.'
#     print('# {}'.format(sentence))
#     pattern, ns, ql = _check_username_call_me_pattern_and_replace(sentence)
#     print(pattern, ns, ql)
#
#     sentence = 'My name is XA MES3.'
#     print('# {}'.format(sentence))
#     pattern, ns, ql = _check_username_call_me_pattern_and_replace(sentence)
#     print(pattern, ns, ql)
#
#
#     sentence = 'Call me Ms. Patel please.'
#     print('# {}'.format(sentence))
#     _, ns, _ = _check_username_call_me_pattern_and_replace(sentence)
#     print(ns)
#
#     sentence = 'My name is Shrushthi. Please call me Shruhsthi P.'
#     print('# {}'.format(sentence))
#     _, ns, _ = _check_username_call_me_pattern_and_replace(sentence)
#     print(ns)
#
#     sentence = 'My name is not just XA, but XAMES3.'
#     print('# {}'.format(sentence))
#     _, ns, _ = _check_not_username_pattern_and_replace(sentence)
#     print(ns)
#
#     sentence = 'My name is not just XA.'
#     print('# {}'.format(sentence))
#     _, ns, _ = _check_not_username_pattern_and_replace(sentence)
#     print(ns)
