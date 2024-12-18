from globals import *

def importFunctionSymbols(symbols: dict, namespace: str = None):
    for (k,v) in symbols.items():
        fk = k
        if namespace is not None:
            fk = namespace + ":" + k
        executableFunctions[fk] = v
    
from modules.motor import export as motorExport

importFunctionSymbols(motorExport(), "motor")