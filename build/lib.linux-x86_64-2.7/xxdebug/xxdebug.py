#!/usr/bin/env python
# @author mikedefrancis
# www.github.com/mikedefrancis
# a usable debug framework for python prints, juicy pdb, module-based debug integration
# nicest thing: enable/disable all of your debug from a cli program. No need to remove your debug prints from your programs anymore.

#########################################################
####         XXDEBUG          ###########################
#### a juicy python 2.7 and up debug framework ##########
#########################################################

import sys
import os
import argparse
import ntpath

import subprocess
import shutil
from shutil import copy2
from os.path import expanduser

# really nice debuging context utilities
import pdb
import inspect


class dlevel():
    DBG_NONE = 0
    DBG_BASIC = 1
    DBG_VERBOSE = 2
    DBG_SUPERUSER = 3



# WRITE 'em HACK to make environment variables persist using a file:
def write_xxdebug_environment_vars_to_file():
    home = expanduser("~")
    thispath = os.path.join(home,'.xxdebug')
    if not os.path.exists(thispath):
        print "creating ~/.xxdebug/ folder"
        os.makedirs(thispath)
    env_file = open(thispath + '/xxdebug.env', 'w+')

    write_env_var_to_file(env_file, 'XXDEBUG_LEVEL')
    write_env_var_to_file(env_file, 'XXDEBUG_SHOW_ONLY_THIS_LEVEL')
    write_env_var_to_file(env_file, 'XXDEBUG_COLOR')
    write_env_var_to_file(env_file, 'XXDEBUG_LOGGING')
    write_env_var_to_file(env_file, 'XXDEBUG_LOGPATH')
    write_env_var_to_file(env_file, 'XXDEBUG_LOGNAME')
    write_env_var_to_file(env_file, 'XXDEBUG_ENABLETRACE')
    write_env_var_to_file(env_file, 'XXDEBUG_ENABLEHIDDENTRACE')


    env_file.close()

# file must already be open
def write_env_var_to_file(f, varname):
    val = os.environ.get(varname)
    if val is not None:
        #  print "writing envvar to file || " + "export " + varname + "=" + str(val)
        f.write("export " + varname + "=" + str(val) + '\n') 

# READ 'em HACK to make environment variables persist using a file:
def get_xxdebug_environment_vars_from_file():
    home = expanduser("~")
    thispath = os.path.join(home,'.xxdebug')
    if not os.path.exists(thispath):
        print "creating ~/.xxdebug/ folder"
        os.makedirs(thispath)
    else:
        if os.path.exists(thispath + '/xxdebug.env'):
            with open(thispath + '/xxdebug.env') as f:
                for line in f:
                    if 'export' not in line:
                        continue
                    # Remove leading `export `
                    # then, split name / value pair
                    key, value = line.replace('export ', '', 1).strip().split('=', 1)
                    #  print "reading envvar || " + str(key) + "=" + str(value)
                    os.environ[key] = value



get_xxdebug_environment_vars_from_file()

#from termcolor import colored
#ONLY INCLUDE COLORS IF WE ARE ON LINUX
#xxcolors can cause errors on certain platforms so do some error checking around the import
#  if os.name == 'posix':
#      env_debug_color = os.environ.get('XXDEBUG_COLOR')
#      if env_debug_color is not None:
#          if env_debug_color.upper() == "COLOR":
#              try:
#                  from xxcolors import *
#              except:
#                  print "xxdebug failed to load colors module. Make sure that you have xxcolors.py."
#                  os.exit(-1)








######################################################################
## COLORS STUFF ######################################################


# NOTE TO USERS:
# I COPIED THIS ENTIRE FILE INTO THE CONTENTS OF THIS ONE (HACKS) 
# IT IS REALLY, REALLY UGLY. BUT IT MAKES IT EASIER TO USE XXDEBUG WITHOUT HAVING ANY DEPENDENCIES ON THIRD PARTY LIBRARIES

#
# colors.py
#
# Color Code Functions in Python
# Works on Winblows or *nix
#
# By: torBot
#
# Use it like a module & import the available functions, then call as you like:
#    from colors import *
#    status("This is a status message")
#    pad(); print red("This is red text")
#    pad(); print blue("This is blue text\n")
#    caution("Cautionary Message")
#    pad()
#    error("This is an error message\n\n")
#

from ctypes import Structure, c_short, c_ushort, byref

if os.name == 'nt' or sys.platform.startswith('win'):
  from ctypes import windll, Structure, c_short, c_ushort, byref

# Winblows Constants
################################
SHORT = c_short
WORD = c_ushort

# winbase.h
STD_INPUT_HANDLE  = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE  = -12

# wincon.h structs
class COORD(Structure):
  _fields_ = [ ("X", SHORT), ("Y", SHORT)]

class SMALL_RECT(Structure):
  _fields_ = [("Left", SHORT), ("Top", SHORT),
    ("Right", SHORT), ("Bottom", SHORT)]

