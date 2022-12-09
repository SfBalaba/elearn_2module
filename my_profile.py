import cProfile
from pstats import Stats, SortKey
import multiprocess

cProfile.run("multiprocess", 'restats')
p = Stats('restats')
p.sort_stats(SortKey.TIME).print_stats(5)