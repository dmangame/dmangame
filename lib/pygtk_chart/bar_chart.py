#       Copyright 2009 John Dickinson <john@johnandkaren.com>
#                      Sven Festersen <sven@sven-festersen.de>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
"""
Contains the BarChart widget.

Author: John Dickinson (john@johnandkaren.com),
Sven Festersen (sven@sven-festersen.de)
"""
__docformat__ = "epytext"
import cairo
import gtk
import gobject
import os
import math

import pygtk_chart
from pygtk_chart.basics import *
from pygtk_chart.chart_object import ChartObject
from pygtk_chart import chart
from pygtk_chart import label

from pygtk_chart import COLORS, COLOR_AUTO

MODE_VERTICAL = 0
MODE_HORIZONTAL = 1

MIN_HEIGHT=100
MIN_WIDTH=100

def draw_rounded_rectangle(context, x, y, width, height, radius=0):
    """
    Draws a rectangle with rounded corners to context. radius specifies
    the corner radius in px.

    @param context: the context to draw on
    @type context: CairoContext
    @param x: x coordinate of the upper left corner
    @type x: float
    @param y: y coordinate of the upper left corner
    @type y: float
    @param width: width of the rectangle in px
    @type width: float
    @param height: height of the rectangle in px
    @type height: float
    @param radius: corner radius in px (default: 0)
    @type radius: float.
    """
    if radius == 0:
        context.rectangle(x, y, width, height)
    else:
        context.move_to(x, y + radius)
        context.arc(x + radius, y + radius, radius, math.pi, 1.5 * math.pi)
        context.rel_line_to(width - 2 * radius, 0)
        context.arc(x + width - radius, y + radius, radius, 1.5 * math.pi, 2 * math.pi)
        context.rel_line_to(0, height - 2 * radius)
        context.arc(x + width - radius, y + height - radius, radius, 0, 0.5 * math.pi)
        context.rel_line_to(-(width - 2 * radius), 0)
        context.arc(x + radius, y + height - radius, radius, 0.5 * math.pi, math.pi)
        context.close_path()