class CONSOLE_SCREEN_BUFFER_INFO(Structure):
  _fields_ = [
    ("dwSize", COORD), ("dwCursorPosition", COORD),
    ("wAttributes", WORD), ("srWindow", SMALL_RECT),
    ("dwMaximumWindowSize", COORD)]


# OS Color Definitions & Setup
################################
if os.name == 'nt' or sys.platform.startswith('win'):
  stdout_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
  SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
  GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo

  # wincon.h
  DIM  = 0x00   # dim
  RS   = ""     # reset (?)
  HC   = 0x08   # hicolor
  BHC  = 0x80   # background hicolor
  UL   = ""     # underline (no workie on winblows)
  INV  = ""     # inverse background and foreground (no workie on winblows)
  FBLK = 0x0000 # foreground black
  FBLK = 0x0008 # foreground grey
  FRED = 0x0004 # foreground red
  FGRN = 0x0002 # foreground green
  FYEL = 0x0006 # foreground yellow
  FBLU = 0x0001 # foreground blue
  FMAG = 0x0005 # foreground magenta
  FCYN = 0x0003 # foreground cyan
  FWHT = 0x0007 # foreground white (grey)
  BBLK = 0x0000 # background black
  BBLK = 0x0080 # background grey
  BRED = 0x0040 # background red
  BGRN = 0x0020 # background green
  BYEL = 0x0060 # background yellow
  BBLU = 0x0010 # background blue
  BMAG = 0x0050 # background magenta
  BCYN = 0x0030 # background cyan
  BWHT = 0x0070 # background white (grey)
else:
  # ANSI color code escapes, for *nix
  DIM  = ""       # dim (no workie)
  RS="\033[0m"    # reset
  HC="\033[1m"    # hicolor
  UL="\033[4m"    # underline
  INV="\033[7m"   # inverse background and foreground
  FBLK="\033[30m" # foreground black
  FRED="\033[31m" # foreground red
  FGRN="\033[32m" # foreground green
  FYEL="\033[33m" # foreground yellow
  FBLU="\033[34m" # foreground blue
  FMAG="\033[35m" # foreground magenta
  FCYN="\033[36m" # foreground cyan
  FWHT="\033[37m" # foreground white
  BBLK="\033[40m" # background black
  BRED="\033[41m" # background red
  BGRN="\033[42m" # background green
  BYEL="\033[43m" # background yellow
  BBLU="\033[44m" # background blue
  BMAG="\033[45m" # background magenta
  BCYN="\033[46m" # background cyan
  BWHT="\033[47m" # background white

def get_text_attr():
  """
      Returns the character attributes (colors) of the console screen buffer.
      Used for windows only
  """
  if os.name == 'nt' or sys.platform.startswith('win'):
    try:
      csbi = CONSOLE_SCREEN_BUFFER_INFO()
      GetConsoleScreenBufferInfo(stdout_handle, byref(csbi))
      return csbi.wAttributes
    except Exception, e:
      pass
  return None


def set_text_attr(color):
  """
      Sets the character attributes (colors) of the console screen
      buffer. Color is a combination of foreground and background color,
      foreground and background intensity.
      Used for windows only
  """
  if os.name == 'nt' or sys.platform.startswith('win'):
    try:
      SetConsoleTextAttribute(stdout_handle, color)
      return True
    except Exception, e:
      pass
  return False


def windows_default_colors():
  """
      Checks and returns the current windows console color mapping
      Returns the necessary foreground and background code to reset later
      Used for windows only
  """
  if os.name == 'nt' or sys.platform.startswith('win'):
    try:
      default_colors = get_text_attr()
      default_bg = default_colors & 0x0070
      return default_bg
    except Exception, e:
      pass
  return None


def restore_windows_colors(default_gb):
  """
      Set or Restore the console colors to the provided foreground + background codes
      Returns True or False
      Used for windows only
  """
  if os.name == 'nt' or sys.platform.startswith('win'):
    try:
      set_text_attr(default_gb)
      return True
    except Exception, e:
      pass
  return False


# Some Simple Print functions
#############################

def caution(msg): 
  """ [*] Print a cautionary message to user """
  if os.name == 'nt' or sys.platform.startswith('win'):
    windows_user_default_color_code = windows_default_colors()
    set_text_attr(FYEL | BBLK | HC | BHC)
    sys.stdout.write("[")
    set_text_attr(FWHT | BBLK | HC | BHC)
    sys.stdout.write("*")
    set_text_attr(FYEL | BBLK | HC | BHC)
    sys.stdout.write("] ")
    set_text_attr(FWHT | BBLK | HC | BHC)
    sys.stdout.write(str(msg) + "\n")
    restore_windows_colors(windows_user_default_color_code)
  else:
    print HC + FYEL + "[" + FWHT + "-" + FYEL + "] " + FWHT + str( msg ) + RS


