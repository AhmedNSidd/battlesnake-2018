import socket, select, os, sys

#non-buffered stdout
#sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

if(len(sys.argv) == 1):
    port = 5505
else:
    port = int(sys.argv[1])
    
print("listening on port {}".format(port))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', port))
s.listen(1)

while 1:
  conn, addr = s.accept()
  print('Connected by {}'.format(addr))

  conn.setblocking(0)

  ready = select.select([conn], [], [], 2)
  if ready[0]:
      data = conn.recv(4096)
      print(data)

