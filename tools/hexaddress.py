class NoHexPositionAvailable(Exception):
	'Tried to access invalid Hex position'
	pass

class HexAddress:

	##.  1  2   3  4
	## 0xFF FF  FF FF

	def __init__(self, address):
		self.value = address
		self.original = address
		self.bytes = {1:None, 2:None, 3:None, 4:None}
		self.initialize_bytes()

	def initialize_bytes(self):
		bytes = self.split_bytes()
		self.bytes[1] = bytes[0]
		self.bytes[2] = bytes[1]
		self.bytes[3] = bytes[2]
		self.bytes[4] = bytes[3]

	def byte_change(self, pos, value, change_type='add'):
		old_address = HexAddress(self.value)
		if change_type.lower() == 'add':
			# return self.byte_add(pos, value)
			if value > 0xff:
				value = value%0x100
				try:
					self.byte_change(pos-1, self.bytes[pos-1]+1)
				except:
					raise NoHexPositionAvailable
		elif change_type.lower() == 'subtract':
			#return self.byte_subtract(pos, value)
			if value < 0x00:
				value = value+0x100
				try:
					self.byte_change(pos-1, self.bytes[pos-1]-0x1, 'subtract')
				except:
					raise NoHexPositionAvailable
		self.bytes[pos] = value
		temp = [self.bytes[1], self.bytes[2], self.bytes[3], self.bytes[4]]
		address = ''
		#Necessary to enforce at preceeding zeros
		for x in temp:
			j = hex(x)[2:]
			if len(j) == 1:
				j = "0{0}".format(j)
			address = address + j
		self.value = int(address,16)
		return self.which_changed(old_address)

	def which_changed(self, old_address):
		changed = []
		for b in self.bytes:
			if self.bytes[b] != old_address.bytes[b]:
				changed.append(b)
		changed.sort()
		return changed

	def split_bytes(self, b=None):
		temp_address = self.value%int('1000000',16)
		byte1 = (self.value-temp_address)/int('1000000',16)
		temp2 = self.value%int('10000',16)
		byte2 = (temp_address-temp2)/int('10000',16)
		temp_address = temp2
		temp2 = self.value%int('100',16)
		byte3 = (temp_address-temp2)/int('100',16)
		byte4 = temp2
		bytes = [byte1, byte2, byte3, byte4]
		if not b == None:
			return bytes[4-b]
		else:
			return bytes