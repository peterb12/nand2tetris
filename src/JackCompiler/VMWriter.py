from jc_types import Scope

class VMWriter:
    arithmeticOperations = ["add", "sub", "and", "or", "not", "neg", "eq", "gt", "lt"]

    scopeTable = { Scope.STATIC : "static",
                   Scope.FIELD : "dunno?",
                   Scope.ARG : "argument",
                   Scope.VAR : "local" }

    def __init__(self, dirName, fname):
        self.f = open(dirName + "/" + fname, "w")

    # For convenience in debugging.
    def _emit(self, string):
        print(string)

    def writePush(self, segment, index):
        self._emit("push " + segment + " " + index)

    def writePop(self, segment, index):
        self._emit("pop " + segment + " " + index)

    def writeArithmetic(self, command):
        if (command in self.arithmeticOperations):
            self._emit(command)
        else:
            assert False, "Internal compiler error."

    def writeLabel(self, label):
        self._emit("label " + label)

    def writeGoto(self, label):
        self._emit("goto " + label)

    def writeIf(self, label):
        self._emit("if-goto " + label)

    def writeCall(self, name, nArgs):
        print("Not implemented")

    def writeFunction(self, name, nLocals):
        print("Not implemented")

    def writeReturn(self):
        self._emit("return")

    def close(self):
        self.f.close()
