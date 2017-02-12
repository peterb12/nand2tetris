from enum import Enum

class TokenType(Enum):
    KEYWORD = 0
    SYMBOL = 1
    IDENTIFIER = 2
    INT_CONST = 3
    STRING_CONST = 4

class LexerState(Enum):
    START = 0
    RECOGNIZE = 1
    CCOMMENT = 2
    CPPCOMMENT = 3
    SYMBOL = 4
    DIGIT = 5
    QUOTE = 6
    ALPHA = 7
    INTEGER = 8
    STRING = 9
    KEYWORD = 10
    IDENTIFIER = 11
    FINISHED = 12

# Theoretically we don't need to enumerate scopes, but I don't
# like the idea of the compiler internally managing all this
# state as arbitrary strings.
class Scope(Enum):
    NONE   = 0
    STATIC = 1
    FIELD  = 2
    ARG    = 3
    VAR    = 4
    @staticmethod
    def scopeForString(inString):
        if (inString == "static"):
            return Scope.STATIC
        elif (inString == "field"):
            return Scope.FIELD
        elif (inString == "arg"):
            return Scope.ARG
        elif (inString == "var"):
            return Scope.VAR
        else:
            return Scope.NONE
