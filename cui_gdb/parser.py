# Copyright (c) 2018 Christoph Landgraf. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import re

RES_CLS_DONE = "done"
RES_CLS_RUNNING = "running"
RES_CLS_CONNECTED = "connected"
RES_CLS_ERROR = "error"
RES_CLS_EXIT = "exit"

RESULT_CLASSES = [
    RES_CLS_DONE,
    RES_CLS_RUNNING,
    RES_CLS_CONNECTED,
    RES_CLS_ERROR,
    RES_CLS_EXIT,
]

CSTRING_TERMINATOR = re.compile('[^\\\\]\\"')


class MiResponseError(Exception):
    pass


def parse_cstring(text):
    CSTRING_TERMINATOR.search(text[1:])
    match = CSTRING_TERMINATOR.search(text[1:])
    if not match:
        raise MiResponseError('Expected terminating \'"\'.')
    terminator = match.span()[1]
    value = text[1:terminator].encode('utf-8').decode('unicode_escape')
    return value, text[terminator + 1:]


terminator_dict = {
    '{': '}',
    '[': ']',
}


def parse_list(text):
    if text[1] in ['{', '[', '"']:
        results, text = parse_values(text[1:], terminator=terminator_dict[text[0]])
    else:
        results, text = parse_results(text[1:], terminator=terminator_dict[text[0]])

    return results, text[1:]


def parse_tuple(text):
    results, text = parse_results(text[1:], terminator=terminator_dict[text[0]])
    return results, text[1:]


def parse_value(text):
    if text[0] == '"':
        value, text = parse_cstring(text)
    elif text[0] == '[':
        value, text = parse_list(text)
    elif text[0] == '{':
        value, text = parse_tuple(text)
    else:
        raise MiResponseError('Expected one of [\'"\', \'[\', \'{\'].')
    return value, text


def parse_values(text, terminator=None):
    parsed_values = []

    end = (lambda text: not text) if terminator == None else (lambda text: text[0] == terminator)

    if end(text):
        return parsed_values, text[0:]

    while True:
        value, text = parse_value(text)
        parsed_values.append(value)

        if end(text):
            break
        elif text[0] != ',':
            if terminator == None:
                raise MiResponseError('Expected end of input or \',\'.')
            else:
                raise MiResponseError('Expected \'%s\' or \',\'.' % terminator)

        text = text[1:]

    return parsed_values, text


def parse_result(text):
    variable, text = text.split('=', 1)
    value, text = parse_value(text)
    return (variable, value), text


def parse_results(text, terminator=None):
    parsed_results = {}

    end = (lambda text: not text) if terminator == None else (lambda text: text[0] == terminator)

    if end(text):
        return parsed_results, text[0:]

    while True:
        (variable, value), text = parse_result(text)
        parsed_results[variable] = value

        if end(text):
            break
        elif text[0] != ',':
            if terminator == None:
                raise MiResponseError('Expected end of input or \',\'.')
            else:
                raise MiResponseError('Expected \'%s\' or \',\'.' % terminator)

        text = text[1:]

    return parsed_results, text


def parse_record(text):
    caret_index = text.index('^')
    if caret_index == -1:
        return None

    result_class, text = text[caret_index + 1:].split(',', 1)
    if result_class not in RESULT_CLASSES:
        raise MiResponseError('Unknown result class \'%s\'.' % result_class)
    return result_class, parse_results(text)[0]
