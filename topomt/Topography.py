class Topography():

    def __init__(self, molecular_system=None, selection='all'):
        self.molecular_system = None
        self.selection = selection
        self.pockets = []
        self.cavities = []
        self.channels = []
        self.mouths = []
        if molecular_system is not None:
            self.molecular_system = msm.convert(molecular_system)