class Bar(chart.Area):
    """
    A class that represents a bar on a bar chart.

    Properties
    ==========
    The Bar class inherits properties from chart.Area.
    Additional properties:
     - corner-radius (radius of the bar's corners, in px; type: float)

    Signals
    =======
    The Bar class inherits signals from chart.Area.
    """

    __gproperties__ = {"corner-radius": (gobject.TYPE_INT, "bar corner radius",
                                "The radius of the bar's rounded corner.",
                                0, 100, 0, gobject.PARAM_READWRITE)}

    def __init__(self, name, value, title=""):
        chart.Area.__init__(self, name, value, title)
        self._label_object = label.Label((0, 0), title)
        self._value_label_object = label.Label((0, 0), "")

        self._corner_radius = 0

    def do_get_property(self, property):
        if property.name == "visible":
            return self._show
        elif property.name == "antialias":
            return self._antialias
        elif property.name == "name":
            return self._name
        elif property.name == "value":
            return self._value
        elif property.name == "color":
            return self._color
        elif property.name == "label":
            return self._label
        elif property.name == "highlighted":
            return self._highlighted
        elif property.name == "corner-radius":
            return self._corner_radius
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def do_set_property(self, property, value):
        if property.name == "visible":
            self._show = value
        elif property.name == "antialias":
            self._antialias = value
        elif property.name == "value":
            self._value = value
        elif property.name == "color":
            self._color = value
        elif property.name == "label":
            self._label = value
        elif property.name == "highlighted":
            self._highlighted = value
        elif property.name == "corner-radius":
            self._corner_radius = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def _do_draw(self, context, rect, n, i, mode, max_value, bar_padding, value_label_size, label_size, draw_labels):
        if not rect or not max_value:
          return

        if mode == MODE_VERTICAL:
            self._do_draw_single_vertical(context, rect, n, i, mode, max_value, bar_padding, value_label_size, label_size, draw_labels)
        elif mode == MODE_HORIZONTAL:
            self._do_draw_single_horizontal(context, rect, n, i, mode, max_value, bar_padding, value_label_size, label_size, draw_labels)

    def _do_draw_single_vertical(self, context,  rect, n, i, mode, max_value, bar_padding, value_label_size, label_size, draw_labels):
        bar_width = (rect.width - (n - 1) * bar_padding) / n
        bar_height = (rect.height - value_label_size - label_size) * self._value / max_value
        bar_x = rect.x + i * (bar_width + bar_padding)
        bar_y = rect.y + rect.height - bar_height - label_size
        context.set_source_rgb(*color_gdk_to_cairo(self._color))
        draw_rounded_rectangle(context, bar_x, bar_y, bar_width, bar_height, self._corner_radius)
        context.fill()

        if self._highlighted:
            context.set_source_rgba(1, 1, 1, 0.1)
            draw_rounded_rectangle(context, bar_x, bar_y, bar_width, bar_height, self._corner_radius)
            context.fill()

        if draw_labels:
            #draw the value label
            self._value_label_object.set_text(str(self._value))
            self._value_label_object.set_color(self._color)
            self._value_label_object.set_max_width(bar_width)
            self._value_label_object.set_position((bar_x + bar_width / 2, bar_y - 3))
            self._value_label_object.set_anchor(label.ANCHOR_BOTTOM_CENTER)
            self._value_label_object.draw(context, rect)
            context.fill()

            #draw label
            self._label_object.set_text(self._label)
            self._label_object.set_color(self._color)
            self._label_object.set_max_width(bar_width)
            self._label_object.set_position((bar_x + bar_width / 2, bar_y + bar_height + 3))
            self._label_object.set_anchor(label.ANCHOR_TOP_CENTER)
            self._label_object.draw(context, rect)
            context.fill()

        chart.add_sensitive_area(chart.AREA_RECTANGLE, (bar_x, bar_y, bar_width, bar_height), self)

    def _do_draw_single_horizontal(self, context,  rect, n, i, mode, max_value, bar_padding, value_label_size, label_size, draw_labels):
        if max_value == 0:
          return

        bar_width = (rect.width - value_label_size - label_size) * self._value / max_value
        bar_height = (rect.height - (n - 1) * bar_padding) / n
        bar_x = rect.x + label_size
        bar_y = rect.y + i * (bar_height + bar_padding)
        context.set_source_rgb(*color_gdk_to_cairo(self._color))
        draw_rounded_rectangle(context, bar_x, bar_y, bar_width, bar_height, self._corner_radius)
        context.fill()

        if self._highlighted:
            context.set_source_rgba(1, 1, 1, 0.1)
            draw_rounded_rectangle(context, bar_x, bar_y, bar_width, bar_height, self._corner_radius)
            context.fill()

        if draw_labels:
            #draw the value label
            self._value_label_object.set_text(str(self._value))
            self._value_label_object.set_color(self._color)
            self._value_label_object.set_position((bar_x + bar_width + 3, bar_y + bar_height / 2))
            self._value_label_object.set_anchor(label.ANCHOR_LEFT_CENTER)
            self._value_label_object.draw(context, rect)
            context.fill()

            #draw label
            self._label_object.set_text(self._label)
            self._label_object.set_color(self._color)
            self._label_object.set_max_width(0.25 * rect.width)
            self._label_object.set_position((bar_x - 3, bar_y + bar_height / 2))
            self._label_object.set_anchor(label.ANCHOR_RIGHT_CENTER)
            self._label_object.draw(context, rect)
            context.fill()

        chart.add_sensitive_area(chart.AREA_RECTANGLE, (bar_x, bar_y, bar_width, bar_height), self)

    def get_value_label_size(self, context, rect, mode, n, bar_padding):
        if mode == MODE_VERTICAL:
            bar_width = (rect.width - (n - 1) * bar_padding) / n
            self._value_label_object.set_max_width(bar_width)
            self._value_label_object.set_text(str(self._value))
            return self._value_label_object.get_calculated_dimensions(context, rect)[1]
        elif mode == MODE_HORIZONTAL:
            self._value_label_object.set_wrap(False)
            self._value_label_object.set_fixed(True)
            self._value_label_object.set_text(str(self._value))
            return self._value_label_object.get_calculated_dimensions(context, rect)[0]

    def get_label_size(self, context, rect, mode, n, bar_padding):
        if mode == MODE_VERTICAL:
            bar_width = (rect.width - (n - 1) * bar_padding) / n
            self._label_object.set_max_width(bar_width)
            self._label_object.set_text(self._label)
            return self._label_object.get_calculated_dimensions(context, rect)[1]
        elif mode == MODE_HORIZONTAL:
            self._label_object.set_max_width(0.25 * rect.width)
            self._label_object.set_text(self._label)
            return self._label_object.get_calculated_dimensions(context, rect)[0]

    def set_corner_radius(self, radius):
        """
        Set the radius of the bar's corners in px (default: 0).

        @param radius: radius of the corners
        @type radius: int in [0, 100].
        """
        self.set_property("corner-radius", radius)
        self.emit("appearance_changed")

    def get_corner_radius(self):
        """
        Returns the current radius of the bar's corners in px.

        @return: int in [0, 100]
        """
        return self.get_property("corner-radius")


