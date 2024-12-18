import re
from globals import *

class CONTROLLER_TYPES:
    UNASSIGNED = 0
    SPARK_MAX = 1
    CIM = 2

class MOTOR_TYPES:
    UNASSIGNED = 0
    BRUSHED = 1
    BRUSHLESS = 2

class Motor():
    controllerType = CONTROLLER_TYPES.UNASSIGNED
    CANId = 0
    motorType = MOTOR_TYPES.UNASSIGNED
    power = 0

    def __init__(self, cType, CANID, mType) -> None:
        self.controllerType = cType
        self.CANId = CANID
        self.motorType = mType
        print("A motor was created")
    
    def run(self, power):
        print("Running at: ", power*100, "%")
        self.power = power
        pass
    
    def stop(self):
        print("The motor was stopped from: ", self.power*100, "%")
        self.power = 0
        pass

global currentMotor
currentMotor: Motor = None

def create(ctx, *args):
    global currentMotor
    Validator.argumentRequirement(args, "motor:create", [
        "Variable Name",
        "Motor Controller Type",
        "CANId", 
        "Motor type"
    ])

    cType = Validator.toEnum(args[1].lower(), CONTROLLER_TYPES, "Controller Type")
    CANID = None
    mType = Validator.toEnum(args[3].lower(), MOTOR_TYPES, "Motor Type")
  
    m = re.search("\d+",args[2].lower())
    if m:
        CANID = int(m.group())
    else:
        print("Unable to convert to CANId, ensure that numbers are present: " + args[2])
        exit(-1)

    motor = Motor(cType, CANID, mType)
    
    ctx.variable[args[0]] = motor

def run(ctx, *args):
    if currentMotor is None: print("No motor available"); return
    
    Validator.argumentRequirement(args, "motor:run", {
        "Percent Power"
    })

    m = re.search("[\d\.]+",args[0].lower())
    if m:
        currentMotor.run(float(m.group()) / 100)

def stop(ctx, *args):
    if currentMotor is None: print("No motor available"); return
    currentMotor.stop()

def use(ctx, *args):
    global currentMotor
    newArgs = exvar(ctx, *args)
    if len(newArgs) < 1: print("Variable name is required"); return
    if not isinstance(newArgs[0], Motor): print("Variable must be a motor"); return
    currentMotor = newArgs[0]
    print("Current motor switched to: ", args[0])

def export():
    return {
        "create": create,
        "run": run,
        "stop": stop,
        "use": use,
    }