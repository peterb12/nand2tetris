import sys
import os
from JackTokenizer import JackTokenizer
from jc_types import TokenType

class CompilationEngine:
    # Constructor
    def __init__(self, fname):
        self.lexer = JackTokenizer(fname)
        self.lexer.advance()
        self.treeLevel = 0

    def genLeaf(self):
        level = self.treeLevel
        leaf = ""
        while (level > 0):
            leaf = leaf + "  "
            level = level - 1
        leaf = leaf + self.lexer.genTokenElement()
        print(leaf)
        # Generating a leaf should advance the lexer.
        self.lexer.advance()

    def genBeginBranch(self, branchName):
        branch = ""
        level = self.treeLevel
        while (level > 0):
            branch = branch + "  "
            level = level - 1
        branch = branch + "<" + branchName + ">"
        self.treeLevel = self.treeLevel + 1
        print(branch)

    def genEndBranch(self, branchName):
        branch = ""
        self.treeLevel = self.treeLevel - 1
        level = self.treeLevel
        while (level > 0):
            branch = branch + "  "
            level = level - 1
        branch = branch + "</" + branchName + ">"
        assert self.treeLevel >= 0, "Parse failure"
        print(branch)

    # 'class' className '{' classVarDec* subroutineDec* '}'
    # className: identifier
    def compileClass(self):
        # Precondition: Lexer advanced to first token.
        assert self.lexer.tokenType() == TokenType.KEYWORD, "Syntax error."
        assert self.lexer.keyWord() == "class", "Syntax error."
        tag = "class"
        self.genBeginBranch(tag)
        self.genLeaf()

        # className
        assert self.lexer.tokenType() == TokenType.IDENTIFIER, "Syntax error."
        self.genLeaf()

        # '{'
        assert self.lexer.tokenType() == TokenType.SYMBOL, "Syntax error."
        assert self.lexer.symbol() == "{", "Syntax error."
        self.genLeaf()

        # Zero or more
        while (self.lexer.tokenType() == TokenType.KEYWORD
              and (self.lexer.keyWord() == "field"
                   or self.lexer.keyWord() == "static")):
            self.compileClassVarDec() # Recurse

        # Zero or more
        while (self.lexer.tokenType() == TokenType.KEYWORD
              and (self.lexer.keyWord() == "constructor"
                   or self.lexer.keyWord() == "function"
                   or self.lexer.keyWord() == "method")):
            self.compileSubroutine() # Recurse

        self.genEndBranch(tag)


    # ('static' | 'field') type varName (',' varName)* ';'
    def compileClassVarDec(self):
        assert self.lexer.tokenType() == TokenType.KEYWORD, "Syntax error."
        varDecType = self.lexer.keyWord()
        assert (varDecType == "field" or varDecType == "static"), "Syntax error."

        tag = "classVarDec"
        self.genBeginBranch(tag)
        self.genLeaf() # field | static
        assert self.lexer.tokenType() == TokenType.KEYWORD
        self.genLeaf() # type
        assert self.lexer.tokenType() == TokenType.IDENTIFIER
        self.genLeaf() # varName
        #  Zero or more
        while (self.lexer.tokenType() == TokenType.SYMBOL
               and (self.lexer.symbol() == ",")):
            self.genLeaf() # ","
            assert self.lexer.tokenType() == TokenType.IDENTIFIER
            self.genLeaf() # varName

        assert self.lexer.tokenType() == TokenType.SYMBOL and self.lexer.symbol() == ";", "Syntax error."
        self.genLeaf()

        self.genEndBranch(tag)

    # ('constructor' | 'function' | 'method')
    #    ('void' | type) subroutineName '(' parameterList ')'
    #    subroutineBody
    def compileSubroutine(self):
        tag = "subroutineDec"
        self.genBeginBranch(tag)
        assert self.lexer.tokenType() == TokenType.KEYWORD, "Syntax error."
        assert (self.lexer.keyWord() == "constructor"
                or self.lexer.keyWord() == "function"
                or self.lexer.keyWord() == "method"), "Syntax error."
        self.genLeaf() # ('constructor' | 'function' | 'method')

        assert (self.lexer.tokenType() == TokenType.IDENTIFIER
                or self.lexer.tokenType() == TokenType.KEYWORD), "Syntax error."
        self.genLeaf() # ('void' | type)

        assert self.lexer.tokenType() == TokenType.IDENTIFIER
        self.genLeaf() # subroutineName

        assert (self.lexer.tokenType() == TokenType.SYMBOL
                and self.lexer.symbol() == "(")
        self.genLeaf() # '('

        self.compileParameterList() # Recurse: parameterList

        assert (self.lexer.tokenType() == TokenType.SYMBOL
                and self.lexer.symbol() == ")")
        self.genLeaf() # ')'

        self.genEndBranch(tag)

    # ( (type varName) (',' type varName)* )?
    def compileParameterList(self):
        tag = "parameterList"
        self.genBeginBranch(tag)

        # A parameterList can appear 0 or 1 times, so if the current
        # token is ")", we are in fact done.
        while (not (self.lexer.tokenType() == TokenType.SYMBOL
                 and self.lexer.symbol() == ")")):
                assert (self.lexer.tokenType() == TokenType.IDENTIFIER
                        or self.lexer.tokenType() == TokenType.KEYWORD), "Syntax error."
                self.genLeaf() # type

                assert self.lexer.tokenType() == TokenType.IDENTIFIER, "Syntax error."
                self.genLeaf() # varName

                #  Zero or more
                if (self.lexer.tokenType() == TokenType.SYMBOL
                       and (self.lexer.symbol() == ",")):
                        self.genLeaf() # ","

        self.genEndBranch(tag)

    def compileVarDec(self):
        print("N/A")

    def compileStatements(self):
        print("N/A")

    def compileDo(self):
        print("N/A")

    def compileLet(self):
        print("N/A")

    def compileWhile(self):
        print("N/A")

    def compileReturn(self):
        print("N/A")

    def compileIf(self):
        print("N/A")

    def compileExpression(self):
        print("N/A")

    def compileTerm(self):
        print("N/A")

    def compileExpressionList(self):
        print("N/A")

pathname = sys.argv[1]
compiler = CompilationEngine(pathname)
compiler.compileClass()
