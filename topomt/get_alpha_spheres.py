import molsysmt as msm

def get_alpha_spheres(molecular_system, selection='all'):

    from .alpha_spheres import AlphaSpheres

    molecular_system = msm.convert(molecular_system, to_form='molsysmt.MolSys')
    atom_centers = msm.get(molecular_system, selection=selection, element='atom', coordinates=True)
    alpha_spheres = AlphaSpheres(points=atom_centers)

    return alpha_spheres
