##############################################################################
# MDTraj: A Python Library for Loading, Saving, and Manipulating
#         Molecular Dynamics Trajectories.
# Copyright 2012-2013 Stanford University and the Authors
#
# Authors: Robert McGibbon
# Contributors: Kyle A. Beauchamp
#
# MDTraj is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with MDTraj. If not, see <http://www.gnu.org/licenses/>.
##############################################################################

from __future__ import print_function, division

__all__ = ['baker_hubbard', 'shrake_rupley', 'kabsch_sander', 'compute_distances',
           'compute_displacements', 'compute_angles', 'compute_dihedrals',
           'compute_phi', 'compute_psi', 'compute_chi1', 'compute_chi2',
           'compute_chi3', 'compute_chi4', 'compute_omega', 'compute_rg',
           'compute_contacts', 'compute_drid', 'compute_center_of_mass']

from mdtraj.geometry.rg import *
from mdtraj.geometry.angle import *
from mdtraj.geometry.distance import *
from mdtraj.geometry.dihedral import *
from mdtraj.geometry.hbond import *
from mdtraj.geometry.sasa import *
from mdtraj.geometry.contact import *
try:
    from mdtraj.geometry.drid import compute_drid
    from mdtraj.geometry._geometry import _processor_supports_sse41
    if not _processor_supports_sse41():
        raise ImportError()
except ImportError:
    def compute_drid(traj, atom_indices=None):
        """This function is stub for the actual DRID [1] function, and indicates a
        failure to compile or import the DRID function, due to the fact that
        the CPU does not support the required instruction set (SSE4.1).

        References
        ----------
        ..[1] Zhou, Caflisch; Distribution of Reciprocal of Interatomic Distances:
        A Fast Structural Metric. JCTC 2012 doi:10.1021/ct3003145
        """
        raise NotImplementedError