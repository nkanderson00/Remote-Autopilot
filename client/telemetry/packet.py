import struct
		   
terminator = 255


def decode(data, formats:dict):
	
	byte = 0
	prefix_index = 0
	fmt = "B"
	values = {}
	prefixes = []
	byte_values = []
	
	while prefix_index < len(data):
		byte = data[prefix_index]
		prefix_index += 1
		if byte == terminator: break
		if not formats.get(byte): return {}
		fmt += "B"
		prefixes.append(byte)
		
	for prefix in prefixes:
		fmt += formats[prefix]
		
	if not fmt: return {}

	try: data = struct.unpack(fmt, data)
	except: return {}
	
	total_offset = len(prefixes)+1
	for i, prefix in enumerate(prefixes):
		offset = len(formats[prefix])
		values[prefix] = data[total_offset:total_offset+offset]
		total_offset += offset
		
	return values

def encode(data:dict, formats:dict):
	
	fmt = ""
	values = list(data.keys())
	values.append(terminator)
	
	fmt += "B"*len(values)
	
	for key, value in data.items():
		if formats.get(key):
			fmt += formats[key]
			values.extend(value)
		else: b''
	
	try: data = struct.pack(fmt, *values)
	except: data = b''
	
	return data
		
	
#as you can refer to line 4, you can see that key 0 can be used
#as a client identifier, 1 can be position, 2 can be rotation.
#these setups can be customized however you want however you can
#only have 0-254 keys (255 is reserved as a terminator)
#data = {0: (42,), 1: (-0.5, 1267.36, -56.7)}

#the data dict is first encoded into bytes.
#data = encode(data)

#using that encoded data, we can next decode it.
#you can see the result is the same as the original data.
#print(decode(data))

#if the data is malformed in encoding or decoding,
#encode() will return an empty byte list
#decode() will return an empty dictionary
