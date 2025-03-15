from __future__ import annotations

from json import dump
from json import load
from os import listdir
from os import makedirs, remove
from pathlib import Path
from sys import argv

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon, QAction, QKeySequence
from PyQt6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QMainWindow, QToolBar, QPushButton,
                             QGridLayout, QDialog, QTabWidget, QMessageBox, QProgressBar, QSlider)
from win32ctypes.pywin32.pywintypes import datetime

from resources.modules.output import OutputOptions
from resources.modules.source import Source, UpdateSources
from resources.modules.stylesheets import tabs
from resources.modules.utility import load_plot_maps, save_plot_map, resource_path


def create_saves():
    """
    Checks if auxiliary data storage folders exist,
     and creates them if they don't.
    Creates the applications spec file if it doesn't exist.
    :return: None
    """
    makedirs('saved/data', exist_ok=True)
    makedirs('saved/plots', exist_ok=True)
    makedirs('saved/outputs', exist_ok=True)
    makedirs('saved/sources', exist_ok=True)
    # if not Path('saved/sources/winequality-red.csv').exists():
    if not Path('saved/spec.json').exists():
        with open(Path(r'saved/spec.json').absolute(), 'w') as f:
            dump({'sources': {}, 'source_dir': '', 'output_dir': ''}, f)


