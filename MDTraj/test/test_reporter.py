# Copyright 2012 mdtraj developers
#
# This file is part of mdtraj
#
# mdtraj is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# mdtraj is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# mdtraj. If not, see http://www.gnu.org/licenses/.

import os
import shutil
import tempfile
import numpy as np

try:
    from simtk.unit import *
    from simtk.openmm import *
    from simtk.openmm.app import *
    HAVE_OPENMM = True
except ImportError:
    HAVE_OPENMM = False

from mdtraj.testing import get_fn, eq, DocStringFormatTester
from mdtraj import topology
from mdtraj import trajectory
from mdtraj.reporters import hdf5reporter, netcdfreporter
from mdtraj.reporters import HDF5Reporter, NetCDFReporter, DCDReporter
from mdtraj import HDF5TrajectoryFile, NetCDFTrajectoryFile
DocStringTester = DocStringFormatTester(hdf5reporter)
DocStringTester = DocStringFormatTester(netcdfreporter)


dir = tempfile.mkdtemp()
def teardown_module(module):
    """remove the temporary directory created by tests in this file
    this gets automatically called by nose"""
    shutil.rmtree(dir)
    #print tempdir


@np.testing.decorators.skipif(not HAVE_OPENMM, 'No OpenMM')
def test_reporter():
    tempdir = os.path.join(dir, 'test1')
    os.makedirs(tempdir)

    pdb = PDBFile(get_fn('native.pdb'))
    forcefield = ForceField('amber99sbildn.xml', 'amber99_obc.xml')
    system = forcefield.createSystem(pdb.topology, nonbondedMethod=CutoffNonPeriodic,
        nonbondedCutoff=1.0*nanometers, constraints=HBonds, rigidWater=True)
    integrator = LangevinIntegrator(300*kelvin, 1.0/picoseconds, 2.0*femtoseconds)
    integrator.setConstraintTolerance(0.00001)

    platform = Platform.getPlatformByName('Reference')
    simulation = Simulation(pdb.topology, system, integrator, platform)
    simulation.context.setPositions(pdb.positions)

    simulation.context.setVelocitiesToTemperature(300*kelvin)

    hdf5file = os.path.join(tempdir, 'traj.h5')
    ncfile = os.path.join(tempdir, 'traj.nc')
    dcdfile = os.path.join(tempdir, 'traj.dcd')

    reporter = HDF5Reporter(hdf5file, 2, coordinates=True, time=True,
        cell=True, potentialEnergy=True, kineticEnergy=True, temperature=True,
        velocities=True)
    reporter2 = NetCDFReporter(ncfile, 2, coordinates=True, time=True, cell=True)
    reporter3 = DCDReporter(dcdfile, 2)

    simulation.reporters.append(reporter)
    simulation.reporters.append(reporter2)
    simulation.reporters.append(reporter3)
    simulation.step(100)

    reporter.close()
    reporter2.close()

    with HDF5TrajectoryFile(hdf5file) as f:
        got = f.read()
        yield lambda: eq(got.temperature.shape, (50,))
        yield lambda: eq(got.potentialEnergy.shape, (50,))
        yield lambda: eq(got.kineticEnergy.shape, (50,))
        yield lambda: eq(got.coordinates.shape, (50, 22, 3))
        yield lambda: eq(got.velocities.shape, (50, 22, 3))
        yield lambda: eq(got.cell_lengths, 2 * np.ones((50, 3)))
        yield lambda: eq(got.cell_angles, 90*np.ones((50, 3)))
        yield lambda: eq(got.time, 0.002*2*(1+np.arange(50)))

        yield lambda: topology.equal(f.topology,
                                     trajectory.load(get_fn('native.pdb')).top)

    with NetCDFTrajectoryFile(ncfile) as f:
        xyz, time, cell_lengths, cell_angles = f.read()
        yield lambda: eq(cell_lengths, 2 * np.ones((50, 3)))
        yield lambda: eq(cell_angles, 90*np.ones((50, 3)))
        yield lambda: eq(time, 0.002*2*(1+np.arange(50)))

    hdf5_traj = trajectory.load(hdf5file)
    dcd_traj = trajectory.load(dcdfile, top=get_fn('native.pdb'))
    netcdf_traj = trajectory.load(ncfile, top=get_fn('native.pdb'))
    
    yield lambda: eq(hdf5_traj.xyz, netcdf_traj.xyz)
    yield lambda: eq(hdf5_traj.unitcell_vectors, netcdf_traj.unitcell_vectors)
    yield lambda: eq(hdf5_traj.time, netcdf_traj.time)

    yield lambda: eq(dcd_traj.xyz, hdf5_traj.xyz)
    yield lambda: eq(dcd_traj.unitcell_vectors, hdf5_traj.unitcell_vectors)


