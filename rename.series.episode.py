import re, os, sys, getopt, datetime

compressionList = ['x264', 'x265']
postFixList = ['480p', '720p', '1080p', 'x264', 'x265', 'HDTV', 'HEVC']
smallWords = ['the', 'of', 'in', 'into', 'it', 'and', 'a', 'an', 'on', 'at', 'to', 'from', 'by', 'but', 'or', 'for', 'nor', 'up', 'as', 'is', 'vs']
undoFile = 'C:\\RenameFiles\\undo'

def RunAsAdmin(forced):
    import win32api, win32con, win32event, win32process
    from win32com.shell.shell import ShellExecuteEx
    from win32com.shell import shellcon
    if forced == False:
        python_exe = sys.executable
    else:
        python_exe = sys.exec_prefix + '\\pythonw.exe'
    params = " ".join(['"%s"' % (x,) for x in sys.argv])
    #print python_exe
    #print params
    showCmd = win32con.SW_SHOWNORMAL
    #showCmd = win32con.SW_HIDE
    lpVerb = 'runas'  # causes UAC elevation prompt.
    procInfo = ShellExecuteEx(nShow=showCmd,
                              fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                              lpVerb=lpVerb,
                              lpFile=python_exe,
                              lpParameters=params)

def undoFileName(inputDirectory, inputFile, extension, forced):
    newFile = inputFile
    replacement = ()
    lines = []
    undoDone = False
    testVar = 'Y'
    title, ext = os.path.splitext(os.path.basename(inputFile))
    inputFile = inputDirectory + "\\" + title + ext
    #print inputFile
    if not os.path.isfile(undoFile):
        print "Invalid Undo File: " + undoFile + "!"
        sys.exit()
    with open(undoFile, "r") as ins:
        for line in ins:
            line = ' '.join(line.split())
            replacement = line.strip('\n').split(';', 1)
            if (replacement[0].strip('"') == inputFile) and not undoDone:
                undoDone = True
                newFile = replacement[1].strip('"')
            else:
                line += '\n'
                lines.append(line)
    if not forced:
        testVar = raw_input("Renaming: \n\"" + inputFile
                            + "\" to \n\"" + newFile
                            + "\".\n[Y(default)|N]")
        testVar = testVar.lower()
    if testVar != 'n' and testVar != 'no' and inputFile != newFile:
        try:
            os.rename(inputFile, newFile)
        except OSError:
            RunAsAdmin(forced)
            sys.exit()
        else:
            with open(undoFile, 'w') as outfile:
                for line in lines:
                    outfile.write(line)

def undo(inputFile, inputDirectory, extension, forced):
    if not os.path.isdir(inputFile):
        if not os.path.isfile(inputFile):
            if os.path.isfile(inputDirectory + "\\" + inputFile):
                inputFile = inputDirectory + "\\" + inputFile
            else:
                print "Invalid File: " + inputFile + " or " + inputDirectory + "\\" + inputFile + " !"
                sys.exit()
        elif os.path.dirname(inputFile) != "":
                inputDirectory = os.path.dirname(inputFile)
        undoFileName(inputDirectory, inputFile, extension, forced)
    else:
        sys.exit()
        

def writeUndoFile(oldName, newName):
    lines = []
    line = ''
    line = '"' + newName + '";"' + oldName + '"\n'
    lines.append(line)
    #print undoFile
    with open(undoFile) as infile:
        for line in infile:
            lines.append(line)
    with open(undoFile, 'w') as outfile:
        for line in lines:
            outfile.write(line)

