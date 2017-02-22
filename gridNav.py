
template = ['***** **** ****',
            '***** **** ****',
            '***** **** ****',
            '******** ******',
            '   **** *******',
            '****** *****   ',
            '*** ***** *****',
            '**** ***** ****',
            '***** ***** ***',
            '   ***** ******',
            '******* ****   ',
            '****** ********',
            '**** **** *****',
            '**** **** *****',
            '**** **** *****']

def getAcrossStart(template, cell):
  i = (cell[0], cell[1])
  while i[1] != -1 and template[i[0]][i[1]] != ' ':
    i = (i[0], i[1]-1)
  i = (i[0], i[1]+1)
  return i

def getDownStart(template, cell):
  i = (cell[0], cell[1])
  while i[0] != -1 and template[i[0]][i[1]] != ' ':
    i = (i[0]-1, i[1])
  i = (i[0]+1, i[1])
  return i

def getAcrossCells(template, acrossStart, asStr=False):
  cells = []
  i = (acrossStart[0], acrossStart[1])
  while i[1] != len(template[0]) and template[i[0]][i[1]] != ' ':
    if asStr:
      cells.append([str(j) for j in i])
    else:
      cells.append(i)
    i = (i[0], i[1]+1)
  return cells

def getDownCells(template, downStart, asStr=False):
  cells = []
  i = (downStart[0], downStart[1])
  while i[0] != len(template) and template[i[0]][i[1]] != ' ':
    if asStr:
      cells.append([str(j) for j in i])
    else:
      cells.append(i)
    i = (i[0]+1, i[1])
  return cells

def getAcrossCellsFromMid(template, acrossMid):
  return getAcrossCells(template, getAcrossStart(template, acrossMid))

def getDownCellsFromMid(template, downMid):
  return getDownCells(template, getDownStart(template, downMid))

def numCells(template):
  return ''.join(template).count('*')

if __name__ == '__main__':
  print getAcrossStart(template, (4,5))
