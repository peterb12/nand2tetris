
class VMWriter:

    def __init__(self, dirName, fname):
        self.f = open(dirName + "/" + fname, "w")

    # For convenience in debugging.
    def _emit(self, string):
        print(string)

    def writePush(self, segment, index):
        self._emit("push " + segment + " " + index)

    def writePop(self, segment, index):
        print("Not implemented")

    def writeArithmetic(self, command):
        print("Not implemented")

    def writeLabel(self, label):
        print("Not implemented")

    def writeGoto(self, label):
        print("Not implemented")

    def writeIf(self, label):
        print("Not implemented")

    def writeCall(self, name, nArgs):
        print("Not implemented")

    def writeFunction(self, name, nLocals):
        print("Not implemented")

    def writeReturn(self):
        self._emit("return")

    def close(self):
        self.f.close()
