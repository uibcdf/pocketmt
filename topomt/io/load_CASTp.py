import os
from topomt import pyunitwizard as puw
import molsysmt as msm

def load_CASTp(poc_file=None, pocInfo_file=None, mouth_file=None, mouthInfo_file=None, pdb_file=None,
               zip_file=None, dir_path=None):
    """
    Load CASTp data.

    """

    if zip_file is not None:
        import zipfile
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall('/tmp/castp_extracted')
        dir_path = '/tmp/castp_extracted'

    if dir_path is not None:
        if not os.path.isdir(dir_path):
            raise ValueError(f"The provided dir_path '{dir_path}' is not a valid directory.")
        for aux_file in os.listdir(dir_path):
            if aux_file.endswith('.poc'):
                poc_file = os.path.join(dir_path, aux_file)
            elif aux_file.endswith('.pocInfo'):
                pocInfo_file = os.path.join(dir_path, aux_file)
            elif aux_file.endswith('.mouth'):
                mouth_file = os.path.join(dir_path, aux_file)
            elif aux_file.endswith('.mouthInfo'):
                mouthInfo_file = os.path.join(dir_path, aux_file)
            elif aux_file.endswith('.pdb'):
                pdb_file = os.path.join(dir_path, aux_file)

    from tmt import Topograpy

    topography = Topography()

    if pdb_file is not None:
        topography.molecular_system = msm.convert(pdb_file, to_form='molsysmt.MolSys')

    if poc_file is not None:

        poc_id_to_atom_indices = dict()
        poc_id_to_pocket_index = dict()

        with open(poc_file, 'r') as fff:
            for line in fff.readlines():
                fields = line.split()
                atom_id = int(fields[1])
                atom_name = fields[2]
                group_name = fields[3]
                chain_id = fields[4]
                group_id = int(fields[5])
                poc_id = int(fields[11])
                poc_marker = fields[12]
                if poc_marker != 'POC':
                    raise ValueError("Unexpected marker in .poc file.")
                atom_index = topography.molecular_system.topology.get_atom_indices(atom_id=atom_id, atom_name=atom_name,
                                                                          group_name=group_name, chain_id=chain_id)
                if len(atom_index) == 0:
                    raise ValueError(f"Atom with id {atom_id}, name {atom_name}, group {group_name}, chain {chain_id} not found.")
                elif len(atom_index) > 1:
                    raise ValueError(f"Multiple atoms found for id {atom_id}, name {atom_name}, group {group_name}, chain {chain_id}.")
                else:
                    atom_index = atom_index[0]

                try:
                    poc_id_to_atom_indices[poc_id].append(atom_index)
                except KeyError:
                    poc_id_to_atom_indices[poc_id] = [atom_index]

        for ii,jj in enumerate(sorted(poc_id_to_atom_indices.keys())):
            poc_id_to_pocket_index[jj] = ii
            aux_pocket = Pocket(atom_indices=poc_id_to_atom_indices[jj], index=ii, id=jj)
            topography.pockets.append(aux_pocket)

        if pocInfo_file is not None:
            with open(pocInfo_file, 'r') as fff:
                _ = fff.readline()
                for line in fff.readlines():
                    fields = line.split()
                    poc_id = int(fields[2])
                    n_mouths = int(fields[3])
                    solvent_accessible_area = puw.quantity(float(fields[4]), 'angstroms**2')
                    molecular_surface_area = puw.quantity(float(fields[5]), 'angstroms**2')
                    solvent_accessible_volume = puw.quantity(float(fields[6]), 'angstroms**3')
                    molecular_surface_volume = puw.quantity(float(fields[7]), 'angstroms**3')
                    length = puw.quantity(float(fields[8]), 'angstroms')
                    corner_points_count = int(fields[9])
                    pocket_index = poc_id_to_pocket_index[poc_id]
                    topography.pockets[pocket_index].n_mouths = n_mouths
                    topography.pockets[pocket_index].solvent_accessible_area = solvent_accessible_area
                    topography.pockets[pocket_index].molecular_surface_area = molecular_surface_area
                    topography.pockets[pocket_index].solvent_accessible_volume = solvent_accessible_volume
                    topography.pockets[pocket_index].molecular_surface_volume = molecular_surface_volume
                    topography.pockets[pocket_index].length = length
                    topography.pockets[pocket_index].corner_points_count = corner_points_count

    if mouth_file is not None:

        mouth_id_to_atom_indices = dict()
        mouth_id_to_mouth_index = dict()

        with open(mouth_file, 'r') as fff:
            for line in fff.readlines():
                fields = line.split()
                atom_id = int(fields[1])
                atom_name = fields[2]
                group_name = fields[3]
                chain_id = fields[4]
                group_id = int(fields[5])
                mouth_id = int(fields[11])
                mouth_marker = fields[12]
                if mouth_marker != 'M4P':
                    raise ValueError("Unexpected marker in .mouth file.")
                atom_index = topography.molecular_system.topology.get_atom_indices(atom_id=atom_id, atom_name=atom_name,
                                                                          group_name=group_name, chain_id=chain_id)
                if len(atom_index) == 0:
                    raise ValueError(f"Atom with id {atom_id}, name {atom_name}, group {group_name}, chain {chain_id} not found.")
                elif len(atom_index) > 1:
                    raise ValueError(f"Multiple atoms found for id {atom_id}, name {atom_name}, group {group_name}, chain {chain_id}.")
                else:
                    atom_index = atom_index[0]

                try:
                    mouth_id_to_atom_indices[mouth_id].append(atom_index)
                except KeyError:
                    mouth_id_to_atom_indices[mouth_id] = [atom_index]

        for ii,jj in enumerate(sorted(mouth_id_to_atom_indices.keys())):
            mouth_id_to_mouth_index[jj] = ii
            aux_mouth = Mouth(atom_indices=mouth_id_to_atom_indices[jj], index=ii, id=jj)
            topography.mouths.append(aux_mouth)

        if mouthInfo_file is not None:
            with open(mouthInfo_file, 'r') as fff:
                _ = fff.readline()
                for line in fff.readlines():
                    fields = line.split()
                    mouth_id = int(fields[2])
                    n_mouths = int(fields[3])
                    solvent_accessible_area = puw.quantity(float(fields[4]), 'angstroms**2')
                    molecular_surface_area = puw.quantity(float(fields[5]), 'angstroms**2')
                    solvent_accessible_length = puw.quantity(float(fields[6]), 'angstroms')
                    molecular_surface_length = puw.quantity(float(fields[7]), 'angstroms')
                    n_triangles = int(fields[8])
                    if n_triangles > 0:
                        mouth_index = mouth_id_to_mouth_index[mouth_id]
                        topography.mouths[mouth_index].solvent_accessible_area = solvent_accessible_area
                        topography.mouths[mouth_index].molecular_surface_area = molecular_surface_area
                        topography.mouths[mouth_index].solvent_accessible_length = solvent_accessible_length
                        topography.mouths[mouth_index].molecular_surface_length = molecular_surface_length
                        topography.mouths[mouth_index].n_triangles = n_triangles

    if zip_file is not None:
        os.remove(dir_path)

    return topography

