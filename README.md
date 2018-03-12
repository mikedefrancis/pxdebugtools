# pxdebugtools
# THIS ONLY WORKS ON LINUX RIGHT NOW
# THIS HAS ONLY BEEN TESTED ON UBUNTU 16.04 (and even then it has only been tested lightly!)
# to install, run './install_pxdebugtools'
# this installs the executable program, pxdebug, to /usr/bin
# this additionally install the pxdebugtools.py python module to your python package directory
# see 'example.py' for a clear demonstration of usage. 
# to use pxdebugtools...
# first add some calls to pxdebug.basic("message"), pxdebug.verbose("message2", pxdebug.breakpoint(), etc. to your normal program.
# then run pxdebug to select your verbosity and debugging options 
# then run your python program and watch the debug prints show up in color
