from globals import *

class ExecContext:
    symbol:str
    variable:dict
    i_var:dict # Internal Variables
    program:list[tuple[str, str]] = []
    ic:int = 0 # Instruction Counter
    jmpReturnCtx:int = -1
    pauseExec:bool = False
    ctxId:int = 0
    
    def __init__(self, program, symbol, ctxId):
        self.variable = {}
        self.i_var = {}
        self.program = program
        self.symbol = symbol
        self.ctxId = ctxId

    def readyForJmp(self, returnCtx:int):
        self.jmpReturnCtx = returnCtx
        self.pauseExec = False
        self.ic = 0

    def execContext(self):
        while not self.pauseExec:
            instruction = self.program[self.ic]

            executableFunctions.get(instruction[0], lambda x, *a: None)(self, *instruction[1])
            self.ic += 1

            if self.ic > len(self.program) - 1:
                self.pauseExec = True
                break
        print(self.variable)