import operator

#Work in progresses. Need to do a different method because I cannot write in Binary.

def main():
	print "Opening file"
	f = open('memory_addresses.txt', 'r')
	data = f.read()
	f.close()
	addresses = data.split('\n')
	try:
		addresses.remove('')
	except:
		"No empty records"
	patterns = {}
	print "Counting Patterns"
	for a in addresses:
		b1 = a[:2]
		b2 = a[2:4]
		b3 = a[4:6]
		b4 = a[-2:]
		try:
			patterns[b1] += 1
		except:
			patterns[b1] = 1
		try:
			patterns[b2] += 1
		except:
			patterns[b2] = 1
		try:
			patterns[b3] += 1
		except:
			patterns[b3] = 1
		try:
			patterns[b4] += 1
		except:
			patterns[b4] = 1
	print "Sorting"
	print "length of patterns: {0}".format(len(patterns))
	sorted_x = sorted(patterns.items(), key=operator.itemgetter(1))
	print "Writing pattern"
	o = open("pattern_count.txt",'w')
	print "length of sorted_x: {0}".format(len(sorted_x))
	sl = []
	for s in reversed(sorted_x):
		sl.append(s[0])
		o.write("{0}:{1}\n".format(s[0],s[1]))
	o.close()
	return sl, addresses

def compress(sorted_x, addresses):
	print "compressing"
	ordered_list = []
	binary = ''
	print "Building Binary"
	for a in addresses:
		b1 = a[:2]
		b2 = a[2:4]
		b3 = a[4:6]
		b4 = a[-2:]
		binary += "{0}0".format('1'*(sorted_x.index(b1)+1))
		binary += "{0}0".format('1'*(sorted_x.index(b2)+1))
		binary += "{0}0".format('1'*(sorted_x.index(b3)+1))
		binary += "{0}0".format('1'*(sorted_x.index(b4)+1))
	print "Writing Binary"
	o = open("compressed.bin",'wb')
	o.write(int(binary,2))
	o.close()

def get_addresses_from_binary():
	f = open('compressed.bin','rb')
	binary = f.read()
	f.close()
	f = open('pattern_count.txt','r')
	pattern = f.read()
	pattern = pattern.split('\n')
	pattern_dict = {}
	for x, p in enumerate(pattern):
		key = p[:p.find(':')]
		pattern_dict[key] = '1'*(x+1)


def test_binary():
	print "opening file"
	f = open('memory_addresses.txt', 'r')
	data = f.read()
	f.close()
	addresses = data.split('\n')
	addresses2 = get_addresses_from_binary()
	print "Address list == Binary Address list: {0}".format(adresses == addresses2)

if __name__ == '__main__':
	sorted_x, addresses = main()
	compress(sorted_x, addresses)