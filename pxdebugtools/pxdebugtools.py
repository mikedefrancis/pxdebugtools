#!/usr/bin/env python
# @author mikedefrancis
# www.github.com/mikedefrancis
# a usable debug framework for python prints, juicy pdb, module-based debug integration
# nicest thing: enable/disable all of your debug from a cli program. No need to remove your debug prints from your programs anymore.

#########################################################
####         pxdebug          ###########################
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
from pdb import Pdb
import inspect


class dlevel():
    DBG_BASIC = 1
    DBG_VERBOSE = 2
    DBG_EXTREME = 3

# WRITE 'em HACK to make environment variables persist using a file:
def write_pxdebug_environment_vars_to_file():
    home = expanduser("~")
    thispath = os.path.join(home,'.pxdebug')
    if not os.path.exists(thispath):
        print("creating ~/.pxdebug/ folder")
        os.makedirs(thispath)
    env_file = open(thispath + '/pxdebug.env', 'w+')

    write_env_var_to_file(env_file, 'PXDEBUG_ENABLE')
    write_env_var_to_file(env_file, 'PXDEBUG_LEVEL')
    write_env_var_to_file(env_file, 'PXDEBUG_COLOR')
    write_env_var_to_file(env_file, 'PXDEBUG_LOGGING')
    write_env_var_to_file(env_file, 'PXDEBUG_LOGPATH')
    write_env_var_to_file(env_file, 'PXDEBUG_LOGNAME')
    write_env_var_to_file(env_file, 'PXDEBUG_ENABLETRACE')
    write_env_var_to_file(env_file, 'PXDEBUG_ENABLEHIDDENTRACE')
    write_env_var_to_file(env_file, 'PXDEBUG_TESTFLAG')

    env_file.close()

# file must already be open
def write_env_var_to_file(f, varname):
    val = os.environ.get(varname)
    if val is not None:
        #  print "writing envvar to file || " + "export " + varname + "=" + str(val)
        f.write("export " + varname + "=" + str(val) + '\n') 

def print_env_var(varname):
    val = os.environ.get(varname)
    if val is not None:
        print(varname + '=' + str(val))


# READ 'em HACK to make environment variables persist using a file:
def get_pxdebug_environment_vars_from_file():
    home = expanduser("~")
    thispath = os.path.join(home,'.pxdebug')
    if not os.path.exists(thispath):
        print("creating ~/.pxdebug/ folder")
        os.makedirs(thispath)
    else:
        if os.path.exists(thispath + '/pxdebug.env'):
            with open(thispath + '/pxdebug.env') as f:
                for line in f:
                    if 'export' not in line:
                        continue
                    # Remove leading `export `
                    # then, split name / value pair
                    key, value = line.replace('export ', '', 1).strip().split('=', 1)
                    #  print "reading envvar || " + str(key) + "=" + str(value)
                    os.environ[key] = value



get_pxdebug_environment_vars_from_file()


######################################################################
## COLORS STUFF ######################################################


# NOTE TO USERS:
# I COPIED THIS ENTIRE FILE INTO THE CONTENTS OF THIS ONE (HACKS) 
# IT IS REALLY, REALLY UGLY. BUT IT MAKES IT EASIER TO USE PXDEBUG WITHOUT HAVING ANY DEPENDENCIES ON THIRD PARTY LIBRARIES

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
    except Exception as e:
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
    except Exception as e:
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
    except Exception as e:
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
    except Exception as e:
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
    print(HC + FYEL + "[" + FWHT + "-" + FYEL + "] " + FWHT + str( msg ) + RS)


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
    print(HC + FGRN + "[" + FWHT + "*" + FGRN + "] " + FWHT + str( msg ) + RS)


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
    print(HC + FRED + "[" + FWHT + "x" + FRED + "] " + FWHT + str( msg ) + RS)


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
    print(HC + FBLU + "[" + FWHT + "*" + FBLU + "] " + FWHT + str( msg ) + RS)


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
    print(HC + FRED + "[" + FWHT + "ERROR" + FRED + "] " + FWHT + str( msg ) + RS)


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




