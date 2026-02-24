import sys

if(len(sys.argv)==2):
    # (first is the running script) it's a file. Load it
    args = []
    with open(sys.argv[1]) as file:
        line = file.readline()
        while(line):
            args += line[:-1].split(' ') # remove newline character
            line = file.readline()
    
    sargs = dict([ (a, b) for a,b in zip(args[0::2], args[1::2])])
else:
    sargs = dict([ (a, b) for a,b in zip(sys.argv[1::2], sys.argv[2::2]) ])
