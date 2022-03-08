from robohash import Robohash
import random, string, sys
#i=sys.argv[1]
#k = 251
k = 32
size = 12000
filename = ''.join(random.choices(string.ascii_letters + string.digits, k=k))
try:
  rh = Robohash(filename)
  rh.assemble(roboset='set4', sizex=size, sizey=size)
  with open("/home/harlan/"+filename+".png", "wb") as f:
    rh.img.save(f, format="png")
  print(filename)
except:
  print()

