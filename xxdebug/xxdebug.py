# @author mikedefrancis
# a usable debug framework for python prints

#########################################################
####         XXDEBUG          ###########################
#### a juicy python 2.7 and up debug printing framework #
#########################################################

import sys
import os
import argparse

import subprocess
import shutil
from shutil import copy2
from os.path import expanduser

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
if os.name == 'posix':
    env_debug_color = os.environ.get('XXDEBUG_COLOR')
    if env_debug_color is not None:
        if env_debug_color.upper() == "COLOR":
            try:
                from colors import *
            except:
                print "xxdebug failed to load colors module. Make sure that you have colors.py."
                os.exit(-1)


# A class to show some debug infos and functions to conditionally print massive amounts of colored text to the screen
# This is just a bunch of static methods with some environment variable stupidity added.
class xxdebug():

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
    logfile_name = "xxdebug_autolog"
    if env_logfile_name is not None:
        logfile_name = env_logfile_name
    
    env_logfile_path = os.environ.get('XXDEBUG_LOGPATH')
    logfile_path = "~/xxdebug/"
    if env_logfile_path is not None:
        logfile_path = env_logfile_path

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
                logpath = os.path.join(Directory.brass_logdir, logfile_full_name)
                logfile = open(logpath, 'w+') 
            ########### END LOG FILE SHENANIGANS ################



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
        if ((xxdebug.debug_enabled == True) and (xxdebug.debug_level >= dlevel.DBG_BASIC)):
            if (xxdebug.show_only_this_level == False) or (xxdebug.debug_level == dlevel.DBG_BASIC):
                if xxdebug.color_enabled == True:
                    print green(msg)
                else:
                    print msg
        xxdebug.logprint(msg)
                
    # a message that shows up bright yellow but only when --color is used    
    @staticmethod
    def verbose_print(msg):
        msg = "VERBOSE DBG: " + str(msg)
        if ((xxdebug.debug_enabled == True) and (xxdebug.debug_level >= dlevel.DBG_VERBOSE)):
            if (xxdebug.show_only_this_level == False) or (xxdebug.debug_level == dlevel.DBG_VERBOSE):
                if xxdebug.color_enabled == True:
                    print yellow(msg)
                else:
                    print msg
        xxdebug.logprint(msg)
       
    # a message that shows up bright yellow but only when --color is used    
    @staticmethod
    def superuser_print(msg):
        msg = "SUPERUSER DBG: " + str(msg)
        if ((xxdebug.debug_enabled == True) and (xxdebug.debug_level >= dlevel.DBG_SUPERUSER)):
            if (xxdebug.show_only_this_level == False) or (xxdebug.debug_level == dlevel.DBG_SUPERUSER):
                if xxdebug.color_enabled == True:
                    print red(msg)
                else:
                    print msg
        xxdebug.logprint(msg)

#    # a message that shows up bright white on console
#    @staticmethod
#    def regular_print(msg):
#        msg = "BASIC DBG: " +str(msg) 
#        if xxdebug.color_enabled == True:
#            #  print white(msg, style='bold')
#            print white(msg)
#        else:
#            print str(msg)
#        xxdebug.logprint(msg)

    # MACROS
    # print basic debug message with a few aliases
    @staticmethod
    def bprint(msg):
        xxdebug.debug_print(msg)
    @staticmethod
    def basic(msg):
        xxdebug.debug_print(msg)         
    @staticmethod
    def debug(msg):
        xxdebug.debug_print(msg)
    @staticmethod
    def bout(msg):
        xxdebug.debug_print(msg)        
    @staticmethod
    def out(msg):
        xxdebug.debug_print(msg)        
    # verbose debug message
    @staticmethod
    def verbose(msg):
        xxdebug.verbose_print(msg)
    @staticmethod
    def vprint(msg):
        xxdebug.verbose_print(msg)
    @staticmethod
    def vout(msg):
        xxdebug.verbose_print(msg)
    # superuser debug message (not for the faint of heart)
    @staticmethod
    def superuser(msg):
        xxdebug.superuser_print(msg)
    @staticmethod
    def sprint(msg):
        xxdebug.superuser_print(msg)
    @staticmethod
    def sout(msg):
        xxdebug.superuser_print(msg)
