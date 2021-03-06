from __future__ import division
from time import sleep
import re, os, sys, getopt, datetime, random

compressionList = ['x264', 'x265']
postFixList = ['480p', '720p', '1080p', 'x264', 'x265', 'HDTV', 'HEVC']
smallWords = ['the', 'of', 'in', 'into', 'it', 'and', 'a', 'an', 'on', 'at', 'to', 'from', 'by', 'but', 'or', 'for', 'nor', 'up', 'as', 'is', 'vs']
undoFile = 'C:\\RenameFiles\\undo'

renameDirList = str(os.environ.get('RENAME_DIR_LIST'))

def findSeriesName(short):
    list = []
    for dir in os.listdir(renameDirList):
        if os.path.isdir(renameDirList + '\\' + dir):
            last = -1
            score = 0.0
            cScore = 0.0
            temp = 0.0
            large = ''
            small = ''
            if len(dir) >= len(short):
                large = dir
                small = short
            else:
                large = short
                small = dir

            ll = len(large)
            sl = len(small)
            for i in range(sl):
                temp = ll - (last + 1)
                last = large.lower().find(small.lower()[i], last + 1)
                if last == -1:
                    break
                cScore = (sl - i) * (ll - last) / temp
                if last != 0:
                    if large[last - 1] == ' ':
                        cScore = cScore * 1.25
                score = score + cScore
            score = 2 * score * 100 / (sl * (sl + 1))
            if score > 100:
                score = 100.0
            list.append((score, dir))
    list.sort(reverse=True)
    return list

def RunAsAdmin(forced):
    import win32api, win32con, win32event, win32process
    from win32com.shell.shell import ShellExecuteEx
    from win32com.shell import shellcon
    if forced == False:
        python_exe = sys.executable
    else:
        python_exe = sys.exec_prefix + '\\pythonw.exe'
    params = " ".join(['"%s"' % (x,) for x in sys.argv])
    showCmd = win32con.SW_SHOWNORMAL
    lpVerb = 'runas'  # causes UAC elevation prompt.
    procInfo = ShellExecuteEx(nShow=showCmd,
                              fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                              lpVerb=lpVerb,
                              lpFile=python_exe,
                              lpParameters=params)

def addNewFileToUndoFile(oldName, newName):
    line = ''
    line = '"' + newName + '";"' + oldName + '"\n'
    renameUndoFile = undoFile + str(random.randint(1, 1000))
    while True:
        try:
            os.rename(undoFile, renameUndoFile)
            with open(renameUndoFile, 'r+b') as f:
                content = f.read()
                f.seek(0, 0)
                f.write(line.rstrip('\r\n') + '\n' + content)
            break
        except OSError:
            sleep(random.uniform(0.5, 1.9))
            continue
        except IOError:
            break

    while True:
        try:
            os.rename(renameUndoFile, undoFile)
            break
        except OSError:
            continue

def writeLinesToUndoFile(lines):
    renameUndoFile = undoFile + str(random.randint(1, 1000))
    while True:
        try:
            os.rename(undoFile, renameUndoFile)
            with open(renameUndoFile, 'wb') as f:
                for line in lines:
                    f.write(line)
            break
        except OSError:
            sleep(random.uniform(0.5, 1.9))
            continue
        except IOError:
            break

    while True:
        try:
            os.rename(renameUndoFile, undoFile)
            break
        except OSError:
            continue

def findFileInUndoFile(file):
    renameUndoFile = undoFile + str(random.randint(1, 1000))
    lineFound = ''
    while True:
        try:
            os.rename(undoFile, renameUndoFile)
            with open(renameUndoFile, "r") as ins:
                for line in ins:
                    line = ' '.join(line.split())
                    replacement = line.strip('\n').split(';', 1)
                    if (replacement[0].strip('"') == file):
                        lineFound = line
                        break
            break
        except OSError:
            sleep(random.uniform(0.5, 1.9))
            continue
        except IOError:
            break

    while True:
        try:
            os.rename(renameUndoFile, undoFile)
            break
        except OSError:
            continue
    return lineFound

def removeLineFromUndoFile(line):
    lines = []
    renameUndoFile = undoFile + str(random.randint(1, 1000))
    while True:
        try:
            os.rename(undoFile, renameUndoFile)
            with open(renameUndoFile, "r") as ins:
                for oldline in ins:
                    oldline = ' '.join(oldline.split())
                    if (oldline != line):
                        lines.append(oldline)
            with open(renameUndoFile, "wb") as f:
                for wline in lines:
                    f.write(wline + '\n')
            break
        except OSError:
            sleep(random.uniform(0.5, 1.9))
            continue
        except IOError:
            break

    while True:
        try:
            os.rename(renameUndoFile, undoFile)
            break
        except OSError:
            continue

