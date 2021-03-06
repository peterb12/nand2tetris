import sys
import os
import re
from vm_types import CmdType
from parser import Parser
from codewriter import CodeWriter

if len(sys.argv) > 1:
    pathname = sys.argv[1]
    vmfiles = []

    ''' "Generate startup code when translating a directory. Do not
        generate startup code when translating a single file. Translation
        of a single file will be used for the basic tests."'''
    ''' Make sure the pathname is canonical. '''
    if os.path.isdir(pathname):
        pathname = os.path.join(pathname,"")
    (dirName, filename) = os.path.split(pathname)
    if os.path.isdir(pathname):
        asmName = os.path.basename(os.path.normpath(pathname))
        for file in os.listdir(pathname):
            if file.endswith(".vm"):
                vmfiles.append(dirName + "/" + file)
        emitStartupCode = True
    else:
        if dirName == "":
            dirName = "."
        (shortname, extension) = os.path.splitext(filename)
        asmName = shortname
        vmfiles.append(pathname)
        emitStartupCode = False

    coder  = CodeWriter("hack", dirName, asmName, emitStartupCode)
    for currFile in vmfiles:
        (currName, filename) = os.path.split(currFile)
        (shortname, extension) = os.path.splitext(filename)
        coder.setFileName(shortname)
        parser = Parser(currFile)
        while parser.hasMoreCommands():
            coder.writeComment(parser.commandName(), parser.commandType(), parser.arg1(), parser.arg2())

            if parser.commandType() == CmdType.C_ARITHMETIC:
                coder.writeArithmetic(parser.arg1())
            elif parser.commandType() == CmdType.C_LABEL:
                coder.writeLabel(parser.arg1())
            elif parser.commandType() == CmdType.C_GOTO:
                coder.writeGoto(parser.arg1())
            elif parser.commandType() == CmdType.C_IF:
                coder.writeIfGoto(parser.arg1())
            elif parser.commandType() == CmdType.C_FUNCTION:
                coder.writeFunction(parser.arg1(), parser.arg2())
            elif parser.commandType() == CmdType.C_CALL:
                coder.writeCall(parser.arg1(), parser.arg2())
            elif parser.commandType() == CmdType.C_RETURN:
                coder.writeReturn()
            else:
                coder.writePushPop(parser.commandType(), parser.arg1(), parser.arg2())
            parser.advance()

    coder.writeExitLabel()
    coder.close()

else:
    print("Usage: " + sys.argv[0] + " [file.vm or directory]")
