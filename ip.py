import ipaddress

x = ipaddress.ip_interface('192.1.6.43')
print (f'Version: {x.version}\t Network: {x.network}')

y = ipaddress.ip_interface('2001:db8::1')
print (f'Version: {y.version}\t Network: {y.network}')

n = x.network

print (n)
for i in n.hosts():
    print(i)
