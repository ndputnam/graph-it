import os.path
from json import dump, load
from os import listdir, remove
from pathlib import Path
from shutil import copyfile
from sys import modules
from typing import Union, TextIO

import numpy as np
from PyQt6.QtCore import QThread, QThreadPool, QMutex, pyqtSlot, QRunnable, QObject, Qt
from PyQt6.QtWidgets import (QDialog, QPushButton, QComboBox, QTextEdit, QGridLayout,
                             QFileDialog, QLabel, QApplication, QCheckBox)
from chardet import universaldetector
from numpy import asarray
from pandas import read_csv, read_json, read_excel, Timestamp

from resources.modules.create_sources import *
from resources.modules.utility import save_data_as_parquet, resource_path


class Source(QDialog):
    def __init__(self, main_win):
        """
        Update internal primary data sources,
         or update obtained primary data sources,
         or obtain new primary data sources.
        :param main_win: Main Window.
        """
        QDialog.__init__(self, parent=main_win)
        # WINDOW DETAILS
        self.setWindowTitle('Modify Source Data')
        self.setWindowIcon(main_win.icon)
        self.resize(300, 100)
        # VARS
        self.main_win = main_win
        self.spec = self.main_win.spec
        self.sources = main_win.sources
        self.source_index = 0
        self.close_requested = False
        self.update_data_action = main_win.update_data_action
        self.update_spec_pool = QThreadPool()
        self.mutex = QMutex()
        # INFO TEXT
        self.info = QLabel('')
        # PREFIX CHECKBOXES
        self.prefix_check = QCheckBox('New Data Source Is Not Isometric')
        self.prefix_check.setTristate(True)
        self.prefix_check.stateChanged.connect(self.update_prefix_check)
        # GET PRIMARY SOURCE BUTTON
        local_csv_button = QPushButton('Get Local Data Source')
        local_csv_button.clicked.connect(lambda click: self.get_new_source())
        # GET SAMPLE SOURCES BUTTON
        samples_button = QPushButton('Load Sample Data Sources')
        samples_button.clicked.connect(lambda click: self.load_samples())
        # MODIFY EXISTING SOURCES LIST
        self.existing_sources = QComboBox(self)
        self.existing_sources.currentIndexChanged.connect(self.show_source)
        # DISPLAY FILE PATH TO INDICATED SOURCE
        self.local_csv_address = QTextEdit('No Source Selected')
        self.local_csv_address.setEnabled(False)
        # DELETE PRIMARY SOURCE BUTTON
        remove_source_button = QPushButton('Remove Data Source')
        remove_source_button.clicked.connect(lambda click: self.remove_source())
        # UPDATE SOURCE LIST WITH EXISTING PRIMARY SOURCES
        if self.sources:
            self.existing_sources.addItems(self.sources)
        # MAIN LAYOUT
        layout = QGridLayout(self)
        layout.addWidget(self.info)
        layout.addWidget(self.prefix_check)
        layout.addWidget(local_csv_button)
        layout.addWidget(samples_button)
        layout.addWidget(self.existing_sources)
        layout.addWidget(self.local_csv_address)
        layout.addWidget(remove_source_button)
        self.setLayout(layout)

    def closeEvent(self, a0):
        """
        Checks if a source is still loading,
         holds the window open and locked until finished.
        :param a0: PyQt close event
        """
        a0.ignore()
        if self.mutex.tryLock():
            self.mutex.unlock()
            if not self.isEnabled():
                self.setDisabled(False)
                self.close_requested = False
            a0.accept()
        else:
            self.setDisabled(True)
            self.close_requested = True
            self.info.setText('Still Loading Primary Source Data,\n'
                              'Window Will Close When Complete.')

    @pyqtSlot()
    def spec_updated(self):
        """
        Reloads applications spec file,
         after new sources are added.
        Closes add source window,
         if it was called.
        """
        with open('saved/spec.json', 'r') as f:
            self.spec = self.main_win.spec = load(f)
        self.info.setText('')
        if self.close_requested:
            self.close()

    def show_source(self, index:int):
        """
        Display selected primary sources file path.
        :param index: Index reference to existing_sources list.
        """
        self.source_index = index
        try:
            self.local_csv_address.setText(self.spec['sources'][self.sources[index]][0])
        except (KeyError, IndexError):
            self.local_csv_address.setText('Data Does Not Have Source Location, Re-Associate Data to Source.')

    def load_samples(self):
        """
        Add included example data sources to available primary source data.
        """
        self.info.setText('Loading Primary Source Data')
        QApplication.processEvents()
        for sample in listdir(resource_path(r'resources/example_data_sources')):
            self.add_new_source(resource_path(r'resources/example_data_sources/' + sample), False)
        self.info.setText('')

    def get_new_source(self):
        """
        Open file dialog to the source directory,
         and get new primary source data.
        """
        root = self.spec['source_dir'] if self.spec['source_dir'] else os.path.abspath(os.sep)
        extensions = 'DATA (*.csv *.xls* *.json)'
        source_file_path, ok = QFileDialog.getOpenFileName(self, 'Select Data Source To Add', root, extensions)
        if ok:
            self.info.setText('Loading Primary Source Data')
            QApplication.processEvents()
            self.add_new_source(source_file_path, True)
            self.info.setText('')

    def update_prefix_check(self):
        """
        User defined format for incoming data.
        :return: Prefix to apply to name.
        """
        state = self.prefix_check.checkState()
        if state == Qt.CheckState.Checked:
            self.prefix_check.setText('New Data Source Is Isometric')
            return 'iso_'
        elif state == Qt.CheckState.PartiallyChecked:
            self.prefix_check.setText('New Data Source Is Triangulation')
            return 'iso_tri_'
        else:
            self.prefix_check.setText('New Data Source Is Not Isometric')
            return ''

    def add_new_source(self, source_file_path:str, new:bool):
        """
        Obtain a new primary source and save a copy to the sources folder.
        Save the file path to the spec dictionary for this primary source.
        :param source_file_path: File path to new primary source data.
        :param new: True if adding new data source.
        """
        pfx = self.update_prefix_check() if new else ''
        source_name = pfx + source_file_path[source_file_path.rfind('/'):][1:]
        copyfile(source_file_path, Path('saved/sources/' + source_name).absolute())
        if source_name not in self.sources:
            self.sources.append(source_name)
            self.existing_sources.addItem(source_name)
            self.existing_sources.setCurrentIndex(self.sources.index(source_name))
            self.update_data_action.setText('Update Data From New Sources')
        update_spec = UpdateSpecSource(self.mutex, source_name, source_file_path)
        update_spec.signals.fin.connect(self.spec_updated)
        self.update_spec_pool.start(update_spec)
        if self.existing_sources.currentIndex() == self.sources.index(source_name):
            self.local_csv_address.setText(source_file_path)
        else:
            self.existing_sources.setCurrentIndex(self.sources.index(source_name))

    def remove_source(self):
        """
        Gets current index of existing_sources list.
        Delete the selected primary source as well as its spec dictionary reference.
        """
        if self.sources:
            if self.sources[self.source_index] in self.spec['sources']:
                self.spec['sources'].pop(self.sources[self.source_index])
                with open('saved/spec.json', 'w') as f:
                    dump(self.spec, f)
            if self.sources[self.source_index] in listdir('saved/sources'):
                remove('saved/sources/%s' % self.sources[self.source_index])
            self.sources.pop(self.source_index)
            self.existing_sources.removeItem(self.source_index)


