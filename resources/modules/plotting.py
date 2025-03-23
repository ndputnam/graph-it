
import numpy as np
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSlider
from matplotlib import ticker, rcParams
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


"""
Blank call to force import of Numpy when building application.
"""
force_numpy_import = np.array([])
del force_numpy_import

"""
PLOT TYPES:
 Primary values define a Matplotlib plotting function to be executed as a string.
 Secondary values define which coordinates are needed to create the given plot.
 Named keys utilize a prefix to define the necessary shape and type of data used.
    Iso must be a multidimensional Numpy array, shape > 1.
    Tri must be a flat or single dimension Numpy array, shape == 1.
    Otherwise it must be a Pandas Dataframe, single dimension.
"""
PLOT_TYPES = {'Standard Plot': ('self._ax.plot(self.x_data, self.y_data, ".", color=(0.0, 0.0, 1.0),'
                                ' markeredgewidth=.1, linewidth=.1)', ('x', 'y')), #done
              'Scatter Plot': ('self._ax.scatter(self.x_data, self.y_data, s=np.array(self.z_data), c=np.array(self.z_data), vmin=0,'
                               ' vmax=max(self.x_data[self.x_data.idxmax()],  self.y_data[self.y_data.idxmax()]))', ('x', 'y', 'z')), #done
              'Bar Plot': ('self._ax.bar(self.x_data, self.y_data, width=1, edgecolor="white", linewidth=0.7)', ('x', 'y')), #done
              '3-D Bar Plot': ('hist, xedges, yedges = np.histogram2d(self.x_data, self.y_data,'
                               ' bins=int(self.x_data[self.x_data.idxmax()] - self.x_data[self.x_data.idxmin()]),'
                               ' range=[[self.x_data[self.x_data.idxmin()], self.x_data[self.x_data.idxmax()]],'
                               ' [self.y_data[self.y_data.idxmin()], self.y_data[self.y_data.idxmax()]]]);'
                               ' xpos, ypos = np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25, indexing="ij");'
                               ' self._ax.bar3d(xpos.ravel(), ypos.ravel(), 0, 0.5 * np.ones_like(0),'
                               ' 0.5 * np.ones_like(0), hist.ravel(), zsort="average")', ('x', 'y')), # done
              'Stem Plot': ('self._ax.stem(self.x_data, self.y_data)', ('x', 'y')), # done
              # 'Fill Plot (no go)': ('self._ax.fill_between(x1, y1, y2, alpha=.5, linewidth=0);'
              #                       ' self._ax.plot(x, (y1 + y2) / 2, linewidth=2)', ('x', 'y')), # LOOK AT IN DETAIL
              'Stack Plot': ('self._ax.stackplot(self.x_data, self.y_data)', ('x', 'y')), # done
              'Stair Plot': ('self._ax.stairs(self.y_data, linewidth=2, fill=True)', 'y'), # done
              'Hist Plot': ('self._ax.hist(self.x_data, bins=10, linewidth=0.5, edgecolor="white")', 'x'), # done
              'Box Plot': ('self._ax.boxplot([self.x_data], positions=[10])', 'x'), # done
              'Error Plot': ('self._ax.errorbar(self.x_data, self.y_data)', ('x', 'y')), # done
              'Violin Plot': ('self._ax.violinplot(self.x_data)', 'x'), # done
              'Event Plot': ('self._ax.eventplot(self.x_data)', 'x'), # done
              'Hist Scatter Plot': ('self._ax.hist2d(self.x_data, self.y_data)', ('x', 'y')), # done
              'Hex Bin Plot': ('self._ax.hexbin(self.x_data, self.y_data)', ('x', 'y')), # done
              'Pie Plot': ('self._ax.pie(np.array(self.x_data))', 'x'), # done ... try with 2d array?
              'ECDF Plot': ('self._ax.ecdf(self.x_data)', 'x'), # done
              # 'Img Show Plot (no go)': ('self._ax.imshow(np.array(self.x_data))', 'x'), # NEED NP ARRAY LIKE OR PIL image,
              # likely need =< 2d, invalid shape
              # 'Color Mesh Plot (no go)': ('self._ax.pcolormesh(self.x_data, self.y_data, self.z_data)', ('x', 'y', 'z')), # NEED ARRAY
              # 'Contour Plot (no go)': ('self._ax.contour(self.x_data, self.y_data)', ('x', 'y')), # need array, z must be 2d
              # 'Contour Fill Plot (no go)': ('self._ax.contourf(self.x_data, self.y_data)', ('x', 'y')), # need array, z must be 2d
              'Barb Plot': ('self._ax.barbs(self.x_data, self.y_data)', ('x', 'y')), # done
              'Quiver Plot': ('self._ax.quiver(self.x_data, self.y_data)', ('x', 'y')), # done
              # 'Stream Plot (no go)': ('self._ax.streamplot(self.x_data, self.y_data)', ('x', 'y')), # missing args u and v
              'Tri Contour Plot': ('self._ax.plot(self.x_data, self.y_data, "o", markersize=2, color="lightgrey");'
                                   ' self._ax.tricontour(self.x_data, self.y_data, self.z_data,'
                                   ' levels=np.linspace(self.z_data[self.z_data.idxmin()], self.z_data[self.z_data.idxmax()], 7))',
                                   ('x', 'y', 'z')), # done
              'Tri Contour Fill Plot': ('self._ax.plot(self.x_data, self.y_data, "o", markersize=2, color="grey");'
                                        ' self._ax.tricontourf(self.x_data, self.y_data, self.z_data,'
                                        ' levels=np.linspace(self.z_data[self.z_data.idxmin()], self.z_data[self.z_data.idxmax()], 7))',
                                        ('x', 'y', 'z')), # done
              'Tri Plot': ('self._ax.triplot(self.x_data, self.y_data)', ('x', 'y')), # done
              'Tri Surf Plot': ('self._ax.plot_trisurf(self.x_data, self.y_data, self.z_data,'
                                ' linewidth=0.2, antialiased=True)', ('x', 'y', 'z')), # done
              'Iso Wireframe Plot': ('self._ax.plot_wireframe(self.x_data, self.y_data, self.z_data,'
                                     ' rstride=10, cstride=10, cmap="viridis")', ('x', 'y', 'z')), # done
              'Iso Wire Plot': ('self._ax.plot_wireframe(self.x_data, self.y_data, self.z_data)', ('x', 'y', 'z')), # done
              'Iso Surface Plot': ('self._ax.plot_surface(self.x_data, self.y_data, self.z_data)', ('x', 'y', 'z')), # done
              'Iso Surface Highlight Plot': ('self._ax.plot_surface(self.x_data, self.y_data, self.z_data,'
                                             ' rstride=1, cstride=1, cmap="viridis", edgecolor="none")',
                                             ('x', 'y', 'z')), # done
              # 'Iso Fill Plot (no go)': ('self._ax.fill_between(x1, y1, z1, x2, y2, z2, alpha=0.5);'
              #                   ' self._ax.plot(x1, y1, z1); ax.plot(x2, y2, z2)', ('x', 'y', 'z')),# LOOK AT IN DETAIL
              'Iso Standard Plot': ('self._ax.plot(self.x_data, self.y_data, self.z_data)', ('x', 'y', 'z')), # done
              # 'Iso Quiver Plot (no go)': ('self._ax.quiver(self.x_data, self.y_data, self.z_data)', ('x', 'y', 'z')), # missing u, v, w
              'Iso Scatter Plot': ('self._ax.scatter(self.x_data, self.y_data, self.z_data)', ('x', 'y', 'z')), # done
              }
              # 'Iso Stem Plot (no go)': ('self._ax.stem(self.x_data, self.y_data, self.z_data)', ('x', 'y', 'z')), # CRASHES, no info!!!
              # 'Iso Voxel Plot (no go)': ('self._ax.voxels(voxelarray)', ('x', 'y', 'z')),  # NEED TO LOOK AT IN DETAIL
              # 'Dynamic Plot (no go)': ('dynamic()', ('x', 'y'))} # NEED TO CREATE


