import sys
import os
from JackTokenizer import JackTokenizer
from jc_types import Scope
from jc_types import TokenType
from SymbolTable import SymbolTable
from VMWriter import VMWriter

class CompilationEngine:

    operators = ["+", "-", "*", "/", "&", "&amp;", "|", "<", "&lt;", "&gt;", ">", "="]
    unaryOperators = ["-", "~"]

    debugMode = False

    # Constructor
    def __init__(self, dirName, filename):
        if (self.debugMode == True):
            print("Compilation engine initialized.")
        (currName, filepart) = os.path.split(filename)
        (shortName, extension) = os.path.splitext(filepart)
        vmName = shortName + ".vm"

        self.lexer = JackTokenizer(filename)
        self.lexer.advance()
        self.symbolTable = SymbolTable()
        self.vmwriter = VMWriter(dirName, vmName)
        self.treeLevel = 0
        self.labelIndex = 0
        if (self.debugMode == True):
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

    def createLabel(self):
        label = "filename$" + str(self.labelIndex)
        self.labelIndex = self.labelIndex + 1
        return label

    # It's called genLeaf(), but the most important thing to note
    # about this is that it advances the lexer!  The corollary to this
    # is that if you are going to generate VM code based on this
    # leaf, you must get whatever you need from the leaf BEFORE
    # you call genLeaf.
    def genLeaf(self, validateType="", validateAtom="", attributes=""):
        if (self.debugMode == True):
            if (validateType != ""):
                self.validate(validateType, validateAtom)
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
        self.genLeaf(TokenType.IDENTIFIER)

        # '{'
        self.genLeaf(TokenType.SYMBOL, "{")

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

        self.genLeaf(TokenType.SYMBOL, "}")

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
        varName = self.lexer.identifier()
        # Now we have a complete variable. Add it to the symbol
        # table.
        self.symbolTable.define(varName, varType, varKind)
        attributes = ""
        if (self.debugMode == True):
            attributes = ' name="' + varName + '" type="' + self.symbolTable.typeOf(varName) + '" kind="'  + str(self.symbolTable.kindOf(varName)) + '" ref="' + str(self.symbolTable.indexOf(varName)) + '"'

        self.genLeaf(TokenType.IDENTIFIER, "", attributes)


        #  Zero or more ("," varName)
        while (self.lexer.tokenType() == TokenType.SYMBOL
               and (self.lexer.symbol() == ",")):
            self.genLeaf() # ","
            varName = self.lexer.identifier()
            self.symbolTable.define(varName, varType, varKind)
            if (self.debugMode == True):
                attributes = ' name="' + varName + '" type="' + self.symbolTable.typeOf(varName) + '" kind="'  + str(self.symbolTable.kindOf(varName)) + '" ref="' + str(self.symbolTable.indexOf(varName)) + '"'

            self.genLeaf(TokenType.IDENTIFIER, "", attributes) # varName

        # ";"
        self.genLeaf(TokenType.SYMBOL, ";")

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
        self.genLeaf(TokenType.IDENTIFIER, "")

        # '('
        self.genLeaf(TokenType.SYMBOL, "(")

        # Recurse: parameterList
        self.compileParameterList()

        # ')'
        self.genLeaf(TokenType.SYMBOL, ")")

        # subroutineBody
        # wrapped in branch, then
        # '{' varDec* statements '}'
        bodyTag = "subroutineBody"
        self.genBeginBranch(bodyTag)

        # '{'
        self.genLeaf(TokenType.SYMBOL, "{")

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
                varType = self._extractType()
                self.genLeaf() # type

                assert self.lexer.tokenType() == TokenType.IDENTIFIER, "Syntax error."
                varName = self.lexer.identifier()
                self.symbolTable.define(varName, varType, Scope.ARG)
                # This debugging boilerplate is a little distracting.
                # Would be great to refactor it so it's hidden
                attributes = ""
                if (self.debugMode == True):
                    attributes = ' name="' + varName + '" type="' + self.symbolTable.typeOf(varName) + '" kind=arg"'  + '" ref="' + str(self.symbolTable.indexOf(varName)) + '"'
                self.genLeaf("", "", attributes) # varName

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
            self.genLeaf(TokenType.IDENTIFIER)

        if (self.lexer.tokenType() == TokenType.SYMBOL):
            if (self.lexer.symbol() == "("):
                self.genLeaf()
                self.compileExpressionList()
                self.genLeaf(TokenType.SYMBOL, ")")
            else:
                self.genLeaf(TokenType.SYMBOL, ".")
                self.genLeaf(TokenType.IDENTIFIER)
                self.genLeaf(TokenType.SYMBOL, "(")
                self.compileExpressionList()
                self.genLeaf(TokenType.SYMBOL, ")")
        else:
            assert False, "Syntax error"



    # 'do' subroutineCall ';'
    def compileDo(self):
        tag = "doStatement"
        self.genBeginBranch(tag)

        # 'do'
        self.genLeaf(TokenType.KEYWORD, "do")

        # subroutineCall.  Note that this does not get its own branch!
        self._emitSubroutineCall(True)

        # ';'
        self.genLeaf(TokenType.SYMBOL, ";")

        self.genEndBranch(tag)

    # 'let' varName ('[' expression ']')? '=' expression ';'
    def compileLet(self):
        tag = "letStatement"
        self.genBeginBranch(tag)

        # 'let'
        self.genLeaf(TokenType.KEYWORD, "let")

        # varName
        # Look up the variable in the symbol table.  Failure to
        # find it is a compiler error, since Jack requires declaration.
        lvar = self.lexer.identifier()
        lkind = Scope.stringForScope(self.symbolTable.kindOf(lvar))
        lidx = self.symbolTable.indexOf(lvar)
        loffset = 0
        self.genLeaf(TokenType.IDENTIFIER, "")

        # 0 or 1 ('[' expresion ']')
        if (self.lexer.tokenType() == TokenType.SYMBOL
            and self.lexer.symbol() == "["):
            # '['
            self.genLeaf()
            self.compileExpression()

            # TODO: We are indexing into an array.  Need to figure this out.
            self.genLeaf(TokenType.SYMBOL, "]")

        # '='
        self.genLeaf(TokenType.SYMBOL, "=")

        # expression
        self.compileExpression()

        # ';'
        self.genLeaf(TokenType.SYMBOL, ";")

        # Complete the assignment by popping the stack.
        self.vmwriter.writePop(lkind, str(lidx))

        self.genEndBranch(tag)

    # 'while' '(' expression ')' '{' statements '}'
    def compileWhile(self):
        tag = "whileStatement"
        self.genBeginBranch(tag)

        # The head of our loop.
        whileLabel = self.createLabel()
        self.vmwriter.writeLabel(whileLabel)
        # 'while'
        self.genLeaf(TokenType.KEYWORD, "while")

        # '('
        self.genLeaf(TokenType.SYMBOL, "(")

        # expression
        self.compileExpression()
        # Negate the expression on the stack, and jump if true
        self.vmwriter.writeArithmetic("not")
        outLabel = self.createLabel()
        self.vmwriter.writeIf(outLabel)

        # ')'
        self.genLeaf(TokenType.SYMBOL, ")")

        # '{'
        self.genLeaf(TokenType.SYMBOL, "{")

        # statements
        self.compileStatements()

        # '}'
        self.genLeaf(TokenType.SYMBOL, "}")

        # Loop has run.  Jump back to the condition and do it again.
        self.vmwriter.writeGoto(whileLabel)
        # And place a target for our exit.
        self.vmwriter.writeLabel(outLabel)
        self.genEndBranch(tag)

    # 'return' expression? ';'
    def compileReturn(self):
        tag = "returnStatement"
        self.genBeginBranch(tag)

        # 'return'
        self.genLeaf(TokenType.KEYWORD, "return")

        # 0 or 1 expressions
        if (not (self.lexer.tokenType() == TokenType.SYMBOL
                 and self.lexer.symbol() == ";")):
            self.compileExpression()
            # compileExpression() will leave the result pushed on the stack.

        self.genLeaf(TokenType.SYMBOL, ";")

        # Process the return.
        self.vmwriter.writeReturn()

        self.genEndBranch(tag)
        # Actually emit the VM code.
        self.vmwriter.writeReturn()

    # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    def compileIf(self):
        tag = "ifStatement"
        self.genBeginBranch(tag)

        # 'if'
        self.genLeaf(TokenType.KEYWORD, "if")

        # '('
        self.genLeaf(TokenType.SYMBOL, "(")

        # expression
        self.compileExpression()
        # If the stack is now true, we should do nothing, aka
        # not jump - we would fallthrough.  Therefore, we want
        # to negate it.
        self.vmwriter.writeArithmetic("not")

        # If true is on the stack at this point, we jump out.
        elseLabel = self.createLabel()
        self.vmwriter.writeIf(elseLabel)

        # ')'
        self.genLeaf(TokenType.SYMBOL, ")")

        # '{'
        self.genLeaf(TokenType.SYMBOL, "{")

        self.compileStatements()

        # '}'
        self.genLeaf(TokenType.SYMBOL, "}")

        # 0 or 1 ('else' '{' statements '}')

        # If we put our jump target here, it is correct regardless
        # of whether or not there is an else clause.
        self.vmwriter.writeLabel(elseLabel)
        if (self.lexer.tokenType() == TokenType.KEYWORD
            and self.lexer.keyWord() == "else"):
            # 'else'
            self.genLeaf()

            # '{'
            self.genLeaf(TokenType.SYMBOL, "{")

            self.compileStatements()

            # '}'
            self.genLeaf(TokenType.SYMBOL, "}")

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

            if (self.lexer.tokenType() == TokenType.KEYWORD):
                # keywordConstant: true, false, null, or this
                print("Not implemented.")
            elif (self.lexer.tokenType() == TokenType.INT_CONST):
                # integerConstant
                self.vmwriter.writePush("constant", self.lexer.integer())
        elif (self.lexer.tokenType() == TokenType.IDENTIFIER):
            self.genLeaf()
            if (self.lexer.tokenType() == TokenType.SYMBOL):
                if (self.lexer.symbol() == "["):
                    # Array case.
                    self.genLeaf()
                    self.compileExpression()
                    self.genLeaf(TokenType.SYMBOL, "]")
                elif (self.lexer.symbol() == "("
                      or self.lexer.symbol() == "."):
                    self._emitSubroutineCall(False)
        elif (self.lexer.tokenType() == TokenType.SYMBOL):
            if (self.lexer.symbol() == "("):
                self.genLeaf()
                self.compileExpression()
                self.genLeaf(TokenType.SYMBOL, ")")
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
