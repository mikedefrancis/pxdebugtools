# pxdebugtools
* This program allows you to add very simple color debug prints throughout your python modules.
     
*     It allows you to set different verbosity levels for each of those debug prints.
     
*     It allows you to automatically log all of those debug prints to log files that are easy to find.
     
*     It allows you to add breakpoints within your python code for step debugging via pdb.
     
*     It allows you to add custom debug flags.
     
*     It allows you to change all of the functionality of all of the debug calls throughout all of your programs.
     
*     This is accomplished using a command like program calle pxdebug that writes a file to ~/.pxdebug/pxdebug.env.
     
*     This file contains many environment variables that get reloaded when the command line program is run or the python module is loaded.
* THIS ONLY WORKS ON LINUX RIGHT NOW.
* THIS HAS ONLY BEEN TESTED ON UBUNTU 16.04 (and even then it has only been tested lightly!)
* to install, 
    Run './install_pxdebugtools'

    This installs the executable program, pxdebug, to /usr/bin.
    This additionally install the pxdebugtools.py python module to your python package directory.

 * To use pxdebugtools... See 'example.py' for a clear demonstration of usage. 
    
    First add some calls to pxdebug.basic("message"), pxdebug.verbose("message2", pxdebug.breakpoint(), etc. to your normal program.
    Then run pxdebug to select your verbosity and debugging options.
    Then run your python program and watch the debug prints show up in color.
