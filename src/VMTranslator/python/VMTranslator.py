import sys
import os
import re
from vm_types import CmdType
from parser import Parser
from codewriter import CodeWriter

if len(sys.argv) > 1:
    '''For testing.'''
    '''pathname =  "/Users/pberger/Dropbox/Project/Programming/nand2tetris/projects/07/MemoryAccess/StaticTest/StaticTest.vm"'''
    pathname = sys.argv[1]
    vmfiles = []

    (dirName, filename) = os.path.split(pathname)
    if os.path.isdir(pathname):
        asmName = os.path.basename(os.path.normpath(pathname))
        for file in os.listdir(pathname):
            if file.endswith(".vm"):
                vmfiles.append(dirName + "/" + file)
    else:
        (shortname, extension) = os.path.splitext(filename)
        asmName = shortname
        vmfiles.append(pathname)

    coder  = CodeWriter("hack", dirName, asmName)
    for currFile in vmfiles:
        (currName, filename) = os.path.split(currFile)
        (shortname, extension) = os.path.splitext(filename)
        coder.setFileName(shortname)
        parser = Parser(currFile)
        while parser.hasMoreCommands():
            if parser.commandType() == CmdType.C_ARITHMETIC:
                coder.writeArithmetic(parser.arg1())
            else:
                coder.writePushPop(parser.commandType(), parser.arg1(), parser.arg2(), parser.commandName())
            parser.advance()

    coder.close()

else:
    print("Usage: " + sys.argv[0] + " [file.vm or directory]")
