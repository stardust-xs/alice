# import nltk
# import re
#
# sentence = 'my name is xa'
#
# tokens = nltk.word_tokenize(sentence)
# tmp_sentence = ' '.join(tokens[:]).strip()
#
#
# print(tmp_sentence)
#
# patt_name = re.compile(
#     r'(\s|^)my\s+name\s+is\s+(.+?)(\s\.|\s,|\s!|$)', re.IGNORECASE)
# patt_call = re.compile(
#     r'(\s|^)call\s+me\s+(.+?)(\s(please|pls))?(\s\.|\s,|\s!|$)', re.IGNORECASE)
#
# math_name = re.search(patt_name, tmp_sentence)
#
# print(math_name)
# math_call = re.search(patt_call, tmp_sentence)
#
# queue_list = []
# found = 0
# if math_name:
#     user_name = math_name.group(2).strip()
#     queue_list.append(user_name)
#     new_sentence = sentence.replace(user_name, ' _name_ ', 1)
#     found += 1
#
#     print(user_name)
#     print(new_sentence)
#
#
#
# my name is xa
# <_sre.SRE_Match object; span=(0, 13), match='my name is xa'>
# xa
# my name is  _name_
