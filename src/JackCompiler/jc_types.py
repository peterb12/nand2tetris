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
    