# NOTE TO USERS: pxdebug does not have a constructor and is used as a static class similar to a namespace
# STEP1: User programs pxdebug settings using the pxdebug executable program
# STEP2: User launches their python program that includes "from pxdebugtools import pxdebug"
# STEP3: pxdebug is initialized at runtime using a file that stores environment variables on linux

# A class to show some debug infos and functions to conditionally print massive amounts of colored text to the screen
# This is just a bunch of static methods with some environment variable stupidity added.
class pxdebug():

    debug_enabled = False
    env_debug_enabled = os.environ.get('PXDEBUG_ENABLE')
    if env_debug_enabled is not None:
        if env_debug_enabled.upper() == "YES":
            debug_enabled = True


    test_flag = False
    env_test_flag = os.environ.get('PXDEBUG_TESTFLAG')
    if env_test_flag is not None:
        if env_test_flag.upper() == "YES":
            test_flag = True


    env_debug_level = os.environ.get('PXDEBUG_LEVEL')
    debug_level = dlevel.DBG_BASIC
    # if the PXDEBUG_LEVEL environment variable has been set, use the value as the debug level
    # this allows the user to change the debug level without having to modify the python code within any files
    # which is pretty nice
    if env_debug_level is not None:
        if env_debug_level.upper() == 'BASIC':
            debug_level = dlevel.DBG_BASIC
        elif env_debug_level.upper() == 'VERBOSE':
            debug_level = dlevel.DBG_VERBOSE
        elif env_debug_level.upper() == 'EXTREME':
            debug_level = dlevel.DBG_EXTREME

    env_debug_color = os.environ.get('PXDEBUG_COLOR')
    color_enabled = False
    if env_debug_color is not None:
        if env_debug_color.upper() == "YES":
            color_enabled = True
        elif env_debug_color.upper() == "NO":
            color_enabled = False

    env_logfile_name = os.environ.get('PXDEBUG_LOGNAME')
    
    env_logfile_path = os.environ.get('PXDEBUG_LOGPATH')
    
    home = expanduser("~")
    thispath = os.path.join(home,'.pxdebug')
    log_folder = 'pxdebug_logs' 

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
        print("creating folder " + str(logfile_path))
        os.makedirs(logfile_path)
    
    
    
    # the default behavior is to put the logs in the place where the user script resides in an xxlogs folder
    # with the name of the script executed plus '_xxlog' and a number
    # the only way to change this behavior is to set the environment vars for logname and logpath
    # however, I do not want changes to these variables to permanently affect where the logs go.
    # this override behavior should be one-time only
    if env_logfile_name is not None:
        if env_logfile_name != "DEFAULT":
            logfile_name = env_logfile_name
            print("TEST HERE HERE THERE IT WAM")
            #reset this so the override only affects the next file
            os.environ['PXDEBUG_LOGNAME'] = "DEFAULT"
  
    if env_logfile_path is not None:
        if env_logfile_path != "DEFAULT":
            logfile_path = env_logfile_path
            os.environ['PXDEBUG_LOGPATH'] = "DEFAULT"


    env_do_logging = os.environ.get('PXDEBUG_LOGGING')
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
    env_trace_enabled = os.environ.get('PXDEBUG_ENABLETRACE')
    if env_trace_enabled is not None:
        if env_trace_enabled.upper() == "YES":
            trace_enabled = True
    hidden_trace_enabled = False
    env_hidden_trace_enabled = os.environ.get('PXDEBUG_ENABLEHIDDENTRACE')
    if env_hidden_trace_enabled is not None:
        if env_hidden_trace_enabled.upper() == "YES":
            hidden_trace_enabled = True

   
    # there are some cases where we may want to change the environment variables right here.
    # for example, when a temporary override was made to logpath or logname (these are changed to DEFAULT)
    write_pxdebug_environment_vars_to_file()



