#!/usr/bin/python2

from math import pow
from os import system
import random
import sys

class GenConfig:
    """ Contains configuration info for given rules/traces setup """

    def __init__( self , title , header , nRules , nTraces , dataSource="PATTFILE" , DCFlag="" ):
        self.title      = title
        self.header     = header
        self.nRules     = nRules
        self.nTraces    = nTraces
        self.dataSource = dataSource # PATTFILE , COUNTER , or RANDOM
        self.DCFlag     = DCFlag
        
        self.nLayers = len(header)
        self.nBits   = [ int(h[:-1]) for h in self.header ]

        self.configStr = "%s_%i_%i_%s" % (self.title,self.nRules,self.nTraces,self.dataSource)
        if not(DCFlag==""): self.configStr+= "_%s" % (DCFlag)

        self.rulesPath         = "rules/Test_"+self.configStr+".rules"
        self.rulesPathCompiled = "rules/Test_"+self.configStr+".bin"
        self.rulesPathOct      = "rules/Test_"+self.configStr+".oct.bin"
        self.tracesPath        = "traces/Test_"+self.configStr+".traces"
        self.pktheadersPath    = "pktheaders/Test_"+self.configStr+".h"
        self.nsptestPath       = "nsptest/nsp_test_"+self.configStr
        self.nspperftestPath   = "nsptest/nsp_perf_test_"+self.configStr

        self.rulesFile  = open( self.rulesPath , 'w' )
        self.tracesFile = open( self.tracesPath , 'w' )

        self.tracesList = []

        self.headerStr = " ".join(self.header)
        self.rulesFile.write( self.headerStr+"\n" )

    def close( self ):
        self.rulesFile.close()
        self.tracesFile.close()

    def baseRule( self , data ):
        # Construct rule for this particular configuration
        d = data[self.dataSource]
        if self.nLayers == 9:
            # This means we have a sort of complicated DC config where we need to split up the
            # last word into a regular part and a DC part
            return [hex(d[l]) for l in range(7)] + [hex(d[7] >> self.nBits[8])] + [hex(d[7] & int(pow(2,self.nBits[8])-1))]
        elif self.DCFlag == "" or self.nLayers <= 8:
            # Nothing complicated to do
            return [ hex(d[l]) for l in range(self.nLayers) ]
        else:
            # Not sure about this case
            sys.exit()
        
    def study( self ):
        print "INFO : Studying configuration",self.configStr,"..."
        nspPath = "/users/jwebster/L1Track/Cavium/NSP-SDK-2.2.1/nsp-utils/"
        cmd1 = nspPath+"nspc -i "+self.rulesPath+" -o "+self.rulesPathCompiled
        #cmd2 = nspPath+"nspc.oct -i "+self.rulesPath+" -o "+self.rulesPathOct
        nsptCmds = [ "load "+self.rulesPathCompiled ,
                     "lib -stats db -name "+self.rulesPathCompiled ,
                     "dev -lookup "+self.tracesPath+" -group "+self.rulesPathCompiled , # --verbose
                     "dev -read stats" ]
        cmd3 = nspPath+"nspt -c \"" + ";".join(nsptCmds[:2]) + "\""
        cmd4 = nspPath+"nspt -c \"" + ";".join(nsptCmds) + "\""
        cmd5 = nspPath+"nspt -c \"" + ";".join(["load "+self.rulesPathCompiled,"run "+self.tracesPath]) + "\""
        cmd6 = nspPath+"nspt -c \"" + ";".join(["lib -add db -file "+self.rulesPathCompiled+" -name db0","lib -add group -name g0 db0","dev -lookup "+self.tracesPath+" -group g0"]) + "\" -dbg=l > "+self.pktheadersPath
        print "  "+cmd1
        system( cmd1 )
        #print "  "+cmd2
        #system( cmd2 )
        print "  "+cmd3
        system( cmd3 + " > TEMP.out" )
        print "  "+cmd4
        system( cmd4 + " >> TEMP.out" )
        print "  "+cmd5
        system( cmd5 + " >> TEMP.out" )
        print "  "+cmd6
        system( cmd6 )

        # Clean up the packet header
        cmd7 = ";".join(["x=`wc -l "+self.pktheadersPath+" | awk '{print $1}'`",
                         "y=`head -n 2 "+self.pktheadersPath+" | tail -n 1 | sed -e 's#,#\\n#g' | wc -l`",
                         "echo \"uint8_t pkt_data[][`expr $y - 1`] = {\" > pktheader.tmp",
                         "tail -n `expr $x - 1` "+self.pktheadersPath+" | head -n `expr $x - 8` >> pktheader.tmp",
                         "tail -n 6 "+self.pktheadersPath+" >> pktheader.tmp",
                         "mv pktheader.tmp "+self.pktheadersPath])
        print "  "+cmd7
        system( cmd7 )

        # Build NSP test executables from header
        cmd8 = ";".join(["cd /users/jwebster/L1Track/Cavium/NSP-SDK-2.2.1/nsp-agent/platform/app/patched_nsp_test",
                         "cp nsp_pkt_test_TEMPLATE.c nsp_pkt_test.c",
                         "perl -p -i -e 's#REPLACEME#/users/jwebster/L1Track/Cavium/scripts/"+self.pktheadersPath+"#g' nsp_pkt_test.c",
                         "make clean && make && cp nsp_test /users/jwebster/L1Track/Cavium/scripts/"+self.nsptestPath,
                         "cd /users/jwebster/L1Track/Cavium/NSP-SDK-2.2.1/nsp-agent/platform/app/patched_nsp_perf_test",
                         "cp nsp_perf_test_TEMPLATE.c nsp_perf_test.c",
                         "perl -p -i -e 's#REPLACEME#/users/jwebster/L1Track/Cavium/scripts/"+self.pktheadersPath+"#g' nsp_perf_test.c",
                         "make clean && make && cp nsp_perf_test /users/jwebster/L1Track/Cavium/scripts/"+self.nspperftestPath,
                         "cd /users/jwebster/L1Track/Cavium/scripts"])
        print cmd8
        system( cmd8 )
        
        
        #system( "cat TEMP.out" )
        # Look at results in temp file
        tmpf = open( "TEMP.out" , 'r' )
        self.nClusters = tmpf.readline().split()[4]
        tmpf.readline()
        self.lookupRate = tmpf.readline().split()[1]
        tmpf.readline()
        tmpf.readline()
        l = tmpf.readline().replace(",","").split()
        self.matchingFraction = float(l[3]) / float(l[1])
        tmpf.close()
        system( "rm -f TEMP.out" )
        
        results = [ self.title , self.dataSource , self.nRules , self.nTraces , self.nClusters , self.lookupRate , self.matchingFraction , self.DCFlag ]
        print "  Results =",results
        return results


