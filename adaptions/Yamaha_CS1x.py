import hashlib


def name():
    return "Yamaha CS1x"


def createDeviceDetectMessage(channel):
    return [0xf0, # SysEx
            0x7e, # Non-realtime message
            0x00, # Channel
            0x06, # General information
            0x01, # Identity request
            0xf7] # End of SysEx


def needsChannelSpecificDetection():
    return False


def channelIfValidDeviceResponse(message):
    if (len(message) == 15
            and message[0] == 0xf0    # SysEx
            and message[1] == 0x7e    # Non-realtime message
            and message[2] == 0x7f    # Channel
            and message[3] == 0x06    # General information
            and message[4] == 0x02    # Identity reply
            and message[5] == 0x43    # Yamaha ID
            and message[6] == 0x00    # Family code
            and message[7] == 0x41    # ""
            and message[8] == 0x10    # Model number
            and message[9] == 0x02    # ""
            and message[10] == 0x00   # Version number
            and message[11] == 0x00   # ""
            and message[12] == 0x00   # ""
            and message[13] == 0x01   # ""
            and message[14] == 0xf7): # End of SysEx
        return 0
    return -1


BULK  = 0x20 # + n
BULKR = 0x00 # + n
PARM = 0x30 # + n

XG = 0x4C
NAT = 0x4B


def genericYamahaRequest(device_number, model_id, request_body):
    return [0xf0, 0x43, device_number, model_id] + request_body + [0xf7]


def isSysEx(message):
    return (len(message) >= 2 and
            message[0] == 0xf0 and
            message[-1] == 0xf7)


def isYamahaHeader(message, device_number, model_id):
    return (isSysEx(message) and
            len(message) >= 5 and  # 2 + 3
            message[1] == 0x43 and # Yamaha ID
            message[2] == device_number and
            message[3] == model_id)


def isYamahaBulkDump(message):
    return (isYamahaHeader(message, BULKR, NAT) and
            len(message) >= 11)  # 5 + 6


def createXGSystemDataQuery():
    return genericYamahaRequest(BULK, XG, [0x00, 0x00, 0x00])


def createXGSystemInformationQuery():
    return genericYamahaRequest(BULK, XG, [0x01, 0x00, 0x00])


def createSystemQuery():
    return genericYamahaRequest(BULK, NAT, [0x50, 0x00, 0x00])


##################### user program

def createUserPerformanceCommonQuery(pp):
    return genericYamahaRequest(BULK, NAT, [0x70, pp, 0x00])


def isUserPerformanceCommonResponse(message):
    return (isYamahaBulkDump(message) and
            len(message) == 11 + 0x2e and
            message[6] == 0x70 and
            message[8] == 0x00)


def createUserPerformanceEffectsQuery(pp):
    return genericYamahaRequest(BULK, NAT, [0x70, pp, 0x30])


def isUserPerformanceEffectsResponse(message):
    return (isYamahaBulkDump(message) and
            len(message) == 11 + 0x15 and
            message[6] == 0x70 and
            message[8] == 0x30)


def createUserPerformanceModulationsQuery(pp):
    return genericYamahaRequest(BULK, NAT, [0x70, pp, 0x50])


def isUserPerformanceModulationsResponse(message):
    return (isYamahaBulkDump(message) and
            len(message) == 11 + 0x09 and
            message[6] == 0x70 and
            message[8] == 0x50)


def createUserPerformanceLayerQuery(pp, l):
    return genericYamahaRequest(BULK, NAT, [0x70 + l + 1, pp, 0x00])


def isUserPerformanceLayerResponse(message):
    return (isYamahaBulkDump(message) and
            len(message) == 11 + 0x29 and
            message[6] >= 0x71 and
            message[6] <= 0x74 and
            message[8] == 0x00)


##################### current buffer

def createCurrentPerformanceCommonQuery():
    return genericYamahaRequest(BULK, NAT, [0x60, 0x00, 0x00])