############ READ HERE!
#########################################################################################
############ PXDEBUG API FUNCTIONS FOR INCORPORATION INTO USER MODULES ############################
############ USER pxdebug.basic(msg) and other functions within your own programs to use
    @staticmethod
    def basic(msg=''):
        if ((pxdebug.debug_enabled == True) and (pxdebug.debug_level >= dlevel.DBG_BASIC)):
            if msg is not '':
                frame = sys._getframe().f_back
                (filename, line_number, function_name, lines, index) = inspect.getframeinfo(frame)
                dmsg = "BASIC DEBUG| " + str(msg)
                if pxdebug.color_enabled == True:
                    print(green(dmsg))
                else:
                    print(dmsg)
                pxdebug.logprint(dmsg)
    
            return True
        return False

    # a message that shows up bright yellow but only when --color is used    
    @staticmethod
    def verbose(msg='', linesplit = False):
        if ((pxdebug.debug_enabled == True) and (pxdebug.debug_level >= dlevel.DBG_VERBOSE)):
            if msg is not '':
                frame = sys._getframe().f_back
                (filename, line_number, function_name, lines, index) = inspect.getframeinfo(frame)
                if linesplit == True:
                    dmsg = "VERBOSE DEBUG(" + filename+" line " + str(line_number) + ")||\n     " + str(msg)
                else:
                    dmsg = "VERBOSE DEBUG(" + filename+" line " + str(line_number) + ")|  " + str(msg)
                if pxdebug.color_enabled == True:
                    print(yellow(dmsg))
                else:
                    print(dmsg)
                pxdebug.logprint(dmsg)
            return True
        return False
       
    # a message that shows up bright yellow but only when --color is used    
    @staticmethod
    def extreme(msg='', linesplit = False):
        if ((pxdebug.debug_enabled == True) and (pxdebug.debug_level >= dlevel.DBG_EXTREME)):
            if msg is not '': 
                frame = sys._getframe().f_back
                (filename, line_number, function_name, lines, index) = inspect.getframeinfo(frame)
                if linesplit == True:
                    dmsg="EXTREME DEBUG(" + filename+" line " + str(line_number) + " [func=" + function_name+"])||\n     " + str(msg)
                else:
                    dmsg="EXTREME DEBUG(" + filename+" line " + str(line_number) + " [func=" + function_name+"])|  " + str(msg)
                if pxdebug.color_enabled == True:
                    print(cyan(dmsg))
                else:
                    print(dmsg)
                pxdebug.logprint(dmsg)
            
            return True
        return False


    ## THIS IS A WRAPPER FOR PDB (command line python debugger)
    # a way to add breakpoints to python programs and enable/disable/hide them at will
    # use pxdebug --disabletrace to disable all breakpoints
    # by default, even with trace is enabled within pxdebug, hidden breakpoints are not hit (hence hidden)
    # if you want to step through even the hidden breakpoints, use pxdebug --enablehiddentrace
    # use pxdebug --disablehiddentrace to restore trace to skip hidden breakpoints
    @staticmethod
    def breakpoint(msg='', hide=False):
        # Only execute the breakpoints when the right set of user defined conditions have been met
        if (pxdebug.debug_enabled == True) and (pxdebug.trace_enabled == True):
            if (pxdebug.hidden_trace_enabled == True) or (hide == False):
                frame = sys._getframe().f_back
                (filename, line_number, function_name, lines, index) = inspect.getframeinfo(frame)
                old_stdout = sys.stdout
                sys.stdout = sys.__stdout__
                if msg is not '':
                    pxdebug.basic(msg)
                pxdebug.basic('---BREAK----> ' + filename +' | func=' + function_name )#+'|line'+str(line_number) + ' <-------')
                try:
                    Pdb().set_trace(frame)
                except e as Exception:
                    print("pxdebug ERROR SETTING TRACE")
                    raise e
                sys.stdout = old_stdout


    # SOME UTILITY FUNCTIONS FOR ENABLING / DISABLING YOUR OWN DEBUG CODE IN YOUR PROGRAMS:
    @staticmethod
    def enabled():
        return (pxdebug.debug_enabled == True)

    @staticmethod
    def flag():
        return (pxdebug.test_flag == True)



