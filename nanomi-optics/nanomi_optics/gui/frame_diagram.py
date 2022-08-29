import numpy as np
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
from nanomi_optics.engine.lens import Lens
from nanomi_optics.engine.optimization import optimize_focal_length

LAMBDA_ELECTRON = 0.0112e-6

LENS_BORE = 25.4*0.1/2

# diameter of condensor aperature
CA_DIAMETER = 0.01

# stores info for the anode
ANODE = [39.1, 30, 1.5, [0.5, 0, 0.3], 'Anode']

# stores info for the sample
SAMPLE = [528.9, 1.5, -1, [1, 0.7, 0], 'Sample']

# stores info for the scintillator
SCINTILLATOR = [972.7, 1.5, 1, [0.3, 0.75, 0.75], 'Scintillator']

# stores info for the condensor aperature
CONDENSOR_APERATURE = [192.4, 1.5, 1, [0, 0, 0], 'Cond. Apert']

# add color of each ray in same order as rays
# red, green, blue, gold
RAY_COLORS = [[1.0, 0, 0], [0.0, 1.0, 0], [0.0, 0.2, 1.0], [0.7, 0.4, 0]]

# pin condenser aperture angle limited as per location and diameter
RAYS = [
    np.array(
        [[1.5e-2], [(CA_DIAMETER/2 - 1.5e-2) / CONDENSOR_APERATURE[0]]]
    ),
    # 2nd ray, at r = 0, angle limited by CA
    np.array(
        [[0], [(CA_DIAMETER/2) / CONDENSOR_APERATURE[0]]]
    ),
    # 3rd ray, at r = tip edge, parallel to opt. axis
    np.array(
        [[1.5e-2], [0]]
    ),
    # 4th ray, at -rG, angle up to +CA edge CRAZY BEAM
    np.array(
        [[-1*1.5e-2], [(CA_DIAMETER/2 + 1.5e-2) / CONDENSOR_APERATURE[0]]]
    )
]


# stores info for the lower lenses
LOWER_LENSES = [
    [551.6, 1.5, -1, [0.3, 0.75, 0.75], 'Objective'],
    [706.4, 1.5, 1, [0.3, 0.75, 0.75], 'Intermediate'],
    [826.9, 1.5, 1, [0.3, 0.75, 0.75], 'Projective']
]

# stores info for the upper lenses
UPPER_LENSES = [
    [257.03, 63.5, 1.5, [0.3, 0.9, 0.65], 'C1'],
    [349, 1.5, 1, [0.3, 0.75, 0.75], 'C2'],
    [517, 1.5, 1, [0.3, 0.75, 0.75], 'C3']
]


