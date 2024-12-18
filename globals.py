import re
program:list[tuple[str, str]] = []
contexts = []

class q_str(str):
    def __new__(cls, content):
        return str.__new__(cls, content)

def isDecimal(s:str):
    float_pattern = re.compile("^[0-9]*\\.[0-9]*$")
    if float_pattern.match(s):
        return True
    return False

class Validator:
    @classmethod
    def argumentRequirement(self, args, fnName: str, requirement: list[str]):
        
        # Good to go, AKA has enough arguments to fill the requirements
        if len(args) >= len(requirement): 
            return 

        print("[ERROR] " + fnName + " is missing required arguments: ")
        for i in range(len(requirement)):
            front = str(i) # Example: [#4] 
            front += "["
            front += "PRESENT" if i < (len(args)) else "MISSING" # Ok if fulfilled 
            front += "] "
            print(front + requirement[i])
        
        impl_pause(None, True)
    @classmethod
    def toEnum(self, arg: str, enumClass, className: str = "", errorOnFail: bool = True):
        enums = [x.lower().replace("_", "") for x in enumClass.__dict__ if not x.startswith("__")]
        
        try:
            return enums.index(arg)
        except ValueError:
            if errorOnFail:
                print("Failed to convert:", arg, ", to", className, "\nPossiable Types:")
                for x in enums:
                    print(x)
                exit(-1) 
            return None

# Expand Variables
def exvar(ctx, *args):
    modArgs = [*args]
    argIndex = 0
    while argIndex < len(modArgs):
        arg = modArgs[argIndex]
        
        if not isinstance(arg, q_str): 
            argIndex += 1
            continue

        var = ctx.variable.get(arg, None)
        if var != None:
            modArgs[argIndex] = var
        argIndex += 1

    return modArgs

def _tokenize(ctx, *args):
    argBlob = ''.join(args)
    tokens_ = re.split("(&&|\\|\\||==|!=)", argBlob)

    tokens:list[any] = exvar(ctx, *[q_str(t) for t in tokens_])
    print(tokens)
    return tokens
    

def impl_let(ctx, *args):
    ctx.variable[args[0]] = exvar(ctx, *args[1:])[0]

def impl_log(ctx, *args):
    print(*args)

def impl_run(ctx, *args):
    if len(args) != 1:
        print("Bad Run Instruction")
        exit(-1)
    
    def evalCtx(ctx_):
        ctx_.readyForJmp(ctx.ctxId)
        ctx_.execContext()

    if type(args[0]) is int:
        evalCtx(contexts[args[0]])

    for ctx_ in contexts:
        if ctx_.symbol == args[0]:
            evalCtx(ctx_)



# Run Code If
def _rcif(ctx, *args):
    impl_logicEval(ctx, *args[0])
    if ctx.i_var["logicVal"] is True:
        impl_run(ctx, args[1])

# Run Code Else If
def _rcelif(ctx, *args):
    if ctx.i_var["logicVal"] is True: 
        # The initial IF or a subsequent ELIF was already true 
        # so don't execute the code in this ELIF even if the
        # expression is true
        return

    impl_logicEval(ctx, *args[0])
    if ctx.i_var["logicVal"] is True:
        impl_run(ctx, args[1])

# Run Code Else
def _rcelse(ctx, *args):
    if ctx.i_var["logicVal"] is False:
        impl_run(ctx, args[0])

def impl_return(ctx, *args):
    ctx.pauseExec = True
    ctx.i_var["return"] = args[0]



def to_bool(arg):
    if type(arg) is bool:
        return arg
    elif type(arg) is float:
        return arg == 1
    

def impl_logicEval(ctx, *args):
    tokens = _tokenize(ctx, *args)
        
    if len(tokens) == 1:
        ctx.i_var["logicVal"] = to_bool(tokens[0])
        return
    if len(tokens) != 3:
        print("Logic statements must be exactly 1 or 3 arguments")
        exit(-1)
    term1 = tokens[0]
    op = tokens[1]
    term2 = tokens[2]
    result: bool = None
    match op:
        case "&&":
            result = to_bool(term1) and to_bool(term2)
        case "||":
            result = to_bool(term1) or to_bool(term2)
        case "==":
            result = term1 == term2
        case "!=":
            result = term1 != term2

    ctx.i_var["logicVal"] = result

def impl_pause(ctx, *args):
    if len(args) > 0:
        if isinstance(args[0], bool):
            if args[0]:
                b = input("Press enter to exit, type 'bypass' and press enter to continue anyway. ")
                if b.lower() == "bypass":
                    return
                exit(0)
    input("Press enter to continue...")

executableFunctions = {
    'let': impl_let,
    'log': impl_log,
    'run': impl_run,
    'return': impl_return,
    'logic': impl_logicEval,
    'pause': impl_pause,
    '_rcif': _rcif,
    '_rcelse': _rcelse,
    '_rcelif': _rcelif
}