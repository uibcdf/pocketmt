from topomt import pyunitwizard as puw
from topomt._private.digestion import digest
import numpy as np
from scipy.spatial import Voronoi
from scipy.spatial.distance import euclidean

class AlphaSpheres():

    """Set of alpha-spheres

    Object with a set of alpha-spheres and its main attributes such as radius and contacted points

    Attributes
    ----------
    points : ndarray (shape=[n_points,3], dtype=float)
        Array of coordinates in space of all points used to generate the set of alpha-spheres.
    n_points: int
        Number of points in space to generate the set of alpha-spheres.
    centers: ndarray (shape=[n_alpha_spheres,3], dtype=float)
        Centers of alpha-spheres.
    radii: ndarray (shape=[n_alpha_spheres], dtype=float)
        Array with the radii of alpha-spheres.
    points_of_alpha_sphere: ndarray (shape=[n_alpha_spheres, 4], dtype=int)
        Indices of points in the surface of each alpha-sphere.
    n_alpha_spheres: int
        Number of alpha-spheres in the set.

    """

    @digest()
    def __init__(self, points=None, radii=None, method='voronoi', skip_digestion=False):

        # method can be 'voronoi' or 'weighted_voronoi' in future implementations

        """Creating a new instance of AlphaSpheres


        Parameters
        ----------

        Examples
        --------

        See Also
        --------

        Notes
        -----

        """

        self.points=None
        self.n_points=None
        self.centers=None
        self.points_of_alpha_sphere=None
        self.radii=None
        self.n_alpha_spheres=None

        if points is not None:

            self.points = points
            self.n_points = points.shape[0]

            # Voronoi class to build the alpha-spheres

            points_value, length_unit = puw.get_value_and_unit(points)
            voronoi = Voronoi(points_value)

            # The alpha-spheres centers are the voronoi vertices

            self.centers = puw.quantity(voronoi.vertices, length_unit)
            self.n_alpha_spheres = voronoi.vertices.shape[0]

            # Let's compute the 4 atoms' sets in contact with each alpha-sphere

            self.points_of_alpha_sphere = [[] for ii in range(self.n_alpha_spheres)]

            n_regions = len(voronoi.regions)
            region_point={voronoi.point_region[ii]:ii for ii in range(self.n_points)}

            for region_index in range(n_regions):
                region=voronoi.regions[region_index]
                if len(region)>0:
                    point_index=region_point[region_index]
                    for vertex_index in region:
                        if vertex_index != -1:
                            self.points_of_alpha_sphere[vertex_index].append(point_index)
            for ii in range(self.n_alpha_spheres):
                self.points_of_alpha_sphere[ii] = sorted(self.points_of_alpha_sphere[ii])


            # Let's finally compute the radius of each alpha-sphere

            self.radii = []

            for ii in range(self.n_alpha_spheres):
                radius = euclidean(voronoi.vertices[ii], points_value[self.points_of_alpha_sphere[ii][0]])
                self.radii.append(radius)

            self.points_of_alpha_sphere = np.array(self.points_of_alpha_sphere)
            self.radii = puw.quantity(np.array(self.radii), length_unit)

    def remove_alpha_spheres(self, indices):

        """Removing alpha-spheres from the set
        The method removes from the set those alpha-spheres specified by the input argument
        `indices`.

        Parameters
        ----------
        indices : numpy.ndarray, list or tuple (dtype:ints)
            List, tuple or numpy.ndarray with the integer numbers corresponding to the alpha-sphere
            indices to be removed from the set.

        Examples
        --------

        """

        mask = np.ones([self.n_alpha_spheres], dtype=bool)
        mask[indices] = False

        self.centers = self.centers[mask,:]
        self.points_of_alpha_sphere = self.points_of_alpha_sphere[mask,:]
        self.radii = self.radii[mask]
        self.n_alpha_spheres = np.count_nonzero(mask)


    def remove_small_alpha_spheres(self, minimum_radius):

        indices_to_remove = np.where(self.radii < minimum_radius)
        self.remove_alpha_spheres(indices_to_remove)


    def remove_big_alpha_spheres(self, maximum_radius):

        indices_to_remove = np.where(self.radii > maximum_radius)
        self.remove_alpha_spheres(indices_to_remove)


    def get_points_of_alpha_spheres(self, indices):

        """Get the points in contact with a subset of alpha-spheres
        The list of point indices accounting for the points in contact with a subset of alpha-spheres is calculated.

        Parameters
        ----------
        indices : numpy.ndarray, list or tuple (dtype:ints)
            List, tuple or numpy.ndarray with the alpha-sphere indices defining the subset.

        Return
        ------
        points_of_alpha_spheres : list
            List of point indices in contact with one or more alpha-spheres of the subset.

        Examples
        --------
        >>> import openpocket as opoc
        >>> points = ([[-1.,  2.,  0.],
        >>>            [ 0.,  2.,  1.],
        >>>            [ 1., -2.,  1.],
        >>>            [ 0.,  1.,  1.],
        >>>            [ 0.,  0.,  0.],
        >>>            [-1., -1.,  0.]])
        >>> aspheres = opoc.AlphaSpheres(points)
        >>> aspheres.get_points_of_alpha_spheres([1,3])
        [0,2,3,4,5]

        """

        point_indices = set([])

        for index in indices:
            point_indices = point_indices.union(set(self.points_of_alpha_sphere[index]))

        return list(point_indices)

    def get_neighbors(self, criterion: str = "point") -> dict[int, list[int]]:
        """Return the symmetric dictionary of alpha-sphere neighbors.

        Parameters
        ----------
        criterion : {"point", "edge", "face"}
            - "point": neighbors that share at least 1 point (atom).
            - "edge": neighbors that share at least 2 points (a edge).
            - "face": neighbors that share at least 3 points (a face).

        Returns
        -------
        neighbors : dict[int, list[int]]
            Dictionary where each key is the alpha-sphere index and the value is
            the sorted list of neighbor alpha-sphere indices.

        Notes
        -----
        This method assumes ``self.points_of_alpha_sphere`` is an array-like
        where each element is the iterable of point indices touched by that
        alpha-sphere.
        """

        criterion_map = {
            "point": 1,
            "edge": 2,
            "face": 3,
        }
        if criterion not in criterion_map:
            raise ValueError(
                f"criterion must be one of {tuple(criterion_map)}, got {criterion!r}"
            )
        min_shared = criterion_map[criterion]

        n_as = self.n_alpha_spheres
        # índice inverso punto -> esferas
        point_to_spheres: dict[int, list[int]] = {}

        for as_idx in range(n_as):
            pts = self.points_of_alpha_sphere[as_idx]
            for p in pts:
                point_to_spheres.setdefault(int(p), []).append(as_idx)

        # diccionario de sets para ir construyendo vecinos simétricos
        neighbors_sets: dict[int, set[int]] = {i: set() for i in range(n_as)}

        # para cada esfera contamos cuántos puntos comparte con las demás
        for as_idx in range(n_as):
            shared_counts: dict[int, int] = {}
            pts = self.points_of_alpha_sphere[as_idx]
            for p in pts:
                for other_idx in point_to_spheres[int(p)]:
                    if other_idx == as_idx:
                        continue
                    shared_counts[other_idx] = shared_counts.get(other_idx, 0) + 1

            # filtramos según el mínimo de puntos compartidos
            for other_idx, count in shared_counts.items():
                if count >= min_shared:
                    neighbors_sets[as_idx].add(other_idx)
                    neighbors_sets[other_idx].add(as_idx)  # simetría

        # lo devolvemos ya como dict de listas ordenadas
        neighbors: dict[int, list[int]] = {
            i: sorted(list(s))
            for i, s in neighbors_sets.items()
            if len(s) > 0
        }

        return neighbors

    def get_centers_distance(self, i: int, j: int):
        """Return the Euclidean distance (Å) between the centers of two alpha-spheres."""
        diff = self.centers[i] - self.centers[j]
        return (diff[0]**2+diff[1]**2+diff[2]**2) ** 0.5

    def view(self, view=None, indices='all'):

        """3D spatial view of alpha-spheres and points
        An NGLview view is returned with alpha-spheres (gray color) and points (red color).

        Parameters
        ----------
        indices : numpy.ndarray, list or tuple (dtype:ints)
            List, tuple or numpy.ndarray with the alpha-sphere indices defining the subset.

        Returns
        -------
        view : nglview
            View object of NGLview.

        Examples
        --------
        >>> import openpocket as opoc
        >>> points = ([[-1.,  2.,  0.],
        >>>            [ 0.,  2.,  1.],
        >>>            [ 1., -2.,  1.],
        >>>            [ 0.,  1.,  1.],
        >>>            [ 0.,  0.,  0.],
        >>>            [-1., -1.,  0.]])
        >>> aspheres = opoc.alpha_spheres.AlphaSpheresSet(points)
        >>> view = aspheres.view([1,3])
        >>> view
        """

        if view is None:

            import nglview as nv

            view = nv.NGLWidget()

        point_indices = []

        if indices=='all':
            indices=range(self.n_alpha_spheres)
            point_indices=range(self.n_points)
        else:
            point_indices=self.get_points_of_alpha_spheres(indices)

        for index in point_indices:
            atom_coordinates = self.points[index,:]
            view.shape.add_sphere(list(atom_coordinates), [0.8,0.0,0.0], 0.2)

        for index in indices:
            sphere_coordinates = self.centers[index,:]
            sphere_radius = self.radii[index]
            view.shape.add_sphere(list(sphere_coordinates), [0.8,0.8,0.8], sphere_radius)

        return view

