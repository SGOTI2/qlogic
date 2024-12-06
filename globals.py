import re
program:list[tuple[str, str]] = []
contexts = []

# Expand Variables
def _exvar(ctx, *args):
    modArgs = [*args]
    argIndex = 0
    while argIndex < len(modArgs):
        arg = modArgs[argIndex]

        if arg.startswith("\""):
            argIndex += 1
            continue
        elif arg == "true":
            modArgs[argIndex] = True
            argIndex += 1
            continue
        elif arg == "false":
            modArgs[argIndex] = False
            argIndex += 1
            continue
        elif re.match("^[\d\.]+$", arg) is not None:
            modArgs[argIndex] = float(arg)
            argIndex += 1
            continue


        var = ctx.variable.get(arg, None)
        if var != None:
            modArgs[argIndex] = var
        argIndex += 1

    return modArgs

def _tokenize(ctx, *args):
    argBlob = ''.join(args)
    tokens = re.split("(&&|\\|\\||==|!=)", argBlob)
    tokens = _exvar(ctx, *tokens)
    return tokens
    

def impl_let(ctx, *args):
    ctx.variable[args[0]] = _exvar(ctx, *args[1:])[0]

def impl_log(ctx, *args):
    print(*[arg.strip("\"\'") for arg in args])

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
    elif type(arg) is str:
        arg = arg.lower()
        if arg == "true":
            return True
        elif arg == "false":
            return False
        else:
            print("Not a boolean")
            exit(0)
    elif type(arg) is float:
        return arg == 1
    

def impl_logicEval(ctx, *args):
    tokens = _tokenize(ctx, *args)
    if len(tokens) < 3:
        if len(tokens) == 1:
            ctx.i_var["logicVal"] = to_bool(tokens[0])
        return
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

executableFunctions = {
    'let': impl_let,
    'log': impl_log,
    'run': impl_run,
    'return': impl_return,
    'logic': impl_logicEval,
    '_rcif': _rcif,
    '_rcelse': _rcelse,
    '_rcelif': _rcelif
}