random.seed( 100 )
    
iFilePath = "MergedPatterns_ss40_1M.out"
iFile     = open( iFilePath , 'r' )

# Skip leading line in patterns file
iFile.seek(0,0)
iFile.readline()

configs = []
#for nRules in [ 500 , 1000 , 10000 , 50000 , 100000 , 150000 , 200000 ]:
for nRules in [ 500 , 1000 , 10000 , 50000 , 100000 , 150000 , 200000 ]:
    # for dataSource in [ "COUNTER" , "PATTFILE" , "RANDOM" ]:
    # for dataSource in [ "RANDOM" ]:
    for dataSource in [ "PATTFILE" ]:
        if dataSource == "COUNTER" or dataSource == "RANDOM":
            configs += [ GenConfig( "32e" , ["32e"] , nRules , nRules/10 , dataSource , "" ) ]
        configs += [
            GenConfig( "NoDC" , ["18e" for l in range(8)] , nRules , nRules/10 , dataSource , "" ) ,            
            #GenConfig( "DC18" , ["18e" for l in range(7)] + ["18m"] , nRules , nRules/10 , dataSource , "0x0" ) ,
            #GenConfig( "DC16" , ["18e" for l in range(7)] + ["18m"] , nRules , nRules/10 , dataSource , "0x30000" ) ,
            #GenConfig( "DC12" , ["18e" for l in range(7)] + ["18m"] , nRules , nRules/10 , dataSource , "0x3f000" ) ,
            #GenConfig( "DC8" , ["18e" for l in range(7)] + ["18m"] , nRules , nRules/10 , dataSource , "0x3ff00" ) ,
            #GenConfig( "DC4" , ["18e" for l in range(7)] + ["18m"] , nRules , nRules/10 , dataSource , "0x3fff0" ) ,
            #GenConfig( "DC3" , ["18e" for l in range(7)] + ["18m"] , nRules , nRules/10 , dataSource , "0x3fff8" ) ,
            #GenConfig( "DC2" , ["18e" for l in range(7)] + ["18m"] , nRules , nRules/10 , dataSource , "0x3fffc" ) ,
            #GenConfig( "DC1" , ["18e" for l in range(7)] + ["18m"] , nRules , nRules/10 , dataSource , "0x3fffe" ) ,
            #GenConfig( "DC0" , ["18e" for l in range(7)] + ["18m"] , nRules , nRules/10 , dataSource , "0x3ffff" ) ,
            #GenConfig( "DCHC4" , ["18e" for l in range(7)] + ["14e","4m"] , nRules , nRules/10 , dataSource , "0x0" ) ,
            #GenConfig( "DCHC3" , ["18e" for l in range(7)] + ["14e","4m"] , nRules , nRules/10 , dataSource , "0x8" ) ,
            #GenConfig( "DCHC2" , ["18e" for l in range(7)] + ["14e","4m"] , nRules , nRules/10 , dataSource , "0xc" ) ,
            #GenConfig( "DCHC1" , ["18e" for l in range(7)] + ["14e","4m"] , nRules , nRules/10 , dataSource , "0xe" ) ,
        ]

