{-# LANGUAGE OverloadedStrings #-}
module HackParse where
import Data.Char
import Data.Void
import Data.Maybe
import qualified Data.Text as T
import qualified Data.Text.IO as T
import Text.Megaparsec
import Text.Megaparsec.Char
import qualified Text.Megaparsec.Char.Lexer as L

import Debug.Trace
type Parser = Parsec Void T.Text

parse = runParser

data Dest = M | D | MD | A | AM | AD | AMD deriving Show
data Jump = JGT | JEQ | JGE | JLT |  JNE | JLE | JMP deriving Show
data Comp = Zero | One | NegOne | Dee | Ay | Mm | NotD | NotA | NotM | NegD | NegA | 
            NegM | DPlusOne | APlusOne | MPlusOne | DMinusOne | AMinusOne | MMinusOne |
            DPlusA | DPlusM | DMinusA | DMinusM | AMinusD | MMinusD | DAndA | DAndM |
            DOrA | DOrM deriving Show
data A_Command = AI Int | AS String deriving Show
data C_Command = C (Maybe Dest) Comp (Maybe Jump) deriving Show
data L_Command = L String deriving Show
data Command = AC A_Command | CC C_Command | LC L_Command deriving Show

hasMoreCommands = undefined

advance = undefined

symbol = undefined

stringToDest :: String -> Dest
stringToDest "AMD" = AMD
stringToDest "AD" = AD
stringToDest "AM" = AM
stringToDest "A" = A
stringToDest "M" = M
stringToDest "D" = D
stringToDest "MD" = MD

sc :: Parser ()
sc = L.space
  space1                         -- (2)
  (L.skipLineComment "//")       -- (3)
  (L.skipBlockComment "/*" "*/") -- (4)

lexeme :: Parser a -> Parser a
lexeme = L.lexeme sc

parseCommands :: Parser [Command]
parseCommands = do
  sc
  cmds <- parseCommand `sepEndBy` sc
  return cmds
  
parseCommand :: Parser Command
parseCommand = 
    do
        command <- choice [
            AC <$> try parseACommand,
            LC <$> try parseLCommand,
            CC <$> parseCCommand
            ]
        -- traceShowM command
        return command

parseAICommand :: Parser A_Command
parseAICommand = 
    do
        char '@'
        address <- some digitChar
        many (satisfy (\x -> x == ' ' || x == '\n' || x == '\t'))
        return (AI (read address))

parseASCommand :: Parser A_Command
parseASCommand = 
      do
        char '@'
        address <- many (letterChar <|> digitChar <|> (char '_')) 
        return (AS address)

parseACommand :: Parser A_Command
parseACommand = 
    do
        address <- try parseAICommand <|> parseASCommand
        return address

parseLCommand :: Parser L_Command
parseLCommand =
    do
        char '('
        label <- many (letterChar <|> digitChar)
        char ')'
        return (L label)

--format of a C-command:
-- dest=comp;jump
parseCCommand :: Parser C_Command
parseCCommand = do
  dest <- (optional . try) parseCDest
  comp <- parseComp
  jump <- optional parseJump
  return (C dest comp jump) 

parseJump :: Parser Jump
parseJump =
  do
    char ';'
    choice 
      [ JGT <$ string "JGT"
      , JEQ <$ string "JEQ"
      , JGE <$ string "JGE"
      , JLT <$ string "JLT"
      , JNE <$ string "JNE"
      , JLE <$ string "JLE"
      , JMP <$ string "JMP" ]

parseComp :: Parser Comp
parseComp =
  do
    choice
      [ Zero      <$ char '0'
      , One       <$ char '1'
      , NegOne    <$ string "-1"
      , NotD      <$ string "!D"
      , NotA      <$ string "!A"
      , NotM      <$ string "!M"
      , NegD      <$ string "-D"
      , NegA      <$ string "-A"
      , NegM      <$ string "-M"
      , DPlusOne  <$ string "D+1"
      , APlusOne  <$ string "A+1"
      , MPlusOne  <$ string "M+1"
      , DMinusOne <$ string "M-1"
      , AMinusOne <$ string "A-1"
      , MMinusOne <$ string "M-1"
      , DPlusA    <$ string "D+A"
      , DPlusM    <$ string "D+M"
      , DMinusA   <$ string "D-A"
      , DMinusM   <$ string "D-M"
      , AMinusD   <$ string "A-D"
      , MMinusD   <$ string "M-D"
      , DAndA     <$ string "D&A"
      , DAndM     <$ string "D&M"
      , DOrA      <$ string "D|A"
      , DOrM      <$ string "D|M"
      , Dee       <$ char 'D'
      , Ay        <$  char 'A'
      , Mm        <$  char 'M' ]
                 
parseCDest :: Parser Dest
parseCDest = 
    do
        try (many (satisfy (\x -> x == '\t' || x == ' ')))
        dest <- pCDest
        char '='
        return dest

pCDest :: Parser Dest
pCDest = choice
  [ AMD <$ string "AMD"
  , AM  <$ string "AM"
  , AD  <$ string "AD"
  , A   <$ string "A"
  , MD  <$ string "MD"
  , D   <$ string "D"
  , M   <$ string "M" ]
  
dest :: C_Command -> Maybe Dest
dest (C dest _ _) = dest

comp :: C_Command -> Comp
comp (C _ comp _) = comp

jump :: C_Command -> Maybe Jump
jump (C _ _ jump )= jump
