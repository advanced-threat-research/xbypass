#!/bin/python
# Xbypass.py example.config
import sys,os
import json
import gadgetFinder
import addition_analyzer
import subtraction_analyzer
import validity_checker

class Target:
    def __init__(self, name,address=None):
        self.name = name
        if address is None:
            self.address = None
        else:
            self.address = address
        # list of tuples
        self.operandsAdd = []
        self.operandsSub = []
        # only allow one gadget per target
        self.gadget =[]

    def findOperands(self,operation):
        if operation == 'ADD':
            analyzer = addition_analyzer.AdditionAnalyzer()
            address = addition_analyzer.HexAddress(self.address)
            analyzer.assign(address, 'target')
            result = analyzer.find_addition()
            self.operandsAdd = [result] if result else []
            
        elif operation == 'SUB':
            analyzer = subtraction_analyzer.SubtractionAnalyzer()
            address = subtraction_analyzer.HexAddress(self.address)
            analyzer.assign(address, 'target')
            result = analyzer.get_operands()
            self.operandsSub = [result] if result else [] 
            

    def printTarget(self, filename , openFile=None):
        if openFile == None:
            out = open(filename, 'w')
        else:
            out = openFile
        
        out.write("Target Name: " + self.name + "\n")
        out.write("Target Address: " + hex(self.address) + "\n")
        out.write("Addition Operands:\n")
        if len(self.operandsAdd) != 0:
            out.write('\n'.join('{0:#0{2}x} {1:#0{2}x}'.format(x[0],x[1],10) for x in self.operandsAdd))
        else:
            out.write("No addition operands found for target\n")
        out.write("\nSubtraction operands:\n")
        if len(self.operandsAdd) != 0:
            out.write('\n'.join('{0:#0{2}x} {1:#0{2}x}'.format(x[0],x[1],10) for x in self.operandsSub))

        else:
            out.write("No subtraction operands found for target\n")
        
        if openFile == None:
            out.close()

class MemorySection:

    def __init__(self,name,path,base,end,arch):
        self.name = name
        self.path = path
        self.baseAddress = int(base,16)
        self.endAddress = int(end,16)
        self.arch = arch
        self.validAddresses = []
        self.gadgets = []
        self.addGadgets = []
        self.subGadgets = []
        self.targets = []
        self.NumOfOperandsToPrint = 5

    def printSection(self):
        out = open(outDir +os.sep+self.name+"_Xbypass.txt", 'w')
        gadgetFinder.printGadgets(None,self.gadgets,self.path,self.arch,rs,openFileHandle=out)
        out.write("Found targets: " + str(len(self.targets)) + "\n")
        out.write("----------------\n")
        out.write("----------------\n")
        if len(self.targets) != 0:
            for t in self.targets:
                t.printTarget(None,out)

        out.close()

def readConfig(filename):
    global maxadd
    global minadd
    global memeoryObjects
    global targetsFromConfig
    validArch = ["x86","x86_64","MIPS","MIPS64","ARM","ARMTHUMB","ARM64","PPC","PPC64"]
    with open(filename, 'r') as f:
        config = json.loads(f.read())
    #create options for each targets by address. Config file expects address to be hex 
    if 'targetAddress' in config:
        for t in config['targetAddress']:
            targetsFromConfig.append(Target("",int(t.split('0x')[-1],16))) #account for the 0x if there
    
    #create object for each entry in executableMemory and find limits on addresses
    if 'executableMemory' in config:
        for l in config['executableMemory']:
            #ensure path is valid in config file
            if not os.path.isfile(l['path']):
                print "File " + l['path'] + " in config file doesn't exists.  Please fix config file.  Exiting.."
                sys.exit(-1)
            try:
                if int(l['endAddress'],16) > maxadd:
                    maxadd = int(l['endAddress'],16)
                if minadd == 0 or int(l['baseAddress'],16) < minadd:
                    minadd = int(l['baseAddress'],16)
            except ValueError:
                print "Error in config file address with  " + l['name'] + ", exiting..."
                sys.exit(-2)
            if l['arch'] not in validArch:
                print "Bad arch with " +l['name'] + ", exiting..."
                sys.exit(-3)
            #config is validated create object
            memeoryObjects.append(MemorySection(l['name'],l['path'],l['baseAddress'],l['endAddress'],l['arch']))
    else:
        print "Unable to find required executableMemory in config file. Exiting..."
        sys.exit()