def good( msg ): 
  """ [*] Print a success message to user """
  if os.name == 'nt' or sys.platform.startswith('win'):
    windows_user_default_color_code = windows_default_colors()
    set_text_attr(FGRN | BBLK | HC | BHC)
    sys.stdout.write("[")
    set_text_attr(FWHT | BBLK | HC | BHC)
    sys.stdout.write("*")
    set_text_attr(FGRN | BBLK | HC | BHC)
    sys.stdout.write("] ")
    set_text_attr(FWHT | BBLK | HC | BHC)
    sys.stdout.write(str(msg) + "\n")
    restore_windows_colors(windows_user_default_color_code)
  else:
    print HC + FGRN + "[" + FWHT + "*" + FGRN + "] " + FWHT + str( msg ) + RS


def bad( msg ): 
  """ [x] Print a warning or bad message to user """
  if os.name == 'nt' or sys.platform.startswith('win'):
    windows_user_default_color_code = windows_default_colors()
    set_text_attr(FRED | BBLK | HC | BHC)
    sys.stdout.write("[")
    set_text_attr(FWHT | BBLK | HC | BHC)
    sys.stdout.write("x")
    set_text_attr(FRED | BBLK | HC | BHC)
    sys.stdout.write("] ")
    set_text_attr(FWHT | BBLK | HC | BHC)
    sys.stdout.write(str(msg) + "\n")
    restore_windows_colors(windows_user_default_color_code)
  else:
    print HC + FRED + "[" + FWHT + "x" + FRED + "] " + FWHT + str( msg ) + RS


def status(msg ): 
  """ [*] Print a status message to user """
  if os.name == 'nt' or sys.platform.startswith('win'):
    windows_user_default_color_code = windows_default_colors()
    set_text_attr(FBLU | BBLK | HC | BHC)
    sys.stdout.write("[")
    set_text_attr(FWHT | BBLK | HC | BHC)
    sys.stdout.write("*")
    set_text_attr(FBLU | BBLK | HC | BHC)
    sys.stdout.write("] ")
    set_text_attr(FWHT | BBLK | HC | BHC)
    sys.stdout.write(str(msg) + "\n")
    restore_windows_colors(windows_user_default_color_code)
  else:
    print HC + FBLU + "[" + FWHT + "*" + FBLU + "] " + FWHT + str( msg ) + RS


def error( msg ): 
  """ [ERROR] Print an ERROR message to user """
  if os.name == 'nt' or sys.platform.startswith('win'):
    windows_user_default_color_code = windows_default_colors()
    set_text_attr(FRED | BBLK | HC | BHC)
    sys.stdout.write("[")
    set_text_attr(FWHT | BBLK | HC | BHC)
    sys.stdout.write("ERROR")
    set_text_attr(FRED | BBLK | HC | BHC)
    sys.stdout.write("] ")
    set_text_attr(FWHT | BBLK | HC | BHC)
    sys.stdout.write(str(msg) + "\n")
    restore_windows_colors(windows_user_default_color_code)
  else:
    print HC + FRED + "[" + FWHT + "ERROR" + FRED + "] " + FWHT + str( msg ) + RS


def underline( msg ): 
  """ Underline message string (no workie on windows) """
  if os.name == 'nt' or sys.platform.startswith('win'):
    return str(msg)
  return UL + str(msg) + RS


# General Colorize Text Wrappers
################################
def blue( msg ): 
  """ Print BLUE Colored String """
  if os.name == 'nt' or sys.platform.startswith('win'):
    windows_user_default_color_code = windows_default_colors()
    set_text_attr(FBLU | BBLK | HC | BHC)
    sys.stdout.write(str(msg))
    restore_windows_colors(windows_user_default_color_code)
  else:
    return HC + FBLU + str(msg) + RS


def cyan( msg ): 
  """ Print CYAN Colored String """
  if os.name == 'nt' or sys.platform.startswith('win'):
    windows_user_default_color_code = windows_default_colors()
    set_text_attr(FCYN | BBLK | HC | BHC)
    sys.stdout.write(str(msg))
    restore_windows_colors(windows_user_default_color_code)
  else:
    return HC + FCYN + str(msg) + RS


def green( msg ): 
  """ Print GREEN Colored String """
  if os.name == 'nt' or sys.platform.startswith('win'):
    windows_user_default_color_code = windows_default_colors()
    set_text_attr(FGRN | BBLK | HC | BHC)
    sys.stdout.write(str(msg))
    restore_windows_colors(windows_user_default_color_code)
  else:
    return HC + FGRN + str(msg) + RS

def magenta(msg): 
  """ Print MAGENTA Colored String """
  if os.name == 'nt' or sys.platform.startswith('win'):
    windows_user_default_color_code = windows_default_colors()
    set_text_attr(FMAG | BBLK | HC | BHC)
    sys.stdout.write(str(msg))
    restore_windows_colors(windows_user_default_color_code)
  else:
    return HC + FMAG + str(msg) + RS


def red( msg ): 
  """ Print RED Colored String """
  if os.name == 'nt' or sys.platform.startswith('win'):
    windows_user_default_color_code = windows_default_colors()
    set_text_attr(FRED | BBLK | HC | BHC)
    sys.stdout.write(str(msg))
    restore_windows_colors(windows_user_default_color_code)
  else:
    return HC + FRED + str(msg) + RS


