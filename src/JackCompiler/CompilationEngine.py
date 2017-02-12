import sys
import os
from JackTokenizer import JackTokenizer
from jc_types import Scope
from jc_types import TokenType
from SymbolTable import SymbolTable

class CompilationEngine:

    operators = ["+", "-", "*", "/", "&", "&amp;", "|", "<", "&lt;", "&gt;", ">", "="]
    unaryOperators = ["-", "~"]

    debugMode = False

    # Constructor
    def __init__(self, dirName, filename):
        if (self.debugMode == True):
            print("Compilation engine initialized.")
        self.lexer = JackTokenizer(filename)
        self.lexer.advance()
        self.symbolTable = SymbolTable()
        self.treeLevel = 0
        if (self.debugMode == True):
            (currName, filepart) = os.path.split(filename)
            (shortName, extension) = os.path.splitext(filepart)
            xmlName = shortName + ".xml"
            self.f = open(dirName + "/" + xmlName, "w")

    # This is just a little convenience function to get some of
    # the messy looking asserts out of the main body of the code.
    def validate(self, tokenType, sequence):
        assert self.lexer.tokenType() == tokenType, "Syntax error."
        if (tokenType == TokenType.SYMBOL):
            assert self.lexer.symbol() == sequence, "Syntax error."
        elif (tokenType == TokenType.KEYWORD):
            assert self.lexer.keyWord() == sequence, "Syntax error."
        # No validation for identifier sequences.

    def genLeaf(self, attributes=""):
        if (self.debugMode == True):
            level = self.treeLevel
            leaf = ""
            while (level > 0):
                leaf = leaf + "  "
                level = level - 1
            leaf = leaf + self.lexer.genTokenElement(attributes) + "\n"
            self.f.write(leaf)
        # Generating a leaf should advance the lexer.
        self.lexer.advance()

    def genBeginBranch(self, branchName):
        if (self.debugMode == True):
            branch = ""
            level = self.treeLevel
            while (level > 0):
                branch = branch + "  "
                level = level - 1
            branch = branch + "<" + branchName + ">\n"
            self.treeLevel = self.treeLevel + 1
            self.f.write(branch)

    def genEndBranch(self, branchName):
        if (self.debugMode == True):
            branch = ""
            self.treeLevel = self.treeLevel - 1
            level = self.treeLevel
            while (level > 0):
                branch = branch + "  "
                level = level - 1
            branch = branch + "</" + branchName + ">\n"
            assert self.treeLevel >= 0, "Parse failure"
            self.f.write(branch)

    # 'class' className '{' classVarDec* subroutineDec* '}'
    # className: identifier
    def compileClass(self):
        # Precondition: Lexer advanced to first token.
        self.validate(TokenType.KEYWORD, "class")

        tag = "class"
        self.genBeginBranch(tag)
        self.genLeaf()

        # className
        self.validate(TokenType.IDENTIFIER, "")
        self.genLeaf()

        # '{'
        self.validate(TokenType.SYMBOL, "{")
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

        self.validate(TokenType.SYMBOL, "}")
        self.genLeaf()

        self.genEndBranch(tag)

    # type: 'int' | 'char' | 'boolean' | className
    def _extractType(self):
        outType = ""
        if (self.lexer.tokenType() == TokenType.KEYWORD):
            outType = self.lexer.keyWord()
            assert (outType == 'int' or outType == 'char' or outType == 'boolean'), "Syntax error."
        else:
            # TODO: Restrict identifier to a className
            outType = self.lexer.identifier()
        return outType


    def _emitGenericVarDec(self):
        # field | static | var, validation must be done by caller.
        varKind = Scope.scopeForString(self.lexer.keyWord())
        self.genLeaf()

        # type
        varType = self._extractType()
        self.genLeaf()

        # varName
        self.validate(TokenType.IDENTIFIER, "")
        varName = self.lexer.identifier()
        # Now we have a complete variable. Add it to the symbol
        # table.
        self.symbolTable.define(varName, varType, varKind)
        attributes = ""
        if (self.debugMode == True):
            attributes = ' name="' + varName + '" type="' + self.symbolTable.typeOf(varName) + '" kind="'  + str(self.symbolTable.kindOf(varName)) + '" ref="' + str(self.symbolTable.indexOf(varName)) + '"'

        self.genLeaf(attributes)


        #  Zero or more ("," varName)
        while (self.lexer.tokenType() == TokenType.SYMBOL
               and (self.lexer.symbol() == ",")):
            self.genLeaf() # ","
            self.validate(TokenType.IDENTIFIER, "")
            varName = self.lexer.identifier()
            self.symbolTable.define(varName, varType, varKind)
            if (self.debugMode == True):
                attributes = ' name="' + varName + '" type="' + self.symbolTable.typeOf(varName) + '" kind="'  + str(self.symbolTable.kindOf(varName)) + '" ref="' + str(self.symbolTable.indexOf(varName)) + '"'

            self.genLeaf(attributes) # varName

        # ";"
        self.validate(TokenType.SYMBOL, ";")
        self.genLeaf()

    # ('static' | 'field') type varName (',' varName)* ';'
    def compileClassVarDec(self):
        assert self.lexer.tokenType() == TokenType.KEYWORD, "Syntax error."
        varDecType = self.lexer.keyWord()
        assert (varDecType == "field"
                or varDecType == "static"), "Syntax error."

        tag = "classVarDec"
        self.genBeginBranch(tag)

        self._emitGenericVarDec()

        self.genEndBranch(tag)

    # ('constructor' | 'function' | 'method')
    #    ('void' | type) subroutineName '(' parameterList ')'
    #    subroutineBody
    def compileSubroutine(self):
        tag = "subroutineDec"
        self.genBeginBranch(tag)

        # ('constructor' | 'function' | 'method')
        assert self.lexer.tokenType() == TokenType.KEYWORD, "Syntax error."
        assert (self.lexer.keyWord() == "constructor"
                or self.lexer.keyWord() == "function"
                or self.lexer.keyWord() == "method"), "Syntax error."
        self.genLeaf()

        # ('void' | type)
        assert (self.lexer.tokenType() == TokenType.IDENTIFIER
                or self.lexer.tokenType() == TokenType.KEYWORD), "Syntax error."
        self.genLeaf()

        # subroutineName
        self.validate(TokenType.IDENTIFIER, "")
        self.genLeaf()

        # '('
        self.validate(TokenType.SYMBOL, "(")
        self.genLeaf()

        # Recurse: parameterList
        self.compileParameterList()

        # ')'
        self.validate(TokenType.SYMBOL, ")")
        self.genLeaf()

        # subroutineBody
        # wrapped in branch, then
        # '{' varDec* statements '}'
        bodyTag = "subroutineBody"
        self.genBeginBranch(bodyTag)

        # '{'
        self.validate(TokenType.SYMBOL, "{")
        self.genLeaf()

        # 0 or more varDeclarations
        while (self.lexer.tokenType() == TokenType.KEYWORD
               and self.lexer.keyWord() == "var"):
            self.compileVarDec()

        # statements
        self.compileStatements()

        assert(self.lexer.tokenType() == TokenType.SYMBOL
               and self.lexer.symbol() == "}"), "Syntax error."
        self.genLeaf()

        self.genEndBranch(bodyTag)
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

    # 'var' type varName (',' varName)* ';'
    def compileVarDec(self):
        tag = "varDec"
        self.genBeginBranch(tag)

        # 'var'
        self.validate(TokenType.KEYWORD, "var")
        self._emitGenericVarDec()

        self.genEndBranch(tag)

    def compileStatements(self):
        tag = "statements"
        self.genBeginBranch(tag)

        # Must be one of: let, if, while, do, return.
        while (not (self.lexer.tokenType() == TokenType.SYMBOL
                    and self.lexer.symbol() == "}")):
            assert self.lexer.tokenType() == TokenType.KEYWORD
            keyword = self.lexer.keyWord()
            if (keyword == "let"):
                self.compileLet()
            elif (keyword == "if"):
                self.compileIf()
            elif (keyword == "while"):
                self.compileWhile()
            elif (keyword == "do"):
                self.compileDo()
            elif (keyword == "return"):
                self.compileReturn()
            else:
                assert False, "Syntax error."

        # Note that we do not emit the closing "}" here - that is
        # handled by compileSubroutine().  We just use it to know when
        # we are done.
        self.genEndBranch(tag)

    # subroutineName '(' expressionlist ')'
    # | (className | varName) '.' subroutineName '(' expressionList ')'
    # THIS DOES NOT CREATE ITS OWN BRANCH, it is a helper function.
    def _emitSubroutineCall(self, includeTarget):
        if (includeTarget):
            self.validate(TokenType.IDENTIFIER, "")
            self.genLeaf()

        if (self.lexer.tokenType() == TokenType.SYMBOL):
            if (self.lexer.symbol() == "("):
                self.genLeaf()
                self.compileExpressionList()
                self.validate(TokenType.SYMBOL, ")")
                self.genLeaf()
            else:
                self.validate(TokenType.SYMBOL, ".")
                self.genLeaf()
                self.validate(TokenType.IDENTIFIER, "")
                self.genLeaf()
                self.validate(TokenType.SYMBOL, "(")
                self.genLeaf()
                self.compileExpressionList()
                self.validate(TokenType.SYMBOL, ")")
                self.genLeaf()
        else:
            assert False, "Syntax error"



    # 'do' subroutineCall ';'
    def compileDo(self):
        tag = "doStatement"
        self.genBeginBranch(tag)

        # 'do'
        self.validate(TokenType.KEYWORD, "do")
        self.genLeaf()

        # subroutineCall.  Note that this does not get its own branch!
        self._emitSubroutineCall(True)

        # ';'
        self.validate(TokenType.SYMBOL, ";")
        self.genLeaf()

        self.genEndBranch(tag)

    # 'let' varName ('[' expression ']')? '=' expression ';'
    def compileLet(self):
        tag = "letStatement"
        self.genBeginBranch(tag)

        # 'let'
        self.validate(TokenType.KEYWORD, "let")
        self.genLeaf()

        # varName
        self.validate(TokenType.IDENTIFIER, "")
        self.genLeaf()

        # 0 or 1 ('[' expresion ']')
        if (self.lexer.tokenType() == TokenType.SYMBOL
            and self.lexer.symbol() == "["):
            # '['
            self.genLeaf()
            self.compileExpression()
            self.validate(TokenType.SYMBOL, "]")
            self.genLeaf()

        # '='
        self.validate(TokenType.SYMBOL, "=")
        self.genLeaf()

        # expression
        self.compileExpression()

        # ';'
        self.validate(TokenType.SYMBOL, ";")
        self.genLeaf()

        self.genEndBranch(tag)

    # 'while' '(' expression ')' '{' statements '}'
    def compileWhile(self):
        tag = "whileStatement"
        self.genBeginBranch(tag)

        # 'while'
        self.validate(TokenType.KEYWORD, "while")
        self.genLeaf()

        # '('
        self.validate(TokenType.SYMBOL, "(")
        self.genLeaf()

        # expression
        self.compileExpression()

        # ')'
        self.validate(TokenType.SYMBOL, ")")
        self.genLeaf()

        # '{'
        self.validate(TokenType.SYMBOL, "{")
        self.genLeaf()

        # statements
        self.compileStatements()

        # '}'
        self.validate(TokenType.SYMBOL, "}")
        self.genLeaf()

        self.genEndBranch(tag)

    # 'return' expression? ';'
    def compileReturn(self):
        tag = "returnStatement"
        self.genBeginBranch(tag)

        # 'return'
        self.validate(TokenType.KEYWORD, "return")
        self.genLeaf()

        # 0 or 1 expressions
        if (not (self.lexer.tokenType() == TokenType.SYMBOL
                 and self.lexer.symbol() == ";")):
            self.compileExpression()

        self.validate(TokenType.SYMBOL, ";")
        self.genLeaf()

        self.genEndBranch(tag)

    # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    def compileIf(self):
        tag = "ifStatement"
        self.genBeginBranch(tag)

        # 'if'
        self.validate(TokenType.KEYWORD, "if")
        self.genLeaf()

        # '('
        self.validate(TokenType.SYMBOL, "(")
        self.genLeaf()

        # expression
        self.compileExpression()

        # ')'
        self.validate(TokenType.SYMBOL, ")")
        self.genLeaf()

        # '{'
        self.validate(TokenType.SYMBOL, "{")
        self.genLeaf()

        self.compileStatements()

        # '}'
        self.validate(TokenType.SYMBOL, "}")
        self.genLeaf()

        # 0 or 1 ('else' '{' statements '}')

        if (self.lexer.tokenType() == TokenType.KEYWORD
            and self.lexer.keyWord() == "else"):
            # 'else'
            self.genLeaf()

            # '{'
            self.validate(TokenType.SYMBOL, "{")
            self.genLeaf()

            self.compileStatements()

            # '}'
            self.validate(TokenType.SYMBOL, "}")
            self.genLeaf()

        self.genEndBranch(tag)

    # term (op term)*
    def compileExpression(self):
        tag = "expression"
        self.genBeginBranch(tag)

        self.compileTerm()
        while (self.lexer.tokenType() == TokenType.SYMBOL
            and self.lexer.symbol() in self.operators):
            self.genLeaf()
            self.compileTerm()

        self.genEndBranch(tag)

    # integerConstant | stringConstant | keywordConstant |
    # varName | varName '[' expresion '] | subroutineCall |
    # '( expression ')' | unaryOp term
    #
    # From the book:
    # "if the current token is an identifier, the routine
    # must distinguish between a variable, an array entry,
    # and a subroutine call. A single lookahead token,
    # which may be one of "[", "(", or "." suffices to
    # distinguish between the three possibilities.  Any other
    # token is not part of this term and should not be
    # advanced over."
    def compileTerm(self):
        tag = "term"
        self.genBeginBranch(tag)

        if (self.lexer.tokenType() == TokenType.INT_CONST
            or self.lexer.tokenType() == TokenType.STRING_CONST
            or self.lexer.tokenType() == TokenType.KEYWORD):
            self.genLeaf()
        elif (self.lexer.tokenType() == TokenType.IDENTIFIER):
            self.genLeaf()
            if (self.lexer.tokenType() == TokenType.SYMBOL):
                if (self.lexer.symbol() == "["):
                    # Array case.
                    self.genLeaf()
                    self.compileExpression()
                    self.validate(TokenType.SYMBOL, "]")
                    self.genLeaf()
                elif (self.lexer.symbol() == "("
                      or self.lexer.symbol() == "."):
                    self._emitSubroutineCall(False)
        elif (self.lexer.tokenType() == TokenType.SYMBOL):
            if (self.lexer.symbol() == "("):
                self.genLeaf()
                self.compileExpression()
                self.validate(TokenType.SYMBOL, ")")
                self.genLeaf()
            elif (self.lexer.symbol() == "-"
                  or self.lexer.symbol() == "~"):
                self.genLeaf()
                self.compileTerm()
        else:
            assert False, "Syntax error."
        # Handle unary op

        self.genEndBranch(tag)

    # (expression (',' expression)* )?
    def compileExpressionList(self):
        tag = "expressionList"
        self.genBeginBranch(tag)

        # 0 or 1
        if (not (self.lexer.tokenType() == TokenType.SYMBOL
                 and self.lexer.symbol() == ")")):
            self.compileExpression()
            # 0 or more
            while (self.lexer.tokenType() == TokenType.SYMBOL
                   and self.lexer.symbol() == ","):
                self.genLeaf()
                self.compileExpression()

        self.genEndBranch(tag)
