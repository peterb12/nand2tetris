import os
import textwrap
from vm_types import CmdType
from parser import Parser


class CodeWriter:
    ''' Generates assembly for given input.'''

    labelIndex = 0

    def __init__(self, architecture, dirName, asmName):
        self.architecture = architecture
        self.asmName = asmName + ".asm"
        self.f = open(dirName + "/" + self.asmName, 'w')

        script_dir = os.path.dirname(__file__)
        arch_dir = os.path.join(script_dir, "arch/" + architecture + "/")

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
        template = open(arch_dir + "conditional.txt","r")
        self.conditional = template.read()
        template.close()
        template = open(arch_dir + "arithOneOp.txt","r")
        self.arithOneOp = template.read()
        template.close()
        template = open(arch_dir + "arithTwoOp.txt","r")
        self.arithTwoOp = template.read()
        template.close()
        template = open(arch_dir + "push.txt","r")
        self.pushOp = template.read()
        template.close()
        template = open(arch_dir + "pop.txt", "r")
        self.popOp = template.read()
        template.close()
        
    def _uniqueLabel(self):
        label = 'vm$lbl' + str(self.labelIndex)
        self.labelIndex += 1
        return label

    '''This gets reused in a few places, so I parameterized it.'''
    def _condCode(self, conditional):
        trueLabel = self._uniqueLabel()
        outLabel  = self._uniqueLabel()
        condString = self.conditional.format(truelabel=trueLabel, outlabel=outLabel, conditional=conditional)
        self.f.write(condString)
        
    def setFileName(self, vmname):
        self.vmname = vmname
        
    def writeArithmetic(self, command):
        self.f.write("// " + command + "\n")

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
            self._condCode("JEQ")
        elif command == "gt":
            self._condCode("JGT")
        elif command == "lt":
            self._condCode("JLT")
        else:
            assert(False) 

    def writePushPop(self, command, segment, index, cmdName):
        self.f.write('// ' + cmdName + ' ' + segment + ' ' + index + "\n")
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
                extra = extra + ('D=M')

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
                    extra = extra + ('D=A+D')
                else:
                    extra = extra + ('D=M+D')
                self.f.write(self.popOp.format(address = index, extra = extra))

    def close(self):
        self.f.close()
