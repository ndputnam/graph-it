from json import dump
from os import listdir, remove
from pathlib import Path
from shutil import copyfile
from sys import modules
from typing import Union, TextIO

from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QDialog, QPushButton, QComboBox, QTextEdit, QGridLayout, QFileDialog
from numpy import asarray
from pandas import read_csv, read_json

from resources.modules.create_sources import *
from resources.modules.utility import save_data_as_parquet


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
        self.spec = main_win.spec
        self.sources = main_win.sources
        self.update_data_action = main_win.update_data_action
        # SET SOURCE DIRECTORY
        self.source_index = 0
        self.sources_root_dir = self.spec['source_dir'] if self.spec['source_dir'] else 'C:\\'
        if self.sources and self.sources[self.source_index] in self.spec['sources']:
            self.sources_root_dir = self.spec['sources'][self.sources[self.source_index]]
        # GET PRIMARY SOURCE BUTTON
        local_csv_button = QPushButton('Get Local CSV:')
        local_csv_button.clicked.connect(lambda click: self.get_new_csv())
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
        add_data_layout = QGridLayout(self)
        add_data_layout.addWidget(local_csv_button)
        add_data_layout.addWidget(self.existing_sources)
        add_data_layout.addWidget(self.local_csv_address)
        add_data_layout.addWidget(remove_source_button)
        self.setLayout(add_data_layout)

    def show_source(self, index:int):
        """
        Display selected primary sources file path.
        :param index: Index reference to existing_sources list.
        :return: None
        """
        self.source_index = index
        try:
            self.local_csv_address.setText(self.spec['sources'][self.sources[index]])
        except KeyError:
            self.local_csv_address.setText('Data Does Not Have Source Location, Re-Associate Data to Source.')

    def get_new_csv(self):
        """
        Open file dialog to the source directory.
        Obtain a new primary source and save a copy to the sources folder.
        Save the file path to the spec dictionary for this primary source.
        :return: None
        """
        csv_file, ok = QFileDialog.getOpenFileName(self, 'Select CSV to Add', self.sources_root_dir, 'CSV (*.csv)')
        if csv_file:
            csv_name = csv_file[csv_file.rfind('/'):][1:]
            copyfile(csv_file, Path('saved/sources/' + csv_name).absolute())
            if csv_name not in self.sources:
                self.sources.append(csv_name)
                self.existing_sources.addItem(csv_name)
                self.existing_sources.setCurrentIndex(self.sources.index(csv_name))
                self.update_data_action.setText('Update Data From New Sources')
            if csv_name not in self.spec['sources']:
                self.spec['sources'][csv_name] = csv_file
                self.spec['source_dir'] = self.sources_root_dir = self.spec['sources'][self.sources[self.source_index]]
                if self.existing_sources.currentIndex() == self.sources.index(csv_name):
                    self.local_csv_address.setText(self.spec['sources'][self.sources[self.source_index]])
                else:
                    self.existing_sources.setCurrentIndex(self.sources.index(csv_name))
            with open('saved/spec.json', 'w') as f:
                dump(self.spec, f)

    def remove_source(self):
        """
        Gets current index of existing_sources list.
        Delete the selected primary source as well as its spec dictionary reference.
        :return: None
        """
        if self.sources[self.source_index] in self.spec['sources']:
            self.spec['sources'].pop(self.sources[self.source_index])
        if self.sources[self.source_index] in listdir('saved/sources'):
            remove('saved/sources/%s' % self.sources[self.source_index])
        self.existing_sources.removeItem(self.source_index)
        self.sources.pop(self.source_index)
        with open('saved/spec.json', 'w') as f:
            dump(self.spec, f)


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
        :return: None
        """
        self.progress.emit('1')
        self.update_sources()
        failed = []
        for data in self.data_sources:
            self.progress.emit('1')
            if hasattr(data, 'internal'):
                source = data()
                source.prog.connect(self.get_prog)
                source_data = source.update()
                source_name = source.name
                save_data_as_parquet(source_data, source_name)
            else:
                source = 'saved/sources/' + data
                df = None
                source_name = 'unnamed'
                if data[-3:] == 'csv':
                    source_name = data[:-4]
                    df = read_csv(source, na_filter=True)
                elif data[-4:] == 'json':
                    source_name = data[:-5]
                    df = read_json(source)
                if df is not None:
                    source_data = {col: asarray(df[col], dtype=type(df[col][0])) for col in df}
                    save_data_as_parquet(source_data, source_name)
                else:
                    failed.append(source_name)
        if failed:
            self.progress.emit('failed %s' % failed)
        self.progress.emit('1')
        self.finished.emit()

    def get_prog(self, prog:str):
        """
        Passes current progress information back to the main window.
        :param prog: Progress string.
        :return: None
        """
        self.progress.emit(str(prog))

    def update_sources(self):
        """
        Uses the spec dictionary reference file path,
         to get the latest version of each saved primary source in the sources folder,
         and copies them over to update saved primary source data.
        Sends a list of any primary sources that are no longer found at their given file path,
         and notifies user to manually reset the file paths.
        :return: None
        """
        created_sources: Union[modules, TextIO] = [Game, IsoTriSurface, IsoWaveform, IsoPeaks, IsoSphere]
        self.data_sources = created_sources
        ex = []
        for source in listdir('saved/sources'):
            try:
                if self.main_window.spec['sources'][source]:
                    csv_file = self.main_window.spec['sources'][source]
                    copyfile(csv_file, Path('saved/sources/' + source).absolute())
                    self.data_sources.append(source)
            except KeyError as e:
                ex.append(e.args)
        if ex:
            ex = [e[0] for e in ex]
            self.progress.emit('invalid %s' % ex)