def white( msg ): 
  """ Print WHITE Colored String """
  if os.name == 'nt' or sys.platform.startswith('win'):
    windows_user_default_color_code = windows_default_colors()
    set_text_attr(FWHT | BBLK | HC | BHC)
    sys.stdout.write(str(msg))
    restore_windows_colors(windows_user_default_color_code)
  else:
    return HC + FWHT + str(msg) + RS


def yellow(msg ): 
  """ Print YELLOW Colored String """
  if os.name == 'nt' or sys.platform.startswith('win'):
    windows_user_default_color_code = windows_default_colors()
    set_text_attr(FYEL | BBLK | HC | BHC)
    sys.stdout.write(str(msg))
    restore_windows_colors(windows_user_default_color_code)
  else:
    return HC + FYEL + str(msg) + RS

























## END COLORS STUFF #################################################
#####################################################################




# A class to show some debug infos and functions to conditionally print massive amounts of colored text to the screen
# This is just a bunch of static methods with some environment variable stupidity added.
class XXDebug():

    debug_enabled = True
    env_debug_level = os.environ.get('XXDEBUG_LEVEL')
    debug_level = dlevel.DBG_BASIC
    # if the XXDEBUG_LEVEL environment variable has been set, use the value as the debug level
    # this allows the user to change the debug level without having to modify the python code within any files
    # which is pretty nice
    if env_debug_level is not None:
        if env_debug_level.upper() == 'NONE':
            debug_level = dlevel.DBG_NONE
        if env_debug_level.upper() == 'BASIC':
            debug_level = dlevel.DBG_BASIC
        elif env_debug_level.upper() == 'VERBOSE':
            debug_level = dlevel.DBG_VERBOSE
            
        elif env_debug_level.upper() == 'SUPERUSER':
            debug_level = dlevel.DBG_SUPERUSER

    env_show_only_this_level = os.environ.get('XXDEBUG_SHOW_ONLY_THIS_LEVEL')
    show_only_this_level = False
    if env_show_only_this_level is not None:
        if env_show_only_this_level.upper() == 'YES':
            show_only_this_level = True
        else:
            show_only_this_level = False


    env_debug_color = os.environ.get('XXDEBUG_COLOR')
    color_enabled = False
    if env_debug_color is not None:
        if env_debug_color.upper() == "COLOR":
            color_enabled = True
        elif env_debug_color.upper() == "NOCOLOR":
            color_enabled = False

    env_logfile_name = os.environ.get('XXDEBUG_LOGNAME')
    
    env_logfile_path = os.environ.get('XXDEBUG_LOGPATH')
    
    home = expanduser("~")
    thispath = os.path.join(home,'.xxdebug')
    log_folder = 'xxdebug_logs' 

    origin_name = ntpath.basename(os.path.realpath(sys.argv[0]))
    origin_dir = os.path.dirname(os.path.realpath(sys.argv[0]))


    logfile_path = os.path.join(origin_dir, log_folder)
    try:
        logfile_name, ext = origin_name.split('.')
    except:
        logfile_name = origin_name
        pass


    logfile_name = logfile_name + '_xxlog'

    if not os.path.exists(logfile_path):
        print "creating folder " + str(logfile_path)
        os.makedirs(logfile_path)
    
    
    
    # the default behavior is to put the logs in the place where the user script resides in an xxlogs folder
    # with the name of the script executed plus '_xxlog' and a number
    # the only way to change this behavior is to set the environment vars for logname and logpath
    # however, I do not want changes to these variables to permanently affect where the logs go.
    # this override behavior should be one-time only
    if env_logfile_name is not None:
        if env_logfile_name != "DEFAULT":
            logfile_name = env_logfile_name
            #reset this so the override only affects the next file
            os.environ['XXDEBUG_LOGNAME'] == "DEFAULT"
  
    if env_logfile_path is not None:
        if env_logfile_path != "DEFAULT":
            logfile_path = env_logfile_path
            os.environ['XXDEBUG_LOGPATH'] == "DEFAULT"


    env_do_logging = os.environ.get('XXDEBUG_LOGGING')
    do_logging = False
    if env_do_logging is not None:
        if env_do_logging.upper() == "YES":
            do_logging = True

    logfile = None
    if do_logging:
        if (logfile_name is not None) and (logfile_path is not None):
            ######### LOG FILE SHENANIGANS ## 
            # initialize the name of the log file
            log_num = 0
            logfile_full_name = logfile_name + str(log_num) + ".txt"
            logpath = os.path.join(logfile_path, logfile_full_name)
            while (os.path.exists(logpath)):
                log_num = log_num + 1
                logfile_full_name = logfile_name + str(log_num) + ".txt"
                logpath = os.path.join(logfile_path, logfile_full_name)
            logfile = open(logpath, 'w+') 
            ########### END LOG FILE SHENANIGANS ################



    trace_enabled = False
    env_trace_enabled = os.environ.get('XXDEBUG_ENABLETRACE')
    if env_trace_enabled is not None:
        if env_trace_enabled.upper() == "YES":
            trace_enabled = True
    hidden_trace_enabled = False
    env_hidden_trace_enabled = os.environ.get('XXDEBUG_ENABLEHIDDENTRACE')
    if env_hidden_trace_enabled is not None:
        if env_hidden_trace_enabled.upper() == "YES":
            hidden_trace_enabled = True

   
    # there are some cases where we may want to change the environment variables right here.
    # for example, when a temporary override was made to logpath or logname (these are changed to DEFAULT)
    write_xxdebug_environment_vars_to_file()


    # @MPD I HAVE MODIFIED THIS TOOL TO NOT USE ANY CONSTRUCTOR AT ALL. 
    # THINGS ARE SIMPLER THIS WAY, ALTHOUGH MAYBE YOU WANT TO ADD YOUR OWN VERSIONS / PATHS THAT 
    # ARE SPECIFIC TO YOUR PROGRAMS.. IN WHICH CASE YOU MAY NOT WANT TO USE ENVIRONMENT VARIABLES
    # THE BEST IDEA HERE WOULD BE TO TEMPORARILY OVERRIDE THE ENVIRONMENT VARIABLES IFF AN INSTANCE HAS BEEN CREATED
    # This constructor is used to initialize the autolog file,
    # set the debug parameters, etc.
    # note that none of these parameters are stored in the instance but rather stored in the 
    #  def __init__(self, fname):



    ########################################################################
    # @MPD Conditional printouts to prevent clutter    
    # a message that shows up bright green but only when --color is used
    @staticmethod
    def debug_print(msg):
        msg = "BASIC DBG: " + str(msg)
        if ((XXDebug.debug_enabled == True) and (XXDebug.debug_level >= dlevel.DBG_BASIC)):
            if (XXDebug.show_only_this_level == False) or (XXDebug.debug_level == dlevel.DBG_BASIC):
                if XXDebug.color_enabled == True:
                    print green(msg)
                else:
                    print msg
                XXDebug.logprint(msg)
                
    # a message that shows up bright yellow but only when --color is used    
    @staticmethod
    def verbose_print(msg):
        msg = "VERBOSE DBG: " + str(msg)
        if ((XXDebug.debug_enabled == True) and (XXDebug.debug_level >= dlevel.DBG_VERBOSE)):
            if (XXDebug.show_only_this_level == False) or (XXDebug.debug_level == dlevel.DBG_VERBOSE):
                if XXDebug.color_enabled == True:
                    print yellow(msg)
                else:
                    print msg
                XXDebug.logprint(msg)
       
    # a message that shows up bright yellow but only when --color is used    
    @staticmethod
    def superuser_print(msg):
        msg = "SUPERUSER DBG: " + str(msg)
        if ((XXDebug.debug_enabled == True) and (XXDebug.debug_level >= dlevel.DBG_SUPERUSER)):
            if (XXDebug.show_only_this_level == False) or (XXDebug.debug_level == dlevel.DBG_SUPERUSER):
                if XXDebug.color_enabled == True:
                    print blue(msg)
                else:
                    print msg
                XXDebug.logprint(msg)



