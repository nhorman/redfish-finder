#!/usr/bin/python

import os
import subprocess
import ipaddress

#
# Helper function to consume the dmidecode output
#
def cursor_consume_next(cursor, needle):
	idx = cursor.find(needle)
	if idx == -1:
		return None
	return cursor[idx + len(needle):]

#
# Some basic enumeration classes
#
class AssignType():
	UNKNOWN = 0
	STATIC = 1
	DHCP = 2
	AUTOCONF = 3
	HOSTSEL = 4

	typestring = ["Unknwon", "Static", "DHCP", "Autoconf", "Host Selected"]


#
# NetDevice class, used to determine the interface name that can reach the BMC
#
class NetDevice(object):
	def __init(self):
		self.name = "Unknown"

	def getifcname(self):
		return self.name

	def __str__(self):
		return "Interface: " + self.name

#
# Subclass of NetDevice, parses the dmidecode output
# to discover interface name
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


#
# class to hold our host config parameters
#
class HostConfig():
	def __init__(self, cursor):
		self.address = None
		self.mask = None
		cursor = cursor_consume_next(cursor, "Host IP Assignment Type: ")
		if cursor == None:
			return None
		if cursor.split()[0] == "Static":
			self.assigntype = AssignType.STATIC
			cursor = cursor_consume_next(cursor, "Host IP Address Format: ")
			if cursor.split()[0] == "IPv4":
				cursor = cursor_consume_next(cursor, "IPv4 Address: ")
				self.address = ipaddress.IPv4Address(unicode(cursor.split()[0], "utf-8"))
				cursor = cursor_consume_next(cursor, "IPv4 Mask: ")
				self.mask = ipaddress.IPv4Address(unicode(cursor.split()[0], "utf-8"))
			elif cursor.split()[0] == "IPv6":
				cursor = cursor_consume_next(cursor, "IPv6 Address: ")
				self.address = ipaddress.IPv6Address(unicode(cursor.split()[0], "utf-8"))
				cursor = cursor_consume_next(cursor, "IPv6 Mask: ")
				self.mask = ipaddress.IPv4Address(unicode(cursor.split()[0], "utf-8"))
		elif cursor.split()[0] == "DHCP":
			self.assigntype = AssignType.DHCP
		else:
			# Support the other types later
			return None

	def __str__(self):
		val = "Host Config(" + AssignType.typestring[self.assigntype] + ")" 
		if (self.assigntype == AssignType.STATIC):
			val = val + " " + str(self.address) + "/" + str(self.mask)
		return val

#
# Class to hold Redfish service information
#
class ServiceConfig():
	def __init__(self, cursor):
		self.address = None
		self.mask = None
		cursor = cursor_consume_next(cursor, "Redfish Service IP Discovery Type: ")
		if cursor == None:
			return None
		if cursor.split()[0] == "Static":
			self.assigntype = AssignType.STATIC
			cursor = cursor_consume_next(cursor, "Redfish Service IP Address Format: ")
			if cursor.split()[0] == "IPv4":
				cursor = cursor_consume_next(cursor, "IPv4 Redfish Service Address: ")
				self.address = ipaddress.IPv4Address(unicode(cursor.split()[0], "utf-8"))
				cursor = cursor_consume_next(cursor, "IPv4 Redfish Service Mask: ")
				self.mask = ipaddress.IPv4Address(unicode(cursor.split()[0], "utf-8"))
			elif cursor.split()[0] == "IPv6":
				cursor = cursor_consume_next(cursor, "IPv6 Redfish Service Address: ")
				self.address = ipaddress.IPv6Address(unicode(cursor.split()[0], "utf-8"))
				cursor = cursor_consume_next(cursor, "IPv6 Mask: ")
				self.mask = ipaddress.IPv4Address(unicode(cursor.split()[0], "utf-8"))
		elif cursor.split()[0] == "DHCP":
			self.assigntype = AssignType.DHCP
		else:
			# Support the other types later
			return None

		cursor = cursor_consume_next(cursor, "Redfish Service Port: ")
		self.port = int(cursor.split()[0])
		cursor = cursor_consume_next(cursor, "Redfish Service Vlan: ")
		self.vlan = int(cursor.split()[0])
		cursor = cursor_consume_next(cursor, "Redfish Service Hostname: ")
		self.hostname = cursor.split()[0]


	def __str__(self):
		val = "Service Config(" + AssignType.typestring[self.assigntype] + ")" 
		if (self.assigntype == AssignType.STATIC):
			val = val + " " + str(self.address) + "/" + str(self.mask)
		return val

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
			self.device = USBNetDevice(cursor)

		if self.device == None:
			return None

		# Now find the Redfish over IP section
		cursor = cursor_consume_next(cursor, "Protocol ID: 04 (Redfish over IP)\n")
		if (cursor == None):
			return None

		self.hostconfig = HostConfig(cursor)
		if self.hostconfig == None:
			return None

		self.serviceconfig = ServiceConfig(cursor)
		if self.serviceconfig == None:
			return None


	def __str__(self):
		return str(self.device) + " | " + str(self.hostconfig) + " | " + str(self.serviceconfig)


def get_info_from_dmidecode():
	dmioutput = subprocess.check_output(["/usr/sbin/dmidecode", "-t42"])
	return dmiobject(dmioutput)

def main():
	smbios_info = get_info_from_dmidecode()
	print smbios_info


if __name__ == "__main__":
	main()


