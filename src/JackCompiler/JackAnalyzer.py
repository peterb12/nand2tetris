import sys
import os
from CompilationEngine import CompilationEngine

if len(sys.argv) > 1:
    pathname = sys.argv[1]
    jackfiles = []

    ''' Make sure the pathname is canonical. '''
    if os.path.isdir(pathname):
        pathname = os.path.join(pathname,"")
    (dirName, filename) = os.path.split(pathname)
    if os.path.isdir(pathname):
        for fn in os.listdir(pathname):
            if fn.endswith(".jack"):
                jackfiles.append(dirName + "/" + fn)
    else:
        if dirName == "":
            dirName = "."
        (shortname, extension) = os.path.splitext(filename)
        jackfiles.append(pathname)

    for currFile in jackfiles:
        compiler = CompilationEngine(dirName, currFile)
        compiler.compileClass()
