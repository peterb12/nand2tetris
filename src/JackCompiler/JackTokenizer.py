import sys
import os
from xml.sax.saxutils import escape
from jc_types import LexerState
from jc_types import TokenType

class JackTokenizer:

    keywords = ["class", "constructor", "function", "method", "field",
                "static", "var", "int", "char", "boolean", "void",
                "true", "false", "null", "this", "let", "do", "if",
                "else", "while", "return"]
    symbols = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*",
                  "/", "&", "|", "<", ">", "=", "~"]

    debugMode = False

    # Constructor
    def __init__(self, fname):
        self.currentFile = open(fname, encoding="utf-8")
        self.currentToken = ""
        self.savedChar = ""
        self.lexerState = LexerState.START
        self.currentTokenType = ""
        if (self.debugMode == True):
            (currName, filepart) = os.path.split(filename)
            (shortName, extension) = os.path.splitext(filepart)
            xmlName = shortName + "Tokens.xml"
            self.f = open(dirName + "/" + xmlName, "w")

    # Return the current token as an XML element.
    def genTokenElement(self, attributeString):
        element = ""
        assert (attributeString == "" or attributeString[0] == ' '), "Internal error."
        attributeString = attributeString + "> "
        if (self.tokenType() == TokenType.KEYWORD):
            element = "<keyword" + attributeString + self.keyWord() + " </keyword>"
        elif (self.tokenType() == TokenType.SYMBOL):
            element = "<symbol" + attributeString + self.symbol() + " </symbol>"
        elif (self.tokenType() == TokenType.IDENTIFIER):
            element = "<identifier" + attributeString + self.identifier() + " </identifier>"
        elif (self.tokenType() == TokenType.INT_CONST):
            element = "<integerConstant" + attributeString + self.intVal() + " </integerConstant>"
        elif (self.tokenType() == TokenType.STRING_CONST):
            element = "<stringConstant" + attributeString + self.stringVal() + " </stringConstant>"
        else:
            # Unhandled input, lexer is broken
            assert False

        if (self.debugMode == True):
            self.f.write(element + "\n")
        return element


    # hasMoreTokens -> Boolean
    # Do we have more tokens in the input?
    # Assumes that advance() has been called at least once.
    def hasMoreTokens(self):
        if self.currentToken and self.currentToken != "":
            return True
        return False

    def advance(self):
        self.lexerState = LexerState.START
        self.currentToken = ""

        while (self.lexerState != LexerState.FINISHED):
            if self.lexerState == LexerState.START:
                # Process lookahead, if any.
                if (self.savedChar != ""):
                    cchar = self.savedChar
                    self.savedChar = ""
                else:
                    # No lookahead, read the next character
                    cchar = self.currentFile.read(1)
                self.lexerState = LexerState.RECOGNIZE
            elif self.lexerState == LexerState.RECOGNIZE:
                if cchar == "":
                    self.lexerState = LexerState.FINISHED
                elif cchar == "/":
                    # Requires lookahead. Most compliated bit.
                    lchar = self.currentFile.read(1)
                    if (lchar != "/" and lchar != "*"):
                        # Not a comment, save lookahead.
                        self.savedChar = lchar
                        self.lexerState = LexerState.SYMBOL
                    else:
                        if (lchar == "/"):
                            self.lexerState = LexerState.CPPCOMMENT
                        elif (lchar == "*"):
                            self.lexerState = LexerState.CCOMMENT
                elif (cchar in self.symbols):
                    self.lexerState = LexerState.SYMBOL
                elif (cchar.isdigit()):
                    self.lexerState = LexerState.DIGIT
                elif (cchar == '"'):
                    self.lexerState = LexerState.QUOTE
                elif (cchar.isalnum() or cchar == "_"):
                    self.lexerState = LexerState.ALPHA
                else:
                    # None of the above.  Advance.
                    self.lexerState = LexerState.START
                # END RECOGNIZE.  After this it's easy.
            elif self.lexerState == LexerState.CCOMMENT:
                # C comments end with "*/"
                cchar = self.currentFile.read(1)
                if (cchar == '*'):
                    # Need lookahead.
                    lchar = self.currentFile.read(1)
                    if (lchar == "/"):
                        self.lexerState = LexerState.START
                    else:
                        self.savedChar = lchar
            elif self.lexerState == LexerState.CPPCOMMENT:
                # CPP comments end at EOL.
                cchar = self.currentFile.read(1)
                if (cchar == '\n'):
                    self.lexerState = LexerState.START
            elif self.lexerState == LexerState.SYMBOL:
                self.currentToken = cchar
                self.currentTokenType = TokenType.SYMBOL
                self.lexerState = LexerState.FINISHED
            elif self.lexerState == LexerState.DIGIT:
                self.currentToken = self.currentToken + cchar
                cchar = self.currentFile.read(1)
                if (not cchar or not cchar.isdigit()):
                    self.savedChar = cchar
                    self.currentTokenType = TokenType.INT_CONST
                    self.lexerState = LexerState.FINISHED
                # We found another digit, advance.
            elif self.lexerState == LexerState.QUOTE:
                cchar = self.currentFile.read(1)
                if (cchar and cchar != '"'):
                    self.currentToken = self.currentToken + cchar
                else:
                    self.lexerState = LexerState.FINISHED
                    self.currentTokenType = TokenType.STRING_CONST
            elif self.lexerState == LexerState.ALPHA:
                self.currentToken = self.currentToken + cchar
                cchar = self.currentFile.read(1)
                if (not cchar or not (cchar.isalnum() or cchar == "_")):
                    self.savedChar = cchar
                    if (self.currentToken in self.keywords):
                        self.currentTokenType = TokenType.KEYWORD
                    else:
                        self.currentTokenType = TokenType.IDENTIFIER
                    self.lexerState = LexerState.FINISHED
                # We just read another alpha.  Advance.

    # Return type of current token.
    def tokenType(self):
        return self.currentTokenType

    # Return keyword which is the current token.
    def keyWord(self):
        return self.currentToken

    # Returns character which is the current token.
    def symbol(self):
        return escape(self.currentToken)

    # Returns identifier which is the current token.
    def identifier(self):
        return self.currentToken

    # Returns integer value of current token (req: INT_CONST)
    def intVal(self):
        return self.currentToken

    # Returns string val of current token without quotes (req: STRING_CONST)
    def stringVal(self):
        return self.currentToken