def isCurrentPerformanceCommonResponse(message):
    return (isYamahaBulkDump(message) and
            len(message) == 11 + 0x2e and
            message[6] == 0x60 and
            message[7] == 0x00 and
            message[8] == 0x00)


def createCurrentPerformanceEffectsQuery():
    return genericYamahaRequest(BULK, NAT, [0x60, 0x00, 0x30])


def isCurrentPerformanceEffectsResponse(message):
    return (isYamahaBulkDump(message) and
            len(message) == 11 + 0x17 and
            message[6] == 0x60 and
            message[7] == 0x00 and
            message[8] == 0x30)


def createCurrentPerformanceModulationsQuery():
    return genericYamahaRequest(BULK, NAT, [0x60, 0x00, 0x50])


def isCurrentPerformanceModulationsResponse(message):
    return (isYamahaBulkDump(message) and
            len(message) == 11 + 0x09 and
            message[6] == 0x60 and
            message[7] == 0x00 and
            message[8] == 0x50)


def createCurrentPerformanceLayerQuery(l):
    return genericYamahaRequest(BULK, NAT, [0x60, l + 1, 0x00])


def isCurrentPerformanceLayerResponse(message):
    return (isYamahaBulkDump(message) and
            len(message) == 11 + 0x29 and
            message[6] == 0x60 and
            message[7] >= 0x01 and
            message[7] <= 0x04 and
            message[8] == 0x00)


##################### program request


def createProgramDumpRequest(channel, pp):
    return (createUserPerformanceCommonQuery(pp) +
            createUserPerformanceEffectsQuery(pp) +
            createUserPerformanceModulationsQuery(pp) +
            createUserPerformanceLayerQuery(pp, 0) +
            createUserPerformanceLayerQuery(pp, 1) +
            createUserPerformanceLayerQuery(pp, 2) +
            createUserPerformanceLayerQuery(pp, 3))


def isPartOfSingleProgramDump(message):
    return (isUserPerformanceCommonResponse(message) or
            isUserPerformanceEffectsResponse(message) or
            isUserPerformanceModulationsResponse(message) or
            isUserPerformanceLayerResponse(message))


def isSingleProgramDump(message):
    messages = splitSysexMessage(message)
    if (len(messages) > 7):
        raise Exception("Not a single program dump!")
    return (len(messages) == 7 and
            isUserPerformanceCommonResponse(messages[0]) and
            isUserPerformanceEffectsResponse(messages[1]) and
            isUserPerformanceModulationsResponse(messages[2]) and
            isUserPerformanceLayerResponse(messages[3]) and
            isUserPerformanceLayerResponse(messages[4]) and
            isUserPerformanceLayerResponse(messages[5]) and
            isUserPerformanceLayerResponse(messages[6]))


def convertToProgramDump(channel, message, program_number):
    if (isUserDump(message)):
        return message
    messages = splitSysexMessage(message)
    messages[0][6:9] = [0x70, program_number, 0x00]
    messages[1][6:9] = [0x70, program_number, 0x30]
    # Edit buffer has two extra bytes in effects dump
    messages[1] = messages[1][0:-4] + messages[1][-2:]
    messages[2][6:9] = [0x70, program_number, 0x50]
    messages[3][6:9] = [0x71, program_number, 0x00]
    messages[4][6:9] = [0x72, program_number, 0x00]
    messages[5][6:9] = [0x73, program_number, 0x00]
    messages[6][6:9] = [0x74, program_number, 0x00]
    return (messages[0] + messages[1] +
            messages[2] + messages[3] +
            messages[4] + messages[5] +
            messages[6])


##################### edit buffer request

def createEditBufferRequest(channel):
    return (createCurrentPerformanceCommonQuery() +
            createCurrentPerformanceEffectsQuery() +
            createCurrentPerformanceModulationsQuery() +
            createCurrentPerformanceLayerQuery(0) +
            createCurrentPerformanceLayerQuery(1) +
            createCurrentPerformanceLayerQuery(2) +
            createCurrentPerformanceLayerQuery(3))