def renameFile(inputDirectory, inputFile, extension, forced):
    newFile = ""
    testVar = ""
    title, ext = os.path.splitext(os.path.basename(inputFile))
    foundEp = False
    if (ext == extension):
        fileList = title.split("-")
        for file in fileList:
            episodeNum = re.split('(s)([0-9]+)(e)([0-9]+)', file, flags=re.IGNORECASE)
            if len(episodeNum) > 1:
                newFile = file
                foundEp = True
                break
            else:
                if any(substring in file for substring in postFixList):
                    newFile = file
                    foundEp = True
                    break
            episodeNum = re.split('([ \\.])([0-9]+)([ \\.])', file, flags=re.IGNORECASE)
            if len(episodeNum) > 1 and len(episodeNum[2]) == 3:
                newFile = file
                foundEp = True
                break
            episodeNum = re.split('([ \\.])(x)([0-9]+)([ \\.])', file, flags=re.IGNORECASE)
            if len(episodeNum) > 1 and len(episodeNum[3]) == 3:
                newFile = file
                foundEp = True
                break
        if not foundEp:
            newFile = fileList[0]
        if newFile == '':
            print 'No file found'
            return
        fileList = re.findall(r"[\w']+", newFile)
        i = 0
        newFileList = []
        found = False
        first = True
        last = True
        foundCompression = False
        for term in fileList:
            episodeNum = re.split('(s)([0-9]+)(e)([0-9]+)', term, flags=re.IGNORECASE)
            if not found and len(episodeNum) == 6:
                found = True
                newFileList.append("S" + episodeNum[2] + "E" + episodeNum[4])
                continue
            episodeNum = re.split('([0-9]+)', term, flags=re.IGNORECASE)
            if not found and len(episodeNum) == 3 and len(episodeNum[1]) == 3 and len(newFileList) >= 1 and len(episodeNum[2]) == 0:
                if term.lower() in (postFix.lower() for postFix in postFixList) or int(episodeNum[1])%100 == 0:
                    newFileList.append(term)
                    continue
                found = True
                #print 'episodeNum:', episodeNum
                newFileList.append("S0" + episodeNum[1][0] + "E" + episodeNum[1][1] + episodeNum[1][2])
                continue
            if found:
                if last:
                    newFileList[-2] = newFileList[-2].title()
                    last = False
                if term.lower() in (postFix.lower() for postFix in postFixList):
                    newFileList.append(term)
                    if term.lower() in (compression.lower() for compression in compressionList):
                        foundCompression = True
            else:
                if (term.lower() in (postFix.lower() for postFix in postFixList)):
                    if not found:
                        found = True
                else:
                    term = term.lower()
                if (first or term.lower() not in smallWords) and term[0].isalpha() and (term.lower() not in (postFix.lower() for postFix in postFixList)):
                        term = term.lower()
                        term = term.title()
                        if len(term) > 1 and term[-2] == '\'':
                            term = term[:-1] + str(term[-1]).lower()
                        first = False
                if term.lower() in (compression.lower() for compression in compressionList):
                    foundCompression = True
                newFileList.append(term)
        if not foundCompression and found:
            newFileList.append('x264')
        newFile = ''
        for term in newFileList:
            newFile = newFile + term + '.'
        newFile = newFile.strip('.')
        inputFile = inputDirectory + "\\" + title + ext
        newFile =  inputDirectory + "\\" + newFile + ext
        if not forced:
            testVar = raw_input("Renaming: \n\"" + inputFile
                                + "\" to \n\"" + newFile
                                + "\".\n[Y(default)|N]")
            testVar = testVar.lower()
        if testVar != 'n' and testVar != 'no' and inputFile != newFile:
            #os.rename(inputFile, newFile)
            try:
                os.rename(inputFile, newFile)
            except OSError:
                RunAsAdmin(forced)
                sys.exit()
            else:
                writeUndoFile(inputFile, newFile)

def rename(isInputFile, inputFile, inputDirectory, extension, recursive, forced):
    if isInputFile:
        if not os.path.isdir(inputFile):
            if not os.path.isfile(inputFile):
                if os.path.isfile(inputDirectory + "\\" + inputFile):
                    inputFile = inputDirectory + "\\" + inputFile
                else:
                    print "Invalid File: " + inputFile + " or " + inputDirectory + "\\" + inputFile + " !"
                    sys.exit()
            elif os.path.dirname(inputFile) != "":
                    inputDirectory = os.path.dirname(inputFile)
            renameFile(inputDirectory, inputFile, extension, forced)
    else:
        if os.path.isdir(inputDirectory):
            for file in os.listdir(inputDirectory):
                if os.path.isdir(inputDirectory + "\\" + file):
                    if recursive:
                        rename(isInputFile, inputFile, inputDirectory + "\\" + file, extension, recursive, forced)
                else:
                    renameFile(inputDirectory, file, extension, forced)
        else:
            print "Invalid Directory: " + inputDirectory + "!"
            sys.exit()

def main(argv):
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
    if not doUndo:
        a = datetime.datetime.now()
        rename(isInputFile, inputFile, inputDirectory, extension, recursive, forced)
        b = datetime.datetime.now()
        print 'Completed the processing in:'
        print b - a
        if debug:
            raw_input()
    else:
        undo(inputFile, inputDirectory, extension, forced)

if __name__ == "__main__":
    main(sys.argv[1:])