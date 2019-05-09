#address must be 4 bytes in 0x######## or ######## format in both command line and while using the function.
#It is of string type and is case insentive.
#
#$python validity_checker.py address
#
#To use as an import call is_valid(address) which returns a bool


import sys

#Hardcoded good bytes file
GOOD_BYTES_FILE= "xmlChecker_out.txt"

def is_valid(address,minAdd=None,maxAdd=None):

	with open('xmlChecker_out.txt') as f:
	    good_bytes = f.readlines()
	good_bytes = [x.strip().lower() for x in good_bytes]

	if minAdd !=None and maxAdd !=None:
		return check_range(minAdd,maxAdd,good_bytes)

	#Getting the addresses and normalizing the format
	address = address.lower().replace('0x','')
	valid_bytes = []
	#Split the address in to 2 nibble and for nibble possibilities.
	two_nibbles = [address[:2], address[2:4], address[4:6], address[6:8]]
	four_nibbles = [address[:4], address[4:8], address[2:6]]
	
	#Find all the valid bytes that are also part of the addresses 2 nibble or 4 nibble posibilities
	for g in good_bytes:
		if g in address:
			if len(g) == 2:
				if g in two_nibbles:
					valid_bytes.append(g)
			if len(g) == 4:
				if g in four_nibbles:
					valid_bytes.append(g)
	#If any of the combinations of valid bytes equal the provided address then the address is valid
	if check_4byte(valid_bytes, address) or check_2xbytes_4bytes(valid_bytes, address) or check_2byte(valid_bytes, address):
		return True
	return False

#This covers the pattern where a pair of 4 nibbles make an address
#I should relabel the function to say nibble instead of byte
def check_4byte(valid_bytes, address):
	four_nibbles = list(filter(lambda x: len(x) == 4, valid_bytes))
	for n in four_nibbles:
		for m in four_nibbles:
			if n + m == address:
				return True
	return False

#This covers the pattern where 4 sets of 2 nibbles are used to make an address
def check_2byte(valid_bytes, address):
	two_nibbles = list(filter(lambda x: len(x) == 2, valid_bytes))
	for n in two_nibbles:
		for m in two_nibbles:
			for o in two_nibbles:
				for p in two_nibbles:
					if n + m + o + p == address:
						return True
	return False

#This covers the pattern where some combination of 1 set of 4 nibbles and 2 sets of 2 nibbles make an address
def check_2xbytes_4bytes(valid_bytes, address):
	two_nibbles = list(filter(lambda x: len(x) == 2, valid_bytes))
	four_nibbles = list(filter(lambda x: len(x) == 4, valid_bytes))
	for n in two_nibbles:
		for m in two_nibbles:
			for o in four_nibbles:
				#Notice that order of the two_nibbles doesn't matter since m and n will eventually swap values.
				if n + m + o == address or o + m + n  == address or m + o + n == address:
					return True
	return False

#return true if any address in range would be valid
def check_range(minadd, maxadd,good_bytes):
	#Getting the addresses and normalizing the format
	minadd = minadd.lower().replace('0x','')
	min_bytes = [minadd[:2], minadd[2:4], minadd[4:6], minadd[6:8]]
	maxadd = maxadd.lower().replace('0x','')
	max_bytes = [maxadd[:2], maxadd[2:4], maxadd[4:6], maxadd[6:8]]

	#print min_bytes
	#print max_bytes
	result_table = [False,False,False,False]
	
	for i in range(4):
		if min_bytes[i] == '00' and max_bytes[i] == '00' and i != 0:
			result_table[i] = True
		if min_bytes[i] == max_bytes[i] and min_bytes[i] in good_bytes:
			result_table[i] = True
		elif min_bytes[i] < max_bytes[i]:
			tmpMin = int(min_bytes[i],16)
			tmpMax = int(max_bytes[i],16)
			for x in range(tmpMin,tmpMax+1):
				if '{0:0{1}X}'.format(x,2) in good_bytes:
					result_table[i] = True
		elif min_bytes[i] > max_bytes[i]:
			tmpMin = int(min_bytes[i],16)
			tmpMax = int(max_bytes[i],16)
			for x in range(tmpMin,0xFF+1):			
				if '{0:0{1}X}'.format(x,2) in good_bytes:
					result_table[i] = True
			for x in range(0,tmpMax,+1):
				if '{0:0{1}X}'.format(x,2) in good_bytes:
					result_table[i] = True	
	#print result_table
	if result_table[0] and result_table[1] and result_table[2] and result_table[3]:
		return True
	return False		


#Code for command line
if __name__ == "__main__":
	if len(sys.argv) == 2:
		addr = sys.argv[1]
		print is_valid(addr)
	else:
		print "Please supply a valid address. Example: $python validity_checker.py 0x8899AABB"
	