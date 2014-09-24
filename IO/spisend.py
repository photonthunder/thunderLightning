#!/usr/bin/env python3

import posix
import struct
from ctypes import addressof, create_string_buffer, sizeof, string_at
from ctypes import Structure, c_uint64, c_uint32, c_uint16, c_uint8, c_char
from fcntl import ioctl
import time

_IOC_NRBITS =	8
_IOC_TYPEBITS =	8

_IOC_SIZEBITS =	14
_IOC_DIRBITS =	2

_IOC_NRMASK =   (1 << _IOC_NRBITS) - 1
_IOC_TYPEMASK = (1 << _IOC_TYPEBITS) - 1
_IOC_SIZEMASK = (1 << _IOC_SIZEBITS) - 1
_IOC_DIRMASK =  (1 << _IOC_DIRBITS) - 1

_IOC_NRSHIFT =	 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT =	 _IOC_SIZESHIFT + _IOC_SIZEBITS

_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ = 2

def _IOC(dir, type, nr, size):
    return (dir  << _IOC_DIRSHIFT) | \
           (type << _IOC_TYPESHIFT) | \
           (nr   << _IOC_NRSHIFT) | \
           (size << _IOC_SIZESHIFT)

def _IOC_TYPECHECK(t):
    return sizeof(t)

def _IOR(type, nr, size):
    return _IOC(_IOC_READ, type, nr, _IOC_TYPECHECK(size))

def _IOW(type, nr, size):
    return _IOC(_IOC_WRITE, type, nr, _IOC_TYPECHECK(size))

SPI_CPHA = 0x01
SPI_CPOL = 0x02

SPI_MODE_0 = 0
SPI_MODE_1 = SPI_CPHA
SPI_MODE_2 = SPI_CPOL
SPI_MODE_3 = SPI_CPOL|SPI_CPHA

SPI_CS_HIGH = 0x04
SPI_LSB_FIRST = 0x08
SPI_3WIRE = 0x10
SPI_LOOP = 0x20
SPI_NO_CS = 0x40
SPI_READY = 0x80

SPI_IOC_MAGIC = ord('k') #107

class spi_ioc_transfer(Structure):

    _fields_ = [
        ("tx_buf", c_uint64),
        ("rx_buf", c_uint64),
        ("len", c_uint32),
        ("speed_hz", c_uint32),
        ("delay_usecs", c_uint16),
        ("bits_per_word", c_uint8),
        ("cs_change", c_uint8),
        ("pad", c_uint32)]

    __slots__ = [name for name,type in _fields_]

def SPI_MSGSIZE(N):
    if ((N)*(sizeof(spi_ioc_transfer))) < (1 << _IOC_SIZEBITS):
        return (N)*(sizeof(spi_ioc_transfer))
    else:
        return 0

def SPI_IOC_MESSAGE(N):
    return _IOW(SPI_IOC_MAGIC, 0, c_char*SPI_MSGSIZE(N))

# Read / Write of SPI mode (SPI_MODE_0..SPI_MODE_3)
SPI_IOC_RD_MODE =			_IOR(SPI_IOC_MAGIC, 1, c_uint8)
SPI_IOC_WR_MODE =			_IOW(SPI_IOC_MAGIC, 1, c_uint8)

# Read / Write SPI bit justification
SPI_IOC_RD_LSB_FIRST =		_IOR(SPI_IOC_MAGIC, 2, c_uint8)
SPI_IOC_WR_LSB_FIRST =		_IOW(SPI_IOC_MAGIC, 2, c_uint8)

# Read / Write SPI device word length (1..N)
SPI_IOC_RD_BITS_PER_WORD =	_IOR(SPI_IOC_MAGIC, 3, c_uint8)
SPI_IOC_WR_BITS_PER_WORD =	_IOW(SPI_IOC_MAGIC, 3, c_uint8)

# Read / Write SPI device default max speed hz
SPI_IOC_RD_MAX_SPEED_HZ =		_IOR(SPI_IOC_MAGIC, 4, c_uint32)
SPI_IOC_WR_MAX_SPEED_HZ =		_IOW(SPI_IOC_MAGIC, 4, c_uint32)

class spibus():
	fd=None
	write_buffer=create_string_buffer(50)
	read_buffer=create_string_buffer(50)

	ioctl_arg = spi_ioc_transfer(
		tx_buf=addressof(write_buffer),
		rx_buf=addressof(read_buffer),
		len=1,
		delay_usecs=0,
		speed_hz=5000000,
		bits_per_word=8,
		cs_change = 0,
	)

	def __init__(self,device):
		self.fd = posix.open(device, posix.O_RDWR)
		ioctl(self.fd, SPI_IOC_RD_MODE, " ")
		ioctl(self.fd, SPI_IOC_WR_MODE, struct.pack('I',0))

	def send(self,len):
		self.ioctl_arg.len=len
		ioctl(self.fd, SPI_IOC_MESSAGE(1),addressof(self.ioctl_arg))

if __name__ == '__main__':
	#Open the SPI bus 0
	spi1bus = spibus("/dev/spidev32765.0")

	#Send two characters
	spi1bus.write_buffer[0]=0x55
	spi1bus.write_buffer[1]=0xAA

	spi1bus.send(2)

	#Shows the 2 byte received in full duplex in hex format
	print(hex(ord(spi1bus.read_buffer[0])))
	print(hex(ord(spi1bus.read_buffer[1])))