# frame that holds the diagram (current values are placeholders)
class DiagramFrame(ttk.Frame):
    """diagram frame creates and handle matplotlib plots"""
    def __init__(self, master):
        """intialize lenses and rays diagram

        Args:
            master (tk.Window): master window
        """
        super().__init__(master, borderwidth=5)

        # create figure
        self.figure = Figure(figsize=(10, 10))
        self.axis = self.figure.add_subplot()
        self.axis.text(
            275, -2.1, 'X [mm]', color=[0, 0, 0], fontsize=6
        )
        self.axis.set_ylabel(
            'Z [mm]', color=[0, 0, 0], fontsize=6
        )

        # put the figure in a widget on the tk window
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.redraw()

        # put the navigation toolbar in a widget on the tk window
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()

        self.x_min, self. x_max, self.y_min, self.y_max = 0, 0, 0, 0
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # initial focal distance of the lenses in [mm]
        self.cf_u = [67.29, 22.94, 39.88]
        self.cf_l = [19.67, 6.498, 6]

        # list for active lenses
        self.active_lu = [True, True, True]
        self.active_ll = [True, True, True]

        # sample rays variables and initialization for lower lenses
        self.distance_from_optical = 0.00001
        self.scattering_angle = 0
        self.last_mag = 0
        self.sample_rays = []
        self.update_l_rays()

        # draws anode
        self.symmetrical_box(*ANODE)

        # draws sample
        self.sample_aperature_box(*SAMPLE)

        # draws condensor aperature
        self.sample_aperature_box(*CONDENSOR_APERATURE)

        # draws scintillator
        self.asymmetrical_box(*SCINTILLATOR)

        # draw red dashed line on x-axis
        self.axis.axhline(0, 0, 1, color='red', linestyle='--')

        # list of points to plot rays
        self.drawn_rays_c, self.drawn_rays_b = [], []

        # list of lenses magnification and plots
        self.mag_lower, self.mag_upper = [], []
        self.mag_u_plot, self.mag_l_plot = [], []

        # crossover points arrays
        self.crossover_points_c, self.crossover_points_b = [], []

        # takes in list of lens info, draws upper lenses
        # and setup magnification plots
        for i, row in enumerate(UPPER_LENSES):
            # draw C1 lens
            if i == 0:
                self.symmetrical_box(*row)
            # draw C2, C3 lens
            else:
                self.asymmetrical_box(*row)
            # set up magnification plot
            self.mag_u_plot.append(
                self.axis.text(
                    UPPER_LENSES[i][0] + 5,
                    0.5, '', color='k', fontsize=8,
                    rotation='vertical',
                    backgroundcolor=[0.8, 1.0, 1.0]
                )
            )
            # green circle to mark the crossover point of each lens
            self.crossover_points_c.append(self.axis.plot([], 'go')[0])

        # takes in list of lens info, draws lower lenses
        # and set up crossover points
        for i, row in enumerate(LOWER_LENSES):
            # draw lens
            self.asymmetrical_box(*row)
            # set up magnification plot
            self.mag_l_plot.append(
                self.axis.text(
                    LOWER_LENSES[i][0] + 5,
                    0.5, '', color='k', fontsize=8,
                    rotation='vertical',
                    backgroundcolor=[0.8, 1, 1]
                )
            )
            # green circle to mark the crossover point of each lens
            self.crossover_points_b.append(self.axis.plot([], 'go')[0])

        # set up lines representing the ray path for upper lenses
        for i in range(len(RAYS)):
            for j in range(len(UPPER_LENSES)):
                self.drawn_rays_c.append(
                    self.axis.plot(
                        [], lw=1, color=RAY_COLORS[i]
                    )[0]
                )
                self.drawn_rays_c.append(
                    self.axis.plot(
                        [], lw=3, color=RAY_COLORS[i]
                    )[0]
                )
                self.drawn_rays_c.append(
                    self.axis.plot(
                        [], lw=1, color="r"
                    )[0]
                )

        # set up lines representing the ray path for lower lenses
        for i in range(len(self.sample_rays)):
            for j in range(len(LOWER_LENSES)):
                self.drawn_rays_b.append(
                    self.axis.plot(
                        [], lw=1, color=RAY_COLORS[i]
                    )[0]
                )
                self.drawn_rays_b.append(
                    self.axis.plot(
                        [], lw=3, color=RAY_COLORS[i]
                    )[0]
                )
                self.drawn_rays_b.append(
                    self.axis.plot(
                        [], lw=1, color="r"
                    )[0]
                )

        # text to display extreme info
        self.extreme_info = self.axis.text(
            300, 1.64, '', color=[0, 0, 0],
            fontsize='large', ha='center'
        )

        # initialize arrays with points info
        self.lines_u, self.lines_l = [], []
        self.display_u_rays()
        self.display_l_rays()

    def symmetrical_box(self, x, w, h, colour, name):
        """ draws symmetrical box in diagram

        Args:
            x (float): box location
            w (float): box width
            h (float): box height
            colour (list): RGB colors
            name (str): lens name
        """
        # x = location of centre point of box along x-axis
        # w = width, h = height, colour = color

        # rectangle box
        self.axis.add_patch(
            Rectangle(
                (x-w/2, -h), w, h*2, edgecolor=colour,
                facecolor='none', lw=1
            )
        )
        # top lens bore (horizontal line)
        self.axis.hlines(LENS_BORE, x-w/2, x+w/2, colors=colour)
        # bottom lens bore (horizontal line)
        self.axis.hlines(-LENS_BORE, x-w/2, x+w/2, colors=colour)
        # electrode location in lens
        self.axis.vlines(x, -h, h, colors=colour, linestyles='--')

        self.axis.text(
            x, -h+0.05, name, fontsize=8,
            rotation='vertical', ha='center'
        )
        return

    # draws an asymmetrical box
    def asymmetrical_box(self, x, h, position, colour, name):
        """ draws symmetrical box in diagram

        Args:
            x (float): box location
            h (float): box height
            position (int): defines dashed line side
            colour (list): RGB colors
            name (str): box name
        """
        # Short, Long distance from mid holder to sample [mm]
        long = 52.2   # mm
        short = 11.6  # mm

        self.axis.add_patch(
            Rectangle(
                (x+position*short, -h), -position*long-position*short,
                2*h, edgecolor=colour, facecolor='none', lw=1
            )
        )
        # electrode Location in lens
        self.axis.vlines(x, -h, h, colors=colour, linestyles='--')
        # bottom lens bore
        self.axis.hlines(-LENS_BORE, x-long, x+short, colors=colour)
        # top lens bore
        self.axis.hlines(LENS_BORE, x-long, x+short, colors=colour)

        self.axis.text(
            x-position*10, -h+0.05, name, fontsize=8,
            rotation='vertical', ha='center'
        )
        return

    # draws box for sample and condensor aperature
    def sample_aperature_box(self, x, h, position, colour, name):
        """draws box for sample and condensor aperature

        Args:
            x (float): location of center point along (true) x-axis
            h (float): height for box
            position (int): defines dashed line side
            colour (list): RGB colors
            name (str): box name
        """
        # Short, Long distance from mid holder to sample [mm]
        long = 25  # mm
        short = 3  # mm

        self.axis.add_patch(
            Rectangle(
                (x+position*short, -h), -position*long-position*short,
                2*h, edgecolor=colour, facecolor='none', lw=1
            )
        )
        # electrode location in lens
        self.axis.vlines(x, h, -h, colors=colour, linestyle='--')
        self.axis.text(
            x-position*10, -h+0.05, name,
            fontsize=8, ha='center', rotation='vertical'
        )
        return

    def display_ray_path(self, rays, lenses, l_plot, m_plot, upper):
        """get all ray paths through each lens

        Args:
            rays (list): contains all rays properties
            lenses (list): contains all lens objects
            l_plot (list): lens plots
            m_plot (list): magnification plots
            upper (bool): is it upper lenses
        """
        num_l = len(lenses)
        for i in range(len(rays)):
            for j, lens in enumerate(lenses):
                if j != 0 or upper:
                    lens.update_output_plane_location()
                sl, el, li, mag = lens.ray_path(
                    rays[i] if j == 0 else
                    lenses[j - 1].ray_out_lens
                )
                sl = ([x for x, y in sl], [y for x, y in sl])
                li = ([x for x, y in li], [y for x, y in li])
                el = ([x for x, y in el], [y for x, y in el])

                l_plot.append(
                    self.axis.plot(sl[0], sl[1],  lw=1, color=RAY_COLORS[i])
                )
                l_plot.append(
                    self.axis.plot(li[0], li[1],  lw=2, color=RAY_COLORS[i])
                )
                l_plot.append(
                    self.axis.plot(el[0], el[1],  lw=1, color="k")
                )
                if mag is not None and i == 0:
                    if upper:
                        self.mag_upper.append(mag)
                        m_plot[j].set_text(f"{mag:.2E}x")
                    elif not upper:
                        self.mag_lower.append(mag)
                        m_plot[j].set_text(f"{mag:.2E}x")
                if not upper and i == 1 and j == (num_l - 1):
                    self.last_mag = abs(
                        lens.ray_in_vac[0][0] / self.distance_from_optical
                    )

    def display_u_rays(self):
        """creates upper lenses that will be part of the ray paths"""
        self.mag_upper = []
        upper_lenses_obj = []
        active_index = [x for x, act in enumerate(self.active_lu) if act]
        # creates a lens object for all active lenses
        # and set ups crossover points plots
        for counter, index in enumerate(active_index):
            upper_lenses_obj.append(
                Lens(
                    UPPER_LENSES[index][0],
                    self.cf_u[index],
                    None if counter == 0 else
                    upper_lenses_obj[counter - 1],
                    3
                )
            )
            self.crossover_points_c[index].set_data(
                upper_lenses_obj[counter].crossover_point_location()
            )
            self.crossover_points_c[index].set_visible(True)
        # initialize ray path last lens
        if len(upper_lenses_obj) > 0:
            upper_lenses_obj.append(
                Lens(
                    SAMPLE[0],
                    0,
                    upper_lenses_obj[-1],
                    1
                )
            )

        # hide all inactive crossover points
        inactive_index = [
            x for x, act in enumerate(self.active_lu) if not act
        ]
        for index in inactive_index:
            self.crossover_points_c[index].set_visible(False)

        # plot ray path
        self.display_ray_path(
            RAYS, upper_lenses_obj, self.lines_u, self.mag_u_plot, True
        )

    def update_u_lenses(self):
        """update upper lenses settings"""
        for line in self.lines_u:
            line.pop(0).remove()
        self.lines_u = []

        self.display_u_rays()
        self.redraw()
        self.canvas.flush_events()

    def update_l_rays(self):
        self.scattering_angle = LAMBDA_ELECTRON / self.distance_from_optical
        self.sample_rays = [
            np.array([[0], [self.scattering_angle]]),
            np.array([[self.distance_from_optical], [self.scattering_angle]]),
            np.array([[self.distance_from_optical], [0]])
        ]

    def display_l_rays(self):
        """creates lower lenses that will be part of the ray paths"""
        self.mag_lower = []
        lower_lenses_obj = []
        active_index = [x for x, act in enumerate(self.active_ll) if act]
        sample = Lens(SAMPLE[0], None, None, None)
        # creates a lens object for all active lenses
        # and set ups crossover points plots
        for counter, index in enumerate(active_index):
            lower_lenses_obj.append(
                Lens(
                    LOWER_LENSES[index][0],
                    self.cf_l[index],
                    sample if counter == 0 else
                    lower_lenses_obj[counter - 1],
                    3 if index != 2 else 2
                )
            )
            self.crossover_points_b[index].set_data(
                lower_lenses_obj[counter].crossover_point_location()
            )
            self.crossover_points_b[index].set_visible(True)

        # initialize ray path last lens
        if len(lower_lenses_obj):
            lower_lenses_obj.append(
                Lens(
                    SCINTILLATOR[0],
                    0,
                    lower_lenses_obj[counter],
                    1
                )
            )

        # hide all inactive crossover points
        inactive_index = [
            x for x, act in enumerate(self.active_ll) if not act
        ]
        for index in inactive_index:
            self.crossover_points_b[index].set_visible(False)

        # plot ray path
        self.display_ray_path(
            self.sample_rays, lower_lenses_obj, self.lines_l,
            self.mag_l_plot, False
        )

    def update_l_lenses(self, opt_bool, opt_sel, lens_sel):
        """update lower lenses settings

        Args:
            opt_bool (bool): do we need to optimize
            opt_sel (str): image mode for optimization
            lens_sel (int): lens index to optimize focal length
        """
        if opt_bool:
            self.cf_l[lens_sel] = optimize_focal_length(
                opt_sel, lens_sel, [cz[0] for cz in LOWER_LENSES],
                self.cf_l, self.sample_rays[0:2], self.active_ll
            )

        for line in self.lines_l:
            line.pop(0).remove()
        self.lines_l = []

        self.update_l_rays()
        self.display_l_rays()
        self.redraw()
        self.canvas.flush_events()

    def redraw(self):
        """redraw diagram"""
        self.axis.relim()
        self.axis.autoscale_view()
        self.canvas.draw()
