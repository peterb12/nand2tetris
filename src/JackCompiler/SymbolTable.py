from jc_types import Scope

class SymbolTable:

    def __init(self):
        self.classTable = {}
        self.subroutineTable = {}
        # Here's where I create a cache coherency bug for myself.
        # But even though I'm not worried about efficiency, the
        # thought of iterating the entire dictionary every time
        # I need to count values is too much to bear.  Fortunately,
        # We never remove things from the symbols tables.  So I'm
        # going ahead and tracking these individually.
        self.metadata = { Scope.STATIC : 0,
                          Scope.FIELD : 0,
                          Scope.ARG : 0,
                          Scope.VAR = 0}

    # Starts a new subroutine scope.
    def startSubroutine(self):
        self.subroutineTable = {}

    # Defines a new identifier of given name, type, and kind,
    # and assigns index numbers
    def define(idName, idType, idKind):
        if (idKind == Scope.STATIC or idKind == Scope.FIELD):
            self.classTable[idName] = (idType, idKind, varCount(idKind))
            self.metadata[idKind] = self.metadata[idKind] + 1
        elif (idKind == Scope.ARG or idKind == Scope.VAR):
            self.subroutineTable[idName] = (idType, idKind, varCount(idKind))
            self.metadata[idKind] = self.metadata[idKind] + 1
        else:
            assert False, "Unexpected variable kind in symbol table."

    # varCount -> Int
    # Returns number of variables of the given kind
    # defined in the current scope.
    def varCount(idKind):
        return self.metadata[idKind]

    # Given a variable return the tuple, if found, from the
    # appropriate scope.
    def __lookup(idName):
        # Check the subroutine table
        if (idName in self.subroutineTable):
            (outType, outKind, outCount) = self.subroutineTable[idName]
        # Fall back to the class table.
        elif (idName in self.classTable):
            (outType, outKind, outCount) = self.classTable[idName]
        # Not found.  Create the appropriate response.
        else:
            (outType, outKind, outCount) = ("", Scope.NONE, -1)

        return (outType, outKind, outIndex)

    # Given a variable, return its kind in the current scope.
    # If name is unknown, return NONE.
    def kindOf(idName):
        (_, outKind, _) = __lookup(idName)
        return outKind

    # Given a variable, return its type in the current scope.
    def typeOf(idName):
        (outType, _, _) = __lookup(idName)
        return outType

    # Given a variable, return its assigned index
    def indexOf(idName):
        (_, _, outIndex) = __lookup(idName)
        return outIndex
