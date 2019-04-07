def _check_wikipedia_this_and_replace(sentence):
    """
    Checks if search on wikipedia is asked during inference.

    Arguments:
        sentence: Statement during inference.
    """
    tokens = nltk.word_tokenize(sentence)
    tmp_sentence = ' '.join(tokens[:]).strip()

    patt_name_1 = re.compile(
        r'(\s|^)(search\s|search\s+for\s)+(.+?)\son+\s+((wikipedia|the\swikipedia))', re.IGNORECASE)
    patt_name_2 = re.compile(
        r'(^)who\s+is\s+(([A-Za-z]+[,.]?[ ]?|[a-z]+[\'-]?)+)+($|\?)', re.IGNORECASE)

    wikipedia_this_1 = re.search(patt_name_1, tmp_sentence)
    wikipedia_this_2 = re.search(patt_name_2, tmp_sentence)
    queue_list = []

    found = 0

    if wikipedia_this_2:
        wikipedia_open = wikipedia_this_2.group(2).strip()
        queue_list.append(wikipedia_open)
        new_sentence = sentence.replace(wikipedia_open, ' _wikipedia_ ')
        found += 1
    else:
        if wikipedia_this_1:
            wikipedia_open = wikipedia_this_1.group(3).strip()
            if wikipedia_open.startswith('for '):
                queue_list.append(wikipedia_open[4:])
                new_sentence = sentence.replace(
                    wikipedia_open, ' _wikipedia_ ')
            else:
                queue_list.append(wikipedia_open)
                new_sentence = sentence.replace(
                    wikipedia_open, ' _wikipedia_ ')
            found += 1
        else:
            queue_list.append('')
            new_sentence = sentence

    if found >= 1:
        return True, new_sentence, queue_list
    else:
        return False, sentence, queue_list
