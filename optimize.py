from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from scipy.spatial import distance_matrix

solution_limit_times = 1000     # 計算回数制限
solution_limit_seconds = 30 # 計算秒数制限

class root_opt:

    def create_data_model(self, coodList, vehicle_num):

        data = {}
        data['locations'] = coodList
        data['distance_matrix'] = distance_matrix(
                            data['locations'], 
                            data['locations']
                            ).tolist()
        data['num_vehicles'] = vehicle_num
        data['depot'] = 0
        return data

    def output_route_list(self, data, manager, routing, solution):

        all_route_list = []

        max_route_distance = 0

        for vehicle_id in range(data['num_vehicles']):

            each_route_list = []

            index = routing.Start(vehicle_id)
            plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
            route_distance = 0
            while not routing.IsEnd(index):

                each_route_list.append(manager.IndexToNode(index))

                # plan_output += ' {} -> '.format(manager.IndexToNode(index))
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
            # plan_output += '{}\n'.format(manager.IndexToNode(index))
            each_route_list.append(manager.IndexToNode(index))
            # plan_output += 'Distance of the route: {}m\n'.format(route_distance)
            max_route_distance = max(route_distance, max_route_distance)
            all_route_list.append(each_route_list)

        return all_route_list, max_route_distance

    def route_optimize_result(self, coodList, vehicle_num):

        # Instantiate the data problem.
        data = self.create_data_model(coodList, vehicle_num)

        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                            data['num_vehicles'], data['depot'])

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)

        # Create and register a transit callback.
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Distance constraint.
        dimension_name = 'Distance'
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            3000,  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name)
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        
        # 計算制限
        search_parameters.solution_limit = solution_limit_times       # 計算回数
        search_parameters.time_limit.seconds = solution_limit_seconds # 計算秒数

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)

        # Print solution on console.
        if solution:
            route_result_list, distance = self.output_route_list(data, manager, routing, solution)
            
            # ルート順からルート順の座標リストを作成
            all_route_result_coodList = []

            for i in range(len(route_result_list)):
                each_route_result_coodList = []

                for j in range(len(route_result_list[i])):
                  each_route_result_coodList.append(coodList[route_result_list[i][j]])
                
                all_route_result_coodList.append(each_route_result_coodList)
            
            
        else:
            distance = 0
            route_result_list = []
            all_route_result_coodList = []

        return all_route_result_coodList, route_result_list, distance
