#!/bin/python
import json
import validity_checker
from ropper import RopperService

#must call add_module first
def find_gadgets(path,base,rs):
    allGadgets = []
    addGadgets = []
    subGadgets = []
    gadget = []
    rs.setImageBaseFor(name=path, imagebase=base)
    #find all gadgets
    rs.loadGadgetsFor(name=path)
    tmpGadgets = rs.getFileFor(name=path).gadgets
    #find addition gadgets
    tmpAddGadgets = rs.search(search="%add% ",name=path)
    #find subtraction gadgets
    tmpSubGadgets = rs.search(search="%sub% ",name=path)
    
    allGadgets = validateGadgets(tmpGadgets)
    addGadgets = validateGadgets(tmpAddGadgets,search=True)
    subGadgets = validateGadgets(tmpSubGadgets,search=True)

    print "Found total of " + str(len(allGadgets)) + " gadgets\n"
    return (allGadgets,addGadgets,subGadgets)

def validateGadgets(gadgetList,search=False):
    validGadgets = []
    if search:
        for file,g in gadgetList:
            if validity_checker.is_valid('{0:0{1}X}'.format(g.address,8)):
                validGadgets.append(g)
    else:    
        for g in gadgetList:
            if validity_checker.is_valid('{0:0{1}X}'.format(g.address,8)):
                validGadgets.append(g)

    return validGadgets

#must call add_module first
def dis_instruction(path,address,base,length,rs):
    #remove image base otherwise can't query specific instruction
    rs.setImageBaseFor(name=path,imagebase=0)
    result =  rs.disassAddress(path,address,length)
    #put image base back
    rs.setImageBaseFor(name=path,imagebase=base)
    #convert output to have full memory address
    result = result.replace(result.split(":")[0],hex(int(result.split(":")[0],16)+base))
    return result

def add_module(path,binArch,rs):
    try:
        rs.addFile(path)
        rs.setArchitectureFor(name=path, arch=binArch)
    except: #file already added
        return 2
    return 1

def prepareLibrary(bb = '',instCount = 6,color=True):
    
    # not all options need to be given
    options = {'color' : color,     # if gadgets are printed, use colored output: default: False
                'badbytes': bb,   # bad bytes which should not be in addresses or ropchains; default: ''
                'all' : False,      # Show all gadgets, this means to not remove double gadgets; default: False
                'inst_count' : instCount,   # Number of instructions in a gadget; default: 6
                'type' : 'all',     # rop, jop, sys, all; default: all
                'detailed' : False} # if gadgets are printed, use detailed output; default: False

    rs = RopperService(options)
    return rs

def printGadgets(filename,gadgets,path,arch,rs,openFileHandle=None):
    if openFileHandle != None:
        out = openFileHandle
    else:
        out = open(filename, 'w')
    out.write("Usable Gadgets: " + str(len(gadgets)) +"\n")
    out.write("----------------\n")
    out.write("----------------\n")
    for g in gadgets:
        for i in g.lines:
            out.write('{0:#0{1}x}'.format(i[0]+g.imageBase,8) +": " +i[1] +"\n")
        if arch == "MIPS" or arch == "MIPS64":
            #ropper doesn't get the delay instruction yet. Accounting for it here until fixed
            out.write(dis_instruction(path,g.lines[-1][0]+4,g.imageBase,1,rs))
        out.write("\n----------------------------------\n")
    if openFileHandle == None:
        out.close()