def isPartOfEditBufferDump(message):
    return (isCurrentPerformanceCommonResponse(message) or
            isCurrentPerformanceEffectsResponse(message) or
            isCurrentPerformanceModulationsResponse(message) or
            isCurrentPerformanceLayerResponse(message))


def isEditBufferDump(message):
    messages = splitSysexMessage(message)
    if (len(messages) > 7):
        raise Exception("Not a single program dump!")
    return (len(messages) == 7 and
            isCurrentPerformanceCommonResponse(messages[0]) and
            isCurrentPerformanceEffectsResponse(messages[1]) and
            isCurrentPerformanceModulationsResponse(messages[2]) and
            isCurrentPerformanceLayerResponse(messages[3]) and
            isCurrentPerformanceLayerResponse(messages[4]) and
            isCurrentPerformanceLayerResponse(messages[5]) and
            isCurrentPerformanceLayerResponse(messages[6]))


def convertToEditBuffer(channel, message):
    if (isCurrentDump(message)):
        return message
    messages = splitSysexMessage(message)
    messages[0][6:9] = [0x60, 0x00, 0x00]
    messages[1][6:9] = [0x60, 0x00, 0x30]
    # User buffer misses two bytes in effects dump
    messages[1] = messages[1][0:-2] + [0x40, 0x00] + messages[1][-2:] # Add two missing bytes
    messages[2][6:9] = [0x60, 0x00, 0x50]
    messages[3][6:9] = [0x60, 0x01, 0x00]
    messages[4][6:9] = [0x60, 0x02, 0x00]
    messages[5][6:9] = [0x60, 0x03, 0x00]
    messages[6][6:9] = [0x60, 0x04, 0x00]
    return (messages[0] + messages[1] +
            messages[2] + messages[3] +
            messages[4] + messages[5] +
            messages[6])


def nameFromEditBuffer(message):
    return categoryString(message[17]) + "".join([chr(x) for x in message[9:17]])


def nameFromDump(message):
    return categoryString(message[17]) + "".join([chr(x) for x in message[9:17]])


def calculateFingerprint(message):
    messages = splitSysexMessage(convertToEditBuffer(0, message))
    data = (messages[0][9:-2] + messages[1][9:-2] +
            messages[2][9:-2] + messages[3][9:-2] +
            messages[4][9:-2] + messages[5][9:-2] +
            messages[6][9:-2])
    return hashlib.md5(bytearray(data)).hexdigest()


def friendlyProgramName(program):
    return "%03d" % (program + 1)


def isUserDump(message):
    return message[6] == 0x70


def isCurrentDump(message):
    return message[6] == 0x60


def categoryString(c):
    if (c == 0):
        return "--:"
    if (c == 1):
        return "Pf:"
    if (c == 2):
        return "Cp:"
    if (c == 3):
        return "Or:"
    if (c == 4):
        return "Gt:"
    if (c == 5):
        return "Ba:"
    if (c == 6):
        return "St:"
    if (c == 7):
        return "En:"
    if (c == 8):
        return "Br:"
    if (c == 9):
        return "Rd:"
    if (c == 10):
        return "Pi:"
    if (c == 11):
        return "Ld:"
    if (c == 12):
        return "Pd:"
    if (c == 13):
        return "Fx:"
    if (c == 14):
        return "Et:"
    if (c == 15):
        return "Pc:"
    if (c == 16):
        return "Se:"
    if (c == 17):
        return "Dr:"
    if (c == 18):
        return "Sc:"
    if (c == 19):
        return "Vo:"
    if (c == 20):
        return "Co:"
    if (c == 21):
        return "Wv:"
    if (c == 22):
        return "Sq:"
    return "!!:"


def generalMessageDelay():
    return 350


def numberOfBanks():
    return 1


def numberOfPatchesPerBank():
    return 128


def splitSysexMessage(messages):
    result = []
    start = 0
    read = 0
    while read < len(messages):
        if messages[read] == 0xf0:
            start = read
        elif messages[read] == 0xf7:
            result.append(messages[start:read + 1])
        read = read + 1
    return result