#    # a message that shows up bright white on console
#    @staticmethod
#    def regular_print(msg):
#        msg = "BASIC DBG: " +str(msg) 
#        if XXDebug.color_enabled == True:
#            #  print white(msg, style='bold')
#            print white(msg)
#        else:
#            print str(msg)
#        XXDebug.logprint(msg)

    # MACROS
    # print basic debug message with a few aliases
    @staticmethod
    def bprint(msg):
        XXDebug.debug_print(msg)
    @staticmethod
    def basic(msg):
        XXDebug.debug_print(msg)         
    @staticmethod
    def debug(msg):
        XXDebug.debug_print(msg)
    @staticmethod
    def bout(msg):
        XXDebug.debug_print(msg)        
    @staticmethod
    def out(msg):
        XXDebug.debug_print(msg)        
    # verbose debug message
    @staticmethod
    def verbose(msg):
        XXDebug.verbose_print(msg)
    @staticmethod
    def vprint(msg):
        XXDebug.verbose_print(msg)
    @staticmethod
    def vout(msg):
        XXDebug.verbose_print(msg)
    # superuser debug message (not for the faint of heart)
    @staticmethod
    def superuser(msg):
        XXDebug.superuser_print(msg)
    @staticmethod
    def sprint(msg):
        XXDebug.superuser_print(msg)
    @staticmethod
    def sout(msg):
        XXDebug.superuser_print(msg)
