//
//  Assembler.swift
//  Hack Assembler
//
//  Created by peterb on 12/29/16.
//  Copyright © 2016 peterb. All rights reserved.
//

import Foundation

enum AsmCommandType {
    case A_COMMAND;
    case C_COMMAND;
    case L_COMMAND;
}

func padTo(size : Int, inString : String) -> String {
    var paddedString = inString
    for _ in 0..<(size - inString.characters.count) {
        paddedString = "0" + paddedString
    }
    return paddedString
}

class Assembler {
    var symbolTable : [String:Int] = Dictionary()
    var romCounter : Int = 0
    var ramCounter : Int = 0
    var parser : Parser
    var coder : Code

    init(asmFile : String) {
        self.parser = Parser(asmFile: asmFile)
        self.coder = Code()
    }

    func buildSymbolTable() {
        while parser.hasMoreCommands() {
            if (parser.commandType() == AsmCommandType.L_COMMAND) {
                // Add item to symbol table.
                let symbol = parser.symbol()
                symbolTable[symbol] = romCounter
            } else {
                romCounter += 1
            }
            parser.advance()
        }
        // Preload RAM table with R0..R15
        for f in 0..<16 {
            symbolTable["R" + String(f)] = f
        }
        symbolTable["SP"] = 0
        symbolTable["LCL"] = 1
        symbolTable["ARG"] = 2
        symbolTable["THIS"] = 3
        symbolTable["THAT"] = 4
        symbolTable["SCREEN"] = 16384
        symbolTable["KBD"] = 24576
        ramCounter = 16
    }

    func assemble(asmFile : String) -> String {
        var machineCode : String = ""

        buildSymbolTable()
        parser.reset()

        while parser.hasMoreCommands() {
            let cmdType = parser.commandType()
            if (cmdType == AsmCommandType.A_COMMAND) {
                let symbol = parser.symbol()
                var maybeAddress : Int? = Int(symbol, radix: 10)
                let binString : String
                if let address = maybeAddress {
                    // Yay, it's numeric, forge on ahead.
                    binString = String(Int(address), radix: 2)
                } else {
                    // Booo, we have to look it up.
                    if let lookupAddress = symbolTable[symbol] {
                        // a hit!
                        binString = String(Int(lookupAddress), radix: 2)
                    } else {
                        // Booooooo, cache miss. Add a new symbol.
                        symbolTable[symbol] = ramCounter
                        binString = String(Int(ramCounter), radix: 2)
                        ramCounter += 1
                    }
                }
                machineCode.append(padTo(size: 16, inString: binString))
                machineCode.append("\n")
            } else if (cmdType == AsmCommandType.C_COMMAND) {
                let rawDest = parser.dest()
                let dest = coder.dest(inDest: rawDest)

                let rawComputation = parser.comp()
                let computation = coder.comp(inComp: rawComputation)

                let rawJump = parser.jump()
                let jump = coder.jump(inJump: rawJump)

                let binString = "111" + computation + dest + jump
                assert(binString.characters.count == 16, "Wrong number of bits in command.")
                machineCode.append(binString)
                machineCode.append("\n")
            }
            // L-Commands are no-ops at this point.
            parser.advance()
        }
        return machineCode
    }
}
