#!/usr/bin/env python

import heapq
from sets import Set
from sys import argv

class Map:

	def __init__(self, lines):
		splitted = [line.split() for line in lines]
		self.n = len(lines)
		self.map = [i for li in splitted for i in li]

		start = self.map.index('P')
		self.start = self.loc(start)
		self.map[start] = '0'

		end = self.map.index('C')
		self.end = self.loc(end)
		self.map[end] = '0'

		self.tel = self._teleporters()		# updates map
		self.shuttle = self._shuttle()		# updates map
		self.map = map(int, self.map)

	def loc(self, index):
		coef = index / self.n
		return (coef + 1, index - self.n * coef + 1)

	def _teleporters(self):
		li = []
		for i in xrange(self.n * self.n):
			if self.map[i][0] == 'T':
				li.append((self.loc(i), int(self.map[i][1])))
				self.map[i] = '0'
		return li

	def _shuttle(self):
		indexs = self.map.index('SS')
		self.map[indexs] = '0'
		indexl = self.map.index('SL')
		self.map[indexl] = '0'
		return (self.loc(indexs), self.loc(indexl))

	def special(self, pos):
		if self.shuttle[0] == pos:
			return [self.shuttle[1]]
		try:
			index = map(lambda (p, _): p, self.tel).index(pos)
			telid = self.tel[index][1]
			return map(lambda (p, _): p, 
				filter(lambda (p, i): i == telid and p != pos, self.tel))
		except:
			return None

	def weight(self, curr, prev):
		manh = 0
		tels = map(lambda (p, _): p, self.tel)
		if prev in tels and curr in tels:
			manh = manhattan(prev, curr)
		if self.shuttle[0] == prev:
			manh = 3 * manhattan(prev, curr)
		hop = abs(self.map[(curr[0]-1)*self.n+curr[1]-1]
					- self.map[(prev[0]-1)*self.n+prev[1]-1])
		return hop + manh

	def closestTeleporter(self, state):
		manh = -1
		curr = None
		for s in self.tel:
			val = manhattan(state, s[0])
			if curr is None:
				manh = val
				curr = s[0]
			elif val < manh:
				manh = val
				curr = s[0]
		return curr


def manhattan((x1, y1), (x2, y2)):
	return abs(x1 - x2) + abs(y1 - y2)

class Node:

	def __init__(self, state, cost, prev):
		self.state = state
		self.cost = cost
		self.prev = prev

	def __cmp__(self, other):
		return self.cost - other.cost

	def __eq__(self, other):
		return self.state == other.state

	def __repr__(self):
		return str(self.state) + ' ' + str(self.cost)

	def __hash__(self):
		return hash(self.state)


def readMap(filename):
	return Map([line.strip() for line in open(filename)])

def trace(node):
	li = []
	while node is not None:
		li.append(node)
		node = node.prev
	li.reverse()
	return li

def goal(state):
	return state == maph.end

def succ(state):
	next = []
	x, y = state	# x=row, y=column
	if x != 1:
		next.append((x-1, y))
	if x != maph.n:
		next.append((x+1, y))
	if y != 1 and y != maph.n / 2 + 1:
		next.append((x, y-1))
	if y != maph.n / 2 and y != maph.n:
		next.append((x, y+1))
	spec = maph.special(state)
	if spec is not None:
		next += spec
	return next

def initial(s0):
	return Node(s0, 0, None)

def expand(node, succ):
	return [Node(s, g(node) + maph.weight(s, node.state), node)
		for s in succ(node.state)]

def search(s0, succ, goal):		# uniform cost search
	openList = []
	closed = Set()
	heapq.heappush(openList, initial(s0))
	while len(openList) > 0:
		node = heapq.heappop(openList)
		if goal(node.state):
			return (node, closed)
		closed.add(node.state)
		for n in expand(node, succ):
			if n.state not in closed:
				heapq.heappush(openList, n)
	return None

def g(n):
	return n.cost

def h1(s):		# manhattan heuristika
	return manhattan(s, maph.end)

def f(n, h):
	return g(n) + h(n.state)

def h2(s):		# druga heuristika
	entrance = maph.closestTeleporter(s)
	exit = maph.closestTeleporter(maph.end)
	x, y = s
	if y > maph.n / 2:
		return manhattan(s, maph.end)
	else:
		return manhattan(s, entrance) + manhattan(entrance, exit)	\
			+ manhattan(exit, maph.end)

def aStarSearch(s0, succ, goal, h):
	openList = []
	closed = []
	un = []
	heapq.heappush(openList, initial(s0))
	while len(openList) > 0:
		node = heapq.heappop(openList)
		if goal(node.state):
			return (node, closed)
		closed.append(node)
		closed = list(set(closed))
		for n in expand(node, succ):
			un = list(set(closed + openList))
			if n in un:
				m = un[un.index(n)]
				if g(m) <= g(n):
					continue
				else:
					if m in openList:
						del openList[openList.index(m)]
					else:
						del closed[closed.index(m)]
			openList = insertSortedBy(lambda n: f(n, h), n, openList)
	return None

def insertSortedBy(f, node, openList):
	openList.append(node)
	openList = sorted(openList, key=f)
	return openList

if __name__ == "__main__":

	maph = readMap(argv[1])		# global
	
	(end, opened) = aStarSearch(maph.start, succ, goal, h2)
	print "Minimal cost:", end.cost
	print "Opened nodes:", len(opened)
	path = trace(end)
	print " ->\n".join(map(str, path))