class UpdateSources(QThread):
    error_occurred = pyqtSignal(Exception, name='ErrorInUpdate')
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    def __init__(self, main_window):
        """
        Updates primary source data in a separate thread,
         for all existing sources in the sources folder,
         as well as internal sample sources.
        :param main_window: Main Window.
        """
        super().__init__()
        self.main_window = main_window
        self.data_sources = []

    def run(self):
        """
        Obtains all primary source data,
         and makes an update call on them if internal,
         or converts saved external sources to parquet,
         for use in the application.
        Saves updated data in the data folder.
        Sends a list of any primary sources that fail,
         potentially due to not being in a csv or JSON format,
         and notifies user to verify the data is valid and correct format.
        """
        self.progress.emit('1')
        self.update_sources()
        failed = []
        for source in self.data_sources:
            if hasattr(source, 'internal'):
                self.progress.emit('1')
                source_func = source()
                source_func.prog.connect(self.get_prog)
                self.progress.emit('1')
                source_data = source_func.update()
                source_name = source_func.name
                save_data_as_parquet(source_data, source_name)
            else:
                source_path = 'saved/sources/' + source
                source_name = source[:source.rfind('.')]
                self.progress.emit('1')
                if source[source.rfind('.'):][:4] == '.csv':
                    df = read_csv(source_path, na_filter=True, encoding=self.main_window.spec['sources'][source][1])
                elif source[source.rfind('.'):][:5] == '.json':
                    df = read_json(source_path, encoding=self.main_window.spec['sources'][source][1])
                elif source[source.rfind('.'):][:4] == '.xls':
                    df = read_excel(source_path, na_values='')
                else:
                    df = None
                self.progress.emit('1')
                if df is not None:
                    source_data = {col: asarray(df[col],
                                   dtype=type(np.datetime64(df[col][1]))
                                   if type(df[col][0]) == Timestamp
                                   else type(df[col][0]))
                                   for col in df}
                    save_data_as_parquet(source_data, source_name)
                else:
                    failed.append(source_name)
        if failed:
            self.progress.emit('failed %s' % failed)
        self.progress.emit('1')
        self.finished.emit()

    def get_prog(self, prog:int):
        """
        Passes current progress information
         back to the main window as a string.
        :param prog: Progress int.
        """
        self.progress.emit(str(prog))

    def update_sources(self):
        """
        Uses the spec dictionary reference file path,
         to get the latest version of each saved primary source in the sources folder,
         and copies them over to update saved primary source data.
        Sends a list of any primary sources that are no longer found at their given file path,
         and notifies user to manually reset the file paths.
        """
        created_sources: Union[modules, TextIO] = [Game, IsoTriSurface, IsoWaveform, IsoPeaks, IsoSphere]
        self.data_sources = created_sources
        loc_error = []
        for source_name in listdir('saved/sources'):
            try:
                is_example = source_name in listdir(resource_path('resources/example_data_sources'))
                if self.main_window.spec['sources'][source_name] and not is_example:
                    source_file_path = self.main_window.spec['sources'][source_name][0]
                    copyfile(source_file_path, Path('saved/sources/' + source_name).absolute())
                    self.data_sources.append(source_name)
            except (KeyError, FileNotFoundError):
                loc_error.append(source_name)
        if loc_error: self.progress.emit('invalid %s' % loc_error)