class MainWindow(QMainWindow):
    def __init__(self):
        """
        Main application window.
        Load data into plot maps,
         which exist as an instance of a PlotMap tab.
        Modify data as desired.
        Displays a table of the data,
         and renders a graph of selected data columns.
        """
        super().__init__()
        # WINDOW DETAILS
        self.setWindowTitle("GRAPH IT - Data Management and Analysis")
        self.icon = QIcon(resource_path('../images/gear.ico'))
        self.setWindowIcon(self.icon)
        self.resize(1200, 800)

        # SPEC
        with open('saved/spec.json', 'r') as f:
            self.spec = load(f)

        # LOAD SOURCES
        self.sources = [source for source in listdir('saved/sources')]

        # LOAD PLOTS
        self.plots = [plot for plot in load_plot_maps(self, True)]  # temporary storage of PlotMap objects

        # UPDATE DATA ACTION
        self.update_data_action = QAction('Need to Obtain Valid Data Sources', self)
        self.update_data_action.triggered.connect(self.update_data)
        self.update_data_action.setShortcut(QKeySequence('Ctrl+u'))
        if listdir('saved/sources'):
            self.update_data_action.setText('Update Data From New Sources')
        if listdir('saved/data'):
            self.update_data_action.setText('Update Data for Session')

        # ADD DATA SOURCE WINDOW
        self.source_win = Source(self)

        # ADD DATA SOURCE ACTION
        self.add_source_action = QAction('Manage Data Sources', self)
        self.add_source_action.triggered.connect(self.source_win.show)
        self.add_source_action.setShortcut(QKeySequence('Ctrl+s'))

        # UPDATE DATA THREAD
        self.sources_updating = False
        self.update_thread = UpdateSources(self)
        self.update_thread.progress.connect(self.data_updating)
        self.update_thread.finished.connect(self.data_updated)
        self.update_thread.finished.connect(self.update_thread.deleteLater)

        # CREATE NEW PLOT ACTION
        self.create_plot_action = QAction("New Plot", self)
        self.create_plot_action.triggered.connect(self.create_new_plot_map)
        self.create_plot_action.setShortcut(QKeySequence("Ctrl+n"))

        # ADD EXISTING OR CREATE NEW PLOT WINDOW
        self.new_plot = False
        self.step = False
        self.load_plot_win = QDialog(self)
        self.load_plot_win.setWindowTitle('Select Existing or Create New Plot')
        self.load_plot_win.setWindowIcon(self.icon)
        self.select_plot = QComboBox(parent=self.load_plot_win)
        self.select_plot.addItem('Select Existing Plot')
        self.select_plot.currentIndexChanged.connect(self.load_plot_map)
        plot_win_button = QPushButton('New', parent=self.load_plot_win)
        plot_win_button.clicked.connect(lambda click: self.get_new_plot())
        plot_win_layout = QHBoxLayout(self.load_plot_win)
        plot_win_layout.addWidget(self.select_plot)
        plot_win_layout.addWidget(plot_win_button)
        self.load_plot_win.setLayout(plot_win_layout)

        # DELETE PLOT ACTION
        self.delete_plot_action = QAction('Delete Plot', self)
        self.delete_plot_action.triggered.connect(self.delete_plot_map)
        self.delete_plot_action.setShortcut(QKeySequence('Ctrl+d'))

        # PLOT SETTINGS ACTION
        self.plot_settings_action = QAction('Plot Settings', self)
        self.plot_settings_action.triggered.connect(self.plot_settings)
        self.plot_settings_action.setShortcut(QKeySequence("Ctrl+o"))

        # OUTPUT PLOT ACTION
        self.output_action = QAction('Output', self)
        self.output_action.triggered.connect(self.output_options)
        self.output_action.setShortcut(QKeySequence("Ctrl+p"))

        # PLOT TABS
        self.removed_tabs = []
        self.tabs = QTabWidget(tabPosition=QTabWidget.TabPosition.West,
                               movable=False,
                               tabShape=QTabWidget.TabShape.Triangular,
                               tabBarAutoHide=True,
                               usesScrollButtons=True,
                               tabsClosable=True)
        self.tabs.setStyleSheet(tabs)
        self.tabs.currentChanged.connect(self.changeEvent)
        self.tabs.tabCloseRequested.connect(self.closeEvent)

        # PRINT PLOT OPTIONS WINDOW
        self.output_win = OutputOptions(self)

        # PROGRESS BAR
        self.prog_val = QSlider()
        self.progress = None

        # POPULATE TABS
        for p in self.plots:
            self.tabs.addTab(p, 'PLOT %s' % p.plot_map['id'])

        # MENU BAR
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(self.add_source_action)
        file_menu.addAction(self.update_data_action)
        file_menu.addAction(self.create_plot_action)
        file_menu.addAction(self.delete_plot_action)
        file_menu.addAction(self.plot_settings_action)
        file_menu.addAction(self.output_action)

        # TOOLBAR
        self.toolbar = QToolBar("My main toolbar")
        self.addToolBar(self.toolbar)
        self.toolbar.addAction(self.add_source_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.update_data_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.create_plot_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.delete_plot_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.plot_settings_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.output_action)
        self.toolbar.addSeparator()

        # SET LAYOUT
        layout = QGridLayout()
        layout.addWidget(self.tabs)
        self.setCentralWidget(self.tabs)

    def closeEvent(self, event):
        """
        Catches if a tab is closed and stores it when closing.
        Closes the PlotMap settings window if it is open when application is closed.
        :param event: PyQt close event.
        :return: None
        """
        if isinstance(event, int):
            index = event
            plot = self.tabs.widget(index)
            self.removed_tabs.append(plot.id)
            self.tabs.removeTab(index)
        else:
            [s.settings.close() for s in self.plots]

    def changeEvent(self, index:int):
        """
        current tab changed
        :param index: current tab index
        :return: None
        """
        if isinstance(index, int):
            if [True for s in self.plots if s.settings.isVisible()]:
                self.plot_settings()
            if self.output_win.isVisible():
                self.output_win.output_name.setText(self.plots[self.tabs.currentIndex()].plot_map['title'])

    def plot_settings(self):
        """
        Opens the settings window associated with the current PlotMap instance shown.
        :return: None
        """
        if self.tabs:
            if not self.plots[self.tabs.currentIndex()].settings.isVisible():
                [s.settings.hide() for s in self.plots]
                self.plots[self.tabs.currentIndex()].settings.show()
        else:
            self.no_plot_msg()

    def output_options(self):
        """
        Opens the output window.
        :return: None
        """
        if self.plots:
            self.output_win.output_name.setText(self.select_plot.currentText())
            self.output_win.show()
        else:
            self.no_plot_msg()

    def no_plot_msg(self):
        """
        Open notification that there isn't a plot map,
         and creates a new instance of one.
        :return: None
        """
        QMessageBox.information(self, "No Plot Loaded", "New Plot Will be created.",
                                buttons=QMessageBox.StandardButton.Ok,
                                defaultButton=QMessageBox.StandardButton.Ok)
        self.create_new_plot_map()

    def update_data(self):
        """
        Initializes and displays the update progress bar.
        Starts the update primary sources thread.
        :return: None
        """
        self.progress = QProgressBar(self)
        self.prog_val.setValue(14 + len(listdir('saved/sources')))
        self.prog_val.valueChanged.connect(self.progress.setValue)
        self.progress.setRange(self.prog_val.value(), self.prog_val.value() + self.prog_val.value())
        self.toolbar.addWidget(self.progress)
        self.sources_updating = True
        self.update_thread.start()

    def data_updating(self, progress:str):
        """
        Updates progress bar while update thread is running.
        Opens a warning window if there is an issue found,
         with any of the primary source data attributes.
        :param progress: Update thread progress.
        :return: None
        """
        parent = self
        if self.plots[self.tabs.currentIndex()].settings.isVisible():
            parent = self.plots[self.tabs.currentIndex()].settings
        if progress[:7] == 'invalid':
            QMessageBox.critical(parent, "Source Location Invalid",
                                 'Data Does Not Have Source Location for\n%s.\n'
                                 'Re-Associate Source in "Manage Data Sources".' % progress[8:],
                                 buttons=QMessageBox.StandardButton.Ok,
                                 defaultButton=QMessageBox.StandardButton.Ok)
        elif progress[:6] == 'failed':
            QMessageBox.critical(parent, "Source Update Failed",
                                 'Primary Data Source Update Failed for\n%s.\n'
                                 'Verify Data is in Valid .csv or .json format.' % progress[7:],
                                 buttons=QMessageBox.StandardButton.Ok,
                                 defaultButton=QMessageBox.StandardButton.Ok)
        else:
            self.prog_val.setValue(self.prog_val.value() + int(progress))

    def data_updated(self):
        """
        Called after primary source data is updated,
         and updates all existing plot maps with new data.
        Re-initializes the update thread object.
        :return: None
        """
        self.prog_val.setValue(self.prog_val.value() + 1)
        if self.plots:
            [plot.settings.update_combo_boxes() for plot in self.plots]
            [plot.settings.set_data(plot.settings.data_selector.findText(plot.plot_map['data_name'])) for plot in self.plots]
            if self.plots[self.tabs.currentIndex()].validate_data():
                self.plots[self.tabs.currentIndex()].run_plot()
        self.update_data_action.setText('DATA UPDATED: %s' % datetime.today().strftime('%c'))
        if self.update_thread.isFinished():
            self.update_thread = UpdateSources(self)
            self.update_thread.progress.connect(self.data_updating)
            self.update_thread.finished.connect(self.data_updated)
            self.update_thread.finished.connect(self.update_thread.deleteLater)
            self.sources_updating = False
            self.prog_val.setValue(self.prog_val.value() + 1)
            QTimer.singleShot(1000, self.progress.deleteLater)

    def create_new_plot_map(self):
        """
        Checks if any PlotMap objects have been closed,
         opens window to give the option to re-open one,
         or to create a new instance and new tab.
        :return: None
        """
        if self.new_plot:
            new_plot = load_plot_maps(self, False)[0]
            self.plots.append(new_plot)
            save_plot_map(new_plot)
            self.tabs.addTab(new_plot, 'PLOT %s' % new_plot.plot_map['id'])
            self.tabs.setCurrentIndex(self.tabs.indexOf(new_plot))
            self.new_plot = False
        elif self.removed_tabs:
            self.select_plot.addItems('Plot: ' + str(tab) for tab in self.removed_tabs)
            self.step = True
            self.load_plot_win.show()
        else:
            self.get_new_plot()

    def get_new_plot(self):
        """
        Create a new PlotMap instance.
        :return: None
        """
        self.new_plot = True
        self.create_new_plot_map()
        if self.load_plot_win.isVisible():
            self.load_plot_win.close()

    def load_plot_map(self, box_id:int):
        """
        Re-opens an existing PlotMap that was previously closed.
        :param box_id: Index of closed PlotMap objects list.
        :return: None
        """
        if self.step and box_id > 0:
            self.step = False
            index = box_id - 1
            reload_plot = [plot for plot in self.plots if plot.id == self.removed_tabs[index]][0]
            if reload_plot is not None:
                self.tabs.insertTab(int(reload_plot.id) - 1, reload_plot, 'PLOT %s' % reload_plot.id)
                self.removed_tabs.remove(self.removed_tabs[index])
                self.select_plot.removeItem(self.select_plot.currentIndex())
                self.select_plot.setCurrentIndex(0)
                self.step = True
            if not self.removed_tabs:
                self.load_plot_win.close()

    def delete_plot_map(self):
        """
        Verify user wants to delete the given plot map.
        Removes plot map JSON file and tab from system.
        :return: None
        """
        index = self.tabs.currentIndex()
        if index >= 0:
            plot = self.plots[index]
            check = QMessageBox.warning(self, "Delete Plot ID: %s" % plot.plot_map['id'],
                                        "Are You Certain About\nPermanently Removing\n%s?" % plot.plot_map['title'],
                                        buttons=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                                        defaultButton=QMessageBox.StandardButton.Cancel)
            if check == 1024:
                self.plots.remove(plot)
                self.tabs.removeTab(index)
                remove('saved/plots/plot_map_%s.json' % plot.plot_map['id'])


if __name__ == "__main__":
    create_saves()
    app = QApplication(argv)
    mw = MainWindow()
    mw.show()
    app.exec()