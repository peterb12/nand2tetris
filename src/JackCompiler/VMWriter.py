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
        self.f.write(string + "\n")

    def writePush(self, segment, index):
        self._emit("push " + segment + " " + str(index))

    def writePop(self, segment, index):
        self._emit("pop " + segment + " " + str(index))

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
        self._emit("call " + name + " " + str(nArgs))

    def writeFunction(self, name, nLocals):
        self._emit("function " + name + " " + str(nLocals))

    def writeReturn(self):
        self._emit("return")

    def close(self):
        self.f.close()
