import sys, os, traceback, types, getopt

def hasPermissions(inputDirectory):
    #print 'C:\Users\admin\Pictures'
    print inputDirectory
    value = os.access(inputDirectory, os.W_OK)
    print value
    return value

def runAsAdmin(cmdLine, forced = False):
    print cmdLine
    wait = True
    if os.name != 'nt':
        raise RuntimeError, "This function is only implemented on Windows."

    import win32api, win32con, win32event, win32process
    from win32com.shell.shell import ShellExecuteEx
    from win32com.shell import shellcon

    python_exe = sys.executable
    print [python_exe]
    print sys.argv
    
    if cmdLine is None:
        cmdLine = [python_exe] + sys.argv
    elif type(cmdLine) not in (types.TupleType,types.ListType):
        raise ValueError, "cmdLine is not a sequence."
    #cmd = '"%s"' % (cmdLine[0],)
    if forced == False:
        cmd = "python.exe"
    else:
        cmd = "pythonw.exe"
    # XXX TODO: isn't there a function or something we can call to massage command line params?
    params = "C:\\RenameFiles\\rename.series.episode.py "
    params += " ".join(['"%s"' % (x,) for x in cmdLine[0:]])
    print params
    cmdDir = ''
    showCmd = win32con.SW_SHOWNORMAL
    #showCmd = win32con.SW_HIDE
    lpVerb = 'runas'  # causes UAC elevation prompt.

    # print "Running", cmd, params

    # ShellExecute() doesn't seem to allow us to fetch the PID or handle
    # of the process, so we can't get anything useful from it. Therefore
    # the more complex ShellExecuteEx() must be used.

    # procHandle = win32api.ShellExecute(0, lpVerb, cmd, params, cmdDir, showCmd)

    print cmd
    procInfo = ShellExecuteEx(nShow=showCmd,
                              fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                              lpVerb=lpVerb,
                              lpFile=cmd,
                              lpParameters=params)

    if wait:
        procHandle = procInfo['hProcess']    
        obj = win32event.WaitForSingleObject(procHandle, win32event.INFINITE)
        rc = win32process.GetExitCodeProcess(procHandle)
        #print "Process handle %s returned code %s" % (procHandle, rc)
    else:
        rc = None

    return rc

def main(argv):
    print argv
    inputDirectory = os.getcwd()
    inputFile = ''
    extension = '.mkv'
    recursive = False
    forced = False
    doUndo = False
    debug = False
    isInputFile = False
    extensionFound = False
    try:
        opts, args = getopt.getopt(argv,"hRFUDi:d:e:", ["inputFile=", "inputDirectory=", "extension="])
    except getopt.GetoptError:
        print 'rename.series.episode.py [-R|F|U|D] -i <inputFile> -d <inputDirectory> -e <extension>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'rename.series.episode.py [-R|F|U|D] -i <inputFile> -d <inputDirectory> -e <extension>'
            sys.exit()
        elif opt == '-R':
            recursive = True
        elif opt == '-F':
            forced = True
        elif opt == '-U':
            doUndo = True
        elif opt == '-U':
            debug = True
        elif opt in ("-d", "--inputDirectory"):
            inputDirectory = arg
        elif opt in ("-i", "--inputFile"):
            isInputFile = True
            inputFile = arg
            if not extensionFound:
                title, ext = os.path.splitext(os.path.basename(inputFile))
                extension = ext
        elif opt in ("-e", "--extension"):
            extension = arg
            extensionFound = True
    inputDirectory = inputDirectory.strip("\\")
    if hasPermissions(inputDirectory):
        print "You're not an admin.", os.getpid(), "params: ", sys.argv
        rc = runAsAdmin(argv)
        #rc = runAsAdmin()
    else:
        print "You are an admin!", os.getpid(), "params: ", sys.argv
        rc = 0
    x = raw_input('Press Enter to exit.')
    return rc


if __name__ == "__main__":
    main(sys.argv[1:])