def undoFileName(inputDirectory, inputFile, extension, forced):
    newFile = inputFile
    replacement = ()
    lines = []
    undoDone = False
    testVar = 'Y'
    title, ext = os.path.splitext(os.path.basename(inputFile))
    inputFile = inputDirectory + "\\" + title + ext
    if not os.path.isfile(undoFile):
        print "Invalid Undo File: " + undoFile + "!"
        sys.exit()
    line = findFileInUndoFile(inputFile)
    if line == '':
        return

    line = ' '.join(line.split())
    newFile = (line.strip('\n').split(';', 1))[1].strip('"')

    if not forced:
        testVar = raw_input("Renaming: \n\"" + inputFile
                            + "\" to \n\"" + newFile
                            + "\".\n[Y(default)|N]")
        testVar = testVar.lower()
    if testVar != 'n' and testVar != 'no' and inputFile != newFile:
        try:
            os.rename(inputFile, newFile)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                RunAsAdmin(forced)
            sys.exit()
        else:
            removeLineFromUndoFile(line)

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
        

def renameFile(inputDirectory, inputFile, extension, forced, validation):
    newFile = ""
    testVar = ""
    title, ext = os.path.splitext(os.path.basename(inputFile))
    foundEp = False
    nameList = []
    seriesNumIndex = -1
    choice = 0
    isMovie = False
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
                newFileList.append("S0" + episodeNum[1][0] + "E" + episodeNum[1][1] + episodeNum[1][2])
                continue
            if found:
                if last:
                    if not isMovie:
                        seriesNumIndex = len(newFileList) - 1
                        nameList = findSeriesName(' '.join(newFileList[0:len(newFileList) - 1]))
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
                        isMovie = True
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
        testVar = 'y'
        if not forced:
            if seriesNumIndex == -1:
                testVar = raw_input("Renaming: \n\"" + inputFile
                                    + "\" to \n\"" + newFile
                                    + "\".\n[Y(default)|N]")
                testVar = testVar.lower()
            else:
                option = ''
                opC = 1
                for name in nameList:
                    if name[0] > 50:
                        option = option + str(opC) + '. ' + str(name[1]) + ' (' + str("%.2f" % name[0]) + '%)' + '\n'
                        opC = opC + 1
                    else:
                        break
                testVar = raw_input('Choose from options: (0 for none) \n' + option)
                testVar = testVar.lower()
                if testVar == '0':
                    testVar = 'n'
                else:
                    if testVar != '':
                        choice = int(testVar) - 1
                    validation = True
        if validation and nameList[choice][0] > 50:
            newFileList = re.findall(r"[\w']+", nameList[choice][1]) + newFileList[seriesNumIndex:]
            newFile = ''
            for term in newFileList:
                newFile = newFile + term + '.'
            newFile = newFile.strip('.')
            inputFile = inputDirectory + "\\" + title + ext
            newFile =  inputDirectory + "\\" + newFile + ext

        if testVar != 'n' and testVar != 'no' and inputFile != newFile:
            try:
                os.rename(inputFile, newFile)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    RunAsAdmin(forced)
                sys.exit()
            else:
                addNewFileToUndoFile(inputFile, newFile)

def rename(isInputFile, inputFile, inputDirectory, extension, recursive, forced, validation):
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
            renameFile(inputDirectory, inputFile, extension, forced, validation)
    else:
        if os.path.isdir(inputDirectory):
            for file in os.listdir(inputDirectory):
                if os.path.isdir(inputDirectory + "\\" + file):
                    if recursive:
                        rename(isInputFile, inputFile, inputDirectory + "\\" + file, extension, recursive, forced)
                else:
                    renameFile(inputDirectory, file, extension, forced, validation)
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
    validation = False
    try:
        opts, args = getopt.getopt(argv,"hRFUDVi:d:e:", ["inputFile=", "inputDirectory=", "extension="])
    except getopt.GetoptError:
        print 'rename.series.episode.py [-R|F|U|D|V] -i <inputFile> -d <inputDirectory> -e <extension>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'rename.series.episode.py [-R|F|U|D|V] -i <inputFile> -d <inputDirectory> -e <extension>'
            sys.exit()
        elif opt == '-R':
            recursive = True
        elif opt == '-F':
            forced = True
        elif opt == '-U':
            doUndo = True
        elif opt == '-D':
            debug = True
        elif opt == '-V':
            validation = True
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
        rename(isInputFile, inputFile, inputDirectory, extension, recursive, forced, validation)
        b = datetime.datetime.now()
        print 'Completed the processing in:'
        print b - a
        if debug:
            raw_input()
    else:
        undo(inputFile, inputDirectory, extension, forced)

if __name__ == "__main__":
    main(sys.argv[1:])