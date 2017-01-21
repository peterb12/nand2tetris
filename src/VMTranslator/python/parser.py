from vm_types import CmdType

class Parser:
    ''' Reads in a file and breaks it up into pieces. '''

    def __init__(self, fname):
        self.currentFile = open(fname, encoding='utf-8')
        self.cmd  = ""
        self._arg1 = ""
        self._arg2 = ""
        self.advance()

    def p_deconstructLine(self):
        ''' Clear previous line. '''
        self.cmd  = ""
        self._arg1 = ""
        self._arg2 = ""
        commentless = self.currentLine.strip().split('//')
        squeezed = list(filter(bool, commentless[0].split(' ')))
        if len(squeezed) > 0:
            self.cmd = squeezed[0]
        if len(squeezed) > 1:
            self._arg1 = squeezed[1]
            self._arg2 = squeezed[2]
        
    def hasMoreCommands(self):
        return self.currentLine != ""

    def advance(self):
        finished = False
        while not finished:
            self.currentLine = self.currentFile.readline()
            if not self.currentLine:
                finished = True
                break
            self.p_deconstructLine()
            if self.cmd != "":
                finished = True

    def commandType(self):
        if self.cmd == "push":
            return CmdType.C_PUSH
        elif self.cmd == "pop":
            return CmdType.C_POP
        else:
            return CmdType.C_ARITHMETIC

    ''' For the comments. '''
    def commandName(self):
        return self.cmd
    
    def arg1(self):
        if self.commandType() == CmdType.C_ARITHMETIC:
            return self.cmd
        else:
            return self._arg1

    def arg2(self):
        return self._arg2

