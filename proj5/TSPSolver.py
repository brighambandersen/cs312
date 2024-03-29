#!/usr/bin/python3

from which_pyqt import PYQT_VER

if PYQT_VER == "PYQT5":
    from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == "PYQT4":
    from PyQt4.QtCore import QLineF, QPointF
else:
    raise Exception("Unsupported Version of PyQt: {}".format(PYQT_VER))


import time
import numpy as np
from TSPClasses import *
import heapq
from node import Node


class TSPSolver:
    def __init__(self, gui_view):
        self._scenario = None

    def setupWithScenario(self, scenario):
        self._scenario = scenario

    """ <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution, 
		time spent to find solution, number of permutations tried during search, the 
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	"""

    def defaultRandomTour(self, time_allowance=60.0):
        results = {}
        cities = self._scenario.getCities()
        ncities = len(cities)
        found_tour = False
        count = 0
        bssf = None
        start_time = time.time()
        while not found_tour and time.time() - start_time < time_allowance:
            # create a random permutation
            perm = np.random.permutation(ncities)
            route = []
            # Now build the route using the random permutation
            for i in range(ncities):
                route.append(cities[perm[i]])
            bssf = TSPSolution(route)
            count += 1
            if bssf.cost < np.inf:
                # Found a valid route
                found_tour = True
        end_time = time.time()
        results["cost"] = bssf.cost if found_tour else math.inf
        results["time"] = end_time - start_time
        results["count"] = count
        results["soln"] = bssf
        results["max"] = None
        results["total"] = None
        results["pruned"] = None
        return results

    """ <summary>
		This is the entry point for the greedy solver, which you must implement for 
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	"""

    def greedy(self, time_allowance=60.0):
        results = {}
        cities = self._scenario.getCities()
        found_tour = False
        start_time = time.time()
        route = []

        # Loop through each city
        for start_city in cities:
            route = [start_city]  # Make new route with starting city

            # For each city, try to find a route
            # T O(n) - Worst case has to do this for all the cities
            while not found_tour and time.time() - start_time < time_allowance:

                cheapest_neighbor = route[
                    -1
                ]  # Initialize to start city so that costTo is inf
                for neighbor in cities:
                    if neighbor not in route and route[-1].costTo(neighbor) < route[
                        -1
                    ].costTo(cheapest_neighbor):
                        cheapest_neighbor = neighbor

                # If invalid route - no neighbors
                # break out of while loop, move onto next city (increment i)
                if route[-1].costTo(cheapest_neighbor) == math.inf:
                    break

                # Append cheapest neighbor
                route.append(cheapest_neighbor)

                # If complete route (includes all cities and last has edge back to first)
                if len(route) == len(cities) and route[-1].costTo(route[0]) < math.inf:
                    found_tour = True

            if found_tour:
                break

        solution = TSPSolution(route)

        end_time = time.time()
        results["cost"] = solution.cost if found_tour else math.inf
        results["time"] = end_time - start_time
        results["count"] = 1 if found_tour else 0  # Greedy only finds 1
        results["soln"] = solution
        results["max"] = None
        results["total"] = None
        results["pruned"] = None
        return results

    """ <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints: 
		max queue size, total number of states created, and number of pruned states.</returns> 
	"""

    def branchAndBound(self, time_allowance=60.0):
        results = {}
        cities = self._scenario.getCities()
        num_cities = len(cities)

        # Make the upper bound be the greedy solution
        greedy_res = self.greedy(time_allowance)
        bssf = greedy_res["soln"]  # Initially set the bssf to be greedy's

        # Initialize other returned variables
        solutions_count = 0  # Number of complete solutions (number of times hit bottom)
        max_queue_size = 0
        node_total = 0
        pruned_total = 0

        # Start timer
        start_time = time.time()

        # Make cost matrix
        matrix = np.zeros((num_cities, num_cities))
        for i in range(np.shape(matrix)[0]):  # Rows
            for j in range(np.shape(matrix)[1]):  # Cols
                matrix[i][j] = cities[i].costTo(cities[j])

        # Make Node class
        start_node = Node(0, matrix, [cities[0]])  # Have first city in queue
        node_total += 1

        # Reduce
        start_node.reduce_cost_matrix()

        # Make queue (following B&B pseudo code from here)
        q = []
        heapq.heappush(q, start_node)  # Only have start node to begin

        while len(q) > 0 and time.time() - start_time < time_allowance:
            if len(q) > max_queue_size:
                max_queue_size = len(q)

            cheapest_node = heapq.heappop(q)

            if cheapest_node.lower_bound < bssf.cost:
                child_nodes = cheapest_node.expand(cities)
                node_total += len(child_nodes)

                for child_node in child_nodes:
                    # If you hit the bottom of tree (complete route)
                    child_solution = TSPSolution(child_node.route)
                    if (
                        child_node.is_complete_route()
                        and child_solution.cost < bssf.cost
                    ):
                        bssf = child_solution
                        solutions_count += 1
                    elif child_node.lower_bound < bssf.cost:
                        heapq.heappush(q, child_node)
                    else:  # Skip over it (prune)
                        pruned_total += 1

        end_time = time.time()
        results["cost"] = bssf.cost
        results["time"] = end_time - start_time
        results["count"] = solutions_count
        results["soln"] = bssf
        results["max"] = max_queue_size
        results["total"] = node_total
        results["pruned"] = pruned_total
        return results

    """ <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found during search, the 
		best solution found.  You may use the other three field however you like.
		algorithm</returns> 
	"""

    def fancy(self, time_allowance=60.0):
        pass
