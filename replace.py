import re, os, sys, getopt

def replaceFile(inputDirectory, inputFile, extension, replacements):
    title, ext = os.path.splitext(os.path.basename(inputFile))
    if (ext == extension):
        print "Input File:\"" + inputFile + "\""
        lines = []
        with open(inputFile) as infile:
            for line in infile:
                line = ' '.join(line.split())
                for src, target in replacements:
                    line = line.replace(src, target)
                lines.append(line)
        with open(inputFile, 'w') as outfile:
            for line in lines:
                outfile.write(line)

def replace(isInputFile, inputFile, inputDirectory, extension, recursive, replacements):
    if isInputFile:
        if not os.path.isdir(inputFile):
            if not os.path.isfile(inputFile):
                if os.path.isfile(inputDirectory + "\\" + inputFile):
                    inputFile = inputDirectory + "\\" + inputFile
                else:
                    print "Invalid File: " + inputFile + " or " + inputDirectory + "\\" + inputFile + "!"
            elif os.path.dirname(inputFile) != "":
                    inputDirectory = os.path.dirname(inputFile)
            replaceFile(inputDirectory, inputFile, extension, replacements)
    else:
        if os.path.isdir(inputDirectory):
            for file in os.listdir(inputDirectory):
                if os.path.isdir(inputDirectory + "\\" + file):
                    if recursive:
                        replace(isInputFile, inputFile, inputDirectory + "\\" + file, extension, recursive, replacements)
                else:
                    replaceFile(inputDirectory, file, extension, replacements)
        else:
            print "Invalid Directory: " + inputDirectory + "!"
            sys.exit()

def main(argv):
    inputDirectory = os.getcwd()
    inputFile = ''
    extension = '.config'
    recursive = False
    isInputFile = False
    extensionFound = False
    replaceFileFound = False
    replaceFileName = ''
    try:
        opts, args = getopt.getopt(argv,"hRi:d:e:r:", ["inputFile=", "inputDirectory=", "extension=", "replaceFile"])
    except getopt.GetoptError:
        print 'invalid or missing argument, use argument -h for help'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'replace.py [-R] -i <inputFile> -d <inputDirectory> -e <extension> -r <replaceFile>'
            print '-R: (optional) Recursive'
            print '-i: (optional) input file (for single file, here -e and -d will be ignored)'
            print '-d: (optional) input directory, default: current directory'
            print '-e: (optional) file extension, default: .config'
            print '-r: (required) input replacement file'
            sys.exit()
        elif opt == '-R':
            recursive = True
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
        elif opt in ("-r", "--extension"):
            replaceFileName = arg
            replaceFileFound = True
    if replaceFileFound == False:
        print '-r <replaceFile> is required'
        sys.exit()
    inputDirectory = inputDirectory.strip("\\")
    
    replacements = []
    if not os.path.isfile(replaceFileName):
        print "Invalid Replacement File: " + replaceFileName + "!"
        sys.exit()
    with open(replaceFileName, "r") as ins:
        for line in ins:
            line = ' '.join(line.split())
            replacements.append(line.strip('\n').split(' ', 1))

    testVar = raw_input("Input: \nInput File:\"" + inputFile
                        + "\"\nInput Directory:\"" + inputDirectory
                        + "\"\nInput Extension:\"" + extension
                        + "\"\nInput Replacement File:\"" + replaceFileName
                        + "\"\nInput Recursive:\"" + str(recursive)
                        + "\".\n[Y(default)|N]")
    testVar = testVar.lower()
    if testVar == '' or testVar == 'y' or testVar == 'yes':
        replace(isInputFile, inputFile, inputDirectory, extension, recursive, replacements)

if __name__ == "__main__":
    main(sys.argv[1:])