def dynamic():
    """
    To be added in the future.
    :return:
    """
    print('DYNAMIC!!')
    pass

class RenderPlot(QWidget):
    prog = pyqtSignal(str)
    fin = pyqtSignal()
    def __init__(self, plot_map_obj):
        """
        Takes data in the form of a Pandas Dataframe
         or as a dictionary of Numpy multidimensional arrays.
        Renders to a Matplotlib figure canvas displayed in a widget.
        :param plot_map_obj: parent, PlotMap instance.
        """
        QWidget.__init__(self, parent=plot_map_obj)
        # VARS
        self.plot_map_obj = plot_map_obj
        self.plot_form = {}
        self._ax = None
        self.x_data = None
        self.y_data = None
        self.z_data = None
        self.iso = None
        self.x_label_size = 0
        self.y_label_size = 0
        self.rotate = True
        # FIGURE CANVAS
        self.fig = Figure(dpi=100, layout='tight')
        self.canvas = FigureCanvas(self.fig)
        self._ax = self.canvas.figure.add_subplot()
        self.watermark = [self._ax.text(0.5, 0.5, 'Graph-It', transform=self._ax.transAxes, fontsize=40,
                                       color='gray', alpha=0.5, ha='center', va='center', rotation=0), ]
        # MOUSE CLICK EVENT
        self.fig.canvas.mpl_connect("button_release_event", self.on_click)
        # ROTATION STYLE
        rcParams['axes3d.mouserotationstyle'] = 'sphere'
        # ELEVATION SLIDER
        self.slider_elev_label = QLabel("Elev\n %s" % 30)
        self.slider_elev = QSlider( orientation=Qt.Orientation.Vertical)
        self.slider_elev.setRange(-180, 180)
        self.slider_elev.valueChanged.connect(self.rotate_elev)
        self.slider_elev.setValue(30)
        # AZIMUTH SLIDER
        self.slider_azim_label = QLabel("Azim\n %s" % 30)
        self.slider_azim = QSlider(orientation=Qt.Orientation.Vertical)
        self.slider_azim.setRange(-180, 180)
        self.slider_azim.valueChanged.connect(self.rotate_azim)
        self.slider_azim.setValue(30)
        # ROLL SLIDER
        self.slider_roll_label = QLabel('Roll\n %s' % 0)
        self.slider_roll = QSlider(orientation=Qt.Orientation.Vertical)
        self.slider_roll.setRange(-180, 180)
        self.slider_roll.valueChanged.connect(self.rotate_roll)
        self.slider_roll.setValue(0)
        # LAYOUTS
        self.slider_elev_layout = QVBoxLayout()
        self.slider_azim_layout = QVBoxLayout()
        self.slider_roll_layout = QVBoxLayout()
        self.main_layout = QHBoxLayout(self)
        self.reset_layout()

    def add_watermark(self, width:int, height:int):
        """
        Applies a watermark, adjusting for plot shape.
        :param width: Plot canvas width.
        :param height: Plot canvas height.
        """
        [mark.set_visible(False) for mark in self.watermark]
        canvas_aspect_ratio = max(width, height) / min(width, height)
        text_aspect_ratio = 4.24868
        rotation = 45
        if text_aspect_ratio < canvas_aspect_ratio:
            text_size = min(width, height)
            rotation = 0 if width >= height else 90
        elif self.x_label_size + self.y_label_size > 0:
            text_size = (self.x_label_size if width >= height else self.y_label_size)
        else:
            text_size = min(width, height)
        text_fit = max(width, height) // (text_size if rotation == 45 else text_size * 1.5)
        text_size = text_size / text_aspect_ratio / 1.34513
        color = 'grey' if self.plot_map_obj.plot_map['color'] != 'slategrey' else 'white'
        spacing = (1 / text_fit) / 2
        if self.iso:
            self.watermark = [self._ax.text2D(spacing if width >= height else 0.5, 0.5 if width >= height else spacing,
                                              'Graph-It', transform=self._ax.transAxes, fontsize=text_size,
                                              color=color, alpha=0.5, ha='center', va='center', rotation=rotation)]
        else:
            for w in range(int(text_fit)):
                watermark = self._ax.text(spacing if width >= height else 0.5, 0.5 if width >= height else spacing,
                                          'Graph-It', transform=self._ax.transAxes, fontsize=text_size,
                                          color=color, alpha=0.5, ha='center', va='center', rotation=rotation)
                self.watermark.append(watermark)
                spacing += 1 / text_fit

    def run(self):
        """
        Renders plot data from the plot map with the specified graph.
        Makes a call to the PLOT_TYPES dict to set the axes for the graph.
        """
        self.fig.clf()
        self.x_label_size = 0
        self.y_label_size = 0
        self.define_column_data()
        graph_name = self.plot_map_obj.plot_map['graph_name']
        try:
            self.set_config()
            exec(PLOT_TYPES[graph_name][0])
            self.structure_plot()
            self.canvas.draw()
            if self.x_label_size + self.y_label_size > 0:
                self.structure_plot()
                self.canvas.draw()
        except (TypeError, KeyError, NameError, ValueError) as e:
            self.plot_error(graph_name, e)
        self.fin.emit()

    def plot_error(self, graph_name:str, error:str):
        """
        Output a plot with the error created from a failed attempt at rendering.
        :param graph_name: name of graph trying to plot.
        :param error: error details.
        """
        self.fig.clf()
        rcParams['xtick.color'] = 'black'
        rcParams['ytick.color'] = 'black'
        self._ax = self.fig.add_subplot()
        self._ax.set_title('GRAPH DATA APPLIED IS NOT VALID FOR "%s" FORMAT.' % graph_name)
        self._ax.text(.02, .8, 'ERROR CALLED:\n%s' % error, wrap=True)
        self._ax.set_facecolor('black')
        self.canvas.draw()

    def define_column_data(self):
        """
        Pull data from plot map data for each defined column.
        """
        col_x = self.plot_map_obj.plot_map['x_coord']
        col_y = self.plot_map_obj.plot_map['y_coord']
        col_z = self.plot_map_obj.plot_map['z_coord']
        if col_x: self.x_data = self.plot_map_obj.plot_map['data'][col_x]
        if col_y: self.y_data = self.plot_map_obj.plot_map['data'][col_y]
        if col_z: self.z_data = self.plot_map_obj.plot_map['data'][col_z]

    def set_config(self):
        """
        Defines the structure of the desired rendering.
        Set the layout to match the style being called for.
        Set the labels respective to the plot map data being applied.
        """
        plot_map = self.plot_map_obj.plot_map
        graph_type = plot_map['graph_name'][:3]
        self.iso = True if graph_type in ['Iso', 'Tri', '3-D'] else False
        self.reset_layout()
        neg_color = 'black' if plot_map['color'] in ['white', 'yellow', 'aqua', 'lightgrey', 'tan'] else 'white'
        pos_color = neg_color if self.iso else 'white'
        rcParams['text.color'] = pos_color
        rcParams['axes.labelcolor'] = pos_color
        rcParams['lines.color'] = neg_color
        rcParams['lines.markerfacecolor'] = neg_color
        rcParams['xtick.color'] = pos_color
        rcParams['ytick.color'] = pos_color
        self._ax = self.canvas.figure.add_subplot(projection="3d") if self.iso else self.canvas.figure.add_subplot()
        self._ax.set_title(self.plot_map_obj.plot_map['title'] + ' ' + plot_map['graph_name'])
        if plot_map['x_coord']: self._ax.set_xlabel(plot_map['x_coord'])
        if plot_map['y_coord']: self._ax.set_ylabel(plot_map['y_coord'])
        if self.iso and graph_type != '3-D': self._ax.set_zlabel(plot_map['z_coord'])
        self.fig.autofmt_xdate(rotation=90, ha='center')
        self.fig.set_facecolor((0,0,0))
        self._ax.set_facecolor(plot_map['color'])

    def structure_plot(self):
        """
        Apply plot structure defined by plot map.
        """
        self.set_gridlines()
        self.set_extended_ticks()
        self.resize_plot()
        self.set_label_size()

    def set_gridlines(self):
        """
        Applies horizontal and vertical gridlines.
        """
        self._ax.xaxis.grid(self.plot_map_obj.plot_map['x_grid'])
        self._ax.yaxis.grid(self.plot_map_obj.plot_map['y_grid'])

    def set_extended_ticks(self):
        """
        Define which ticks are shown and how often.
        """
        if not self.plot_map_obj.plot_map['fit'] and not self.iso:
            if self.plot_map_obj.plot_map['x_coord']:
                if self.plot_map_obj.plot_map['label_all']:
                    self._ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
                unique_x = self.plot_map_obj.plot_map['data'].duplicated(self.plot_map_obj.plot_map['x_coord'])
                self._ax.set_xlim(-1, unique_x.value_counts().to_dict()[False] + 1)
            if self.plot_map_obj.plot_map['y_coord']:
                if self.plot_map_obj.plot_map['label_all']:
                    self._ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
                unique_y = self.plot_map_obj.plot_map['data'].duplicated(self.plot_map_obj.plot_map['y_coord'])
                self._ax.set_ylim(-1, unique_y.value_counts().to_dict()[False] + 1)

    def resize_plot(self):
        """
        Applies DPI,effectively resizing fonts
         while maintaining overall size aspects relative to the display area.
        Scale plot to parameters set in plot map.
        """
        canvas_width, canvas_height = self.canvas.figure.get_size_inches() * self.fig.dpi
        horz_stretch = self.set_horz_stretch(canvas_width)
        vert_stretch = self.set_vert_stretch(canvas_height)
        scroll_area_size = self.plot_map_obj.canvas_scroll_area.size()
        dpi = self.plot_map_obj.plot_map['dpi']
        self.canvas.figure.set_dpi(dpi)
        width = int((scroll_area_size.width() - 2) * horz_stretch)
        height = int((scroll_area_size.height() - 2) * vert_stretch)
        self.canvas.figure.set_size_inches((width - 20) / dpi, (height - 20) / dpi)
        self.setFixedSize(width, height)
        self.add_watermark(width, height)

    def set_horz_stretch(self, canvas_width:float) -> float:
        """
        Define scaling of horizontal axis
        :param canvas_width: current width of the plot canvas
        :return: horizontal stretch.
        """
        if self.plot_map_obj.plot_map['horz_stretch'] > 0:
            return self.plot_map_obj.plot_map['horz_stretch']
        if self.x_label_size == 0 or self.plot_map_obj.plot_map['fit'] and self.iso:
            return 1
        return self.x_label_size / canvas_width

    def set_vert_stretch(self, canvas_height:float) -> float:
        """
        Define scaling of vertical axis.
        :param canvas_height: current height of the plot canvas
        :return: vertical stretch.
        """
        if self.plot_map_obj.plot_map['vert_stretch'] > 0:
            return self.plot_map_obj.plot_map['vert_stretch']
        if self.plot_map_obj.plot_map['fit'] and self.iso or self.y_label_size == 0:
            return 1
        return self.y_label_size / canvas_height


    def set_label_size(self):
        """
        Define the size factor for the new plot,
         redraws the plot if label sizes are > 0,
         sets which ticks are affected based on plot map parameters.
        """
        if not self.iso and not self.plot_map_obj.plot_map['fit']:
            renderer = self.canvas.get_renderer()
            plot_title_height = 50
            x_title = 50
            y_title = 50
            if self.plot_map_obj.plot_map['vert_stretch'] == 0:
                y_label_size = sum([t.get_window_extent(renderer=renderer).height for t in self._ax.get_yticklabels()])
                x_text_length = max([t.get_window_extent(renderer=renderer).height for t in self._ax.get_xticklabels()])
                self.y_label_size = y_label_size + x_text_length + x_title + plot_title_height
            if self.plot_map_obj.plot_map['horz_stretch'] == 0:
                x_label_size = sum([t.get_window_extent(renderer=renderer).width for t in self._ax.get_xticklabels()])
                y_text_length = max([t.get_window_extent(renderer=renderer).width for t in self._ax.get_yticklabels()])
                self.x_label_size = x_label_size + y_text_length + y_title

    def on_click(self, event):
        """
        Rotates isometric by degrees provided when left mouse button is held down.
        :param event: PyQt mouse click event.
        """
        if self.iso:
            elev, azim, roll = self._ax.elev, self._ax.azim, self._ax.roll
            self.rotate = False
            self.slider_elev.setValue(int(elev))
            self.slider_azim.setValue(int(azim))
            self.slider_roll.setValue(int(roll))
            self.rotate =True

    def rotate_elev(self, value:int):
        """
        Redraws after adjusting view along the vertical axis.
        :param value: Degrees applying to axis rotation.
        """
        if self.iso:
            self.slider_elev_label.setText("Elev\n %s" % value)
            if self.rotate:
                self._ax.view_init(value, self._ax.azim, self._ax.roll)
                self.canvas.draw()

    def rotate_azim(self, value:int):
        """
        Redraws after adjusting view along the horizontal axis.
        :param value: Degrees applying to axis rotation.
        """
        if self.iso:
            self.slider_azim_label.setText("Azim\n %s" % value)
            if self.rotate:
                self._ax.view_init(self._ax.elev, value, self._ax.roll)
                self.canvas.draw()

    def rotate_roll(self, value:int):
        """
        Redraws after adjusting view in a rotational axis.
        :param value: Degrees applying to axis rotation.
        """
        if self.iso:
            self.slider_roll_label.setText('Roll\n %s' % value)
            if self.rotate:
                self._ax.view_init(self._ax.elev, self._ax.azim, value)
                self.canvas.draw()

    def reset_layout(self):
        """
        Reconstructs layout depending on if it is rendering flat or isometric.
        """
        self.deleteItemsOfLayout(self.main_layout)
        if not self.iso: self.main_layout.addWidget(self.canvas) # RECREATE MAIN LAYOUT FOR 2-D.
        elif self.slider_azim_layout not in self.main_layout.children(): # RECREATE MAIN LAYOUT WITH SLIDERS FOR 3-D.
            self.slider_elev_layout.addWidget(self.slider_elev_label)
            self.slider_elev_layout.addWidget(self.slider_elev)
            self.slider_azim_layout.addWidget(self.slider_azim_label)
            self.slider_azim_layout.addWidget(self.slider_azim)
            self.slider_roll_layout.addWidget(self.slider_roll_label)
            self.slider_roll_layout.addWidget(self.slider_roll)
            self.main_layout.addWidget(self.canvas, 15)
            self.main_layout.addSpacing(10)
            self.main_layout.addLayout(self.slider_elev_layout, 0)
            self.main_layout.addLayout(self.slider_azim_layout, 0)
            self.main_layout.addLayout(self.slider_roll_layout, 0)
            self.main_layout.addSpacing(10)

    def deleteItemsOfLayout(self, layout):
        """
        Clears current layout so it can be reconstructed.
        :param layout: Current main layout.
        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None: widget.setParent(None)
                else: self.deleteItemsOfLayout(item.layout())