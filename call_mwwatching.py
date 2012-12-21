
from mwmatching import maxWeightMatching


edges = [(1,2,-10) , (30,40,-100) , (1,30,-20) , (2,40,-30)]
ans = maxWeightMatching(edges,True)
print ans
