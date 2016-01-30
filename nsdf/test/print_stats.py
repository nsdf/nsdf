from __future__ import print_function
import pstats
import sys
if len(sys.argv) < 2:
    print('Usage: %s infile\n' % (sys.argv[0]))
    print('Print profile info from `infile`.')
    sys.exit(1)
infile = sys.argv[1]
pstats.Stats(infile).strip_dirs().sort_stats("name", "cumulative").print_stats()


