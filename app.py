from bokeh.events import Tap
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Column, Button, CustomJS, Slider, Arrow, VeeHead
from bokeh.layouts import row
from bokeh.palettes import d3
from bokeh.plotting import figure
import numpy as np
import optimize
from PIL import Image

# 背景画像の読込
img_path = "static/4564885_m.jpg"
img_file = Image.open(img_path)
img_file = np.array(img_file)
img = np.empty((img_file.shape[0], img_file.shape[1]), dtype=np.uint32)
view = img.view(dtype=np.uint8).reshape((img_file.shape[0], img_file.shape[1], 4))
view[:, :, 0:3] = np.flipud(img_file[:, :, 0:3])#上下反転あり
view[:, :, 3] = 255


opt = optimize.root_opt() # ルート最適化用のインスタンス作成
depo = (880, 700) # 出発点の座標
coord_list=[depo] # クリックした場所の位置を保存するリスト。初期値として出発点の座標を設定。

# 画面構成
plot = figure(
            title='スライダーバーで指定した飛行機の数でクリックした座標を巡回する',
            tools="tap", 
            height=600, 
            width=1000,
            x_range=(0, img_file.shape[1]),
            y_range=(0, img_file.shape[0]),
          )

# 背景画像を表示
plot.image_rgba(
            image=[img],
            x=0, 
            y=0, 
            dw=img_file.shape[1], 
            dh=img_file.shape[0],
            global_alpha=0.3
            )

text_padding = 20.0

source = ColumnDataSource(data=dict(x=[], y=[]))           # 全体で使用する bokeh 用データ
plot.circle(source=source,x='x',y='y', radius=10.0, alpha=0.8) # クリックして作成する巡回先を点として表示
plot.diamond([depo[0]], [depo[1]], size=30, color="red", alpha=1.0)       # 出発点をひし形として表示
plot.text(
          x=[depo[0] + text_padding],
          y=[depo[1] + text_padding], 
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
          x=[event.x + text_padding],
          y=[event.y + text_padding], 
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

## 飛行機の台数を決めるスライダー
slider = Slider(start=1, end=10, value=3, step=1, title="飛行機の数")
slider.js_on_change("value", CustomJS(code="""
    console.log('slider: value=' + this.value, this.toString())
"""))


# スライドバーとボタンを縦に並べる
widgets = Column(slider, button, sizing_mode="fixed", height=250, width=150)

# 全体の構成
layout = Column(row(plot, widgets), sizing_mode='scale_width')

# ブラウザに表示するために必要な処理
curdoc().add_root(layout)