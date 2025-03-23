from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor, QKeySequence
from PyQt6.QtWidgets import (QTableView, QScrollArea, QVBoxLayout, QPushButton,
                             QWidget, QMessageBox, QSplitter, QHBoxLayout)
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from resources.modules.plot_settings import Settings
from resources.modules.plotting import PLOT_TYPES, RenderPlot
from resources.modules.stylesheets import button
from resources.modules.table import TableModel


class PlotMap(QWidget):
    def __init__(self, main_win, plot_map):
        """
        Base level module of a plot map instance.
        Exists as a tab in the main window.
        Show the current plot map data in top half as a table.
        Renders the current plot map data in bottom half as a graph.
        :param main_win: Instance of the main window, primary application.
        :param plot_map: Instance of the plot map being applied to module.
        """
        QWidget.__init__(self, main_win)
        # DEFINE PLOT MAP
        self.main_win = main_win
        self.plot_map = plot_map
        self.id = self.plot_map['id']
        # BACKGROUND COLOR
        self.setAutoFillBackground(True)
        self.set_bg_color()
        # RUN BUTTON
        self.loading_plot = False
        self.run_plot_button = QPushButton()
        self.run_plot_button.setStyleSheet(button)
        self.reset_run_plot_button_title()
        self.run_plot_button.clicked.connect(lambda checked: self.run_plot())
        self.run_plot_button.setShortcut(QKeySequence("Ctrl+r"))
        # SCROLL AREA
        self.scroll_area = QWidget()
        # TABLE
        table = QScrollArea(self.scroll_area)
        table.setWidgetResizable(True)
        self.table_data = QTableView()
        QTimer.singleShot(1000, self.table_data.resizeColumnsToContents)
        self.table_model = TableModel
        if self.plot_map['data'] is not None:
            self.table_model = TableModel(self.plot_map['data'])
            self.table_data.setModel(self.table_model)
        self.table_data.verticalHeader().setVisible(False)
        table.setWidget(self.table_data)
        # PLOT CANVAS
        self.canvas_scroll_area = QScrollArea()
        self.canvas_scroll_area.resize(800, 400)
        self.plot_canvas = RenderPlot(self)
        self.plot_canvas.prog.connect(self.plot_loading_prog)
        self.plot_canvas.fin.connect(self.plot_loaded)
        self.canvas_scroll_area.setWidget(self.plot_canvas)
        # TOOLBAR
        self.toolbar = NavigationToolbar(self.plot_canvas.canvas, self)
        self.toolbar.setStyleSheet("background-color: black;")
        self.toolbar.setOrientation(Qt.Orientation.Vertical)
        self.toolbar.setFixedWidth(25)
        # CANVAS TOOLBAR LAYOUT
        canvas_area = QWidget()
        can_layout = QHBoxLayout()
        can_layout.addWidget(self.toolbar)
        can_layout.addWidget(self.canvas_scroll_area)
        canvas_area.setLayout(can_layout)
        # SETTINGS
        self.settings = Settings(self)
        # SPLITTER
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(table)
        splitter.addWidget(canvas_area)
        # SET LAYOUT
        layout = QVBoxLayout()
        layout.addWidget(self.run_plot_button)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def reset_run_plot_button_title(self):
        """
        Set default run plot button label.
        Shows: The current graph to be rendered.
               The current plot map name.
               The plot map id.
        """
        self.run_plot_button.setText('DRAW PLOT: %s     ON: %s     PLOT ID: %s'
            % (self.plot_map['graph_name'], self.plot_map['title'], self.plot_map['id']))

    def set_bg_color(self):
        """
        Sets background color from plot map color
        """
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self.plot_map['color']))
        self.setPalette(palette)

    def update_data(self, plot_map:dict):
        """
        Get updated plot map when being saved in settings.
        Sets run plot button to default value.
        :param plot_map:
        """
        self.plot_map = plot_map
        self.reset_run_plot_button_title()

    def plot_loading_prog(self, prog:str):
        """
        Callback connection to RenderPlot.
        Updates run plot button with relevant information,
         obtained during plot rendering.
        :param prog:
        """
        self.run_plot_button.setText(prog)

    def plot_loaded(self):
        """
        Callback connection to RenderPlot.
        Sets run plot button to default value once plot is rendered
        """
        if self.main_win.isEnabled():
            self.reset_run_plot_button_title()

    def validate_data(self) -> bool:
        """
        Obtain the required coords from PLOT_TYPES necessary
         to run the plot given by the plot map graph name
         and verify they are set in the plot map.
        :return: True if all required parameters are set.
        """
        if self.plot_map['graph_name'] in PLOT_TYPES:
            axes_ids = PLOT_TYPES[self.plot_map['graph_name']][1]
            defined = {'x': self.plot_map['x_coord'], 'y': self.plot_map['y_coord'], 'z': self.plot_map['z_coord']}
            checklist = [defined[axes_id] for axes_id in axes_ids]
            if [True for check in checklist if not check]:
                return False
            return True
        return False

    def run_plot(self):
        """
        Render plot if necessary parameters are set.
        Otherwise, open settings window,
         or request parameterise get set if settings is open.
        """
        if self.validate_data():
            self.run_plot_button.setText(' < < < RENDERING PLOT > > > ')
            QTimer.singleShot(10, self.plot_canvas.run)
        else:
            if self.settings.isVisible():
                QMessageBox.information(self.settings,
                                        "Plot Structure Incomplete",
                                        "Set All Required Values For Desired Plot.",
                                        buttons=QMessageBox.StandardButton.Ok,
                                        defaultButton=QMessageBox.StandardButton.Ok)
            else:
                self.settings.show()