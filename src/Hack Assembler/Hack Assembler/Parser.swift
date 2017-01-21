//
//  Parser.swift
//  Hack Assembler
//
//  Created by peterb on 12/28/16.
//  Copyright © 2016 peterb. All rights reserved.
//

import Foundation

// The overall symbol-less assembler program can now be implemented as follows. First, the program
// opens an output file named Prog.hack. Next, the program marches through the lines (assembly instructions)
// in the supplied Prog.asm file. For each C-instruction, the program concatenates the translated binary
// codes of the instruction fields into a single 16-bit word. Next, the program writes this word into the
// Prog.hack file. For each A-instruction of type @Xxx, the program translates the decimal constant
// returned by the parser into its binary representation and writes the resulting 16-bit word into the
// Prog.hack file.

// "// Computes R0 = 2 + 3  (R0 refers to RAM[0])
//
//@2
//D=A
//@3
//D=D+A
//@0
//M=D"

extension String {
    var stringByRemovingWhitespaces: String {
        let components = self.components(separatedBy: .whitespaces)
        return components.joined(separator: "")
    }
}

class Parser {
    
    // let file :
    var fileString : String = "";
    var lineArray : [String]
    var currentIndex : Int = 0

    init() {
        lineArray = []
    }

    init(asmFile : String) {
        var cleanArray : [String] = []
        do {
            fileString = try String(contentsOfFile: asmFile, encoding: String.Encoding.utf8)

            let rawFileArray = fileString.characters.split { $0 == "\n" || $0 == "\r\n" }.map(String.init)
            // Remove all comments and whitespace
            var ix = 0

            for line in rawFileArray {
                let components = line.components(separatedBy: "//")
                let commentlessString = components[0]
                let cleanString = commentlessString.stringByRemovingWhitespaces
                if (cleanString.characters.count > 0) {
                    cleanArray.append(cleanString)
                }
                ix += 1
            }
        } catch {
            assert(false, "Aiiiiiiieeeeeee")
        }
        lineArray = cleanArray;
    }
    
    func hasMoreCommands() -> Bool {
        return currentIndex < (lineArray.count)
    }

    func reset() {
        currentIndex = 0
    }

    func advance() {
        currentIndex += 1
    }
    
    func commandType() -> AsmCommandType {
        if (lineArray[currentIndex].contains("@")) {
            return AsmCommandType.A_COMMAND
        } else if (lineArray[currentIndex].characters.first == "(") {
            return AsmCommandType.L_COMMAND
        } else {
            return AsmCommandType.C_COMMAND
        }
        // TODO: Handle L-Commands.
    }
    
    func symbol() -> String {
        assert(commandType() != AsmCommandType.C_COMMAND)
        let symbolToReturn : String
        if commandType() == AsmCommandType.A_COMMAND {
            let components = lineArray[currentIndex].components(separatedBy: "@")
            symbolToReturn = components[1]
        } else {
            let parens = CharacterSet(charactersIn:"()")
            let components = lineArray[currentIndex].components(separatedBy: parens)
            symbolToReturn = components[1]
        }
        return symbolToReturn
    }
    
    func dest() -> String {
        assert(commandType() == AsmCommandType.C_COMMAND)
        var destToReturn : String = ""
        if (lineArray[currentIndex].contains("=")) {
            let components = lineArray[currentIndex].components(separatedBy: "=")
            destToReturn = components[0]
        }
        return destToReturn
    }
    
    func comp() -> String {
        assert(commandType() == AsmCommandType.C_COMMAND)
        var interim : String

        if (lineArray[currentIndex].contains("=")) {
            let components = lineArray[currentIndex].components(separatedBy: "=")
            interim = components[1]
        } else {
            interim = lineArray[currentIndex]
        }
        let cmdComponents = interim.components(separatedBy: ";")
        let compToReturn = cmdComponents[0]

        return compToReturn
    }
    
    func jump() -> String {
        assert(commandType() == AsmCommandType.C_COMMAND)

        var jumpToReturn : String

        if (lineArray[currentIndex].contains(";")) {
            let cmdComponents = lineArray[currentIndex].components(separatedBy: ";")
            jumpToReturn = cmdComponents[1]
        } else {
            jumpToReturn = ""
        }

        return jumpToReturn
    }
}
