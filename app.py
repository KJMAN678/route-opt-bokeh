from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Column
from bokeh.io import curdoc
from bokeh.events import Tap
from bokeh.models import Button, CustomJS, Slider, Div, Arrow, VeeHead
import optimize
import numpy as np

# ルート最適化用のインスタンス作成
opt = optimize.root_opt()

# クリックした場所の位置を保存するリスト
coordList=[(0, 0)]

TOOLS = "tap"
bound = 10
p = figure(title='スライダーバーで指定した台数の車両でクリックした座標を巡回する',
           tools=TOOLS, height=500, width=700,
           x_range=(-bound, bound), y_range=(-bound, bound),
           sizing_mode="stretch_width"
           )

source = ColumnDataSource(data=dict(x=[], y=[]))   
p.circle(source=source,x='x',y='y', radius=0.2, alpha=0.8)
p.diamond([0], [0], size=30, color="red", alpha=0.8)

# クリックすると 点を追加する
def callback_click(event):
    global coordList
    Coords=(event.x,event.y)
    coordList.append(Coords) 
    source.data = dict(x=[i[0] for i in coordList], y=[i[1] for i in coordList])

p.on_event(Tap, callback_click)

result = ""
### ボタン処理
def callback_button():
    global result
    all_route_result_coodList, route_result_list, distance = opt.route_optimize_result(coordList, slider.value)
        
    for i in range(len(all_route_result_coodList)):
      if len(all_route_result_coodList[i]) == 1:
        continue
      
      p.line(
        np.array(all_route_result_coodList[i])[:, 0],
        np.array(all_route_result_coodList[i])[:, 1],
        legend_label=str(i)
        
      )
      
      for j in range(len(all_route_result_coodList[i])-1):
        
        p.add_layout(
                Arrow(
                    end=VeeHead(line_color="firebrick", line_width=0.1),
                    x_start=all_route_result_coodList[i][j][0],
                    y_start=all_route_result_coodList[i][j][1],
                    x_end=all_route_result_coodList[i][j+1][0],
                    y_end=all_route_result_coodList[i][j+1][1],
                    )
        )
        
        p.add_layout(p.legend[0], 'right')
        
    


# add a button widget andconfigure with the call back
button = Button(label="Press Me")
button.on_click(callback_button)

## スライダー
slider = Slider(start=1, end=10, value=3, step=1, title="車両台数")
slider.js_on_change("value", CustomJS(code="""
    console.log('slider: value=' + this.value, this.toString())
"""))

print(slider.value)

layout=Column(p, slider, button)

# ブラウザに表示するために必要
curdoc().add_root(layout)