import match, gridNav,random, time
import subprocess
import shlex, time

def resizeWindow(n):
  id_cmd='xdotool getactivewindow'
  resize_cmd='xdotool windowsize --usehints {id} '+str(n*2+3)+' '+str(n+3)

  proc=subprocess.Popen(shlex.split(id_cmd),stdout=subprocess.PIPE)
  windowid,err=proc.communicate()
  proc=subprocess.Popen(shlex.split(resize_cmd.format(id=windowid)))
  proc.communicate()

functionTimes = {}

def timing(f):
  def wrap(*args):
    time1 = time.time()
    ret = f(*args)
    time2 = time.time()
    if f.func_name not in functionTimes.keys():
      functionTimes[f.func_name] = 0
    functionTimes[f.func_name] += (time2-time1)*1000.0
    return ret
  return wrap

class Delta:
  
  @timing
  def __init__(self, template):
    self.removedCells = {}
    self.removedAcross = {}
    self.removedDown = {}
    self.isDeadEnd = False
    
    # cells
    for i in range(len(template)):
      for j in range(len(template[0])):
        if template[i][j] == ' ': continue
        self.removedCells[(i,j)] = Cell()
    
    # across
    for i in range(len(template)):
      line = template[i]
      j = 0
      words = line.split(' ')
      for w in words:
        if len(w) != 0:
          self.removedAcross[(i,j)] = []
        j += len(w)+1
    
    # down
    for j in range(len(template[0])):
      line = ''.join([template[i][j] for i in range(len(template))])
      i = 0
      words = line.split(' ')
      for w in words:
        if len(w) != 0:
          self.removedDown[(i,j)] = []
        i += len(w)+1
  
  @timing
  def __repr__(self):
    cellline = 'cells: '+str(len(''.join(self.removedCells.values())))
    acrline = 'across: '+str(sum([len(acr) for acr in self.removedAcross.values()]))
    dwnline = 'down: '+str(sum([len(dwn) for dwn in self.removedDown.values()]))
    return cellline+'\n'+acrline+'\n'+dwnline

class Cell:
  
  def __init__(self):
    self.down = {}
    self.across = {}
    for ch in 'abcdefghijklmnopqrstuvwxyz':
      self.down[ch] = 0
      self.across[ch] = 0
  
  def __repr__(self):
    l = self.possLetters()
    if len(l) == 1: return l[0]
    #elif l == 0: return 'X'
    #elif l < 5: return '#'
    #elif l < 10: return '*'
    #elif l < 15: return '+'
    #elif l < 20: return '-'
    #elif l < 24: return ','
    #elif l < 26: return '.'
    else: return '*'
  
  def isSolved(self):
    return len(self.possLetters()) == 1
  
  def possLetters(self):
    poss = ''
    for ch in 'abcdefghijklmnopqrstuvwxyz':
      if self.down[ch] > 0 and self.across[ch] > 0:
        poss += ch
    return poss

