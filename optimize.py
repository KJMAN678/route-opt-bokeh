from scipy.spatial import distance_matrix
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# パラメーター
solution_limit_times = 1000  # 最適化の計算回数制限
solution_limit_seconds = 30  # 最適化の計算秒数制限

class root_opt:
  
    # 最適化用のデータセット作成
    def create_data_model(self, cood_list, vehicle_num):

        data = {}
        data['locations'] = cood_list              # 座標
        data['distance_matrix'] = distance_matrix( # 距離
                            data['locations'], 
                            data['locations']
                            ).tolist()
        data['num_vehicles'] = vehicle_num         # 車両台数
        data['depot'] = 0                          # 出発点のインデックス
        return data

    # ルート順のインデックスを作成する
    def output_route_list(self, data, manager, routing, solution):

        all_route_list = []    # 全車両のルート順を保存するリスト
        max_route_distance = 0 # 距離を保存する変数

        for vehicle_id in range(data['num_vehicles']):

            each_route_list = [] # 1つの車両のルート順を保存するリスト

            index = routing.Start(vehicle_id)
            route_distance = 0
            while not routing.IsEnd(index):

                each_route_list.append(manager.IndexToNode(index)) # 巡回する場所のインデックスをリストに追加
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
                
            each_route_list.append(manager.IndexToNode(index))
            max_route_distance = max(route_distance, max_route_distance)
            all_route_list.append(each_route_list) # 1つの車両のルート順を全体のルート順のリストに保存

        return all_route_list, max_route_distance

    # ルート最適化の実行
    def route_optimize_result(self, cood_list, vehicle_num):

        # データセットの作成
        data = self.create_data_model(cood_list, vehicle_num)

        # ルーティングインデックスマネージャーの作成
        manager = pywrapcp.RoutingIndexManager(
                                len(data['distance_matrix']),
                                data['num_vehicles'], data['depot']
                              )

        # ルーティングモデルの作成
        routing = pywrapcp.RoutingModel(manager)

        # 距離の制約用の関数
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # コストの定義
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # 距離の制約を設定
        dimension_name = 'Distance'
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            3000,  # 最大距離
            True,  # start cumul to zero
            dimension_name
            )
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        # ヒューリスティック解を求めるよう設定
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        
        # 計算制限を設定
        search_parameters.solution_limit = solution_limit_times       # 計算の回数
        search_parameters.time_limit.seconds = solution_limit_seconds # 計算の秒数

        # 最適化の実行
        solution = routing.SolveWithParameters(search_parameters)

        # 最適化の解を取得
        if solution:
          
            route_result_list, distance = self.output_route_list(data, manager, routing, solution)
            
            # ルート順からルート順の座標リストを作成
            all_route_result_cood_list = []

            for i in range(len(route_result_list)):
                each_route_result_cood_list = []

                for j in range(len(route_result_list[i])):
                  each_route_result_cood_list.append(cood_list[route_result_list[i][j]])
                
                all_route_result_cood_list.append(each_route_result_cood_list)
            
        else:
            distance = 0
            route_result_list = []
            all_route_result_cood_list = []

        return all_route_result_cood_list, route_result_list, distance
