import numpy as np
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSlider
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

"""
Blank call to force import of Numpy when building application.
"""
force_numpy_import = np.array([])

"""
PLOT TYPES:
 Primary values define a Matplotlib plotting function to be executed as a string.
 Secondary values define which coordinates are needed to create the given plot.
 Named keys utilize a prefix to define the necessary shape and type of data used.
    Iso must be a multidimensional Numpy array, shape > 1.
    Tri must be a flat or single dimension Numpy array, shape == 1.
    Otherwise it must be a Pandas Dataframe, single dimension.
"""
PLOT_TYPES = {'Standard Plot': ('self._ax.plot(x_data, y_data, ".", color=(0.0, 0.0, 1.0),'
                                ' markeredgewidth=.1, linewidth=.1)', ('x', 'y')), #done
              'Scatter Plot': ('self._ax.scatter(x_data, y_data, s=np.array(z_data), c=np.array(z_data), vmin=0,'
                               ' vmax=max(x_data[x_data.idxmax()],  y_data[y_data.idxmax()]))', ('x', 'y', 'z')), #done
              'Bar Plot': ('self._ax.bar(x_data, y_data, width=1, edgecolor="white", linewidth=0.7)', ('x', 'y')), #done
              '3-D Bar Plot': ('hist, xedges, yedges = np.histogram2d(x_data, y_data,'
                               ' bins=x_data[x_data.idxmax()] - x_data[x_data.idxmin()],'
                               ' range=[[x_data[x_data.idxmin()], x_data[x_data.idxmax()]],'
                               ' [y_data[y_data.idxmin()], y_data[y_data.idxmax()]]]);'
                               ' xpos, ypos = np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25, indexing="ij");'
                               ' self._ax.bar3d(xpos.ravel(), ypos.ravel(), 0, 0.5 * np.ones_like(0),'
                               ' 0.5 * np.ones_like(0), hist.ravel(), zsort="average")', ('x', 'y')), # done
              'Stem Plot': ('self._ax.stem(x_data, y_data)', ('x', 'y')), # done
              'Fill Plot (no go)': ('self._ax.fill_between(x1, y1, y2, alpha=.5, linewidth=0);'
                                    ' self._ax.plot(x, (y1 + y2) / 2, linewidth=2)', ('x', 'y')), # LOOK AT IN DETAIL
              'Stack Plot': ('self._ax.stackplot(x_data, y_data)', ('x', 'y')), # done
              'Stair Plot': ('self._ax.stairs(y_data, linewidth=2)', 'y'), # done
              'Hist Plot': ('self._ax.hist(x_data, bins=10, linewidth=0.5, edgecolor="white")', 'x'), # done
              'Box Plot': ('self._ax.boxplot([x_data], positions=[10])', 'x'), # done
              'Error Plot': ('self._ax.errorbar(x_data, y_data)', ('x', 'y')), # done
              'Violin Plot': ('self._ax.violinplot(x_data)', 'x'), # done
              'Event Plot': ('self._ax.eventplot(x_data)', 'x'), # done
              'Hist Scatter Plot': ('self._ax.hist2d(x_data, y_data)', ('x', 'y')), # done
              'Hex Bin Plot': ('self._ax.hexbin(x_data, y_data)', ('x', 'y')), # done
              'Pie Plot (no go)': ('self._ax.pie(np.array(x_data))', 'x'), # done ... try with 2d array?
              'ECDF Plot': ('self._ax.ecdf(x_data)', 'x'), # done
              'Img Show Plot (no go)': ('self._ax.imshow(np.array(x_data))', 'x'), # NEED NP ARRAY LIKE OR PIL image,
              # likely need =< 2d, invalid shape
              'Color Mesh Plot (no go)': ('self._ax.pcolormesh(x_data, y_data, z_data)', ('x', 'y', 'z')), # NEED ARRAY
              'Contour Plot (no go)': ('self._ax.contour(x_data, y_data)', ('x', 'y')), # need array, z must be 2d
              'Contour Fill Plot (no go)': ('self._ax.contourf(x_data, y_data)', ('x', 'y')), # need array, z must be 2d
              'Barb Plot': ('self._ax.barbs(x_data, y_data)', ('x', 'y')), # done
              'Quiver Plot': ('self._ax.quiver(x_data, y_data)', ('x', 'y')), # done
              'Stream Plot (no go)': ('self._ax.streamplot(x_data, y_data)', ('x', 'y')), # missing args u and v
              'Tri Contour Plot': ('self._ax.plot(x_data, y_data, "o", markersize=2, color="lightgrey");'
                                   ' self._ax.tricontour(x_data, y_data, z_data,'
                                   ' levels=np.linspace(z_data[z_data.idxmin()], z_data[z_data.idxmax()], 7))',
                                   ('x', 'y', 'z')), # done
              'Tri Contour Fill Plot': ('self._ax.plot(x_data, y_data, "o", markersize=2, color="grey");'
                                        ' self._ax.tricontourf(x_data, y_data, z_data,'
                                        ' levels=np.linspace(z_data[z_data.idxmin()], z_data[z_data.idxmax()], 7))',
                                        ('x', 'y', 'z')), # done
              'Tri Plot': ('self._ax.triplot(x_data, y_data)', ('x', 'y')), # done
              'Tri Surf Plot': ('self._ax.plot_trisurf(x_data, y_data, z_data,'
                                ' linewidth=0.2, antialiased=True)', ('x', 'y', 'z')), # done
              'Iso Wireframe Plot': ('self._ax.plot_wireframe(x_data, y_data, z_data,'
                                     ' rstride=10, cstride=10, cmap="viridis")', ('x', 'y', 'z')), # done
              'Iso Wire Plot': ('self._ax.plot_wireframe(x_data, y_data, z_data)', ('x', 'y', 'z')), # done
              'Iso Surface Plot': ('self._ax.plot_surface(x_data, y_data, z_data)', ('x', 'y', 'z')), # done
              'Iso Surface Highlight Plot': ('self._ax.plot_surface(x_data, y_data, z_data,'
                                             ' rstride=1, cstride=1, cmap="viridis", edgecolor="none")',
                                             ('x', 'y', 'z')), # done
              'Iso Fill Plot (no go)': ('self._ax.fill_between(x1, y1, z1, x2, y2, z2, alpha=0.5);'
                                ' self._ax.plot(x1, y1, z1); ax.plot(x2, y2, z2)', ('x', 'y', 'z')),# LOOK AT IN DETAIL
              'Iso Standard Plot': ('self._ax.plot(x_data, y_data, z_data)', ('x', 'y', 'z')), # done
              'Iso Quiver Plot (no go)': ('self._ax.quiver(x_data, y_data, z_data)', ('x', 'y', 'z')), # missing u, v, w
              'Iso Scatter Plot': ('self._ax.scatter(x_data, y_data, z_data)', ('x', 'y', 'z')), # done
              'Iso Stem Plot (no go)': ('self._ax.stem(x_data, y_data, z_data)', ('x', 'y', 'z')), # CRASHES, no info!!!
              'Iso Voxel Plot (no go)': ('self._ax.voxels(voxelarray)', ('x', 'y', 'z')),  # NEED TO LOOK AT IN DETAIL
              'Dynamic Plot (no go)': ('dynamic()', ('x', 'y'))} # NEED TO CREATE

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
        self.iso = None
        # FIGURE CANVAS
        self.fig = Figure(dpi=100, layout='constrained')
        self.canvas = FigureCanvas(self.fig)
        # AXIS ROTATION SLIDERS
        slid_min = 0
        slid_max = 360
        # AZIMUTH SLIDER
        self.slider_azim_label = QLabel("Horz")
        self.slider_azim_max_label = QLabel(f"{slid_max}")
        self.slider_azim = QSlider(orientation=Qt.Orientation.Vertical)
        self.slider_azim_min_label = QLabel(f"{slid_min}")
        self.slider_azim.setRange(slid_min, slid_max)
        # ELEVATION SLIDER
        self.slider_elev_label = QLabel("Vert")
        self.slider_elev_max_label = QLabel(f"{slid_max}")
        self.slider_elev = QSlider( orientation=Qt.Orientation.Vertical)
        self.slider_elev_min_label = QLabel(f"{slid_min}")
        self.slider_elev.setRange(slid_min, slid_max)
        # AZIMUTH LAYOUT
        self.slider_azim_layout = QVBoxLayout()
        self.slider_azim_layout.addWidget(self.slider_azim_label, 1)
        self.slider_azim_layout.addWidget(self.slider_azim_max_label)
        self.slider_azim_layout.addWidget(self.slider_azim, 5)
        self.slider_azim_layout.addWidget(self.slider_azim_min_label)
        # ELEVATION LAYOUT
        self.slider_elev_layout = QVBoxLayout()
        self.slider_elev_layout.addWidget(self.slider_elev_label, 1)
        self.slider_elev_layout.addWidget(self.slider_elev_max_label)
        self.slider_elev_layout.addWidget(self.slider_elev, 5)
        self.slider_elev_layout.addWidget(self.slider_elev_min_label)
        # MAIN LAYOUT
        self.main_layout = QHBoxLayout(self)
        self.reset_layout()
        # SET SIGNALS
        self.slider_azim.valueChanged.connect(self.rotate_azim)
        self.slider_elev.valueChanged.connect(self.rotate_elev)
        self.slider_azim.setValue(30)
        self.slider_elev.setValue(30)
        self.fig.canvas.mpl_connect("button_release_event", self.on_click)

    def run(self):
        """
        Renders plot data from the plot map with the specified graph.
        Makes a call to the PLOT_TYPES dict to set the axes for the graph.
        :return: None
        """
        self.fig.clf()
        col_x = self.plot_map_obj.plot_map['x_coord']
        col_y = self.plot_map_obj.plot_map['y_coord']
        col_z = self.plot_map_obj.plot_map['z_coord']
        if col_x: x_data = self.plot_map_obj.plot_map['data'][col_x]
        if col_y: y_data = self.plot_map_obj.plot_map['data'][col_y]
        if col_z: z_data = self.plot_map_obj.plot_map['data'][col_z]
        self.set_config()
        try:
            exec(PLOT_TYPES[self.plot_map_obj.plot_map['graph_name']][0])
            self.canvas.draw()
        except (TypeError, KeyError, NameError, ValueError) as e:
            self.plot_error(e)
        self.fin.emit()

    def plot_error(self, error):
        """
        Output a plot with the error created from a failed attempt at rendering.
        :param error: error details.
        :return: None
        """
        print('error rendering plot: %s' % error)
        self.fig.clf()
        self._ax = self.fig.add_subplot()
        self._ax.set_title('GRAPH DATA APPLIED IS NOT VALID FOR THIS PLOTTING FORMAT.')
        self._ax.text(.02, .8, '%s' % error, wrap=True)
        self.canvas.draw()

    def set_config(self):
        """
        Defines the structure of the desired rendering.
        Set the layout to match the style being called for.
        Set the labels respective to the plot map data being applied.
        :return: None
        """
        self.fig.set_canvas(self.canvas)
        self.set_dpi()
        graph_type = self.plot_map_obj.plot_map['graph_name'][:3]
        if graph_type in ['Iso', 'Tri', '3-D']:
            self.iso = True
            self.reset_layout()
            self._ax = self.canvas.figure.add_subplot(projection="3d")

            self._ax.view_init(30, 30)
            if graph_type != '3-D':
                self._ax.set_zlabel(self.plot_map_obj.plot_map['z_coord'])
        else:
            self.iso = False
            self.reset_layout()
            self._ax = self.canvas.figure.add_subplot()
        self._ax.set_title(self.plot_map_obj.plot_map['graph_name'])
        self._ax.set_xlabel(self.plot_map_obj.plot_map['x_coord'])
        self._ax.set_ylabel(self.plot_map_obj.plot_map['y_coord'])

    def set_dpi(self):
        """
        Updates the figure with the current DPI saved to the plot map.
        Effectively resizes fonts while maintaining overall size aspects relative to the display area.
        :return: None
        """
        val = self.plot_map_obj.plot_map['dpi']
        scroll_area_size = self.plot_map_obj.canvas.size()
        self.canvas.figure.set_dpi(val)
        self.canvas.figure.set_size_inches(scroll_area_size.width() / val,
                                           scroll_area_size.height() / val)
        can_size = self.canvas.get_width_height(physical=True)
        self.setFixedSize(can_size[0], can_size[1])
        return True

    def change_dpi(self):
        """
        Manual call to update the DPI of the rendered figure.
        :return: None
        """
        self.set_dpi()
        self.run()

    def on_click(self, event):
        """
        Rotates isometric by degrees provided when left mouse button is held down.
        :param event: PyQt mouse click event.
        :return: None
        """
        if self.iso:
            azim, elev = self._ax.azim, self._ax.elev
            self.slider_azim.setValue(azim + 180)
            self.slider_elev.setValue(elev + 180)

    def rotate_azim(self, value:int):
        """
        Redraws after adjusting view along the horizontal axis.
        :param value: degrees of change applying to axis rotation.
        :return: None
        """
        if self.iso:
            self._ax.view_init(self._ax.elev, value)
            self.fig.set_canvas(self.canvas)
            self.canvas.draw()

    def rotate_elev(self, value:int):
        """
        Redraws after adjusting view along the vertical axis.
        :param value: degrees of change applying to axis rotation.
        :return: None
        """
        if self.iso:
            self._ax.view_init(value, self._ax.azim)
            self.fig.set_canvas(self.canvas)
            self.canvas.draw()

    def reset_layout(self):
        """
        Reconstructs layout depending on if it is rendering flat or isometric.
        :return: None
        """
        self.deleteItemsOfLayout(self.main_layout)
        if not self.iso:
            # RECREATE MAIN LAYOUT FOR 2-D
            self.main_layout.addWidget(self.canvas)
        elif self.slider_azim_layout not in self.main_layout.children():
            # RECREATE AZIMUTH SLIDER
            self.slider_azim_layout.addWidget(self.slider_azim_label, 1)
            self.slider_azim_layout.addWidget(self.slider_azim_max_label)
            self.slider_azim_layout.addWidget(self.slider_azim, 5)
            self.slider_azim_layout.addWidget(self.slider_azim_min_label)
            # RECREATE ELEVATION SLIDER
            self.slider_elev_layout.addWidget(self.slider_elev_label, 1)
            self.slider_elev_layout.addWidget(self.slider_elev_max_label)
            self.slider_elev_layout.addWidget(self.slider_elev, 5)
            self.slider_elev_layout.addWidget(self.slider_elev_min_label)
            # RECREATE MAIN LAYOUT FOR ISOMETRIC
            self.main_layout.addWidget(self.canvas, 15)
            self.main_layout.addSpacing(50)
            self.main_layout.addLayout(self.slider_azim_layout, 0)
            self.main_layout.addLayout(self.slider_elev_layout, 5)

    def deleteItemsOfLayout(self, layout):
        """
        Clears current layout so it can be reconstructed.
        :param layout: Current main layout.
        :return: None
        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.deleteItemsOfLayout(item.layout())