########################################################################

    # A function to cause a software breakpoint
    @staticmethod
    def breakx(msg=None):
        text = "<Manual Breakpoint> "+ str(msg)
        XXDebug.basic(text)
        raise ValueError(text)

    #A function to print text and then request user input in order to continue
    @staticmethod
    def breaki(msg=None):
        text = "<Manual Breakpoint> "+ str(msg)
        XXDebug.basic(text)
        input(text)

    # A function to print the output from the most recent invocation of IDA Pro to the command line
    # This function prints the output in color if the -c option was passed to brass
    @staticmethod
    def print_and_erase_idalog():
        # 
        if not os.path.exists(XXDebug.idalog_path):
            vout("IDALOG does not exist")
            return
        else:
            with open(XXDebug.idalog_path) as f:
                if XXDebug.color_enabled == True:
                    print yellow("~~~~ !! OUTPUT FROM IDA PRO (stage/idalog.txt) [errors in yellow] !! ~~~~", style='bold')
                    for line in f:
                        if line:
                            if "DBG: " in line:
                                print green(line.rstrip(), style='bold')
                            elif "VERBOSE: " in line:
                                print red(line.rstrip(), style='bold')
                            elif "OUT: " in line:
                                print white(line.rstrip(), style='bold')
                            # @MPD this is the neat one.. looks for error messages in the ida output
                            elif ("error" in line) or (", line " in line) or ("Traceback" in line) or (" has no " in line):
                                print yellow(line.rstrip(), style='bold')
                            else:
                                print cyan(line.rstrip(), style='bold')                                          
                else:
                    print "~~~~ !! OUTPUT FROM IDA PRO (stage/idalog.txt) !! ~~~~"
                    for line in f:
                        # Ignore the empty lines to save space on the terminal
                        if line:
                            print line.rstrip()
                # finally, also print the line to the output logfile
                XXDebug.logprint(line.rstrip())
            
            # NOW DELETE THE IDALOG FILE
            copy2(XXDebug.idalog_path, XXDebug.idalog_back_path)
            os.unlink(XXDebug.idalog_path)    
            
            
    # the most basic of output to file 
    @staticmethod
    def logprint(text):
        # for stupidity's sake, lets keep the logfile open the entire time so that we can keep adding to it
        # and then just have python close the file for us when the interpreter detects the end of the program =D
        # TODO: hacks
        if XXDebug.do_logging:
            if XXDebug.logfile is not None:
                XXDebug.logfile.write(text + '\n')
        
    @staticmethod
    def parse_environment_arguments(options):

        parser = argparse.ArgumentParser(description='XXDebug - automagic verbose color debug autologging for python 2.7+', \
                                        epilog='Use xxdebug to control debug level, color printing, and autologging to file \
                                        across all of your python programs.')
        
        
        # It is required for an input file to be specified
        parser.add_argument('-l', '--level', action="store",  type=str, help="define the verbosity level of debug output \n" \
                            + " options=['NONE', 'BASIC', 'VERBOSE', 'SUPERUSER', 'DEFAULT (basic)', 'MAX (superuser)'] default is BASIC \n" \
                            + " import xxdebug and use xxdebug_print(msg) for BASIC, xxdebug_verbose(msg), or xxdebug(su) for SUPERUSER")

        parser.add_argument('-x', '--showonlythislevel', action="store_true", help="force xxdebug to show only the selected \n" \
                            + " level of debug output (eg. verbose), rather than this and all lesser (eg. verbose, basic)")
       

        parser.add_argument('-z', '--showapplicable', action="store_true", help="default print setting inverse of -x option")

        parser.add_argument('-a', '--autolog', action="store_true", help="force xxdebug to log all xxdebug prints to a logfile \
                            \n NOTE: LOGS are stored in xxdebug_logs folder within the directory of the user script")

        parser.add_argument('-c', '--color', action="store_true", help="(default) force xxdebug to print output in color")

        parser.add_argument('-y', '--nocolor', action="store_true", help="tell xxdebug to print output without color")

        parser.add_argument('-p', '--logpath', action="store", type=str, help="specify a custom path for xxdebug logfile \
                (default = ~/xxdebug/) NOTE: THIS OVERRIDE TO THE PATH ONLY AFFECTS THE NEXT [ONE] LOG")

        parser.add_argument('-n', '--logname', action="store", type=str, help="specify a custom name for the logfile \
                (default = xxdebug_autolog) NOTE: THIS OVERRIDE TO THE NAME ONLY AFFECTS THE NEXT [ONE] LOG")
 
        parser.add_argument('-d', '--default','--defaults', action="store_true", help="revert xxdebug to defaults specified in help")

        parser.add_argument('-m', '--max', action="store_true", help="enable the maximum amount of xxdebug logging/prints")

        parser.add_argument('-o', '--off', action="store_true", help="disable all xxdebug output from all files using xxdebug")

        parser.add_argument('--enable', action="store_true", help="enable default xxdebug output from all files using xxdebug")

        parser.add_argument('--disable', action="store_true", help="disable all xxdebug output from all files using xxdebug")
       
        parser.add_argument('-t', '--enabletrace', action="store_true", help="enable pdb debug trace via xxdebug_bp()")

        parser.add_argument('--disabletrace', action="store_true", help="disable pdb debug trace via xxdebug_bp()")

        parser.add_argument('--disablehiddentrace', action="store_true", help="enable pdb debug trace via xxdebug_bp()")

        parser.add_argument('--enablehiddentrace', action="store_true", help="disable pdb debug trace via xxdebug_bp()")


        args = parser.parse_args(options)
        
        if args.color is not None:
            if args.color == True:
                print "enabling xxdebug color print"
                os.environ['XXDEBUG_COLOR'] = 'COLOR'

        if args.nocolor is not None:
            if args.nocolor==True:
                print "disabling xxdebug color print"
                os.environ['XXDEBUG_COLOR'] = 'NOCOLOR'

        if args.level is not None:
            print "setting xxdebug logging level to " + args.level.upper()
            if args.level.upper() == "NONE":
                os.environ['XXDEBUG_LEVEL'] = "NONE"
            elif args.level.upper() == "BASIC":
                os.environ['XXDEBUG_LEVEL'] = "BASIC"
            elif args.level.upper() == "VERBOSE": 
                os.environ['XXDEBUG_LEVEL'] = "VERBOSE"
            elif args.level.upper() == "SUPERUSER":
                os.environ['XXDEBUG_LEVEL'] = "SUPERUSER"
            elif args.level.upper() == "DEFAULT":
                os.environ['XXDEBUG_LEVEL'] = "BASIC"
            elif args.level.upper() == "MAX":
                os.environ['XXDEBUG_LEVEL'] = "SUPERUSER"

        if args.showapplicable is not None:
            #default setting no need to use unless showonlythislevel is used at some point
            if args.showapplicable == True:
                print "setting show_only_this_level to False"
                os.environ['XXDEBUG_SHOW_ONLY_THIS_LEVEL'] = 'NO'
        if args.showonlythislevel is not None:
            if args.showonlythislevel == True:
                print "setting show_only_this_level to True"
                os.environ['XXDEBUG_SHOW_ONLY_THIS_LEVEL'] = 'YES'
        if args.autolog is not None:
            if args.autolog == True:
                print "enabling xxdebug logging feature"
                os.environ['XXDEBUG_LOGGING'] = "YES"
        if args.logpath is not None:
            if args.logpath != "":
                print "setting xxdebug logpath to " + args.logpath
                os.environ['XXDEBUG_LOGPATH'] = args.logpath
        if args.logname is not None:
            if args.logname != "":
                print "setting xxdebug logname to " + args.logname
                os.environ['XXDEBUG_LOGNAME'] = args.logname
        if args.default is not None:
            if args.default == True:
                print "restoring xxdebug defaults"
                os.environ['XXDEBUG_LEVEL'] = "BASIC"
                os.environ['XXDEBUG_SHOW_ONLY_THIS_LEVEL'] = 'NO'
                os.environ['XXDEBUG_COLOR'] = "COLOR"
                os.environ['XXDEBUG_LOGGING'] = "YES"
                os.environ['XXDEBUG_LOGPATH'] = "DEFAULT"
                os.environ['XXDEBUG_LOGNAME'] = "DEFAULT"
                os.environ['XXDEBUG_ENABLETRACE'] = "NO"
                os.environ['XXDEBUG_ENABLEHIDDENTRACE'] = "NO"
        if args.max is not None:
            if args.max == True:
                print "enabling all xxdebug features"
                os.environ['XXDEBUG_LEVEL'] = "SUPERUSER"
                os.environ['XXDEBUG_SHOW_ONLY_THIS_LEVEL'] = 'NO'
                os.environ['XXDEBUG_COLOR'] = "COLOR"
                os.environ['XXDEBUG_LOGGING'] = "YES"
        if args.off is not None:
            if args.off == True:
                print "disabling xxdebug features"
                os.environ['XXDEBUG_LEVEL'] = "NONE"
                os.environ['XXDEBUG_SHOW_ONLY_THIS_LEVEL'] = 'NO'
                os.environ['XXDEBUG_COLOR'] = "NOCOLOR"
                os.environ['XXDEBUG_LOGGING'] = "NO"
        if args.enable is not None:
            if args.enable == True:
                print "enabling xxdebug with default settings"
                os.environ['XXDEBUG_LEVEL'] = "BASIC"
                #  os.environ['XXDEBUG_SHOW_ONLY_THIS_LEVEL'] = 'NO'
                #  os.egnviron['XXDEBUG_COLOR'] = "COLOR"
                #  os.environ['XXDEBUG_LOGGING'] = "YES"
                os.environ['XXDEBUG_LOGPATH'] = "DEFAULT"
                os.environ['XXDEBUG_LOGNAME'] = "DEFAULT"
                
        if args.disable is not None:
            if args.disable == True:
                print "disabling xxdebug features"
                os.environ['XXDEBUG_LEVEL'] = "NONE"
                os.environ['XXDEBUG_SHOW_ONLY_THIS_LEVEL'] = 'NO'
                os.environ['XXDEBUG_COLOR'] = "NOCOLOR"
                os.environ['XXDEBUG_LOGGING'] = "NO"
                os.environ['XXDEBUG_ENABLETRACE'] = "NO"
                os.environ['XXDEBUG_ENABLEHIDDENTRACE'] = "NO"

        if args.enabletrace is not None:
            if args.enabletrace == True:
                print "enabling pdb debug trace features"            
                #  os.environ['XXDEBUG_LEVEL'] = "VERBOSE" #some nice additional messages when debugging?
                os.environ['XXDEBUG_ENABLETRACE'] = "YES"
        if args.disabletrace is not None:
            if args.disabletrace == True:
                print "disabling pdb debug trace features"
                os.environ['XXDEBUG_ENABLETRACE'] = "NO"
        if args.enablehiddentrace is not None:
            if args.enablehiddentrace == True:
                print "enabling pdb debug hidden trace features"
                os.environ['XXDEBUG_ENABLEHIDDENTRACE'] = "YES"
        if args.disablehiddentrace is not None:
            if args.disablehiddentrace == True:
                print "disabling pdb debug hidden trace features"
                os.environ['XXDEBUG_ENABLEHIDDENTRACE'] = "NO"

        write_xxdebug_environment_vars_to_file()
        



