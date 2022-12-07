import cProfile
from pstats import Stats, SortKey

cProfile.run("statistics.get_stat()", 'restats')
p = Stats('restats')
p.sort_stats(SortKey.TIME).print_stats(5)