############# END USER API ################
##########################################################################



    # THIS ONE NOT REALLY INTENDED FOR USER
    # the most basic of output to file 
    @staticmethod
    def logprint(text):
        # for stupidity's sake, lets keep the logfile open the entire time so that we can keep adding to it
        # and then just have python close the file for us when the interpreter detects the end of the program =D
        # TODO: hacks
        if pxdebug.debug_enabled == True:
            if pxdebug.do_logging:
                if pxdebug.logfile is not None:
                    try:
                        pxdebug.logfile.write(text + '\n')
                    except:
                        print("PXDEBUG ERROR WRITING TO LOGFILE")
                        pass

    @staticmethod
    def parse_environment_arguments(options):

        parser = argparse.ArgumentParser(description='pxdebug - automagic verbose color debug autologging for python 2.7+', \
                                        epilog='Use pxdebug to control debug level, color printing, breakpoints, and output logs \
                                        across all of your python programs. use "from pxdebugtools import pxdebug" to include \
                                        pxdebug features across all of your python programs.')
        
        parser.add_argument('-l', '--level', action="store",  type=str, help="define the verbosity level of debug output \n" \
                            + " options=['BASIC', 'VERBOSE', 'EXTREME', 'DEFAULT (verbose)', 'MAX (extreme)'] \n")

        parser.add_argument('--enablelogging', action="store_true", help="force pxdebug to log all pxdebug prints to a logfile \
                            \n NOTE: LOGS are stored in pxdebug_logs folder within the directory of the user script")

        parser.add_argument('--disablelogging', action="store_true", help="force pxdebug to stop logging output")

        parser.add_argument('--enablecolor', action="store_true", help="(default) force pxdebug to print output in color")

        parser.add_argument('--disablecolor', action="store_true", help="tell pxdebug to print output without color")

        parser.add_argument('--logpath', action="store", type=str, help="specify a custom path for pxdebug logfile \
                                         \n THIS OVERRIDE TO THE PATH ONLY AFFECTS THE NEXT [ONE] LOG")

        parser.add_argument('--logname', action="store", type=str, help="specify a custom name for the logfile \
                                         \n THIS OVERRIDE TO THE NAME ONLY AFFECTS THE NEXT [ONE] LOG")
 
        parser.add_argument('-d', '--default','--defaults', action="store_true", help="revert pxdebug to defaults specified in help")

        parser.add_argument('-a', '-m', '--max', '--all', action="store_true", help="turn on all pxdebug features and enable pxdebug")
       
        parser.add_argument('-t', '--enabletrace', action="store_true", help="enable pdb debug trace via pxdebug_bp()")

        parser.add_argument('--disabletrace', action="store_true", help="disable pdb debug trace via pxdebug_bp()")

        parser.add_argument('--disablehiddentrace', action="store_true", help="enable pdb debug trace via pxdebug_bp()")

        parser.add_argument('--enablehiddentrace', action="store_true", help="disable pdb debug trace via pxdebug_bp()")

        parser.add_argument('--on', '--enable', action="store_true", help="enable pxdebug features in all modules")

        parser.add_argument('--off', '--disable', action="store_true", help="disable pxdebug features in all modules")

        parser.add_argument('-s', '--show', '--settings', action="store_true", help="display pxdebug settings and exit")

        parser.add_argument('--setflag', action="store_true", help="set a flag for use with 'if pxdebug.flag() == True:'")

        parser.add_argument('--unsetflag', action="store_true", help="unset the debug flag to skip your test code")

        args = parser.parse_args(options)
        
        if args.enablecolor is not None:
            if args.enablecolor == True:
                print("enabling pxdebug color print")
                os.environ['PXDEBUG_COLOR'] = 'YES'

        if args.disablecolor is not None:
            if args.disablecolor==True:
                print("disabling pxdebug color print")
                os.environ['PXDEBUG_COLOR'] = 'NO'

        if args.level is not None:
            print("setting pxdebug logging level to " + args.level.upper())
            if args.level.upper() == "BASIC":
                os.environ['PXDEBUG_LEVEL'] = "BASIC"
            elif args.level.upper() == "VERBOSE": 
                os.environ['PXDEBUG_LEVEL'] = "VERBOSE"
            elif args.level.upper() == "EXTREME":
                os.environ['PXDEBUG_LEVEL'] = "EXTREME"
            elif args.level.upper() == "DEFAULT":
                os.environ['PXDEBUG_LEVEL'] = "BASIC"
            elif args.level.upper() == "MAX":
                os.environ['PXDEBUG_LEVEL'] = "EXTREME"

        if args.enablelogging is not None:
            if args.enablelogging == True:
                print("enabling pxdebug logging feature")
                os.environ['PXDEBUG_LOGGING'] = "YES"       
        if args.disablelogging is not None:
            if args.disablelogging == True:
                print("disabling pxdebug logging feature")
                os.environ['PXDEBUG_LOGGING'] = "YES"
        if args.logpath is not None:
            if args.logpath != "":
                print("setting pxdebug logpath to " + args.logpath)
                os.environ['PXDEBUG_LOGPATH'] = args.logpath
        if args.logname is not None:
            if args.logname != "":
                print("setting pxdebug logname to " + args.logname)
                os.environ['PXDEBUG_LOGNAME'] = args.logname
        if args.default is not None:
            if args.default == True:
                print("restoring pxdebug defaults")
                os.environ['PXDEBUG_ENABLE'] = "YES"
                os.environ['PXDEBUG_LEVEL'] = "VERBOSE"
                os.environ['PXDEBUG_COLOR'] = "YES"
                os.environ['PXDEBUG_LOGGING'] = "YES"
                os.environ['PXDEBUG_LOGPATH'] = "DEFAULT"
                os.environ['PXDEBUG_LOGNAME'] = "DEFAULT"
                os.environ['PXDEBUG_ENABLETRACE'] = "YES"
                os.environ['PXDEBUG_ENABLEHIDDENTRACE'] = "NO"      
                os.environ['PXDEBUG_TESTFLAG'] = "NO"
        if args.max is not None:
            if args.max == True:
                print("enabling all pxdebug features")
                os.environ['PXDEBUG_ENABLE'] = "YES"
                os.environ['PXDEBUG_LEVEL'] = "EXTREME"
                os.environ['PXDEBUG_COLOR'] = "YES"
                os.environ['PXDEBUG_LOGGING'] = "YES"
                os.environ['PXDEBUG_ENABLETRACE'] = "YES"
                os.environ['PXDEBUG_ENABLEHIDDENTRACE'] = "YES"
                os.environ['PXDEBUG_TESTFLAG'] = "YES"
        if args.off is not None:
            if args.off == True:
                print("disabling pxdebug features")
                os.environ['PXDEBUG_ENABLE'] = "NO"

        if args.on is not None:
            if args.on == True:
                print("enabling pxdebug")
                os.environ['PXDEBUG_ENABLE'] = "YES"

        if args.enabletrace is not None:
            if args.enabletrace == True:
                print("enabling pdb debug trace features") 
                #  os.environ['PXDEBUG_LEVEL'] = "VERBOSE" #some nice additional messages when debugging?
                os.environ['PXDEBUG_ENABLETRACE'] = "YES"
        if args.disabletrace is not None:
            if args.disabletrace == True:
                print("disabling pdb debug trace features")
                os.environ['PXDEBUG_ENABLETRACE'] = "NO"
        if args.enablehiddentrace is not None:
            if args.enablehiddentrace == True:
                print("enabling pdb debug hidden trace features")
                os.environ['PXDEBUG_ENABLEHIDDENTRACE'] = "YES"
        if args.disablehiddentrace is not None:
            if args.disablehiddentrace == True:
                print("disabling pdb debug hidden trace features")
                os.environ['PXDEBUG_ENABLEHIDDENTRACE'] = "NO"

        if args.setflag is not None:
            if args.setflag == True:
                print("enabling the test flag")
                os.environ['PXDEBUG_TESTFLAG'] = "YES"

        if args.unsetflag is not None:
            if args.unsetflag == True:
                print("disabling the test flag")
                os.environ['PXDEBUG_TESTFLAG'] = "NO"