########################################################################

    # A function to cause a software breakpoint
    @staticmethod
    def breakx(msg=None):
        text = "<Manual Breakpoint> "+ str(msg)
        vout(text)
        raise ValueError(text)

    #A function to print text and then request user input in order to continue
    @staticmethod
    def breaki(msg=None):
        text = "<Manual Breakpoint> "+ str(msg)
        vout(text)
        input(text)

    # A function to print the output from the most recent invocation of IDA Pro to the command line
    # This function prints the output in color if the -c option was passed to brass
    @staticmethod
    def print_and_erase_idalog():
        # 
        if not os.path.exists(xxdebug.idalog_path):
            vout("IDALOG does not exist")
            return
        else:
            with open(xxdebug.idalog_path) as f:
                if xxdebug.color_enabled == True:
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
                xxdebug.logprint(line.rstrip())
            
            # NOW DELETE THE IDALOG FILE
            copy2(xxdebug.idalog_path, xxdebug.idalog_back_path)
            os.unlink(xxdebug.idalog_path)    
            
            
    # the most basic of output to file 
    @staticmethod
    def logprint(text):
        # for stupidity's sake, lets keep the logfile open the entire time so that we can keep adding to it
        # and then just have python close the file for us when the interpreter detects the end of the program =D
        # TODO: hacks
        if xxdebug.do_logging:
            print 'here we are'
            if xxdebug.logfile is not None:
                print 'there we are'
                xxdebug.logfile.write(text + '\n')
        
    @staticmethod
    def parse_environment_arguments(options):

        parser = argparse.ArgumentParser(description='xxdebug - automagic verbose color debug autologging for python 2.7+', \
                                        epilog='Use xxdebug to control debug level, color printing, and autologging to file \
                                        across all of your python programs.')
        
        
        # It is required for an input file to be specified
        parser.add_argument('-l', '--level', action="store",  type=str, help="define the verbosity level of debug output \n" \
                            + " options=['NONE', 'BASIC', 'VERBOSE', 'SUPERUSER', 'DEFAULT (basic)', 'MAX (superuser)'] default is BASIC")

        parser.add_argument('-x', '--showonlythislevel', action="store_true", help="force xxdebug to show only the selected \n" \
                            + " level of debug output (eg. verbose), rather than this and all lesser (eg. verbose, basic)")
       

        parser.add_argument('-z', '--showapplicable', action="store_true", help="default print setting inverse of -x option")

        parser.add_argument('-a', '--autolog', action="store_true", help="force xxdebug to log all xxdebug prints to a logfile \
                            \n NOTE: LOGGING IS DISABLED BY DEFAULT UNTIL THIS OPTION IS PASSED TO XXDEBUG")

        parser.add_argument('-c', '--color', action="store_true", help="(default) force xxdebug to print output in color")

        parser.add_argument('-y', '--nocolor', action="store_true", help="tell xxdebug to print output without color")

        parser.add_argument('-p', '--logpath', action="store", type=str, help="specify a custom path for xxdebug logfile \
                            (default = ~/xxdebug/)")

        parser.add_argument('-n', '--logname', action="store", type=str, help="specify a custom name for the logfile \
                            (default = xxdebug_autolog)")
 
        parser.add_argument('-d', '--default','--defaults', action="store_true", help="revert xxdebug to defaults specified in help")

        parser.add_argument('-m', '--max', action="store_true", help="enable the maximum amount of xxdebug logging/prints")

        parser.add_argument('-o', '--off', action="store_true", help="disable all xxdebug output from all files using xxdebug")

        parser.add_argument('--enable', action="store_true", help="enable default xxdebug output from all files using xxdebug")

        parser.add_argument('--disable', action="store_true", help="disable all xxdebug output from all files using xxdebug")
        
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
                os.environ['XXDEBUG_LOGPATH'] = "~/xxdebug/"
                os.environ['XXDEBUG_LOGNAME'] = "xxdebug_autolog"
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
                os.environ['XXDEBUG_SHOW_ONLY_THIS_LEVEL'] = 'NO'
                os.egnviron['XXDEBUG_COLOR'] = "COLOR"
                os.environ['XXDEBUG_LOGGING'] = "YES"
                os.environ['XXDEBUG_LOGPATH'] = "~/xxdebug/"
                os.environ['XXDEBUG_LOGNAME'] = "xxdebug_autolog"
        if args.disable is not None:
            if args.disable == True:
                print "disabling xxdebug features"
                os.environ['XXDEBUG_LEVEL'] = "NONE"
                os.environ['XXDEBUG_SHOW_ONLY_THIS_LEVEL'] = 'NO'
                os.environ['XXDEBUG_COLOR'] = "NOCOLOR"
                os.environ['XXDEBUG_LOGGING'] = "NO"


        write_xxdebug_environment_vars_to_file()
        








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
        xxdebug.parse_environment_arguments(args)
        os.exit(1)
    else:
        print("Configuring xxdebug environment...")
        xxdebug.parse_environment_arguments(args) 
        print("...xxdebug environment configured.")  
    









