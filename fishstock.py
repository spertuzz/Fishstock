import random
from termcolor import colored

W = 1
B = -1
DRAW = 0
UNUSED = None
MAX_DEPTH = 2

class state:

  def __init__(self):
    self.pieces = dict()
    self.pieces[W] = []
    self.pieces[B] = []
    self.can_passant = []
    self.current_player = W

  def __eq__(self, other):
    if not isinstance(other, state):
      return NotImplemented
    self.can_passant = other.can_passant
    return (
        self.pieces[W] == other.pieces[W] and self.pieces[B] == other.pieces[B]
        and self.current_player == other.current_player
    )

  def taken(self):
    arr = []
    for player in self.pieces:
      for piece in self.pieces[player]:
        arr.append(piece['location'])
    return arr

  def copy(self):
    new_state = state()
    new_state.pieces = dict()
    new_state.pieces[W] = self.pieces[W].copy()
    new_state.pieces[B] = self.pieces[B].copy()
    new_state.can_passant = self.can_passant.copy()
    new_state.current_player = self.current_player
    return new_state

  def setup_start(self):
    # Add pawns
    for i in range(8):
      self.pieces[W].append(dict(symbol="P", location=(1, i)))
      self.pieces[B].append(dict(symbol="P", location=(6, i)))
    # Add other pieces
    for i in range(2):
      # Rooks
      self.pieces[W].append(dict(symbol="R", location=(0, 7 * i)))
      self.pieces[B].append(dict(symbol="R", location=(7, 7 * i)))
      # Knights
      self.pieces[W].append(dict(symbol="N", location=(0, 1 + 5 * i)))
      self.pieces[B].append(dict(symbol="N", location=(7, 1 + 5 * i)))
      # Bishops
      self.pieces[W].append(dict(symbol="B", location=(0, 2 + 3 * i)))
      self.pieces[B].append(dict(symbol="B", location=(7, 2 + 3 * i)))
    # Queens
    self.pieces[W].append(dict(symbol="Q", location=(0, 3)))
    self.pieces[B].append(dict(symbol="Q", location=(7, 3)))
    # Kings
    self.pieces[W].append(dict(symbol="K", location=(0, 4)))
    self.pieces[B].append(dict(symbol="K", location=(7, 4)))

  def get_piece(self, location):
    for player in self.pieces:
      for piece in self.pieces[player]:
        if piece['location'] == location:
          return dict(pc=piece, plr=player)
    return None

  def within_bounds(self, location):
    return location[0] >= 0 and location[0] <= 7 and location[1] >= 0 and location[1] <= 7

  def create_new_state(self, new_pieces, removed_pieces, passants=[]):
    new_state = self.copy()
    for piece in removed_pieces:
      new_state.pieces[piece['plr']].remove(piece['pc'])
    for piece in new_pieces:
      new_state.pieces[piece['plr']].append(piece['pc'])
    new_state.can_passant = passants
    return new_state

  def continuous_movement(self, piece, vectors, max=8):
    states = []
    for vector in vectors:
        for i in range(1, max + 1):
          new_location = (piece['location'][0] + i * vector[0], piece['location'][1] + i * vector[1])
          if not self.within_bounds(new_location):
            break
          to_take = UNUSED
          if new_location in self.taken():
            to_take = self.get_piece(new_location)
            if to_take['plr'] == self.current_player:
              break
          new_piece = dict(symbol=piece['symbol'], location=new_location)
          to_remove = [dict(pc=piece, plr=self.current_player)]
          if to_take != UNUSED:
            to_remove.append(to_take)
          states.append(self.create_new_state(
              [dict(pc=new_piece, plr=self.current_player)],
              to_remove
          ))
          if to_take != UNUSED:
            break
    return states

  def checked(self):
    """states = self.neighbors(False)
    for state in states:
      king_found = False
      for piece in state.pieces[state.current_player]:
        if piece['symbol'] == 'K':
          king_found = True
          break
      if not king_found:
        return True"""

    king = None
    for piece in self.pieces[self.current_player]:
      if piece['symbol'] == 'K':
        king = piece['location']
        break
    if king == None:
      return None
    vectors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for vector in vectors:
      for i in range(1, 8):
        new_location = (king[0] + vector[0] * i, king[1] + vector[1] * i)
        if not self.within_bounds(new_location):
          break
        if new_location in self.taken():
          to_take = self.get_piece(new_location)
          if to_take != None:
            if to_take['plr'] != self.current_player and (
                to_take['pc']['symbol'] != 'P' and to_take['pc']['symbol'] != 'K'):
              if (vector[0] == 0 or vector[1] == 0) and to_take['pc']['symbol'] == 'R':
                return True
              if (vector[0] != 0 and vector[1] != 0) and to_take['pc']['symbol'] == 'B':
                return True
              if i == 1 and to_take['pc']['symbol'] == 'K':
                return True
              if to_take['pc']['symbol'] == 'Q':
                return True
            break
    vectors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for vector in vectors:
      new_location = (king[0] + vector[0], king[1] + vector[1])
      if self.within_bounds(new_location):
        to_take = self.get_piece(new_location)
        if to_take != None:
          if to_take['plr'] != self.current_player and to_take['pc']['symbol'] == 'K':
            return True
    vectors = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    for vector in vectors:
      new_location = (king[0] + vector[0], king[1] + vector[1])
      if self.within_bounds(new_location):
        to_take = self.get_piece(new_location)
        if to_take != None:
          if to_take['plr'] != self.current_player and to_take['pc']['symbol'] == 'N':
            return True
    for i in range(-1, 2, 2):
      row = self.current_player
      col = i
      new_location = (king[0] + row, king[1] + col)
      if self.within_bounds(new_location):
        to_take = self.get_piece(new_location)
        if to_take != None:
          if to_take['plr'] != self.current_player and to_take['pc']['symbol'] == 'P':
            return True
    return False

  def neighbors(self, ignore_checks=False):
    moves = []
    for piece in self.pieces[self.current_player]:
      # Pawn
      if piece['symbol'] == 'P':
        for i in range(1, 3):
          if not (
              (piece['location'][0] == 1 and self.current_player == W)
              or (piece['location'][0] == 6 and self.current_player == B)
              ) and i == 2:
            break
          amount = i * self.current_player
          new_location = (piece['location'][0] + amount, piece['location'][1])
          if (new_location not in self.taken() and self.within_bounds(new_location)):
            new_symbol = piece['symbol']
            if piece['location'][0] + amount == 0 or piece['location'][0] + amount == 7:
              new_symbol = 'Q'
            new_piece = dict(symbol=new_symbol, location=new_location)
            passants = []
            if i == 2:
              passants.append(new_piece['location'])
            moves.append(self.create_new_state(
                [dict(pc=new_piece, plr=self.current_player)],
                [dict(pc=piece, plr=self.current_player)],
                passants
            ))
        for i in range(-1, 2, 2):
          col = i
          row = self.current_player
          to_take = None
          new_location = (piece['location'][0] + row, piece['location'][1] + col)
          if new_location in self.taken():
            to_take = self.get_piece(new_location)
            if to_take['plr'] == self.current_player:
              to_take = None
          elif (new_location[0], new_location[1] - col) in self.taken():
            to_take = self.get_piece((new_location[0], new_location[1] - col))
            if not (to_take['plr'] != self.current_player
                and to_take['pc']['symbol'] == 'P'
                and to_take['pc']['location'] in self.can_passant):
              to_take = None
          if to_take != None:
            new_state = self.copy()
            new_symbol = piece['symbol']
            if new_location[0] == 0 or new_location[0] == 7:
              new_symbol = 'Q'
            new_piece = dict(symbol=new_symbol, location=new_location)
            moves.append(self.create_new_state(
                [dict(pc=new_piece, plr=self.current_player)],
                [dict(pc=piece, plr=self.current_player), to_take]
            ))
      # Knight
      elif piece['symbol'] == 'N':
        vectors = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        states = self.continuous_movement(piece, vectors, 1)
        moves.extend(states)
      # Bishop
      elif piece['symbol'] == 'B':
        vectors = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        states = self.continuous_movement(piece, vectors)
        moves.extend(states)
      # Rook
      elif piece['symbol'] == 'R':
        vectors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        states = self.continuous_movement(piece, vectors)
        moves.extend(states)
      # Queen
      elif piece['symbol'] == 'Q':
        vectors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        states = self.continuous_movement(piece, vectors)
        moves.extend(states)
      # King
      elif piece['symbol'] == 'K':
        vectors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        states = self.continuous_movement(piece, vectors, 1)
        moves.extend(states)
    if ignore_checks:
      return moves
    valid_moves = []
    for move in moves:
      if move.checked() == False:
        move.current_player *= -1
        valid_moves.append(move)
    return valid_moves

  def heuristic(self):
    # Function for scaling
    def f(x):
      val = 0.00130208 * x * x -0.0729167 * x + 1
      if val < 0:
        val = 0
      return val
    # Material and piece positioning
    material_vals = dict(P=1, N=3, B=3, R=5, Q=9, K=0)
    material_score = 0
    doubled_pawns = []
    for col in range(8):
      for player in self.pieces:
        pawns = []
        for piece in self.pieces[player]:
          if piece['symbol'] == 'P' and piece['location'][1] == col:
            pawns.append(piece)
        if len(pawns) > 1:
          doubled_pawns.extend(pawns)
    remaining_count = len(self.pieces[W]) + len(self.pieces[B])
    endgame_must_haves = ['P', 'R', 'Q']
    for player in self.pieces:
      for piece in self.pieces[player]:
        value = material_vals[piece['symbol']]
        if (piece['symbol'] == 'P' or piece['symbol'] == 'N'):
          if (piece['location'][1] == 0 or piece['location'][1] == 7):
            value /= 1.5
          elif (piece['location'][1] == 3 or piece['location'][1] == 4):
            value *= 1.5
          if piece in doubled_pawns:
            value *= 0.6
          if piece['symbol'] == 'P' and (piece['location'][0] == 1 or piece['location'][0] == 6):
            value *= 2
          if piece['symbol'] == 'N' and (piece['location'][0] == 0 or piece['location'][0] == 7):
            value /= 1.5
        if piece in endgame_must_haves and remaining_count < 8:
          value *= 2
          if piece['symbol'] == 'P':
            value *= 2
        material_score += value * player
    # Developing pieces
    common_score = 0
    default_state = state()
    default_state.setup_start()
    for player in default_state.pieces:
      for piece in default_state.pieces[player]:
        if piece in self.pieces[player]:
          mult = 1
          if piece['symbol'] != 'P' and piece['symbol'] != 'R':
            mult = 3
          common_score += -player * mult
    common_score *= remaining_count >= 12
    # Available moves and checks
    neighbors = self.neighbors()
    moves_score = len(neighbors) * self.current_player
    check_score = 0
    for new_state in neighbors:
      if new_state.checked():
        check_score += self.current_player
    self.current_player *= -1
    neighbors = self.neighbors(True)
    moves_score += len(neighbors) * self.current_player
    for new_state in neighbors:
      if new_state.checked():
        check_score += -self.current_player
    self.current_player *= -1
    moves_score *= f(remaining_count) + 1
    check_score *= f(remaining_count) * f(remaining_count) + 1
    # Current checks
    current_check_score = self.current_player
    if self.checked():
      current_check_score = -self.current_player
    current_check_score *= (f(remaining_count))
    return 5 * material_score + common_score + 2 * moves_score + 2 * check_score + current_check_score * 5

  def terminal(self):
    states = self.neighbors()
    if len(states) < 1 and self.checked():
      return -self.current_player * float('inf')
    elif len(states) < 1:
      return DRAW
    return None

  def min(self, depth, alpha, beta):
    term = self.terminal()
    if term != None:
      return (term, self, depth)
    if depth < MAX_DEPTH:
      states = self.neighbors()
      vals = []
      for state in states:
        temp = state.max(depth + 1, alpha, beta)
        vals.append(temp)
        beta = min(beta, temp[0])
        if alpha >= beta:
          break
      minimum = float('inf')
      current = []
      for val in vals:
        if val[0] < minimum:
          minimum = val[0]
          current = [val]
        elif val[0] == minimum:
          current.append(val)
      current = random.choice(current)
      if depth == 0:
        return (minimum, current[1], current[2])
      else:
        return (minimum, self, current[2])
    return (self.heuristic(), self, depth)

  def max(self, depth, alpha, beta):
    term = self.terminal()
    if term != None:
      return (term, self, depth)
    if depth < MAX_DEPTH:
      states = self.neighbors()
      vals = []
      for state in states:
        temp = state.min(depth + 1, alpha, beta)
        vals.append(temp)
        alpha = max(alpha, temp[0])
        if alpha >= beta:
          break
      maximum = float('-inf')
      current = []
      for val in vals:
        if val[0] > maximum:
          maximum = val[0]
          current = [val]
        elif val[0] == maximum:
          current.append(val)
      current = random.choice(current)
      if depth == 0:
        return (maximum, current[1], current[2])
      else:
        return (maximum, self, current[2])
    return (self.heuristic(), self, depth)

  def minimax(self):
    if self.current_player == W:
      return self.max(0, float('-inf'), float('inf'))
    else:
      return self.min(0, float('-inf'), float('inf'))

  def render_board(self):
    for i in range(8):
      print(str(8 - i) + "   ", end="")
      for j in range(8):
        x = 7 - i
        y = j
        if (x, y) in self.taken():
          found = False
          for player in self.pieces:
            for piece in self.pieces[player]:
              if piece['location'] == (x, y):
                if (player == B):
                  print(colored(piece['symbol'], 'red', force_color=True), end="")
                else:
                  print(piece['symbol'], end="")
                found = True
                break
            if found:
              break
        else:
          print(" ", end="")
      print()
    print()
    print("    abcdefgh")
    print()

  def get_player_move(self):
    while True:
      move = input('Enter move: ')
      split = move.split(' ')
      if len(split) != 2:
        print('Invalid move, try again.')
        continue
      positions = [[], []]
      positions[0] = split[0]
      positions[1] = split[1]
      allowed = [2, 3]
      if len(positions[0]) not in allowed or len(positions[1]) not in allowed:
        print('Invalid move, try again.')
        continue
      cols = [[], []]
      rows = [[], []]
      allowed_rows = ['1', '2', '3', '4', '5', '6', '7', '8']
      allowed_cols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
      allowed_symbols = ['P', 'N', 'B', 'R', 'Q', 'K']
      for i in range(2):
        for j in range(len(positions[i])):
          if positions[i][j] in allowed_cols:
            cols[i].append(allowed_cols.index(positions[i][j]))
          elif positions[i][j] in allowed_rows:
            rows[i].append(allowed_rows.index(positions[i][j]))
          elif positions[i][j] not in allowed_symbols:
            print('Invalid move, try again.')
            continue
        if len(cols[i]) != 1 or len(rows[i]) != 1:
          print('Invalid move, try again.')
          continue
      old_pos = (rows[0][0], cols[0][0])
      new_pos = (rows[1][0], cols[1][0])
      new_state = self.copy()
      to_move = self.get_piece(old_pos)
      if to_move == None:
        print('Invalid move, try again.')
        continue
      if to_move['plr'] != self.current_player:
        print('Illegal move, try again.')
        continue
      to_remove = None
      if new_pos in self.taken():
        to_remove = self.get_piece(new_pos)
        if to_remove['plr'] == self.current_player:
          print('Illegal move, try again.')
          continue
      new_piece = dict(symbol=to_move['pc']['symbol'], location=new_pos)
      new_state.pieces[self.current_player].remove(to_move['pc'])
      new_state.pieces[self.current_player].append(new_piece)
      if to_remove != None:
        new_state.pieces[-self.current_player].remove(to_remove['pc'])
      neighbors = self.neighbors()
      found = False
      for other_state in neighbors:
        new_state.current_player = other_state.current_player
        if new_state == other_state:
          found = True
          new_state = other_state
          break
      if not found:
        print('Illegal move, try again.')
        continue
      return (0, new_state)

def clear():
    output.clear()

def main():
  chess = state()
  chess.setup_start()
  chess.render_board()
  if random.random() > 0.5:
    bot_color = W
  else:
    bot_color = B
  while True:
    if bot_color == chess.current_player:
      print("AI is thinking...")
      result = chess.minimax()
      result[1].render_board
    else:
      result = chess.get_player_move()
      print()
    clear()
    chess = result[1]
    chess.render_board()
    term = chess.terminal()
    if term != None:
      if term > 0:
        print('CHECKMATE! White wins!')
      elif term < 0:
        print('CHECKMATE! Black wins!')
      else:
        print("It's a draw by stalemate.")
      break
    else:
      if chess.checked():
        print("Check!")
        print()
      if abs(result[0]) > 2**1000:
        print("M" + str(result[2]) + " is guaranteed for ")
        if result[0] > 0:
          print("white.")
        else:
          print("black.")
        print()


if __name__ == '__main__':
  main()