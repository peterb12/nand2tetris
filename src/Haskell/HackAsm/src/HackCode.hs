module HackCode where
import HackParse
import Text.Printf


encodeCommand :: Command -> String
encodeCommand (AC ac) = encodeAddress ac
encodeCommand (CC cc) = encodeOperation cc
encodeCommand (LC lc) = encodeLabel lc

encodeOperation :: C_Command -> String
encodeOperation (C dest comp jump) = "111" ++ encodeComp comp ++ encodeDest dest ++ encodeJump jump

encodeAddress :: A_Command -> String
encodeAddress (AI x) = "0" ++ printf "%015.15b" x
encodeAddress (AS xs) = undefined

encodeLabel = undefined

encodeDest :: Maybe Dest -> String
encodeDest Nothing    = "000"
encodeDest (Just M)   = "001"
encodeDest (Just D)   = "010"
encodeDest (Just MD)  = "011"
encodeDest (Just A)   = "100"
encodeDest (Just AM)  = "101"
encodeDest (Just AD)  = "110"
encodeDest (Just AMD) = "111"

encodeJump :: Maybe Jump -> String
encodeJump Nothing    = "000"
encodeJump (Just JGT) = "001"
encodeJump (Just JEQ) = "010"
encodeJump (Just JGE) = "011"
encodeJump (Just JLT) = "100"
encodeJump (Just JNE) = "101"
encodeJump (Just JMP) = "111"

encodeComp :: Comp -> String
encodeComp Zero      = "0101010"
encodeComp One       = "0111111"
encodeComp NegOne    = "0111010"
encodeComp Dee       = "0001100"
encodeComp Ay        = "0110000"
encodeComp Mm        = "1110000"
encodeComp NotD      = "0001101"
encodeComp NotA      = "0110001"
encodeComp NotM      = "1110001"
encodeComp NegD      = "0001111"
encodeComp NegA      = "0110011"
encodeComp NegM      = "1110011"
encodeComp DPlusOne  = "0011111"
encodeComp APlusOne  = "0110111"
encodeComp MPlusOne  = "1110111"
encodeComp DMinusOne = "0001110"
encodeComp AMinusOne = "0110010"
encodeComp MMinusOne = "1110010"
encodeComp DPlusA    = "0000010"
encodeComp DPlusM    = "1000010"
encodeComp DMinusA   = "0010011"
encodeComp DMinusM   = "1010011"
encodeComp AMinusD   = "0000111"
encodeComp MMinusD   = "1000111"
encodeComp DAndA     = "0000000"
encodeComp DAndM     = "1000000"
encodeComp DOrA      = "0010101"
encodeComp DOrM      = "1010101"