class Grid(ChartObject):
    """
    This class represents the grid on BarChart and MultiBarChart
    widgets.

    Properties
    ==========
    bar_chart.Grid inherits properties from ChartObject.
    Additional properties:
     - line-style (the style of the grid lines, type: a line style
      constant)
     - color (the color of the grid lines, type: gtk.gdk.Color)
     - show-values (sets whether values should be shown at the grid
      lines, type: boolean)
     - padding (the grid's padding in px, type: int in [0, 100]).

    Signals
    =======
    The Grid class inherits signal from chart_object.ChartObject.
    """

    __gproperties__ = {"show-values": (gobject.TYPE_BOOLEAN, "show values",
                                        "Set whether to show grid values.",
                                        True, gobject.PARAM_READWRITE),
                        "color": (gobject.TYPE_PYOBJECT, "color",
                                    "The color of the grid lines.",
                                    gobject.PARAM_READWRITE),
                        "line-style": (gobject.TYPE_INT, "line style",
                                        "The grid's line style", 0, 3, 0,
                                        gobject.PARAM_READWRITE),
                        "padding": (gobject.TYPE_INT, "padding",
                                    "The grid's padding", 0, 100, 6,
                                    gobject.PARAM_READWRITE)}

    def __init__(self):
        ChartObject.__init__(self)
        #private properties:
        self._show_values = True
        self._color = gtk.gdk.color_parse("#dedede")
        self._line_style = pygtk_chart.LINE_STYLE_SOLID
        self._padding = 6

    def do_get_property(self, property):
        if property.name == "visible":
            return self._show
        elif property.name == "antialias":
            return self._antialias
        elif property.name == "show-values":
            return self._show_values
        elif property.name == "color":
            return self._color
        elif property.name == "line-style":
            return self._line_style
        elif property.name == "padding":
            return self._padding
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def do_set_property(self, property, value):
        if property.name == "visible":
            self._show = value
        elif property.name == "antialias":
            self._antialias = value
        elif property.name == "show-values":
            self._show_values = value
        elif property.name == "color":
            self._color = value
        elif property.name == "line-style":
            self._line_style = value
        elif property.name == "padding":
            self._padding = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def _do_draw(self, context, rect, mode, maximum_value, value_label_size, label_size):
        if maximum_value == 0:
          return
        exp = int(math.log10(maximum_value))
        if exp:
          n = maximum_value / 10 ** exp
        else:
          n = maximum_value / 10
        context.set_antialias(cairo.ANTIALIAS_NONE)
        set_context_line_style(context, self._line_style)
        labels = []
        if mode == MODE_VERTICAL:
            delta = (rect.height - value_label_size - label_size) / n
            if self._show_values:
                max_label_size = 0
                for i in range(0, int(n + 1)):
                    y = rect.y + rect.height - i * delta - label_size
                    value = maximum_value * float(i) / n
                    value_label = label.Label((rect.x, y), str(value))
                    max_label_size = max(max_label_size, value_label.get_calculated_dimensions(context, rect)[0])
                    labels.append(value_label)
                max_label_size += 3
                rect = gtk.gdk.Rectangle(int(rect.x + max_label_size), rect.y, int(rect.width - max_label_size), rect.height)
                for i in range(0, len(labels)):
                    y = rect.y + rect.height - i * delta - label_size
                    value_label = labels[i]
                    value_label.set_position((rect.x - 3, y))
                    value_label.set_anchor(label.ANCHOR_RIGHT_CENTER)
                    value_label.draw(context, rect)
                    context.fill()

        elif mode == MODE_HORIZONTAL:
            delta = (rect.width - value_label_size - label_size) / n

            if self._show_values:
                max_label_size = 0
                for i in range(0, int(n + 1)):
                    x = rect.x + i * delta + label_size
                    value = maximum_value * float(i) / n
                    value_label = label.Label((x, rect.y + rect.height), str(value))
                    max_label_size = max(max_label_size, value_label.get_calculated_dimensions(context, rect)[1])
                    labels.append(value_label)
                max_label_size += 3
                rect = gtk.gdk.Rectangle(rect.x, rect.y, rect.width, int(rect.height - max_label_size))
                for i in range(0, len(labels)):
                    x = rect.x + i * delta + label_size
                    value_label = labels[i]
                    value_label.set_position((x, rect.y + rect.height + 3))
                    value_label.set_anchor(label.ANCHOR_TOP_CENTER)
                    value_label.draw(context, rect)
                    context.fill()

            for i in range(0, int(n + 1)):
                x = rect.x + i * delta + label_size
                context.set_source_rgb(*color_gdk_to_cairo(self._color))
                context.move_to(x, rect.y)
                context.rel_line_to(0, rect.height)
                context.stroke()
            rect = gtk.gdk.Rectangle(rect.x, rect.y + self._padding, rect.width, rect.height - 2 * self._padding)
        return rect

    #set and get methods
    def set_show_values(self, show):
        """
        Set whether values should be shown.

        @type show: boolean.
        """
        self.set_property("show-values", show)
        self.emit("appearance_changed")

    def get_show_values(self):
        """
        Returns True if grid values are shown.

        @return: boolean.
        """
        return self.get_property("show-values")

    def set_color(self, color):
        """
        Set the color of the grid lines.

        @param color: the grid lines' color
        @type color: gtk.gdk.Color.
        """
        self.set_property("color", color)
        self.emit("appearance_changed")

    def get_color(self):
        """
        Returns the current color of the grid lines.

        @return: gtk.gdk.Color.
        """
        return self.get_property("color")

    def set_line_style(self, style):
        """
        Set the style of the grid lines. style has to be one of
         - pygtk_chart.LINE_STYLE_SOLID (default)
         - pygtk_chart.LINE_STYLE_DOTTED
         - pygtk_chart.LINE_STYLE_DASHED
         - pygtk_chart.LINE_STYLE_DASHED_ASYMMETRIC

        @param style: the new line style
        @type style: one of the constants above.
        """
        self.set_property("line-style", style)
        self.emit("appearance_changed")

    def get_line_style(self):
        """
        Returns the current grid's line style.

        @return: a line style constant.
        """
        return self.get_property("line-style")

    def set_padding(self, padding):
        """
        Set the grid's padding.

        @type padding: int in [0, 100].
        """
        self.set_property("padding", padding)
        self.emit("appearance_changed")

    def get_padding(self):
        """
        Returns the grid's padding.

        @return: int in [0, 100].
        """
        return self.get_property("padding")