##################################################################
########## FOR USERS #############################################
########## THESE ARE THE ONLY FUNCTIONS THAT YOU SHOULD BE USING
########## FOLLOW THE KISS PRINCIPLE. FOUR FUNCTIONS. USE WISELY

def xxdebug_print(msg):
    XXDebug.basic(msg)

def xxdebug_verbose(msg):
    XXDebug.verbose(msg)

def xxdebug_su(msg):
    XXDebug.superuser(msg)


# read and understand my humility 
def xxdebug_bp(msg='', hidden=False, funcptr=None, funcargs=[]):
    # a clever (ZOMG i am the boss) way to add breakpoints to python programs and enable/disable/hide them at will
    # xxdebug does not do trace by default. Use xxdebug --enabletrace to enable breakpoints with xxdebug
    # use xxdebug --disabletrace to disable all breakpoints
    # by default, even with trace is enabled within xxdebug, hidden breakpoints are not hit (hence hidden)
    # if you want to step through even the hidden breakpoints, use xxdebug --enablehiddentrace
    # use xxdebug --disablehiddentrace to restore trace to skip hidden breakpoints

    if XXDebug.trace_enabled == True:
        if (XXDebug.hidden_trace_enabled == True) or (hidden == False):
            # user defined debug function that is enabled/disabled at will by xxdebug
            if funcptr is not None:
                if funcargs==[]:
                    funcptr()
                else:
                    #@TODO HACKS test this with some args
                    funcptr(funcargs)

            XXDebug.verbose_print('HIT BREAKPOINT AND NOW DESCENDING INTO PDB (command line debugger)')
            XXDebug.debug_print('________________________________________________________________')
            # grab the context of the caller to get the original line number!
            previous_frame = inspect.currentframe().f_back
            (filename, line_number, function_name, lines, index) = inspect.getframeinfo(previous_frame)
            XXDebug.debug_print('bp @ file-------->   '+ filename )
            XXDebug.debug_print('bp @ func-------->   '+ function_name )
            XXDebug.debug_print('bp @ line-------->   '+  str(line_number) )
            XXDebug.debug_print('________________________________________________________________')
            XXDebug.verbose_print("Use 'u<enter>' or 'up' to return to function context and 'print <var><enter>' to inspect context.")
            XXDebug.verbose_print("Use 'up<enter>' and 'down<enter>' to further traverse call stack. use 'cont<enter>' to continue.")
            if msg is not '':
                XXDebug.debug_print(msg)
            # NOTE that user needs to use 'up' to exit this debug_bp function context to return to where THIS function was called.
            pdb.set_trace() 


