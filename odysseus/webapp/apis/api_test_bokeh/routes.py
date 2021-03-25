
from flask import Blueprint, jsonify, request
from bokeh.plotting import Figure
from bokeh.resources import CDN
from bokeh.embed import json_item
from bokeh.layouts import column
from bokeh.models import CustomJS, ColumnDataSource, Slider
from bokeh.sampledata.autompg import autompg
from numpy import cos, linspace
import numpy as np

from bokeh.io import show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, RangeTool
from bokeh.plotting import figure
import json
import pandas as pd
import os
from flask_cors import CORS


api_bokeh = Blueprint('api_bokeh', __name__)
CORS(api_bokeh)

#https://docs.bokeh.org/en/latest/docs/gallery/range_tool.html

@api_bokeh.route('/plot1',methods=['POST','GET'])
def plot1():
    sim_charges_df = pd.read_csv("/Users/brendanpolidori/Desktop/project_repos/inter_webapp.nosync/e3f2s/e3f2s/webapp/apis/api_test_bokeh/sim_booking_requests_test_bre.csv")

    dates = np.array(sim_charges_df["start_time"],dtype=np.datetime64)
    source = ColumnDataSource(data=dict(date=np.array(sim_charges_df["start_time"],dtype=np.datetime64), close=list(sim_charges_df["n_vehicles_available"])))

    p = figure(plot_height=300, plot_width=800, tools="xpan", toolbar_location=None,
            x_axis_type="datetime", x_axis_location="above",
            background_fill_color="#efefef", x_range=(dates[1500], dates[2500]))

    p.line('date', 'close', source=source)
    p.yaxis.axis_label = 'Number Vehicles Available'

    select = figure(title="Drag the middle and edges of the selection box to change the range above",
                    plot_height=130, plot_width=800, y_range=p.y_range,
                    x_axis_type="datetime", y_axis_type=None,
                    tools="", toolbar_location=None, background_fill_color="#efefef")

    range_tool = RangeTool(x_range=p.x_range)
    range_tool.overlay.fill_color = "navy"
    range_tool.overlay.fill_alpha = 0.2

    select.line('date', 'close', source=source)
    select.ygrid.grid_line_color = None
    select.add_tools(range_tool)
    select.toolbar.active_multi = range_tool

    show(column(p, select))
    
    return json.dumps(json_item(p, "myplot"))

@api_bokeh.route('/plot3')
def plot3():
    x = linspace(-6, 6, 100)
    y = cos(x)
    p = figure(width=500, height=500, toolbar_location="below",
                     title="Plot 1")
    p.circle(x, y, size=7, color="firebrick", alpha=0.5)
 
    # following above points: 
    #  + pass plot object 'p' into json_item
    #  + wrap the result in json.dumps and return to frontend
    return json.dumps(json_item(p, "myplot"))





@api_bokeh.route('/plot2', methods=['POST','GET'])
def plot2():
    # copy/pasted from Bokeh 'JavaScript Callbacks' - used as an example
    # https://bokeh.pydata.org/en/latest/docs/user_guide/interaction/callbacks.html

    x = [x*0.005 for x in range(0, 200)]
    y = x

    source = ColumnDataSource(data=dict(x=x, y=y))

    plot = Figure(plot_width=400, plot_height=400)
    plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)

    callback = CustomJS(args=dict(source=source), code="""
        var data = source.data;
        var f = cb_obj.value
        var x = data['x']
        var y = data['y']
        for (var i = 0; i < x.length; i++) {
            y[i] = Math.pow(x[i], f)
        }
        source.change.emit();
    """)

    slider = Slider(start=0.1, end=4, value=1, step=.1, title="power")
    slider.js_on_change('value', callback)
    layout = column(slider, plot)
    print("thiss is p")

    return json.dumps(json_item(layout, "myplot"))







@api_bokeh.route('/test', methods=['POST','GET'])
def test():
    data = [
        {
            "userId":1,
            "id":1,
            "title":"tizio",
            "body":"daaans",

        },
        {
            "userId":2,
            "id":2,
            "title":"caio",
            "body":"yoooo",
        }
    ]
    return jsonify(data)

@api_bokeh.route('/test_post', methods=['POST'])
def test_post():
    data = request.get_json()
    print("The data received is: ",data)
    return jsonify({"hi":1})