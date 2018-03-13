
from pxdebugtools import pxdebug

def print_math():
    two = 2
    three = 3
    print(2*3)

if __name__ == "__main__":
   number = 10
   print_math()
   print ("a regular print message from python that works when xxdebug has been disabled")
   if pxdebug.enabled():
       print("this print only occurs when pxdebug is enabled")
   pxdebug.basic("basic output message from xxdebug (will be logged to file if autologging enabled)")
   pxdebug.breakpoint("regular breakpoint here")
   pxdebug.verbose("verbose output message from xxdebug (will be logged to file if autologging enabled)") 
   pxdebug.breakpoint("hidden breakpoint here", hide=True)
   pxdebug.extreme("extreme output message from xxdebug (will be logged to file if autologging enabled)", linesplit=True)
   if pxdebug.flag() == True:
       print ("this message is displayed if the pxdebug test flag has been set using pxdebug --setflag")
   if pxdebug.extreme() == True:
       for i in [1,2,3,4]:
           print ("this code only executes when debug level set to extreme")
   