def resolveTargets():
    global memeoryObjects
    global targetsFromConfig
    for m in memeoryObjects:
        itemsToRemove = []
        print "Looking for targets in " + m.name
        for t in targetsFromConfig:
           if t.address != None and t.address >= m.baseAddress and t.address <= m.endAddress:
                # get one instruction after due to delay instruction
                #gadgetFinder.add_module(m.path,m.arch,rs)
                #t.gadget = gadgetFinder.dis_instruction(m.path,t.address - m.baseAddress,m.baseAddress,2, rs)
                #we found the module this address goes with, do not process for rest of modules
                m.targets.append(t)
                itemsToRemove.append(t)
        for t in itemsToRemove:
            targetsFromConfig.remove(t)


def findTargetOperands():
    global memeoryObjects
    for m in memeoryObjects:
        for t in m.targets:
            t.findOperands('ADD')
            t.findOperands('SUB')
            #print target file
            t.printTarget(outDir +os.sep+hex(t.address)+"_operands.txt")

            


def findROPGadgets():
    global memeoryObjects
    global minadd
    exists = False
    global maxadd
    #find gadgets for each library
    for m in memeoryObjects:
        if validity_checker.is_valid(None,minAdd=hex(m.baseAddress),maxAdd=hex(m.endAddress)):
            print "Found usable addresses!!"
            exists = True
            print "Finding gadgets for " + m.name
            gadgetFinder.add_module(m.path,m.arch,rs)
            gadgetTuple = gadgetFinder.find_gadgets(m.path,m.baseAddress,rs)
            m.gadgets = gadgetTuple[0]
            m.addGadgets = gadgetTuple[1]
            m.subGadgets = gadgetTuple[2]
            if len(m.addGadgets) != 0: 
                print str(len(m.addGadgets)) + " Add gadgets found, writing to file."
                gadgetFinder.printGadgets(outDir + os.sep + m.name+"_add_gadgets.txt",m.addGadgets,m.path,m.arch,rs)
            if len(m.subGadgets) != 0: 
                print str(len(m.subGadgets)) + " Sub gadgets found, writing to file."
                gadgetFinder.printGadgets(outDir + os.sep + m.name+"_sub_gadgets.txt",m.subGadgets,m.path,m.arch,rs)
        else:
            print m.path +": No valid addresses for this module, skipping..."
    if not exists:
       print "No addesses exist which will bypass the xml filter within the given config file :("

if __name__ == "__main__":
    minadd = 0
    maxadd = 0
    outDir = "output"
    targetsFromConfig = []
    memeoryObjects = []
    if len(sys.argv) != 2:
        print "Wrong number of paramters. Usage python Xbypass [config file]"
        sys.exit()

    rs = gadgetFinder.prepareLibrary(color=False) #making global to handle no delay instruction in output for now
    if type(rs) == 'NoneType':
        print "Ropper failed to initialize..."
        sys.exit()

    readConfig(sys.argv[1])
    #create output directory if doesn't exists
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    print "Finding all possible ROP gadgets...."
    # find all rop gadgets that will bypass xml filter in executable space
    findROPGadgets()
    # search by name and perform addtion and subtraction
    print "Resolving provided targets....."
    resolveTargets() #doesn't depend on load
    #For each target calculate add and subtract possibilities
    print "Calculating operands..."
    findTargetOperands() #depends on load and resolveTargets own thread

    print "Writing results to file...."
    for m in memeoryObjects:
        m.printSection()
    print "Finished!"


