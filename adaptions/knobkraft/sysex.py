#
#   Copyright (c) 2022 Christof Ruch. All rights reserved.
#
#   Dual licensed: Distributed under Affero GPL license by default, an MIT license is available for purchase
#
from typing import List, Tuple


def load_sysex(filename):
    with open(filename, mode="rb") as midi_messages:
        content = midi_messages.read()
        messages = []
        start_index = 0
        for index, byte in enumerate(content):
            if byte == 0xf7:
                messages.append(list(content[start_index:index + 1]))
                start_index = index + 1
        return messages


def splitSysexMessage(messages):
    result = []
    start = 0
    for read in range(len(messages)):
        if messages[read] == 0xf0:
            start = read
        elif messages[read] == 0xf7:
            result.append(messages[start:read + 1])
    return result


def findSysexDelimiters(messages, max_no=None) -> List[Tuple[int, int]]:
    result = []
    start = 0
    for read in range(len(messages)):
        if messages[read] == 0xf0:
            start = read
        elif messages[read] == 0xf7:
            result.append((start, read + 1))
            if max_no is not None and len(result) >= max_no:
                # Early abort when we only want the first max_no messages
                return result
    return result


def splitSysex(byte_list):
    result = []
    index = 0
    while index < len(byte_list):
        sysex = []
        if byte_list[index] == 0xf0:
            # Sysex start
            while byte_list[index] != 0xf7 and index < len(byte_list):
                sysex.append(byte_list[index])
                index += 1
            sysex.append(0xf7)
            index += 1
            result.append(sysex)
        else:
            print("Skipping invalid byte", byte_list[index])
            index += 1
    return result