# IF WE GET ALL THE WAY TO HERE AND FOR SOME REASON NO ENVIRONMENT VARIABLES HAVE BEEN SET
# THIS CANNOT BE THE CASE IF WE ARE USING --help or pxdebug with no ARGS
# IF NO ENV ARGS HAVE BEEN SET THEN THE ENVIRONMENT WAS NEVER CONFIGURED IN THE FIRST PLACE
# SO IN THIS CASE SET THE ENVIRONMENT TO USE THE DEFAULTS

        enabled = os.environ.get('PXDEBUG_ENABLE')
        if enabled is None:
            # THE ENVIRONMENT NEEDS TO BE PROVISIONED WITH AN INITIAL CONFIG
            print("creating intial pxdebug config with default settings")
            os.environ['PXDEBUG_ENABLE'] = "YES"
            os.environ['PXDEBUG_LEVEL'] = "VERBOSE"
            os.environ['PXDEBUG_COLOR'] = "YES"
            os.environ['PXDEBUG_LOGGING'] = "YES"
            os.environ['PXDEBUG_LOGPATH'] = "DEFAULT"
            os.environ['PXDEBUG_LOGNAME'] = "DEFAULT"
            os.environ['PXDEBUG_ENABLETRACE'] = "YES"
            os.environ['PXDEBUG_ENABLEHIDDENTRACE'] = "NO"                
            os.environ['PXDEBUG_TESTFLAG'] = "NO"

        write_pxdebug_environment_vars_to_file()
       

        # also, if we got here we must have entered a valid option
        # so either we changed something or we used the --show command
        # either way print the new environment settings
        print_env_var('PXDEBUG_ENABLE')
        print_env_var('PXDEBUG_LEVEL')
        print_env_var('PXDEBUG_COLOR')
        print_env_var('PXDEBUG_LOGGING')
        print_env_var('PXDEBUG_LOGPATH')
        print_env_var('PXDEBUG_LOGNAME')
        print_env_var('PXDEBUG_ENABLETRACE')
        print_env_var('PXDEBUG_ENABLEHIDDENTRACE')
        print_env_var('PXDEBUG_TESTFLAG')


if __name__ == "__main__":
    
    
    
    args = sys.argv[1:] #all arguments except the program name
    if len(args) == 0:
        args = ['--help']
    if '--help' in args:
        print("THIS PROGRAM CONTROLS GLOBAL DEBUG SETTINGS FOR pxdebug.basic() and other")
        print("ROUTINES IN PYTHON MODULES WITH 'from pxdebugtools import pxdebug'")
        print("")
        print("YOU MUST SUPPLY AN OPTION WHEN RUNNING THIS PROGRAM. Examples:")
        print("use 'pxdebug --show' to show the current pxdebug settings without making changes")
        print("use 'pxdebug --enable' to enable pxdebug.out() and others in imported modules")
        print("use 'pxdebug --disable' to disable pxdebug.out() and others in imported modules")
        print("use 'pxdebug --max' to turn on all debug output from pxdebug including verbose and extreme levels")
        print("")
        pxdebug.parse_environment_arguments(args)
        os.exit(1)
    else:
        print("Configuring pxdebug environment...")
        pxdebug.parse_environment_arguments(args) 
        print("...pxdebug environment configured.")  
    









