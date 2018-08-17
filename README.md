# redfish-finder


## What is redfish?
Redfish is a standard developed by the DMTF to provide a RESTful interface to
System Board Management Computers (BMC's):
https://www.dmtf.org/sites/default/files/standards/documents/DSP0266_1.4.1.pdf

Redfish allows for both remote management of large hardware installations via a
centralized location over a network, as well as for local OS hardware monitoring
and management using the same REST api via a host accessible interface

## What is the redfish host interface specification?
To enable localized OS access to the local system BMC, the BMC exports a system
management controller infomation block via SMBIOS:
https://www.dmtf.org/sites/default/files/DSP0270_1.0.1.pdf

This block publishes information to the host OS, which it can use to locally
access the BMC.  This information includes, among other items:
* The OS network interface over which the BMC is reachable
* The HOST OS Network interface settings/addresses which it should configure
* The Redfish Service Network Address


## What does redfish-finder do?
One of the difficulties of using the Redfish host api is the translation of the
SMBIOS data above into meaningful application configuration data.  That is to
say, any application wishing to use the Redfish API must first:
* parse the smbios data
* determine if the network interface has been configured properly
* translate the service information into a url to access the Redfish API

redfish-finder centralizes that functionality, so that applications can simply
point to a canonical name to access the API without additional configuration.
Specifically, redfish-finder:
* parses the smbios data for Redfish access
* Translates the device specification to an OS interface name
* Uses NetworkManager to configure the network interface with the appropriate
settings
* Adds an entry to /etc/hosts mapping the name redfish-localhost to the
Discovered Redfish service address.

Applications wishing to use the local redfish service can then point to the
canonical url:
https://redfish-localhost/redfish/v1
to use the service without additional configuration

## What are the requirements for redfish-finder
Currently, to use redfish you need:
* python version 2 or later
* the dmidecode utility, at a version capable of parsing type 42 data
* the nmcli utility to build networkmanager configurations

