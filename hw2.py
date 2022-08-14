#!/usr/bin/env python
# coding: utf-8
# cs131 hw2
# Neal Zhao
# 2/23/2022
#*****************************************************************************************
# important: This code must be run with python version >= 3.10

import numpy as np
import bisect


# define the heuristic function of the program,detail see `readme`
# parameter: p: a tuple that represent the pancake stack
    # cost_function: 'astar' or 'UCS'. Indicating with searching algorithms to use
# return the heuristic cost of the stack
def heuristic(p, cost_function):
    cost = 0
    if cost_function == 'astar': # if it is 'astar', calculate the distance, otherwise return 0
        for i in range(len(p)-1): # for each pair of adjacent pancakes
            if abs(p[i] - p[i+1]) > 1:
                cost += 1
        if p[0] != len(p): # if the bottom one is wrong
            cost += 1
    return cost


# this function flip all pancakes above one position
# paramerter: 
    # n: a node
    # s: the number of pancakes *under* the flipped pancakes. i.e. if the top 4 cakes are to be flipped, s = 6
    # cost_function: 'astar' or 'UCS'. Indicating with searching algorithms to use
# return a new node
def flip(n, s, cost_function):
    p = n.state
    new_p = list(p)
    for i in range(s, len(p)): # for each pancakes that will change its position
        new_p[i] = p[len(p) + s - i - 1]
    result = node(tuple(new_p), n.total_cost + 1 + heuristic(new_p, cost_function), n.backward_cost + 1, n, s)
    return result


# this class represent a search node
# parameters:
    # state: a tuple store the pancake state
    # total_cost: integer, the forward heuristic cost plus backward cost
    # backward_cost: integer, the backward cost, aka number of flips done
    # parent_node: node, the node before last flip
    # flip_position: integer, last flip position
class node():
    def __init__(self, state, total_cost, backward_cost, parent_node, flip_position):
        self.state = state 
        self.total_cost = total_cost
        self.backward_cost = backward_cost
        self.parent_node = parent_node
        self.flip_position = flip_position
        
        
        
def node_key(node): # return the total cost of the node
    return node.total_cost
        
    
# a priority queue and a dict that stores the frontier node
class Frontier():
    # basic structure: a list of node
        # the node is also stored in a dict as {pancake_state:node} for easy update purpose. 
    # each time a node is inserted, it is inserted in a sorted posiition. 
    def __init__(self):
        self.queue = list()
        self.frontier = dict()
    
    def insert(self, node): # insert a node into the sorted queue
        bisect.insort(self.queue, node, key = node_key)
    
    def update(self, node): # if the node already exist, update it if it is better, otherwise insert it
        state = node.state
        if state in self.frontier: # node already exist, update its value
            old_node = self.frontier[state]
            if node.total_cost < self.frontier[state].total_cost: # the given new node is better
                # update the node in the frontier
                self.frontier.update({state: node})
                # remove the old node and insert the new node to the queue to keep the queue sorted
                i = bisect.bisect_left(self.queue, old_node.total_cost, key = node_key) # the left-most node with the same cost
                for n in range(i, len(self.queue)): # search from that left-most node to the right
                    if self.queue[n].state == old_node.state: # the same node (state)
                        self.queue.pop(n)
                        self.insert(node)
                        break
                        
        else:# not in frontier yet
            self.frontier.update({state: node})
            self.insert(node)
    
    def pop(self): # remove and return the node with the smallest key
        node_poped = self.queue.pop(0)
        self.frontier.pop(node_poped.state)
        return node_poped
    
    
# the main class for searching
# parameters:
    # initial: a tutple that represents the initial state of the 
    # cost_function: 'astar' or 'UCS'. Indicating with searching algorithms to use
class Search():
    def __init__(self, initial, cost_function = 'astar'):
        self.visited = set()
        self.frontier = Frontier()
        self.start = initial
        self.cost_function = cost_function
        self.stack_size = len(initial)
        self.goal = tuple(list(range(len(initial), 0, -1)))
        self.solution = list()
        self.initial = initial
    
    # this function search the solution and return the last 
    def search(self):
        init_node = node(self.initial, heuristic(self.initial, self.cost_function), 0, None, self.stack_size)
        self.frontier.update(init_node)
        
        while(len(self.frontier.queue) != 0): # frontier not empty
            current_node = self.frontier.pop() # get the node with least distance
            if current_node.state == self.goal: # if it is the goal
                return current_node
            for i in range(self.stack_size): # check each child
                child = flip(current_node, i, self.cost_function)
                if child not in self.visited:
                    self.frontier.update(child)
        return 'Failure'
    
    # this function print the solution
    # parameter: end_node: the last node that reached the goal
    def print_solution(self, node):
        self.solution.append(node)
        
        # note that the begining node is at the end
        while(node.parent_node != None):
            node = node.parent_node
            self.solution.append(node)
        for i in range(len(self.solution) - 1, -1, -1): # loop the solution list from back to begin
            current = self.solution[i]
            print('After {} step(s), flipped top {} pancakes, we have the stack {}'.
                      format(current.backward_cost, self.stack_size - current.flip_position, current.state))
        print('Solution found')
        return
    
    
# main function
if __name__ == "__main__":
    cost_func = input('Cost function: `astar` or `ucs`, case sensitive: ')
    if cost_func != 'astar' and cost_func != 'ucs': 
        raise ValueError('invalid cost function')
        
    initial_str = input('Input the initial stack, use space to separate numbers. Example: `1 2 3 4`: ')
    initial = list(map(int, initial_str.split()))
    if sorted(initial) != list(range(1, len(initial) + 1)):
        raise ValueError('invalid pancake stack')
        
    print('')
    print('Using {} to solve the problem'.format(cost_func))
    s = Search(tuple(initial), cost_func)
    s.print_solution(s.search())


