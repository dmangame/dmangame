#       Copyright 2009 Sven Festersen <sven@sven-festersen.de>
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
Contains the MultiBarChart widget.

Author: Sven Festersen (sven@sven-festersen.de)
"""
__docformat__ = "epytext"
import cairo
import gtk
import gobject
import os
import math

import pygtk_chart
from pygtk_chart.basics import *
from pygtk_chart import bar_chart
from pygtk_chart.chart_object import ChartObject
from pygtk_chart import chart
from pygtk_chart import label

MODE_VERTICAL = 0
MODE_HORIZONTAL = 1

COLOR_AUTO = 0
COLORS = gdk_color_list_from_file(os.sep.join([os.path.dirname(__file__), "data", "tango.color"]))


class Bar(bar_chart.Bar):
    """
    This is a special version of the bar_chart.Bar class that draws the
    bars on a MultiBarChart widget.
    
    Properties
    ==========
    This class inherits properties from bar_chart.Bar.
    
    Signals
    =======
    This class inherits signals from bar_chart.Bar. 
    """
    
    def __init__(self, name, value, title=""):
        bar_chart.Bar.__init__(self, name, value, title)
    
    #drawing methods
    def _do_draw(self, context, rect, group, bar_count, n, i, m, j, mode, group_padding, bar_padding, maximum_value, group_end, value_label_size, label_size, label_rotation, draw_labels):
        if mode == MODE_VERTICAL:
            return self._do_draw_multi_vertical(context, rect, group, bar_count, n, i, m, j, mode, group_padding, bar_padding, maximum_value, group_end, value_label_size, label_size, label_rotation, draw_labels)
        elif mode == MODE_HORIZONTAL:
            return self._do_draw_multi_horizontal(context, rect, group, bar_count, n, i, m, j, mode, group_padding, bar_padding, maximum_value, group_end, value_label_size, label_size, label_rotation, draw_labels)
            
    def _do_draw_multi_vertical(self, context, rect, group, bar_count, n, i, m, j, mode, group_padding, bar_padding, maximum_value, group_end, value_label_size, label_size, label_rotation, draw_labels):
        bar_width = (rect.width - (bar_count - n) * bar_padding - (n - 1) * group_padding) / bar_count
        bar_height = (rect.height - value_label_size - label_size) * self._value / maximum_value
        bar_x = group_end + j * (bar_width + bar_padding)
        bar_y = rect.y + rect.height - bar_height - label_size
        context.set_source_rgb(*color_gdk_to_cairo(self._color))
        bar_chart.draw_rounded_rectangle(context, bar_x, bar_y, bar_width, bar_height, self._corner_radius)
        context.fill()
        
        chart.add_sensitive_area(chart.AREA_RECTANGLE, (bar_x, bar_y, bar_width, bar_height), (group, self))
        
        if self._highlighted:
            context.set_source_rgba(1, 1, 1, 0.1)
            bar_chart.draw_rounded_rectangle(context, bar_x, bar_y, bar_width, bar_height, self._corner_radius)
            context.fill()
            
        if draw_labels:
            #draw the value label
            self._value_label_object.set_max_width(bar_width)
            self._value_label_object.set_text(str(self._value))
            self._value_label_object.set_color(self._color)
            self._value_label_object.set_position((bar_x + bar_width / 2, bar_y - 3))
            self._value_label_object.set_anchor(label.ANCHOR_BOTTOM_CENTER)
            self._value_label_object.draw(context, rect)
            context.fill()
            
            #draw label
            self._label_object.set_rotation(label_rotation)
            self._label_object.set_wrap(False)
            self._label_object.set_color(self._color)
            self._label_object.set_fixed(True)
            self._label_object.set_max_width(3 * bar_width)
            self._label_object.set_text(self._label)
            self._label_object.set_position((bar_x + bar_width / 2 + 5, bar_y + bar_height + 8))
            self._label_object.set_anchor(label.ANCHOR_TOP_RIGHT)
            self._label_object.draw(context, rect)
            context.fill()
        
        return bar_x + bar_width
            
    def _do_draw_multi_horizontal(self, context, rect, group, bar_count, n, i, m, j, mode, group_padding, bar_padding, maximum_value, group_end, value_label_size, label_size, label_rotation, draw_labels):
        bar_height = (rect.height - (bar_count - n) * bar_padding - (n - 1) * group_padding) / bar_count
        bar_width = (rect.width - value_label_size - label_size) * self._value / maximum_value
        bar_x = rect.x + label_size
        bar_y = group_end + j * (bar_height + bar_padding)
        context.set_source_rgb(*color_gdk_to_cairo(self._color))
        bar_chart.draw_rounded_rectangle(context, bar_x, bar_y, bar_width, bar_height, self._corner_radius)
        context.fill()
        
        chart.add_sensitive_area(chart.AREA_RECTANGLE, (bar_x, bar_y, bar_width, bar_height), (group, self))
        
        if self._highlighted:
            context.set_source_rgba(1, 1, 1, 0.1)
            bar_chart.draw_rounded_rectangle(context, bar_x, bar_y, bar_width, bar_height, self._corner_radius)
            context.fill()
            
        if draw_labels:
            #draw the value label
            self._value_label_object.set_text(str(self._value))
            self._value_label_object.set_wrap(False)
            self._value_label_object.set_color(self._color)
            self._value_label_object.set_position((bar_x + bar_width + 3, bar_y + bar_height / 2))
            self._value_label_object.set_anchor(label.ANCHOR_LEFT_CENTER)
            self._value_label_object.draw(context, rect)
            context.fill()
            
            #draw label
            self._label_object.set_rotation(0)
            self._label_object.set_wrap(False)
            self._label_object.set_color(self._color)
            self._label_object.set_fixed(True)
            self._label_object.set_max_width(0.25 * rect.width)
            self._label_object.set_text(self._label)
            self._label_object.set_position((bar_x - 3, bar_y + bar_height / 2))
            self._label_object.set_anchor(label.ANCHOR_RIGHT_CENTER)
            self._label_object.draw(context, rect)
            context.fill()
        
        return bar_y + bar_height
        
    def get_value_label_size(self, context, rect, mode, bar_count, n, group_padding, bar_padding):
        if mode == MODE_VERTICAL:
            bar_width = (rect.width - (bar_count - n) * bar_padding - (n - 1) * group_padding) / bar_count
            self._value_label_object.set_max_width(bar_width)
            self._value_label_object.set_text(str(self._value))
            return self._value_label_object.get_calculated_dimensions(context, rect)[1]  
        elif mode == MODE_HORIZONTAL:
            self._value_label_object.set_wrap(False)
            self._value_label_object.set_fixed(True)
            self._value_label_object.set_text(str(self._value))
            return self._value_label_object.get_calculated_dimensions(context, rect)[0]
            
    def get_label_size(self, context, rect, mode, bar_count, n, group_padding, bar_padding, label_rotation):
        if mode == MODE_VERTICAL:
            bar_width = (rect.width - (bar_count - n) * bar_padding - (n - 1) * group_padding) / bar_count
            self._label_object.set_rotation(label_rotation)
            self._label_object.set_wrap(False)
            self._label_object.set_fixed(True)
            self._label_object.set_max_width(3 * bar_width)
            self._label_object.set_text(self._label)
            return self._label_object.get_calculated_dimensions(context, rect)[1]   
        elif mode == MODE_HORIZONTAL:
            self._label_object.set_max_width(0.25 * rect.width)
            self._label_object.set_text(self._label)
            return self._label_object.get_calculated_dimensions(context, rect)[0]
        
        
        
class BarGroup(ChartObject):
    """
    This class represents a group of bars on the MultiBarChart widget.
    
    Properties
    ==========
    This class has the following properties:
     - name (a unique identifier for the group, type: string)
     - title (a title for the group, type: string)
     - bar-padding (the space between two bars of the group in px,
       type: int in [0, 100])
     - bars (a list of the bars in the group, read only)
     - maximum-value (the maximum value of the bars in the group, read
      only)
     - bar-count (the number of bars in the group, read only).
    
    Signals
    =======
    The BarGroup class inherits signals from chart_object.ChartObject.
    """
    
    __gproperties__ = {"name": (gobject.TYPE_STRING, "group name",
                                "A unique identifier for this group.",
                                "", gobject.PARAM_READABLE),
                        "title": (gobject.TYPE_STRING, "group title",
                                    "The group's title.", "",
                                    gobject.PARAM_READWRITE),
                        "bar-padding": (gobject.TYPE_INT, "bar padding",
                                        "The space between bars in this group.",
                                        0, 100, 2, gobject.PARAM_READWRITE),
                        "bars": (gobject.TYPE_PYOBJECT, "bars in the group",
                                "A list of bars in this group.",
                                gobject.PARAM_READABLE),
                        "maximum-value": (gobject.TYPE_FLOAT, "max value",
                                        "The maximum value of the bars in this group.",
                                        0, 9999999, 0, gobject.PARAM_READABLE),
                        "bar-count": (gobject.TYPE_INT, "bar count",
                                        "The number of bars in this group.",
                                        0, 100, 0, gobject.PARAM_READWRITE)}
    
    def __init__(self, name, title=""):
        ChartObject.__init__(self)
        #private properties:
        self._group_label_object = label.Label((0, 0), title)
        #gobject properties:
        self._bars = []
        self._name = name
        self._title = title
        self._bar_padding = 2
    
    #gobject set_* and get_* methods
    def do_get_property(self, property):
        if property.name == "visible":
            return self._show
        elif property.name == "antialias":
            return self._antialias
        elif property.name == "name":
            return self._name
        elif property.name == "title":
            return self._title
        elif property.name == "bar-padding":
            return self._bar_padding
        elif property.name == "bars":
            return self._bars
        elif property.name == "maximum-value":
            return max(bar.get_value() for bar in self._bars)
        elif property.name == "bar-count":
            return len(self._bars)
        else:
            raise AttributeError, "Property %s does not exist." % property.name
            
    def do_set_property(self, property, value):
        if property.name == "visible":
            self._show = value
        elif property.name == "antialias":
            self._antialias = value
        elif property.name == "name":
            self._name = value
        elif property.name == "title":
            self._title = value
        elif property.name == "bar-padding":
            self._bar_padding = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name
            
    def get_bar_count(self):
        """
        Returns the number of bars in this group.
        
        @return: int in [0, 100].
        """
        return self.get_property("bar-count")
        
    def get_maximum_value(self):
        """
        Returns the maximum value of the bars in this group.
        
        @return: float.
        """
        return self.get_property("maximum-value")
        
    def get_bars(self):
        """
        Returns a list of the bars in this group.
        
        @return: list of multi_bar_chart.Bar.
        """
        return self.get_property("bars")
        
    def get_name(self):
        """
        Returns the name (a unique identifier) of this group.
        
        @return: string.
        """
        return self.get_property("name")
        
    def set_title(self, title):
        """
        Set the title of the group.
        
        @param title: the new title
        @type title: string.
        """
        self.set_property("title", title)
        self.emit("appearance_changed")
        
    def get_title(self):
        """
        Returns the title of the group.
        
        @return: string.
        """
        return self.get_property("title")
        
    def get_label(self):
        """
        Alias for get_title.
        
        @return: string.
        """
        return self.get_title()
        
    def set_bar_padding(self, padding):
        """
        Set the distance between two bars in this group (in px).
        
        @param padding: the padding in px
        @type padding: int in [0, 100].
        """
        self.set_property("bar-padding", padding)
        self.emit("appearance_changed")
        
    def get_bar_padding(self):
        """
        Returns the distance of two bars in the group (in px).
        
        @return: int in [0, 100].
        """
        return self.get_property("bar-padding")
        
    #drawing methods
    def _do_draw(self, context, rect, bar_count, n, i, mode, group_padding, maximum_value, group_end, value_label_size, label_size, label_rotation, draw_labels, rotate_label_horizontal):
        end = group_end
        for j, bar in enumerate(self._bars):
            end = bar.draw(context, rect, self, bar_count, n, i, len(self._bars), j, mode, group_padding, self._bar_padding, maximum_value, group_end, value_label_size, label_size, label_rotation, draw_labels)
        
        if draw_labels and mode == MODE_VERTICAL:
            context.set_source_rgb(0, 0, 0)
            group_width = end - group_end
            self._group_label_object.set_text(self._title)
            self._group_label_object.set_fixed(True)
            self._group_label_object.set_max_width(group_width)
            self._group_label_object.set_position((group_end + group_width / 2, rect.y + rect.height))
            self._group_label_object.set_anchor(label.ANCHOR_BOTTOM_CENTER)
            self._group_label_object.draw(context, rect)
            context.fill()
        elif draw_labels and mode == MODE_HORIZONTAL:
            context.set_source_rgb(0, 0, 0)
            group_height = end - group_end
            if rotate_label_horizontal:
                self._group_label_object.set_rotation(90)
                offset = self.get_group_label_size(context, rect, mode, rotate_label_horizontal) #fixes postioning bug
            else:
                self._group_label_object.set_rotation(0)
                offset = 0
            self._group_label_object.set_text(self._title)
            self._group_label_object.set_wrap(False)
            self._group_label_object.set_fixed(True)
            self._group_label_object.set_position((rect.x + offset, group_end + group_height / 2))
            self._group_label_object.set_anchor(label.ANCHOR_LEFT_CENTER)
            self._group_label_object.draw(context, rect)
            context.fill()
        
        return end + group_padding
    
    #other methods        
    def add_bar(self, bar):
        """
        Add a bar to the group.
        
        @param bar: the bar to add
        @type bar: multi_bar_chart.Bar.
        """
        if bar.get_color() == COLOR_AUTO:
            bar.set_color(COLORS[len(self._bars) % len(COLORS)])
        self._bars.append(bar)
        self.emit("appearance_changed")
        
    def get_value_label_size(self, context, rect, mode, bar_count, n, group_padding, bar_padding):
        value_label_size = 0
        for bar in self._bars:
            value_label_size = max(value_label_size, bar.get_value_label_size(context, rect, mode, bar_count, n, group_padding, bar_padding))
        return value_label_size
        
    def get_label_size(self, context, rect, mode, bar_count, n, group_padding, bar_padding, label_rotation):
        label_size = 0
        for bar in self._bars:
            label_size = max(label_size, bar.get_label_size(context, rect, mode, bar_count, n, group_padding, bar_padding, label_rotation))
        return label_size
        
    def get_group_label_size(self, context, rect, mode, rotate_label_horizontal):
        self._group_label_object.set_text(self._title)
        if mode == MODE_VERTICAL:
            return self._group_label_object.get_calculated_dimensions(context, rect)[1]
        elif mode == MODE_HORIZONTAL:
            if rotate_label_horizontal:
                self._group_label_object.set_rotation(90)
            else:
                self._group_label_object.set_rotation(0)
            self._group_label_object.set_wrap(False)
            return self._group_label_object.get_calculated_dimensions(context, rect)[0]
        
        
class MultiBarChart(bar_chart.BarChart):
    """
    The MultiBarChart widget displays groups of bars.
    Usage: create multi_bar_chart.BarGroups and
    add multi_bar_chart.Bars. The add the bar groups to MultiBarChart.
    
    Properties
    ==========
    The MultiBarChart class inherits properties from bar_chart.BarChart
    (except bar-padding). Additional properties:
     - group-padding (the space between two bar groups in px, type: int
      in [0, 100], default: 16)
     - label-rotation (the angle (in degrees) that should be used to
      rotate bar labels in vertical mode, type: int in [0, 360],
      default: 300)
     - rotate-group-labels (sets whether group labels should be roteated
      by 90 degrees in horizontal mode, type: boolean, default: False).
      
    Signals
    =======
    The MultiBarChart class inherits the signal 'bar-clicked' from
    bar_chart.BarChart. Additional signals:
     - group-clicked: emitted when a bar is clicked, callback signature:
      def group_clicked(chart, group, bar).
    """
    
    __gsignals__ = {"group-clicked": (gobject.SIGNAL_RUN_LAST, 
                                    gobject.TYPE_NONE, 
                                    (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))}
                                    
    __gproperties__ = {"group-padding": (gobject.TYPE_INT, "group padding",
                                        "The space between two bar groups.",
                                        0, 100, 16, gobject.PARAM_READWRITE),
                        "label-rotation": (gobject.TYPE_INT, "label rotation",
                                            "The angle that should bar labels be rotated by in vertical mode.",
                                            0, 360, 300, gobject.PARAM_READWRITE),
                        "rotate-group-labels": (gobject.TYPE_BOOLEAN,
                                                "rotate group label",
                                                "Sets whether the group label should be rotated by 90 degrees in horizontal mode.",
                                                False, gobject.PARAM_READWRITE),
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
        bar_chart.BarChart.__init__(self)
        #private properties:
        self._groups = []
        #gobject properties:
        self._group_padding = 16
        self._label_rotation = 300
        self._rotate_group_label_in_horizontal_mode = False
        
    #gobject set_* and get_* methods
    def do_get_property(self, property):
        if property.name == "group-padding":
            return self._group_padding
        elif property.name == "label-rotation":
            return self._label_rotation
        elif property.name == "rotate-group-labels":
            return self._rotate_group_label_in_horizontal_mode
        elif property.name == "mode":
            return self._mode
        elif property.name == "draw-labels":
            return self._draw_labels
        elif property.name == "enable-mouseover":
            return self._mouseover
        else:
            raise AttributeError, "Property %s does not exist." % property.name
            
    def do_set_property(self, property, value):
        if property.name == "group-padding":
            self._group_padding = value
        elif property.name == "label-rotation":
            self._label_rotation = value
        elif property.name == "rotate-group-labels":
            self._rotate_group_label_in_horizontal_mode = value
        elif property.name == "mode":
            self._mode = value
        elif property.name == "draw-labels":
            self._draw_labels = value
        elif property.name == "enable-mouseover":
            self._mouseover = value
        else:
            raise AttributeError, "Property %s does not exist." % property.name
            
    def set_group_padding(self, padding):
        """
        Set the amount of free space between bar groups (in px,
        default: 16).
        
        @param padding: the padding
        @type padding: int in [0, 100].
        """
        self.set_property("group-padding", padding)
        self.queue_draw()
        
    def get_group_padding(self):
        """
        Returns the amount of free space between two bar groups (in px).
        
        @return: int in [0, 100].
        """
        return self.get_property("group-padding")
        
    def set_label_rotation(self, angle):
        """
        Set the abgle (in degrees) that should be used to rotate the
        bar labels in vertical mode (defualt: 300 degrees).
        
        @type angle: int in [0, 360].
        """
        self.set_property("label-rotation", angle)
        self.queue_draw()
        
    def get_label_rotation(self):
        """
        Returns the angle by which bar labels are rotated in vertical
        mode.
        
        @return: int in [0, 350].
        """
        return self.get_property("label-rotation")
        
    def set_rotate_group_labels(self, rotate):
        """
        Set wether the groups' labels should be rotated by 90 degrees in
        horizontal mode (default: False).
        
        @type rotate: boolean.
        """
        self.set_property("rotate-group-labels", rotate)
        self.queue_draw()
        
    def get_rotate_group_labels(self):
        """
        Returns True if group labels should be rotated by 90 degrees
        in horizontal mode.
        
        @return: boolean.
        """
        return self.get_property("rotate-group-labels")
        
    #callbacks
    def _cb_motion_notify(self, widget, event):
        if not self._mouseover: return
        active = chart.get_sensitive_areas(event.x, event.y)
        if active == []: return
        for group in self._groups:
            for bar in group.get_bars():
                bar.set_highlighted((group, bar) in active)
        self.queue_draw()
        
    def _cb_button_pressed(self, widget, event):
        active = chart.get_sensitive_areas(event.x, event.y)
        for group, bar in active:
            self.emit("group-clicked", group, bar)
            self.emit("bar-clicked", bar)
        
    #drawing methods
    def _do_draw_groups(self, context, rect, maximum_value, value_label_size, label_size, bar_count):
        if self._groups == []: return
        
        if self._mode == MODE_VERTICAL:
            group_end = rect.x
        else:
            group_end = rect.y
        
        for i, group in enumerate(self._groups):
            group_end = group.draw(context, rect, bar_count, len(self._groups), i, self._mode, self._group_padding, maximum_value, group_end, value_label_size, label_size, self._label_rotation, self._draw_labels, self._rotate_group_label_in_horizontal_mode)
        
    def draw(self, context):
        """
        Draw the widget. This method is called automatically. Don't call it
        yourself. If you want to force a redrawing of the widget, call
        the queue_draw() method.
        
        @type context: cairo.Context
        @param context: The context to draw on.
        """
        label.begin_drawing()
        chart.init_sensitive_areas()
        
        rect = self.get_allocation()
        rect = gtk.gdk.Rectangle(0, 0, rect.width, rect.height) #transform rect to context coordinates
        context.set_line_width(1)
                                    
        rect = self.draw_basics(context, rect)
        
        maximum_value = max(group.get_maximum_value() for group in self._groups)
        bar_count = 0
        for group in self._groups: bar_count += group.get_bar_count()
        
        value_label_size = 0
        if self._draw_labels:
            for group in self._groups:
                value_label_size = max(value_label_size, group.get_value_label_size(context, rect, self._mode, bar_count, len(self._groups), self._group_padding, self._bar_padding))
        
        label_size = 0
        if self._draw_labels:
            for group in self._groups:
                label_size = max(label_size, group.get_label_size(context, rect, self._mode, bar_count, len(self._groups), self._group_padding, self._bar_padding, self._label_rotation))
            label_size += 10
            label_size += group.get_group_label_size(context, rect, self._mode, self._rotate_group_label_in_horizontal_mode)
        
        rect = self._do_draw_grid(context, rect, maximum_value, value_label_size, label_size)
        self._do_draw_groups(context, rect, maximum_value, value_label_size, label_size, bar_count)
        
        label.finish_drawing()
        n = len(self._groups)
        if self._mode == MODE_VERTICAL:
            minimum_width = rect.x + self._padding + bar_count * 10 + n * self._group_padding
            minimum_height = rect.y + self._padding + 200
        elif self._mode == MODE_HORIZONTAL:
            minimum_width = rect.x + self._padding + 200
            minimum_height = rect.y + self._padding + bar_count * 10 + n * self._group_padding
        self.set_size_request(minimum_width, minimum_height)
    
    #other methods        
    def add_group(self, group):
        """
        Add a BarGroup to the chart.
        
        @type group: multi_bar_chart.BarGroup.
        """
        self._groups.append(group)
        self.queue_draw()
        
    def add_bar(self, bar):
        """
        Alias for add_group.
        This method is deprecated. Use add_group instead.
        """
        print "MultiBarChart.add_bar is deprecated. Use add_group instead."
        self.add_group(bar)
