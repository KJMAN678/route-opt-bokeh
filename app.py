from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Column
from bokeh.io import curdoc
from bokeh.events import DoubleTap, MouseEnter, Press, Tap

# クリックした場所の位置を保存するリスト
coordList=[]

TOOLS = "tap"
bound = 10
p = figure(title='Double click to leave a dot.',
           tools=TOOLS,height=700,
           x_range=(-bound, bound), y_range=(-bound, bound),
           sizing_mode="stretch_width"
           )

source = ColumnDataSource(data=dict(x=[], y=[]))   
p.circle(source=source,x='x',y='y', radius=0.3, alpha=0.5)

# クリックすると 点を追加する
def callback(event):
    Coords=(event.x,event.y)
    coordList.append(Coords) 
    source.data = dict(x=[i[0] for i in coordList], y=[i[1] for i in coordList])        
p.on_event(Tap, callback)

layout=Column(p)

# ブラウザに表示するために必要
curdoc().add_root(layout)