class WorkerSignals(QObject):
    """
    Creates signals within a PyQt object.
    """
    prog_int = pyqtSignal(int)
    prog_str = pyqtSignal(str)
    fin = pyqtSignal()


class UpdateSpecSource(QRunnable):
    def __init__(self, mutex, source_name, source_file_path):
        """
        Thread pool object to update primary sources in the spec file.
        :param mutex: Thread lock mechanism.
        :param source_file_path: Path to new sources.
        """
        super().__init__()
        self.mutex = mutex
        self.source_name = source_name
        self.source_file_path = source_file_path
        self.root_dir = self.source_file_path[:self.source_file_path.rfind('/')]
        if self.root_dir == resource_path('resources/example_data_sources'):
            self.root_dir = ''
        self.setAutoDelete(True)
        self.signals = WorkerSignals()

    def detect_encoding(self):
        """
        Detect encoding of text in a given file.
        :return: Text encoding type.
        """
        detector = universaldetector.UniversalDetector()
        with open(self.source_file_path, 'rb') as file:
            for line in file:
                detector.feed(line)
                if detector.done: break
            detector.close()
        return detector.result['encoding']

    def run(self):
        """
        Locks thread while updating spec file with new sources.
        Updates primary sources root directory if a new source is added.
        """
        self.mutex.lock()
        with open('saved/spec.json', 'r') as f: spec = load(f)
        add_source = self.source_name not in spec['sources']
        if self.root_dir: spec['source_dir'] = self.root_dir
        if add_source: spec['sources'][self.source_name] = (self.source_file_path, self.detect_encoding())
        if self.root_dir or add_source:
            with open('saved/spec.json', 'w') as f: dump(spec, f)
        self.signals.fin.emit()
        self.mutex.unlock()