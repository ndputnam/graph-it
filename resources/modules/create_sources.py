from math import log, ceil

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget
from mpl_toolkits.mplot3d import axes3d
from numpy import array, linspace, pi, newaxis, append, cos, sin, meshgrid, sqrt, outer, ones, size


class Game(QWidget):
    internal = True
    name = 'game_data'
    prog = pyqtSignal(int)
    def __init__(self):
        """
        Numpy arrays for sample game data structure.
        """
        super().__init__()
        self.game_data = {}

    def create_game_data(self):
        """
        Create a small sample of data for player levels,
         similar to what could be found in a game.
        :return: Dict of Numpy arrays.
        """
        player_level = []
        enemy_level = []
        player_hp = []
        enemy_hp = []
        diff = []
        hardness0 = 0
        hardness1 = 0
        for i in range(100):
            hardness0 += 1
            for j in range(100):
                hardness1 += 1
                hard_diff = max(1, hardness0 - hardness1)
                player_level.append(hardness0)
                enemy_level.append(hardness1)
                player_hp.append(hardness0 * 1000)
                enemy_hp.append(ceil(1000 * log(hard_diff + 1) * hardness1))
                diff.append(hard_diff)
            hardness1 = 0
        self.game_data['player_level'] = array(player_level)
        self.game_data['enemy_level'] = array(enemy_level)
        self.game_data['player_hp'] = array(player_hp)
        self.game_data['enemy_hp'] = array(enemy_hp)
        self.game_data['diff'] = array(diff)
        self.prog.emit(1)
        return self.game_data

    def update(self):
        """
        Call to recreate game data.
        :return: Dict of Numpy arrays.
        """
        return self.create_game_data()


class IsoTriSurface(QWidget):
    internal = True
    name = 'iso_tri_surface'
    prog = pyqtSignal(int)
    def __init__(self):
        """
        Numpy single dimension triangulated structure of a surface.
        """
        super().__init__()
        self.coords = {}

    def create_tri_surface(self):
        """
        Create single dimension x, y, z coordinates for graphing a triangulated surface.
        :return: Dict of Numpy arrays.
        """
        radii = linspace(0.125, 1.0, 8)
        angles = linspace(0, 2 * pi, 36, endpoint=False)[..., newaxis]
        x = append(0, (radii * cos(angles)).flatten())
        y = append(0, (radii * sin(angles)).flatten())
        z = sin(-x * y)
        self.coords['x_coordinate'] = x
        self.coords['y_coordinate'] = y
        self.coords['z_coordinate'] = z
        self.prog.emit(1)
        return self.coords

    def update(self):
        """
        Call to recreate a triangulated surface.
        :return: Dict of Numpy arrays.
        """
        return self.create_tri_surface()


class IsoWaveform(QWidget):
    internal = True
    name = 'iso_waveform'
    prog = pyqtSignal(int)
    def __init__(self):
        """
        Numpy matrix structure of a waveform like surface.
        """
        super().__init__()
        self.coords = {}

    def create_wave(self):
        """
        Create x, y, z coordinates for graphing a surface waveform.
        :return: Dict of Numpy arrays.
        """
        x, y, z = axes3d.get_test_data(0.03)
        self.coords['x_coordinate'] = x
        self.coords['y_coordinate'] = y
        self.coords['z_coordinate'] = z
        self.prog.emit(1)
        return self.coords

    def update(self):
        """
        Call to recreate waveform surface.
        :return: Dict of Numpy arrays.
        """
        return self.create_wave()


class IsoPeaks(QWidget):
    internal = True
    name = 'iso_peaks'
    prog = pyqtSignal(int)
    def __init__(self):
        """
        Numpy matrix structure of a surface with peaks.
        """
        super().__init__()
        self.coords = {}

    def create_peaks(self):
        """
        Create x, y, z coordinates for graphing a surface.
        :return: Dict of Numpy arrays.
        """
        x, y = meshgrid(linspace(-6, 6, 50), linspace(-6, 6, 30))
        z = sin(sqrt(x ** 2 + y ** 2))
        self.coords['x_coordinate'] = x
        self.coords['y_coordinate'] = y
        self.coords['z_coordinate'] = z
        self.prog.emit(1)
        return self.coords

    def update(self):
        """
        Call to recreate peaks surface.
        :return: Dict of Numpy arrays.
        """
        return self.create_peaks()


class IsoSphere(QWidget):
    internal = True
    name = 'iso_sphere'
    prog = pyqtSignal(int)
    def __init__(self):
        """
        Numpy matrix structure of a sphere.
        """
        super().__init__()
        self.coords = {}

    def create_sphere(self) -> dict:
        """
        Create x, y, z coordinates for graphing a sphere.
        :return: Dict of Numpy arrays
        """
        u = linspace(0, 2 * pi, 100)
        v = linspace(0, pi, 100)
        x = 10 * outer(cos(u), sin(v))
        y = 10 * outer(sin(u), sin(v))
        z = 9 * outer(ones(size(u)), cos(v))
        self.coords['x_coordinate'] = x
        self.coords['y_coordinate'] = y
        self.coords['z_coordinate'] = z
        self.prog.emit(1)
        return self.coords

    def update(self) -> dict:
        """
        Call to recreate sphere.
        :return: Dict of Numpy arrays.
        """
        return self.create_sphere()