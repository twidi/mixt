class State(object):
    DATA = 1
    # unused states: charrefs, RCDATA, script, RAWTEXT, PLAINTEXT
    TAG_OPEN = 7
    END_TAG_OPEN = 8
    TAG_NAME = 9
    # unused states: RCDATA, RAWTEXT, script
    BEFORE_ATTRIBUTE_NAME = 34
    ATTRIBUTE_NAME = 35
    AFTER_ATTRIBUTE_NAME = 36
    BEFORE_ATTRIBUTE_VALUE = 37
    ATTRIBUTE_VALUE_DOUBLE_QUOTED = 38
    ATTRIBUTE_VALUE_SINGLE_QUOTED = 39
    ATTRIBUTE_VALUE_UNQUOTED = 40
    # unused state: CHARREF_IN_ATTRIBUTE_VALUE = 41
    AFTER_ATTRIBUTE_VALUE = 42
    SELF_CLOSING_START_TAG = 43
    # unused state: BOGUS_COMMENT_STATE = 44
    MARKUP_DECLARATION_OPEN = 45
    COMMENT_START = 46
    COMMENT_START_DASH = 47
    COMMENT = 48
    COMMENT_END_DASH = 49
    COMMENT_END = 50
    # unused state: COMMENT_END_BANG = 51
    DOCTYPE = 52
    DOCTYPE_CONTENTS = 53 # Gross oversimplification. Not to spec.
    # unused states: doctypes
    CDATA_SECTION = 68

    @classmethod
    def state_name(cls, state_val):
        for k, v in cls.__dict__.items():
            if v == state_val:
                return k
        assert False, "impossible state value %r!" % state_val
