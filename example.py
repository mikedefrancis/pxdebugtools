
from xxdebug import *


if __name__ == "__main__":
   print ("a regular print message from python that works when xxdebug has been disabled")
   xxdebug_print("basic output message from xxdebug (will be logged to file if autologging enabled)")
   xxdebug_bp("regular breakpoint here")
   xxdebug_verbose("verbose output message from xxdebug (will be logged to file if autologging enabled)") 
   xxdebug_bp("hidden breakpoint here", hidden=True)
   xxdebug_su("superuser output message from xxdebug (will be logged to file if autologging enabled)") 