class BarChart(chart.Chart):
    """
    This is a widget that show a simple BarChart.

    Properties
    ==========
    The BarChart class inherits properties from chart.Chart.
    Additional properites:
     - draw-labels (set wether to draw bar label, type: boolean)
     - enable-mouseover (set whether to show a mouseover effect, type:
      boolean)
     - mode (the mode of the bar chart, type: one of MODE_VERTICAL,
      MODE_HORIZONTAL)
     - bar-padding (the sace between bars in px, type: int in [0, 100]).

    Signals
    =======
    The BarChart class inherits signals from chart.Chart.
    Additional signals:
     - bar-clicked: emitted when a bar on the bar chart was clicked
      callback signature:
      def bar_clicked(chart, bar).

    """

    __gsignals__ = {"bar-clicked": (gobject.SIGNAL_RUN_LAST,
                                    gobject.TYPE_NONE,
                                    (gobject.TYPE_PYOBJECT,))}

    __gproperties__ = {"bar-padding": (gobject.TYPE_INT, "bar padding",
                                        "The distance between two bars.",
                                        0, 100, 16,
                                        gobject.PARAM_READWRITE),
                        "mode": (gobject.TYPE_INT, "mode",
                                "The chart's mode.", 0, 1, 0,
                                gobject.PARAM_READWRITE),
                        "draw-labels": (gobject.TYPE_BOOLEAN,
                                        "draw labels", "Set whether to draw labels on bars.",
                                        True, gobject.PARAM_READWRITE),
                        "enable-mouseover": (gobject.TYPE_BOOLEAN, "enable mouseover",
                                        "Set whether to enable mouseover effect.",
                                        True, gobject.PARAM_READWRITE)}

    def __init__(self):
        super(BarChart, self).__init__()
        #private properties:
        self._bars = []
        self._areas = self._bars
        #gobject properties:
        self._bar_padding = 16
        self._mode = MODE_VERTICAL
        self._draw_labels = True
        self._mouseover = True
        #public attributes:
        self.grid = Grid()
        #connect callbacks:
        self.grid.connect("appearance_changed", self._cb_appearance_changed)

    def do_get_property(self, property):
        if property.name == "padding":
            return self._padding
        elif property.name == "bar-padding":
            return self._bar_padding
        elif property.name == "mode":
            return self._mode
        elif property.name == "draw-labels":
            return self._draw_labels
        elif property.name == "enable-mouseover":
            return self._mouseover
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    def do_set_property(self, property, value):
        if property.name == "padding":
            self._padding = value
        elif property.name == "bar-padding":
            self._bar_padding = value
        elif property.name == "mode":
            self._mode = value
        elif property.name == "draw-labels":
            self._draw_labels = value
        elif property.name == "enable-mouseover":
            self._mouseover = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name

    #drawing methods
    def draw(self, context):
        """
        Draw the widget. This method is called automatically. Don't call it
        yourself. If you want to force a redrawing of the widget, call
        the queue_draw() method.

        @type context: cairo.Context
        @param context: The context to draw on.
        """
        label.begin_drawing()

        rect = self.get_allocation()
        rect = gtk.gdk.Rectangle(0, 0, rect.width, rect.height) #transform rect to context coordinates
        context.set_line_width(1)

        rect = self.draw_basics(context, rect)
        maximum_value = max(bar.get_value() for bar in self._bars)
        #find out the size of the value labels
        value_label_size = 0
        if self._draw_labels:
            for bar in self._bars:
                value_label_size = max(value_label_size, bar.get_value_label_size(context, rect, self._mode, len(self._bars), self._bar_padding))
            value_label_size += 3

        #find out the size of the labels:
        label_size = 0
        if self._draw_labels:
            for bar in self._bars:
                label_size = max(label_size, bar.get_label_size(context, rect, self._mode, len(self._bars), self._bar_padding))
            label_size += 3

        rect = self._do_draw_grid(context, rect, maximum_value, value_label_size, label_size)
        if rect:
          self._do_draw_bars(context, rect, maximum_value, value_label_size, label_size)

          label.finish_drawing()

          if self._mode == MODE_VERTICAL:
              n = len(self._bars)
              minimum_width = rect.x + self._padding + (n - 1) * self._bar_padding + n * 10
              minimum_height = MIN_HEIGHT + self._padding + rect.y
          elif self._mode == MODE_HORIZONTAL:
              n = len(self._bars)
              minimum_width = rect.x + self._bar_padding + MIN_WIDTH
              minimum_height = rect.y + self._padding + (n - 1) * self._bar_padding + n * 10
          self.set_size_request(minimum_width, minimum_height)

    def draw_basics(self, context, rect):
        """
        Draw basic things that every plot has (background, title, ...).

        @type context: cairo.Context
        @param context: The context to draw on.
        @type rect: gtk.gdk.Rectangle
        @param rect: A rectangle representing the charts area.
        """
        self.background.draw(context, rect)
        self.title.draw(context, rect, self._padding)

        #calculate the rectangle that's available for drawing the chart
        title_height = self.title.get_real_dimensions()[1]
        rect_height = int(rect.height - 3 * self._padding - title_height)
        rect_width = int(rect.width - 2 * self._padding)
        rect_x = int(rect.x + self._padding)
        rect_y = int(rect.y + title_height + 2 * self._padding)
        return gtk.gdk.Rectangle(rect_x, rect_y, rect_width, rect_height)

    def _do_draw_grid(self, context, rect, maximum_value, value_label_size, label_size):
        if self.grid.get_visible():
            return self.grid.draw(context, rect, self._mode, maximum_value, value_label_size, label_size)
        else:
            return rect

    def _do_draw_bars(self, context, rect, maximum_value, value_label_size, label_size):
        if self._bars == []:
            return

        #draw the bars
        chart.init_sensitive_areas()
        for i, bar in enumerate(self._bars):
            bar.draw(context, rect, len(self._bars), i, self._mode, maximum_value, self._bar_padding, value_label_size, label_size, self._draw_labels)

    #other methods
    def add_bar(self, bar):
        if bar.get_color() == COLOR_AUTO:
            bar.set_color(COLORS[len(self._bars) % len(COLORS)])
        self._bars.append(bar)
        bar.connect("appearance_changed", self._cb_appearance_changed)

    #callbacks
    def _cb_motion_notify(self, widget, event):
        if not self._mouseover: return
        bars = chart.get_sensitive_areas(event.x, event.y)
        if bars == []: return
        for bar in self._bars:
            bar.set_property("highlighted", bar in bars)
        self.queue_draw()

    def _cb_button_pressed(self, widget, event):
        bars = chart.get_sensitive_areas(event.x, event.y)
        for bar in bars:
            self.emit("bar-clicked", bar)

    #set and get methods
    def set_bar_padding(self, padding):
        """
        Set the space between two bars in px.

        @param padding: space between bars in px
        @type padding: int in [0, 100].
        """
        self.set_property("bar-padding", padding)
        self.queue_draw()

    def get_bar_padding(self):
        """
        Returns the space between bars in px.

        @return: int in [0, 100].
        """
        return self.get_property("bar-padding")

    def set_mode(self, mode):
        """
        Set the mode (vertical or horizontal) of the BarChart. mode has
        to be bar_chart.MODE_VERTICAL (default) or
        bar_chart.MODE_HORIZONTAL.

        @param mode: the new mode of the chart
        @type mode: one of the mode constants above.
        """
        self.set_property("mode", mode)
        self.queue_draw()

    def get_mode(self):
        """
        Returns the current mode of the chart: bar_chart.MODE_VERTICAL
        or bar_chart.MODE_HORIZONTAL.

        @return: a mode constant.
        """
        return self.get_property("mode")

    def set_draw_labels(self, draw):
        """
        Set whether labels should be drawn on bars.

        @type draw: boolean.
        """
        self.set_property("draw-labels", draw)
        self.queue_draw()

    def get_draw_labels(self):
        """
        Returns True if labels are drawn on bars.

        @return: boolean.
        """
        return self.get_property("draw-labels")

    def set_enable_mouseover(self, mouseover):
        """
        Set whether a mouseover effect should be shown when the pointer
        enters a bar.

        @type mouseover: boolean.
        """
        self.set_property("enable-mouseover", mouseover)

    def get_enable_mouseover(self):
        """
        Returns True if the mouseover effect is enabled.

        @return: boolean.
        """
        return self.get_property("enable-mouseover")

