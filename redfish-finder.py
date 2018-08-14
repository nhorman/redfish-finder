#!/usr/bin/python

import os
import subprocess

def cursor_consume_next(cursor, needle):
	idx = cursor.find(needle)
	if idx == -1:
		return None
	return cursor[idx + len(needle):]

class NetDevice(object):
	def __init(self):
		self.name = "Unknown"

	def getifcname(self):
		return self.name

class USBNetDevice(NetDevice):
	def __init__(self, dmioutput):
		super(NetDevice, self).__init__()
		dmioutput = cursor_consume_next(dmioutput, "idVendor: ")
		# Strip the 0x off the front of the vendor and product ids
		#NOTE: IM SWAPPING THESE BECAUSE THEY ARE BACKWARDS ON MY DEVEL SYSTEM
		#THIS NEEDS TO BE REVERTED
		self.product = (dmioutput.split()[0])[2:]
		self.vendor = (dmioutput.split()[2])[2:]

		# Now we need to find the corresponding device name in sysfs
		if self.find_device() == False:
			return None

	def getifcname(self, dpath):
		for root, dirs, files in os.walk(dpath, topdown=False):
			for d in dirs:
				try:
					if d != "net":
						continue
					dr = os.listdir(os.path.join(root, d))
					self.name = dr[0]
					return True
				except:
					continue
		return False

	def find_device(self):
		for root,dirs,files in os.walk("/sys/bus/usb/devices", topdown=False):
			for d in dirs:
				try:
					f = open(os.path.join(root, d, "idVendor"))
					lines = f.readlines()
					if lines[0][0:4] != self.vendor:
						f.close()
						continue
					f.close()
					f = open(os.path.join(root, d, "idProduct"))
					lines = f.readlines()
					if lines[0][0:4] != self.product:
						f.close()
						continue
					f.close()
					# We found a matching product and vendor, go find the net directory
					# and get the interface name
					return self.getifcname(os.path.join(root, d))
				except:
					continue
		return False 

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


