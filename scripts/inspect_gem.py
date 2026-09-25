import sys,json
from pathlib import Path
sys.path.insert(0,r'C:/Users/etqdo/Documents/maya/LtMAO/src')
from LtMAO.pyRitoFile.so import SO
p=Path('work/original/ASSETS/Characters/Briar/Skins/Base/Particles/Briar_Base_R_Gem.scb')
s=SO().read_scb(str(p));print('GEM',len(s.positions),len(s.indices),s.flags,s.central,[(min(tuple(v)[i] for v in s.positions),max(tuple(v)[i] for v in s.positions)) for i in range(3)])