# @TODO HACKS. colors should be configured by the user. Should add this feature later.
#  def xxdgreen(msg):
#      XXDebug.basic(msg)
#
#  def xxdyellow(msg):
#      XXDebug.verbose(msg)
#
#  def xxdblue(msg):
#      XXDebug.superuser(msg)

if __name__ == "__main__":
    
    
    
    args = sys.argv[1:] #all arguments except the program name
    if len(args) == 0:
        args = ['--help']
    if '--help' in args:
        print "THIS PROGRAM CONTROLS GLOBAL DEBUG SETTINGS FOR XXDEBUG.out() and other"
        print "ROUTINES IN PYTHON MODULES IMPORTING XXDEBUG.py"
        print ""
        print "YOU MUST SUPPLY AN OPTION WHEN RUNNING THIS PROGRAM"
        print "use 'xxdebug --enable' to enable xxdebug.out() and others in imported modules"
        print "use 'xxdebug --disable' to disable xxdebug.out() and others in imported modules"
        print "use 'xxdebug --max' to turn on all debug output from xxdebug including verbose and superuser levels"
        print ""
        print "HELP FOR XXDEBUG:"
        XXDebug.parse_environment_arguments(args)
        os.exit(1)
    else:
        print("Configuring xxdebug environment...")
        XXDebug.parse_environment_arguments(args) 
        print("...xxdebug environment configured.")  
    









