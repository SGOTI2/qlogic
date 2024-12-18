import os.path
from globals import *
from execContext import ExecContext
import module    


filePath = os.path.join(os.path.dirname(__file__), "program.qlogic")

def flattenProgram(unFlattenedProgram:list[str]):
    returningProgram:list[tuple[str, any]] = []

    for line in unFlattenedProgram:
        splitLine:list[q_str] = line.strip().split()
        if splitLine == []: continue
        
        args = splitLine[1:]
        parsedArgs = []
        argIndex = 0
        while argIndex < len(args):
            arg = args[argIndex]
            if args[argIndex].startswith("\""):
                groupedArg = ""
                while argIndex < len(args):
                    groupedArg += args[argIndex] + " "
                    if args[argIndex].endswith("\""):
                        break
                    argIndex += 1
                parsedArgs.append(str(groupedArg.removesuffix("\" ").removeprefix("\"")))
            elif arg == "true":
                parsedArgs.append(True)
            elif arg == "false":
                parsedArgs.append(False)
            elif arg.isdigit():
                parsedArgs.append(int(arg))
            elif isDecimal(arg):
                parsedArgs.append(float(arg))
            else:
                parsedArgs.append(q_str(args[argIndex]))
            argIndex += 1

        returningProgram.append((splitLine[0], parsedArgs))

    return returningProgram

def loadProgram():
    global program
    with open(filePath, "r") as f:
        programUnSplit = f.read()
        program = flattenProgram(programUnSplit.split(";"))




### NOTE: Find Scope Contexts  

def findScopes(parentCtxId:int, awaitingIfClose:bool = False) -> int:
    parentCtx = contexts[parentCtxId]

    lineNumber = 0
    subFunctionsLen = 0 # Keeps track of how many lines have been removed so they can be applied to the parent
    while lineNumber < len(parentCtx.program):
        programLine = parentCtx.program[lineNumber]
        if programLine[0] == "func":
            subProgram = parentCtx.program[(lineNumber+1):] # Next line and onward (INCLUDING This Function's End)
            symbol = programLine[1][0]
            
            ctxId = len(contexts)
            contexts.append(ExecContext(subProgram, symbol, ctxId))

            functionLen = findScopes(ctxId)
            if functionLen == None:
                print("Unclosed Function")
                exit(0)
            subFunctionsLen += functionLen

            del parentCtx.program[lineNumber:(lineNumber + functionLen)] # Delete the function from this function's code
            continue # Re-Run for the next line now that the function has been removed

        elif programLine[0] == "else" and awaitingIfClose:

            if parentCtxId == 0:
                print("Too many ends")
                exit(0)

            del parentCtx.program[lineNumber:]

            return lineNumber + subFunctionsLen + 1 # Include the else line
        
        elif programLine[0] == "elif" and awaitingIfClose:

            if parentCtxId == 0:
                print("Too many ends")
                exit(0)

            del parentCtx.program[lineNumber:]

            return lineNumber + subFunctionsLen + 1 # Include the else line

        elif programLine[0] in ["if", "else", "elif"]:
            subProgram = parentCtx.program[(lineNumber+1):] # Next line and onward
            
            ctxId = len(contexts)
            contexts.append(ExecContext(subProgram, "", ctxId))

            functionLen = findScopes(ctxId, True)
            if functionLen == None:
                print("Unclosed If/Else Statement")
                exit(0)
            subFunctionsLen += functionLen

            del parentCtx.program[lineNumber:(lineNumber + functionLen)] # Delete the code in the if statement
            
            if programLine[0] == "if":
                parentCtx.program.insert(lineNumber, ["_rcif", [*programLine[1:], ctxId]])
            elif programLine[0] == "else":
                parentCtx.program.insert(lineNumber, ["_rcelse", [ctxId]])
            elif programLine[0] == "elif":
                parentCtx.program.insert(lineNumber, ["_rcelif", [*programLine[1:], ctxId]])

        elif programLine[0] == "end":

            if parentCtxId == 0:
                print("Too many ends")
                exit(0)

            del parentCtx.program[lineNumber:]

            return lineNumber + subFunctionsLen + 2 # Include the end line + func line


        lineNumber += 1

### NOTE: Run the program

if __name__ == "__main__":
    loadProgram()
    contexts.append(ExecContext(program, "_main", 0))
    findScopes(0)
    
    contexts[0].readyForJmp(-1)
    contexts[0].execContext()

