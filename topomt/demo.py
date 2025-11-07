import sys

from importlib.resources import files
def path(package, file_or_dir):
    return files(package).joinpath(file_or_dir)

demo = {}

# TcTIM

demo['TcTIM'] = {}
demo['TcTIM']['1tcd.pdb'] = path('topomt.data.TcTIM.CASTp_1tcd', '1tcd.pdb')
demo['TcTIM']['CASTp_1tcd'] = path('topomt.data.TcTIM', 'CASTp_1tcd')

# HIV-1 Protease

demo['HIV-1 Protease'] = {}
demo['HIV-1 Protease']['1hiv.pdb'] = path('topomt.data.HIV-1-Protease.CASTp_1hiv', '1hiv.pdb')
demo['HIV-1 Protease']['CASTp_1tcd'] = path('topomt.data.HIV-1-Protease', 'CASTp_1hiv')
