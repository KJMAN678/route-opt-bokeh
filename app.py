from bokeh.events import Tap
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Column, Button, CustomJS, Slider, Arrow, VeeHead
from bokeh.layouts import row
from bokeh.palettes import d3
from bokeh.plotting import figure
import numpy as np
import optimize

opt = optimize.root_opt() # ルート最適化用のインスタンス作成
depo = (0, 0) # 出発点の座標
coord_list=[depo] # クリックした場所の位置を保存するリスト。初期値として出発点の座標を設定。

bound = 10 # 表示するグラフの範囲
plot = figure(
            title='スライダーバーで指定した台数の車両でクリックした座標を巡回する',
            tools="tap", 
            height=600, 
            width=1000,
            x_range=(-bound*2, bound*2), 
            y_range=(-bound, bound),
          )

source = ColumnDataSource(data=dict(x=[], y=[]))           # 全体で使用する bokeh 用データ
plot.circle(source=source,x='x',y='y', radius=0.2, alpha=0.8) # クリックして作成する巡回先を点として表示
plot.diamond([0], [0], size=30, color="red", alpha=0.8)       # 出発点をひし形として表示
plot.text(
          x=[0.5], 
          y=[0.5], 
          text=["出発点"], 
          text_font_size="18px",
          text_baseline="middle", 
          text_align="center"
        )

click_count = 1
# クリックすると点を追加する処理の関数
def callback_click(event):
    
    global ds
    global coord_list
    global click_count
    
    coord=(event.x,event.y)  # クリックした位置の座標をタプルに保存
    coord_list.append(coord) # 座標をリストに保存
    source.data = dict(      # 他の機能で共通して使えるよう座標を souse に保存
              x=[i[0] for i in coord_list], 
              y=[i[1] for i in coord_list]
            )
    plot.text( # クリックした回数をテキスト表示
          x=[event.x+0.5], 
          y=[event.y+0.5], 
          text=[click_count], 
          text_font_size="18px",
          text_baseline="middle", 
          text_align="center"
        )
    click_count += 1         # クリックした回数をカウント

# クリックイベントを反映
plot.on_event(Tap, callback_click)

### ボタン処理の関数
def callback_button():
  
    # 最適化関数を実行して最適ルートの座標を取得
    all_route_result_coodList, route_result_list, distance = opt.route_optimize_result(
                                                              coord_list,  # クリックして決定した座標のリスト
                                                              slider.value # スライダーバーで決定した車両台数
                                                              )
        
    # ルート順及びルートの向きをグラフに表示する処理
    for i in range(len(all_route_result_coodList)):
      
      # 出発点の座標以外を巡回しない場合は処理しない
      if len(all_route_result_coodList[i]) <= 2:
        continue
      
      # 各ルートの軌跡をラインで表示。次の矢印でも軌跡は表示できるが、凡例を作成するために使用。
      plot.line(
        np.array(all_route_result_coodList[i])[:, 0],
        np.array(all_route_result_coodList[i])[:, 1],
        legend_label=str(i),
        color=d3['Category10'][10][i]
      )
      
      # 各ルートの方向を矢印として表示
      for j in range(len(all_route_result_coodList[i])-1):
        
        plot.add_layout(
                Arrow(
                      end=VeeHead(line_color="firebrick", line_width=0.1),
                      x_start=all_route_result_coodList[i][j][0],
                      y_start=all_route_result_coodList[i][j][1],
                      x_end=all_route_result_coodList[i][j+1][0],
                      y_end=all_route_result_coodList[i][j+1][1],
                      line_color=d3['Category10'][10][i],
                    )
        )
        
        plot.add_layout(plot.legend[0], 'right') # 凡例の追加
        
# ボタンウィジェットの実装
button = Button(label="最適化の実行")
button.on_click(callback_button)

## 車両台数を決めるスライダー
slider = Slider(start=1, end=10, value=3, step=1, title="車両台数")
slider.js_on_change("value", CustomJS(code="""
    console.log('slider: value=' + this.value, this.toString())
"""))

# 各機能をWeb画面にレイアウトする
# layout=Column(row(slider, button), plot, sizing_mode='scale_width')

widgets = Column(slider, button, sizing_mode="fixed", height=250, width=150)

layout = Column(row(plot, widgets), sizing_mode='scale_width')

# ブラウザに表示するために必要な処理
curdoc().add_root(layout)