class Grid:
  
  @timing
  def __init__(self, template, includeWords = [], excludeWords = []):
    self.template = template
    self.cells = {}
    self.across = {}
    self.down = {}
    self.assignments = []
    
    # cells
    for i in range(len(template)):
      for j in range(len(template[0])):
        if template[i][j] == ' ': continue
        self.cells[(i,j)] = Cell()
    
    # across
    for i in range(len(template)):
      line = template[i]
      j = 0
      words = line.split(' ')
      for w in words:
        if len(w) != 0:
          self.across[(i,j)] = match.getMatchingWords(w, includeWords, excludeWords)
          for word in self.across[(i,j)]:
            for ind in range(len(word)):
              self.cells[(i,j+ind)].across[word[ind]] += 1
        j += len(w)+1
    
    # down
    for j in range(len(template[0])):
      line = ''.join([template[i][j] for i in range(len(template))])
      i = 0
      words = line.split(' ')
      for w in words:
        if len(w) != 0:
          self.down[(i,j)] = match.getMatchingWords(w, includeWords, excludeWords)
          for word in self.down[(i,j)]:
            for ind in range(len(word)):
              self.cells[(i+ind,j)].down[word[ind]] += 1
        i += len(w)+1
  
    #self.updateAll()
  
  @timing
  def __repr__(self):
    grid = ' '
    #regions = self.getRegions()
    regionKeys = ['.','*','#']
    for i in range(len(self.template)):
      for j in range(len(self.template[0])):
        if self.template[i][j] == ' ': grid += ' '
        else: grid += self.cells[(i,j)].__repr__()
        grid += ' '
      grid += '\n '
    return grid
  
  @timing
  def updateAll(self):
    #done = []
    for cell in self.cells.keys():
    #  if cell in done:
    #    continue
      delta = self.update(cell, '', Delta(self.template))
    #  done += delta.updatedCells()
  
  @timing
  def decide(self, cell, assignment):
    delta = Delta(self.template)
    return self.update(cell, assignment, delta)
  
  @timing
  def update(self, start, assignment, delta = None):
    trackingChanges = delta != None
    queue = [(start, assignment)]
    while len(queue) > 0:
      cell, assn = queue.pop(0)
      across = gridNav.getAcrossStart(self.template, cell)
      down = gridNav.getDownStart(self.template, cell)
      
      # across
      toRemove = []
      index = cell[1] - across[1]
      for word in self.across[across]:
        if assn != '':
          if word[index] != assn:
            toRemove.append(word)
        elif self.cells[cell].across[word[index]] <= 0 or self.cells[cell].down[word[index]] <= 0:
          toRemove.append(word)
      for rem in toRemove:
        self.across[across].remove(rem)
        delta.removedAcross[across].append(rem)
        acrossCells = gridNav.getAcrossCells(self.template, across)
        for acrossCellInd in range(len(acrossCells)):
          acrossCell = acrossCells[acrossCellInd]
          self.cells[acrossCell].across[rem[acrossCellInd]] -= 1
          delta.removedCells[acrossCell].across[rem[acrossCellInd]] += 1
          if self.cells[acrossCell].across[rem[acrossCellInd]] == 0:
            if max(self.cells[acrossCell].across.values()) == 0:
              delta.isDeadEnd = True
              return delta
            queue.append((acrossCell,''))
      
      # down
      toRemove = []
      index = cell[0] - down[0]
      for word in self.down[down]:
        if assn != '':
          if word[index] != assn:
            toRemove.append(word)
        elif self.cells[cell].across[word[index]] <= 0 or self.cells[cell].down[word[index]] <= 0:
          toRemove.append(word)
      for rem in toRemove:
        self.down[down].remove(rem)
        delta.removedDown[down].append(rem)
        downCells = gridNav.getDownCells(self.template, down)
        for downCellInd in range(len(downCells)):
          downCell = downCells[downCellInd]
          self.cells[downCell].down[rem[downCellInd]] -= 1
          delta.removedCells[downCell].down[rem[downCellInd]] += 1
          if self.cells[downCell].down[rem[downCellInd]] == 0:
            if max(self.cells[downCell].down.values()) == 0:
              delta.isDeadEnd = True
              return delta
            queue.append((downCell,''))
    
    return delta
  
  @timing
  def restore(self, removed):
    for cell in removed.removedCells.keys():
      for ch in 'abcdefghijklmnopqrstuvwxyz':
        self.cells[cell].across[ch] += removed.removedCells[cell].across[ch]
        self.cells[cell].down[ch] += removed.removedCells[cell].down[ch]
    for space in removed.removedAcross.keys():
      self.across[space] += removed.removedAcross[space]
    for space in removed.removedDown.keys():
      self.down[space] += removed.removedDown[space]
  
  @timing
  def regionedCell(self):
    lowestCell = (-1,-1)
    regions = self.getRegions()
    smallestRegion = regions[-1]
    lowestValue = 27
    for cell in smallestRegion:
      #if self.cells[cell].isSolved(): continue
      if len(self.cells[cell].possLetters()) < lowestValue:
        lowestValue = len(self.cells[cell].possLetters())
        lowestCell = cell
    if lowestCell == (-1,-1):
      print smallestRegion
      for i in smallestRegion:
        print self.cells[i]
      raw_input()
    return lowestCell, smallestRegion
  
  @timing
  def isSolved(self):
    for cellObj in self.cells.values():
      if not cellObj.isSolved():
        return False
    return True

  @timing
  def getRegions(self):
    visited = []
    regions = []
    for cell in self.cells.keys():
      if not self.cells[cell].isSolved() and cell not in visited:
        regions.append(self.floodfill(cell, visited))
    return sorted(regions, key=lambda reg: -sum([len(self.cells[c].possLetters()) for c in reg]))         #-len(reg))

  @timing
  def floodfill(self, cell, visited):
    region = []
    Q = []

    dirs = { (-1, 0), (1, 0), (0, -1), (0, 1) }

    Q.append( cell )
    visited.append(cell)

    while len(Q) > 0:
      (r, c) = Q.pop(0)
      region.append( (r, c) )
      for (dr, dc) in dirs:
        if (r+dr, c+dc) in self.cells.keys() and not self.cells[(r+dr, c+dc)].isSolved() and (r+dr, c+dc) not in visited:
          Q.append((r + dr, c + dc))
          visited.append((r+dr, c+dc))
    return region
  
  @timing
  def getWordList(self):
    return sorted([i[0] for i in self.across.values() + self.down.values()])
  
  @timing
  def solve(self, printout=False):
    if printout:
      print self
    if self.isSolved():
      return (True,)
    cell, region = self.regionedCell()
    l = list(self.cells[cell].possLetters())
    random.shuffle(l)
    letters = ''.join(l)
    for letter in letters:
      removed = self.decide(cell, letter)
      if removed.isDeadEnd:
        self.restore(removed)
        continue
      soln = self.solve(printout)
      if soln[0]:
        return (True,)
      self.restore(removed)
      #if soln[1] not in region:#removed.updatedCells():
      #  return (False, soln[1], soln[2])
    return (False, cell, region)

includeWords = ['andy','jonathan','ruth','carla','chris','hana']
f = open('templates/15x15/1', 'r')
template = f.read().split('\n')
while '' in template: template.remove('')
n = Grid(template, includeWords, [])

# index includeWords list
includeLengths = {}
for w in includeWords:
  if len(w) not in includeWords.keys(): includeWords[len(w)] = []
  includeWords[len(w)].append(w)


















































