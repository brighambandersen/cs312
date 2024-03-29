#!/usr/bin/python3


from CS312Graph import *
import time
import math


class Queue:
    def __init__(self):
        self.queue = []

    def __len__(self):
        return len(self.queue)

    def deleteMin(self, dist):
        pass

    def decreaseKey(self, idx, dist):
        pass

    def insert(self, dist_arr_idx, dist):
        pass

    def makeQueue(self, num_dist_arr_indices, dist):                                                    # Fn - T O(|V|), 
        for i in range(num_dist_arr_indices):
            self.insert(i, dist)

class ArrayQueue(Queue):
    def deleteMin(self, dist):                                                                          # Fn - T O(log|V|), worst amount of recursive calls - S O(1), just stores ints
        min_idx = 0     # Index which points to smallest item in dist
        for i in range(len(self.queue)):
            if dist[self.queue[i]] < dist[self.queue[min_idx]]:     # Compare values in dist that exist in queue
                min_idx = i
        min_val = self.queue[min_idx]
        del self.queue[min_idx]
        return min_val

    def decreaseKey(self, idx, dist):                                                                   # Fn - T O(1) - S O(1)
        pass    # Don't have to do anything here for array implementation

    def insert(self, dist_arr_idx, dist):                                                               # Fn - T O(1), appending is constant - S O(1), adds one item to array
        self.queue.append(dist_arr_idx)


class HeapQueue(Queue):
    def __init__(self):
        super().__init__()
        self.map = []   # Says where to find nodes in the queue

    def __get_parent_idx(self, child_idx):
        if child_idx <= 2:
            return 0
        return (child_idx - 1) // 2

    def __get_left_child_idx(self, parent_idx):
        return (parent_idx * 2) + 1

    def __get_right_child_idx(self, parent_idx):
        return (parent_idx * 2) + 2

    def __get_last_idx(self):
        return len(self.queue) - 1

    def __get_min_child_idx(self, parent_idx, dist):                                                   # Fn - T O(1) - S O(1), just stores ints
        lc_idx = self.__get_left_child_idx(parent_idx)
        rc_idx = self.__get_right_child_idx(parent_idx)

        # Edge cases
        if lc_idx > self.__get_last_idx() or rc_idx > self.__get_last_idx():
            return -1

        if (dist[self.queue[lc_idx]] < dist[self.queue[rc_idx]]):
            return lc_idx
        return rc_idx

    def __swap_values(self, idx1, idx2):                                                               # Fn - T O(1), just assignments - S O(1), just 2 ints created
        # Swap queue values
        temp = self.queue[idx1]
        self.queue[idx1] = self.queue[idx2]
        self.queue[idx2] = temp
        # Swap map values
        temp = self.map[self.queue[idx1]]
        self.map[self.queue[idx1]] = self.map[self.queue[idx2]]
        self.map[self.queue[idx2]] = temp

    def __bubble_up(self, idx, dist):                                                                   # Fn - T O(log|V|), calls bubble up - S O(1), makes 1 int
        parent_idx = self.__get_parent_idx(idx)

        # Bubble up (rec) if the parent is bigger than the child
        if dist[self.queue[parent_idx]] > dist[self.queue[idx]]:
            self.__swap_values(idx, parent_idx)
            self.__bubble_up(parent_idx, dist)


    def __sift_down(self, idx, dist):                                                                   # Fn - T O(log|V|), worst amount of recursive calls - S O(1), makes 1 int
        min_child_idx = self.__get_min_child_idx(idx, dist)
        
        # Edge cases
        if min_child_idx < 1 or min_child_idx > self.__get_last_idx():
            return

        # Sift down (rec) if parent is bigger than the smallest child
        if dist[self.queue[idx]] > dist[self.queue[min_child_idx]]:
            self.__swap_values(idx, min_child_idx)
            self.__sift_down(min_child_idx, dist)
        

    def deleteMin(self, dist):                                                                          # Fn - T O(log|V|), calls sift down - S O(1), just stores an int
        first_val = self.queue[0]   
        self.queue[0] = self.queue[self.__get_last_idx()]   # Replace 1st val with last
        self.map[self.queue[0]] = 0
        self.queue.pop()                                # Remove last item
        self.__sift_down(0, dist)
        return first_val

    def decreaseKey(self, node_val, dist):                                                              # Fn - T O(log|V|), calls bubble up - S O(1), stores 1 int
        idx = self.map[node_val]
        self.__bubble_up(idx, dist)

    def insert(self, dist_arr_idx, dist):                                                               # Fn - T O(log|V|), appending is constant but then calls bubble up - S O(1), adds values to array
        self.queue.append(dist_arr_idx)
        self.map.append(dist_arr_idx)
        self.__bubble_up(self.__get_last_idx(), dist)


class NetworkRoutingSolver:
    def __init__(self):
        self.dist = []
        self.prev = []

    def initializeNetwork( self, network ):
        assert( type(network) == CS312Graph )
        self.network = network

    def getShortestPath( self, destIndex ):
        self.dest = destIndex
        
        path_edges = []

        cur_edge = self.prev[self.dest] # Start with last edge

        while cur_edge: # Work backwards
            path_edges.append( (cur_edge.src.loc, cur_edge.dest.loc, '{:.0f}'.format(cur_edge.length)) )
            cur_edge = self.prev[cur_edge.src.node_id]

        return {'cost':self.dist[self.dest], 'path':path_edges}


    def computeShortestPaths( self, srcIndex, use_heap=False ):
        self.source = srcIndex
        t1 = time.time()

        # Clear arrays each time you start over
        self.dist.clear()
        self.prev.clear()

        queue = HeapQueue() if use_heap else ArrayQueue()   # Sets the right queue implementation based on settings

        # Start of Dijkstra's                                                                       # T O(|V|(cost-to-insert+cost-to-deletemin)+|E|(cost-to-decreasekey)),
        self.dist = [math.inf] * len(self.network.nodes)                                            # S O(|V|), biggest array size is amount of vertices
        self.prev = [None] * len(self.network.nodes)
        self.dist[srcIndex] = 0

        queue.makeQueue(len(self.network.nodes), self.dist)                                         # T O(|V|)*cost-to-insert
        while len(queue) > 0:                                                                       # T O(|V|), loop
            cur_node_idx = queue.deleteMin(self.dist)                                               # T O(1)*cost-to-deletemin

            cur_edges = self.network.nodes[cur_node_idx].neighbors

            for i in range(len(cur_edges)):                                                         # T O(|E|), loops through all edges
                dest_node_idx = cur_edges[i].dest.node_id

                if self.dist[cur_node_idx] + cur_edges[i].length < self.dist[dest_node_idx]:
                    self.dist[dest_node_idx] = self.dist[cur_node_idx] + cur_edges[i].length
                    self.prev[dest_node_idx] = cur_edges[i]
                    queue.decreaseKey(dest_node_idx, self.dist)                                     # T O(1)*cost-to-decreasekey

        t2 = time.time()
        return (t2-t1)