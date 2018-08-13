#!/usr/bin/python

import subprocess

def cursor_consume_next(cursor, needle):
	idx = cursor.find(needle)
	if idx == -1:
		return None
	return cursor[idx + len(needle):]

class NetDevice(object):
	def __init(self):
		self.name = "Unknown"

class USBNetDevice(NetDevice):
	def __init__(self, dmioutput):
		super(NetDevice, self).__init__()

class dmiobject():
	def __init__(self, dmioutput):
		cursor = dmioutput
		# Find the type 42 header, if not found, nothing to do here
		cursor = cursor_consume_next(cursor, "Management Controller Host Interface\n") 
		if (cursor == None):
			return None
		cursor = cursor_consume_next(cursor, "Host Interface Type: Network\n")
		if (cursor == None):
			return None

		# If we get here then we know this is a network interface device
		cursor = cursor_consume_next(cursor, "Device Type: ")
		# The next token should either be:
		# USB
		# PCI/PCIe
		# OEM
		# Unknown
		dtype = cursor.split()[0]
		if (dtype == "USB"):
			self.device = USBNetDevice(dmioutput)


def get_info_from_dmidecode():
	dmioutput = subprocess.check_output(["/usr/sbin/dmidecode", "-t42"])
	return dmiobject(dmioutput)

def main():
	smbios_info = get_info_from_dmidecode()



if __name__ == "__main__":
	main()


