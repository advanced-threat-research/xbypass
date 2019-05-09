from subtraction_analyzer import *
from addition_analyzer import *
import sys

class AnalyzerInterface:

    def __init__(self, target_address):
        self.target = target_address

    @staticmethod
    def get_operands(address, operand_type="BOTH"):
        if isinstance(address, str):
            address = int(address,16)

        analyzer1 = SubtractionAnalyzer()
        analyzer2 = AdditionAnalyzer()
        address1 = HexAddress(address)
        address2 = HexAddress(address)
        analyzer1.assign(address1, 'target')
        analyzer2.assign(address2, 'target')

        results = {"ADDITION": None, "SUBTRACTION": None}
        if operand_type.upper() == 'ADDITION':
            results["ADDITION"] = analyzer2.find_addition()
        elif operand_type.upper() == 'SUBTRACTION':
            results["SUBTRACTION"] = analyzer1.get_operands()
        elif operand_type.upper() == 'BOTH':
            results["ADDITION"] = analyzer2.find_addition()
            results["SUBTRACTION"] = analyzer1.get_operands()
        else:
            print "Invalid operand_type. Try leaving it blank."
        return results

def write_candidates(fname, tpl, operation='add'):
    operation = operation.lower()
    if operation == 'add':
        append = '-addition'
    elif operation == 'sub':
        append = '-subtraction'
    else:
        append = ''
    with open(fname + '{0}.txt'.format(append), 'w') as f:
        f.write("{0},{1}\n".format(hex(tpl[0]),hex(tpl[1])))

if __name__ == "__main__":
    address = ''
    if len(sys.argv) == 2:
        address = sys.argv[-1]
    else:
        print "Please include address"
        exit()

    result = AnalyzerInterface.get_operands(address)
    print 'ADDRESS: \t' + address.lower()
    if result["ADDITION"]:
        print 'ADDITION: \t' + hex(result["ADDITION"][0]) + ', ' +  hex(result["ADDITION"][1])
        write_candidates(address, result["ADDITION"], 'add')
    if result["SUBTRACTION"]:
        print 'SUBTRACTION: \t' + hex(result["SUBTRACTION"][0]) + ', ' + hex(result["SUBTRACTION"][1])
        write_candidates(address, result["SUBTRACTION"], 'sub')