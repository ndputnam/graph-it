import sys
from ast import literal_eval
from copy import deepcopy
from io import StringIO
from json import dump, loads, load, dumps, JSONEncoder
from os import listdir, path, getenv
from pathlib import Path
from time import sleep
from typing import Union

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
from cryptography.fernet import Fernet
from numpy import array, ndarray
from pandas import DataFrame
from pandas import read_json
from pyarrow import schema, field, from_numpy_dtype, Table
from pyarrow.parquet import write_table

from resources.modules.plot_map import PlotMap

"""
Predefined colors list
"""
COLORS = ['white', 'red', 'orange', 'blue', 'yellow', 'aqua', 'skyblue', 'slategrey', 'maroon', 'coral', 'tan', 'green',
          'crimson', 'darkgoldenrod', 'deeppink', 'magenta','goldenrod', 'lightgrey', 'lightseagreen', 'plum', 'black',]

"""
Base plot map dictionary structure.
"""
PLOT = {'id': 0,                                     # plot map identifier.
        'title': 'Title of Plot Map',                         # plot title.
        'color': 'blue',                           # background color name.
        'graph_name': '',             # plot name reference for Plot_Types.
        'x_coord': '',                                     # x column name.
        'y_coord': '',                                     # y column name.
        'z_coord': '',                                     # z column name.
        'x_grid': False,                            # show horizontal grid.
        'y_grid': False,                              # show vertical grid.
        'dpi': 100,                          # plot font size / resolution.
        'fit': False,                    # fit plot to window or expandable.
        'label_all': False,          # show all plot point labels on graph.
        'horz_stretch': 0, # expand plot horizontally by factor of * / 10.
        'vert_stretch': 0,   # expand plot vertically by factor of * / 10.
        'data_name': '',          # source name of dataframe with prefixes.
        'data': None}           # pandas dataframe or dict of numpy arrays.

def error_func(in_txt, func, *args, **kwargs):
    """
    Single location to test individual function calls.
    :param in_txt: Define where test is occurring.
    :param func: Function to test.
    :param args: Argument variables.
    :param kwargs: Keyword argument variables.
    :return: Result of function if successful.
    """
    try:
        print('test function: %s' % str(func))
        return func(*args, **kwargs)
    except Exception as e:
        print('ERROR in %s: %s' % (in_txt, e))
        return None

def resource_path(relative_path: str) -> str:
    """
    adjusts path if necessary, applicable when packaged.
    :param relative_path: base path
    :return: functional environment path
    """
    try:
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = Path(__file__).parent.parent.parent
    except AttributeError:
        base_path = path.abspath("")
    return path.join(base_path, relative_path)

def save_data_as_parquet(source_data, source_name):
    """
    Creates parquets of internally created sample data.
    Converts primary source data from csv to parquet format,
     grabs shape if multidimensional and flatten as necessary.
    :param source_data: Primary source data csv.
    :param source_name: Primary source data name.
    """
    metadata = {'shapes': []}
    single_dim = True
    data_schema = schema([], metadata={'shape': b''})
    for column in source_data:
        for row in source_data[column]:
            if hasattr(row, 'shape'):
                if len(row.shape) > 0:
                    single_dim = False
        if not single_dim:
            single_dim = True
            metadata['shapes'].append(source_data[column].shape)
            source_data[column] = source_data[column].reshape(-1)
            source_field = field(column, from_numpy_dtype(source_data[column][0].dtype))
            data_schema = data_schema.append(source_field)
        else:
            data_schema = data_schema.append(field(column, from_numpy_dtype(source_data[column].dtype)))
    shapes = ''.join(str(metadata['shapes'])).encode()
    data_schema = data_schema.with_metadata({'shape': shapes})
    source_table = Table.from_pydict(source_data, data_schema)
    write_table(source_table, 'saved/data/%s.pqt' % source_name, compression='GZIP')

