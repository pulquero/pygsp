# -*- coding: utf-8 -*-

import numpy as np

from pygsp.graphs import NNGraph  # prevent circular import in Python < 3.5

def _import_hp():
    try:
        import healpy as hp
    except Exception as e:
        raise ImportError('Cannot import healpy. Choose another graph '
                          'or try to install it with '
                          'conda install healpy. '
                          'Original exception: {}'.format(e))
    return hp


class SphereHealpix(NNGraph):
    r"""Spherical-shaped graph using HEALPix sampling scheme (NN-graph).

    Parameters
    ----------
    Nside : int
        Resolution of the sampling scheme. It should be a power of 2 (default = 1024)
    nest : bool
        ordering of the pixels (default = True)

    See Also
    --------
    SphereEquiangular, SphereIcosahedron

    Notes
    -----
    This graph us based on the HEALPix[1]_ sampling scheme mainly used by the cosmologist.
    Heat Kernel Distance is used to find its weight matrix.

    References
    ----------
    [1] K. M. Gorski et al., « HEALPix -- a Framework for High Resolution Discretization,
    and Fast Analysis of Data Distributed on the Sphere », ApJ, vol. 622, nᵒ 2, p. 759‑771, avr. 2005.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> G = graphs.SphereHealpix(Nside=4)
    >>> fig = plt.figure()
    >>> ax1 = fig.add_subplot(121)
    >>> ax2 = fig.add_subplot(122, projection='3d')
    >>> _ = ax1.spy(G.W, markersize=1.5)
    >>> _ = _ = G.plot(ax=ax2)

    """

    def __init__(self, Nside=1024, nest=True, **kwargs):
        # TODO: add part of sphere construction
        hp = _import_hp()
        self.Nside = Nside
        self.nest = nest
        npix = hp.nside2npix(Nside)
        indexes = np.arange(npix)
        x, y, z = hp.pix2vec(Nside, indexes, nest=nest)
        self.lat, self.lon = hp.pix2ang(Nside, indexes, nest=nest, lonlat=False)
        coords = np.vstack([x, y, z]).transpose()
        coords = np.asarray(coords, dtype=np.float32)
        ## TODO: n_neighbors in function of Nside
        n_neighbors = 6 if Nside==1 else 8
        ## TODO: find optimal sigmas
        opt_std = {1: 0.5, 2: 0.15, 4: 0.05, 8: 0.0125, 16: 0.005, 32: 0.001}
        try:
            sigma = opt_std[Nside]
        except:
            raise ValueError('Unknown sigma for nside>32')

        plotting = {
            'vertex_size': 80,
            "limits": np.array([-1, 1, -1, 1, -1, 1])
        }
        super(SphereHealpix, self).__init__(coords, k=n_neighbors, kernel_width=2*sigma, plotting=plotting, **kwargs)