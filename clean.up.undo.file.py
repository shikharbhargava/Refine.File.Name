import os, sys

undoFile = 'C:\\RenameFiles\\undo'
maxLines = 250

def cleanUpUndoFile():
    replacement = ()
    lines = []
    lineCount = 0
    
    if not os.path.isfile(undoFile):
        print "Invalid Undo File: " + undoFile + "!"
        sys.exit()
    with open(undoFile, "r") as ins:
        for line in ins:
            line = ' '.join(line.split())
            replacement = line.strip('\n').split(';', 1)
            if os.path.isfile(replacement[0].strip('"')):
                line += '\n'
                lines.append(line)
    with open(undoFile, 'w') as outfile:
        for line in lines:
            if lineCount < maxLines:
                outfile.write(line)
                lineCount += 1
            else:
                break

def main(argv):
    cleanUpUndoFile()

if __name__ == "__main__":
    main(sys.argv[1:])