maxRules = max( [ c.nRules for c in configs ] )

ruleList = []

for irule in range(maxRules):

    if irule % 1000 == 0: print "INFO : Generating rule %i / %i" % (irule,maxRules)

    data = { "COUNTER" : [int(irule) for l in range(8)] ,
             "RANDOM"  : [int(random.uniform(0,pow(2,18)-1)) for l in range(8)] }
    
    # Generate rule
    # Keep regenerating until we have come accross a unique pattern
    # Sometimes the patterns will overlap due to the DC bits in the final 18b word
    # I only bother with this procedure for PATTFILE rules
    while True:
    
        line = iFile.readline()
        if line == '':
            print "ERROR : Input patterns file ended prematurely"
            sys.exit()
        
        hits  = line.split()

        data["PATTFILE"] = [ int(hits[l]) for l in range(1,9) ]

        if data["PATTFILE"][:-1] in ruleList:
            #print "WARN  : Overlapping pattern found, trying again"
            #print data["PATTFILE"][:-1]
            continue

        ruleList += [ data["PATTFILE"][:-1] ]
        break

    for c in configs:

        if irule > c.nRules:
            continue

        tmprule = c.baseRule( data )

        if irule % (c.nRules/c.nTraces) == 0:
            # Construct a list of traces that we will randomly scramble
            c.tracesList += [ ( random.random() , " ".join(tmprule+[str(irule+1)]) + "\n" ) ]
            #c.tracesFile.write( " ".join(tmprule+[str(irule+1)]) + "\n" )
                    
        if not( c.DCFlag == "" ):
            tmprule[-1] += "/" + c.DCFlag

        c.rulesFile.write( " ".join(tmprule) + "\n" )

# Save randomly ordered traces to file
for c in configs:
    c.tracesList.sort()
    for t in c.tracesList:
        c.tracesFile.write( t[1] )

table = []
for c in configs:
    c.close()
    table += [c.study()]

for r in table:
    print r

for r in table:
    print " ".join(["%-15s"%str(i) for i in r])
