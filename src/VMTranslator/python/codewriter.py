import os
import textwrap
from vm_types import CmdType
from parser import Parser


class CodeWriter:
    ''' Generates assembly for given input.'''

    labelIndex = 0
    userLabelDict = {}

    def __createOpTemplate(self, architecture, templateFile):
        script_dir = os.path.dirname(__file__)
        arch_dir = os.path.join(script_dir, "arch/" + architecture + "/")
        template = open(arch_dir + templateFile, "r")
        opTemplate = template.read()
        template.close()
        return opTemplate

    def __init__(self, architecture, dirName, asmName):
        self.architecture = architecture
        self.asmName = asmName + ".asm"
        self.f = open(dirName + "/" + self.asmName, "w")

        self.segmentTable = { "local"    : "LCL",
                              "argument" : "ARG",
                              "this"     : "THIS",
                              "that"     : "THAT",
                              "pointer"  : "THIS",
                              "temp"     : "R5"}

        ''' For ease of reading (and also for ease of porting this
            to other CPUs in the future) most (though not all) of the
            assembly language is located in templated text files.
            It's unclear that this is all that useful given the other
            assumptions baked into this code (e.g. number of registers
            and segments) but a programmer can dream.'''
        self.comparison = self.__createOpTemplate(architecture, "comparison.txt")
        self.arithOneOp = self.__createOpTemplate(architecture, "arithOneOp.txt")
        self.arithTwoOp = self.__createOpTemplate(architecture, "arithTwoOp.txt")
        self.pushOp     = self.__createOpTemplate(architecture, "push.txt")
        self.popOp      = self.__createOpTemplate(architecture, "pop.txt")
        self.gotoOp     = self.__createOpTemplate(architecture, "goto.txt")
        self.ifGotoOp   = self.__createOpTemplate(architecture, "ifgoto.txt")
        self.functionOp = self.__createOpTemplate(architecture, "function.txt")
        self.callOp     = self.__createOpTemplate(architecture, "call.txt")
        self.returnOp   = self.__createOpTemplate(architecture, "return.txt")
        
    def _uniqueLabel(self):
        label = 'vm$' + str(self.labelIndex)
        self.labelIndex += 1
        return label

    '''This gets reused in a few places, so I parameterized it.'''
    def _compCode(self, comparison):
        trueLabel = self._uniqueLabel()
        outLabel  = self._uniqueLabel()
        condString = self.comparison.format(truelabel=trueLabel, outlabel=outLabel, comparison=comparison)
        self.f.write(compString)
        
    def setFileName(self, vmname):
        self.vmname = vmname

    def userLabel(self, label):
        if label in self.userLabelDict:
            cachedLabel = self.userLabelDict[label]
        else:
            cachedLabel = self._uniqueLabel() + label
            self.userLabelDict[label] = cachedLabel
        return cachedLabel

    def writeComment(self, cmdName, cmdType, arg1, arg2):
        self.f.write("// " + cmdName)
        if cmdType != CmdType.C_ARITHMETIC:
            self.f.write(" " + arg1)
        if cmdType == CmdType.C_PUSH or cmdType == CmdType.C_POP:
            self.f.write(" " + arg2)
        self.f.write("\n")
                
    '''TODO: Test.'''
    ''' "The scope of the label is the function in which it is defined" '''
    def writeLabel(self, label):
        self.f.write("(" + self.userLabel(self.currFunction + "." + label) + ")\n")

    ''' "The jump destination must be located in the same function'''
    ''' TODO: Test.'''                
    def writeGoto(self, destination):
        self.f.write(self.gotoOp.format(dest=self.userLabel(self.currFunction + "." + destination)))

    ''' TODO: Make function-local.'''
    def writeIfGoto(self, destination):
        self.f.write(self.ifGotoOp.format(dest=self.userLabel(self.currFunction + "." + destination)))

    def writeFunction(self, name, numLocals):
        self.currFunction = name
        loopLabel = self._uniqueLabel()
        outLabel = self._uniqueLabel()
        entryPoint = self.userLabel("fn." + name)
        self.f.write(self.functionOp.format(entry=entryPoint, nLocals=numLocals, loop=loopLabel, out=outLabel))

    def writeCall(self, name, numArgs):
        entryPoint = self.userLabel("fn." + name)
        exitPoint = self._uniqueLabel()

        ''' Push return address.'''
        self.writePushPop(CmdType.C_PUSH, "constant", exitPoint)
        ''' Save caller register state '''
        self.writePushPop(CmdType.C_PUSH, "constant", self.segmentTable["local"])
        self.writePushPop(CmdType.C_PUSH, "constant", self.segmentTable["argument"])
        self.writePushPop(CmdType.C_PUSH, "constant", self.segmentTable["this"])
        self.writePushPop(CmdType.C_PUSH, "constant", self.segmentTable["that"])
        ''' Configure the rest of the stack frame, notably repositioning LCL. '''
        self.f.write(self.callOp.format(nArgs=numArgs))
        ''' Jump in to the function '''
        self.f.write(self.gotoOp.format(dest=entryPoint))
        ''' Provide the label for 'return' to use. '''
        self.writeLabel(exitPoint)
            
    def writeReturn(self):
        self.writePushPop(CmdType.C_POP, "argument", 0)
        self.f.write(self.returnOp)
        
    def writeArithmetic(self, command):
        if command == "add":
            self.f.write(self.arithTwoOp.format(operation="M=D+M"))
        elif command == "sub":
            self.f.write(self.arithTwoOp.format(operation="M=M-D"))
        elif command == "and":
            self.f.write(self.arithTwoOp.format(operation="M=D&M"))            
        elif command == "or":
            self.f.write(self.arithTwoOp.format(operation="M=D|M"))            
        elif command == "not":
            self.f.write(self.arithOneOp.format(operation="M=!M"))
        elif command == "neg":
            self.f.write(self.arithOneOp.format(operation="M=-M"))
        elif command == "eq":
            self._compCode("JEQ")
        elif command == "gt":
            self._compCode("JGT")
        elif command == "lt":
            self._compCode("JLT")
        else:
            assert(False) 

    def writePushPop(self, command, segment, index):
        if command == CmdType.C_PUSH:
            if segment == "constant":
                self.f.write(self.pushOp.format(address=index,refmode="D=A",extra=""))
            elif segment == "static":
                addr = self.vmname + '.' + index
                self.f.write(self.pushOp.format(address=addr,refmode="D=M",extra=""))
            else:
                ''' Sadly, this one is complicated. Note that 'extra' MUST
                    begin with a newline. '''
                extra = "\n@" + self.segmentTable[segment] + "\n"
                if segment == "temp" or segment == "pointer":
                    extra = extra + ("A=A+D\n")
                else:
                    extra = extra + ("A=M+D\n")
                extra = extra + ("D=M")

                self.f.write(self.pushOp.format(address=index,refmode="D=A",extra=extra))
        else:
            assert command == CmdType.C_POP
            if segment == "static":
                addr = self.vmname + '.' + index
                self.f.write(self.popOp.format(address=addr,extra=""))
            else:
                ''' Note that "extra" must start with a newline. '''
                extra = "\n@" + self.segmentTable[segment] + "\n"
                if segment == "temp" or segment == "pointer":
                    extra = extra + ("D=A+D")
                else:
                    extra = extra + ("D=M+D")
                self.f.write(self.popOp.format(address = index, extra = extra))

    def close(self):
        self.f.close()