@np.testing.decorators.skipif(not HAVE_OPENMM, 'No OpenMM')
def test_reporter_subset():
    tempdir = os.path.join(dir, 'test_2')
    os.makedirs(tempdir)

    pdb = PDBFile(get_fn('native.pdb'))
    forcefield = ForceField('amber99sbildn.xml', 'amber99_obc.xml')
    system = forcefield.createSystem(pdb.topology, nonbondedMethod=CutoffNonPeriodic,
        nonbondedCutoff=1.0*nanometers, constraints=HBonds, rigidWater=True)
    integrator = LangevinIntegrator(300*kelvin, 1.0/picoseconds, 2.0*femtoseconds)
    integrator.setConstraintTolerance(0.00001)

    platform = Platform.getPlatformByName('Reference')
    simulation = Simulation(pdb.topology, system, integrator, platform)
    simulation.context.setPositions(pdb.positions)

    simulation.context.setVelocitiesToTemperature(300*kelvin)

    hdf5file = os.path.join(tempdir, 'traj.h5')
    ncfile = os.path.join(tempdir, 'traj.nc')
    dcdfile= os.path.join(tempdir, 'traj.dcd')

    atomSubset = [0,1,2,  4,5]

    reporter = HDF5Reporter(hdf5file, 2, coordinates=True, time=True,
        cell=True, potentialEnergy=True, kineticEnergy=True, temperature=True,
                            velocities=True, atomSubset=atomSubset)
    reporter2 = NetCDFReporter(ncfile, 2, coordinates=True, time=True,
                               cell=True, atomSubset=atomSubset)
    reporter3 = DCDReporter(dcdfile, 2, atomSubset=atomSubset)

    simulation.reporters.append(reporter)
    simulation.reporters.append(reporter2)
    simulation.reporters.append(reporter3)
    simulation.step(100)

    reporter.close()
    reporter2.close()

    t = trajectory.load(get_fn('native.pdb'))
    t.restrict_atoms(atomSubset)

    with HDF5TrajectoryFile(hdf5file) as f:
        got = f.read()
        yield lambda: eq(got.temperature.shape, (50,))
        yield lambda: eq(got.potentialEnergy.shape, (50,))
        yield lambda: eq(got.kineticEnergy.shape, (50,))
        yield lambda: eq(got.coordinates.shape, (50, len(atomSubset), 3))
        yield lambda: eq(got.velocities.shape, (50, len(atomSubset), 3))
        yield lambda: eq(got.cell_lengths, 2 * np.ones((50, 3)))
        yield lambda: eq(got.cell_angles, 90*np.ones((50, 3)))
        yield lambda: eq(got.time, 0.002*2*(1+np.arange(50)))
        yield lambda: topology.equal(f.topology, t.topology)

    with NetCDFTrajectoryFile(ncfile) as f:
        xyz, time, cell_lengths, cell_angles = f.read()
        yield lambda: eq(cell_lengths, 2 * np.ones((50, 3)))
        yield lambda: eq(cell_angles, 90*np.ones((50, 3)))
        yield lambda: eq(time, 0.002*2*(1+np.arange(50)))
        yield lambda: eq(xyz.shape, (50, len(atomSubset), 3))

    hdf5_traj = trajectory.load(hdf5file)
    dcd_traj = trajectory.load(dcdfile, top=hdf5_traj)
    netcdf_traj = trajectory.load(ncfile, top=hdf5_traj)
    
    yield lambda: eq(hdf5_traj.xyz, netcdf_traj.xyz)
    yield lambda: eq(hdf5_traj.unitcell_vectors, netcdf_traj.unitcell_vectors)
    yield lambda: eq(hdf5_traj.time, netcdf_traj.time)

    yield lambda: eq(dcd_traj.xyz, hdf5_traj.xyz)
    yield lambda: eq(dcd_traj.unitcell_vectors, hdf5_traj.unitcell_vectors)
