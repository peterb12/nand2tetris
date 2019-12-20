{-# LANGUAGE OverloadedStrings #-}
module Main where
import HackParse
import qualified Data.Text.IO as T
import Data.Either


main :: IO ()
main = do
  asmfile <- T.readFile "/Users/pberger/code/haskell/nand2tetris/projects/06/max/MaxL.asm"
  let theParse = parse parseCommands "" asmfile
  let result = fromRight [] theParse
  putStrLn $ show result

  