def save_plot_map(plot_obj):
    """
    Takes a copy of plot map from its PlotMap,
     modifies existing data to JSON format,
     saves plot map in JSON format.
    :param plot_obj: Instance of PlotMap.
    """
    plot_map = deepcopy(plot_obj.plot_map)
    if plot_map['data'] is not None:
        plot_map['data'] = dumps(plot_map['data'], cls=NumpyEncoder)
    with open('saved/plots/plot_map_%s.json' % plot_obj.plot_map['id'], 'w') as f:
        dump(str(plot_map), f, separators=(',', ':'), sort_keys=True, indent=4)

def load_plot_maps(main_win, load_all:bool):
    """
    Creates instances of PlotMap module
     from saved JSON plot maps
     or create new instance of a plot map.
    :param main_win: Instance of Main Window passed to PlotMap.
    :param load_all: True if loading all saved JSON plot maps.
                     False if creating an individual plot map.
    :return: list of created PlotMap instances.
    """
    plots = []
    plot_id = 1
    plots_json = sorted(listdir('saved/plots'))
    if load_all:
        for p in plots_json:
            with open('saved/plots/%s' % p, 'r') as f:
                plot = literal_eval(load(f))
                if plot['data'] is not None:
                    data_obj = loads(plot['data'])
                    if isinstance(data_obj, str):
                        plot['data'] = read_json(StringIO(data_obj))
                    elif isinstance(data_obj, dict):
                        for column in data_obj:
                            data_obj[column] = array(data_obj[column])
                        plot['data'] = data_obj
                    else:
                        plot['data'] = None
                        QMessageBox.critical(main_win, 'Bad Data, No Dataframe For You!',
                                             'Data is invalid or corrupted.\n'
                                             'It has been deleted,\n'
                                             'try reloading from source again.',
                                             buttons=QMessageBox.StandardButton.Ok,
                                             defaultButton=QMessageBox.StandardButton.Ok)
                plots.append(PlotMap(main_win, plot))
        return plots
    for i in range(1, max(1, len(plots_json) + 2)):
        plot_id = '%02d' % i
        if 'plot_map_' + str(plot_id) + '.json' not in plots_json:
            break
    plot = deepcopy(PLOT)
    plot['id'] = plot_id
    plots.append(PlotMap(main_win, plot))
    return plots


class NumpyEncoder(JSONEncoder):
    def default(self, obj:  Union[DataFrame, ndarray]):
        """
        Re-instance JSONEncoder
         to handle different plot map data types
         into JSON format.
        :param obj: Plot map data.
        :return: JSON object.
        """
        if isinstance(obj, ndarray):
            return obj.tolist()
        elif isinstance(obj, DataFrame):
            return obj.to_json()
        return super().default(obj)


class WaitTimer(QThread):
    prog = pyqtSignal(float)
    fin = pyqtSignal()
    def __init__(self, wait_sec):
        """
        Creates an instance of a wait delay
         in a separate thread.
        :param wait_sec: Delay time
        """
        super().__init__()
        self.delay = wait_sec

    def run(self):
        """
        Start timer and run for designated delay time.
        Signal prog every 10th of a second.
        Signal fin when countdown complete.
        """
        while self.delay >= 0:
            self.prog.emit(round(self.delay, 1))
            sleep(.1)
            self.delay -= .1
        self.fin.emit()


class Encrypt:
    def __init__(self):
        """
        Method for encrypting keys to encrypt objects.
        """
        key = getenv('ENCRYPT_KEY')
        self.handler = Fernet(key)

    def encrypt_key(self, msg: Union[str, bytes]) -> str:
        """
        Encrypts key.
        :param msg: Key with size of
        :return: Encrypted key used to encrypt data.
        """
        encoded_msg = msg if isinstance(msg, bytes) else msg.encode()
        treatment = self.handler.encrypt(encoded_msg)
        return str(treatment, 'utf-8')

    def decrypt_key(self, msg: Union[str, bytes]) -> str:
        """
        Decrypts key.
        :param msg: Key with size of
        :return: Decrypted key used to encrypt data.
        """
        encoded_msg = msg if isinstance(msg, bytes) else msg.encode()
        treatment = self.handler.decrypt(encoded_msg)
        return str(treatment, 'utf-8')