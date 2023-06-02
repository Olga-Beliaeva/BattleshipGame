import random
from itertools import product
from random import choice
# pip install pandas
import pandas as pd
from typing import Union
"""
Customized Battleship game:
- two player game: Player (human) + Computer
- 10 ships for each player
- ship placement restrictions: the ships cannot overlap
- Player chooses whether he wants to place ships manually or at random
- Player has a guesses board where he sees all his shots marked with X (hit)
  or M (miss)
- all hits|misses made by Computer, Player sees on his play board
- both boards (play & guess) printed after every Player's shot side by side
- a tracking success table shows up after each success shot
- a not-to-hit-one-cell-twice protection for both players

"""
class Ship:
    """Class on behalf of a ship"""
    def __init__(self, name: str, length: int):
        self.name = name
        self.length = length
        self.hit = 0

    def is_sunk(self) -> bool:
        return self.hit == self.length

class Board:
    """Class on behalf of a board"""
    def __init__(self, start: int, size: int):
        self.size = size
        self.board = [['.' for _ in range(start, size)] for _ in range(start, size)]

    def __getitem__(self, coord: tuple) -> Union[str, Ship]:
        r,c = coord
        return self.board[r][c]

    def __setitem__(self, coord: tuple, value: Union[str, Ship]):
        r, c = coord
        self.board[r][c] = value

    def can_place_ship(self, ship: Ship, r: int, c: int, direction: str) -> bool:
        """ return True if cells are available """
        if direction.upper() == 'H':
            if c + ship.length > self.size:
                return False
            for i in range(ship.length):
                if self.board[r][c + i] != '.':
                    return False
        else:
            if r + ship.length > self.size:
                return False
            for i in range(ship.length):
                if self.board[r + i][c] != '.':
                    return False
        return True

    def place_ship(self, ship: Union[str, Ship], r: int, c: int, direction: str, length:int = 0):
        """ assign value to a cell """
        length = length if isinstance(ship, str) else ship.length
        if direction.upper() == 'H':
            for i in range(length):
                self.board[r][c + i] = ship
        else:
            for i in range(length):
                self.board[r + i][c] = ship

    def trace(self) -> dict:
        """ return dict of hit ships  """
        record = {
            'Battleship': 0,
            'Cruiser': 0,
            'Destroyer': 0,
            'Submarine': 0
        }
        for i in range(self.size):
            for j in range(self.size):
                cell = self.board[i][j]
                if isinstance(cell, Ship) and cell.is_sunk():
                    record[cell.name] += 1 / cell.length
        return record

    def update_board(self, r: int, c: int, hit: bool):
        """ update a board: to_print | guess """
        if hit:
            self.board[r][c] = 'X'
        else:
            self.board[r][c] = 'M'


class Player:
    """Class on behalf of players (a person or a computer)"""
    SIZE = 10
    ships_base = [
        ('Battleship', 4, 1),
        ('Cruiser', 3, 2),
        ('Destroyer', 2, 3),
        ('Submarine', 1, 4)
    ]

    def __init__(self):
        self.ships = []
        self.board_play = Board(0, self.SIZE)
        self.board_print = Board(0, self.SIZE)
        self.board_guesses = Board(1, self.SIZE+1)

    def place_ships(self):
        """
        choose how to place ships -  randomly or manually
        """
        while True:
            try:
                answer = int(input('If you want to place ships randomly, input 1.\n'
                                   'If you want to place ships manually, input 2. Input here: '))
            except Exception:
                print('Invalid answer. Please try again')
                continue

            if answer not in [1, 2]:
                print('Invalid answer. Please try again')
                continue
            if answer == 1:
                self.place_ships_randomly()
                break
            else:
                self.place_ships_manually()
                break

    def place_ships_randomly(self):
        """
        place ships randomly:
        - place ships bows in randomly chosen cells
        - before placement check if all cells for a  ship are available
        - repeat till get proper cells
        option works by default for the computer
        """
        for ship_set in self.ships_base:
            name, length, amount = ship_set
            for _ in range(amount):
                ship = Ship(name, length)
                self.ships.append(ship)

                # try to place ships till all placed
                while True:
                    r = random.randint(0, self.SIZE-1)
                    c = random.randint(0, self.SIZE-1)
                    direction = random.choice(['H', 'V'])
                    if self.board_play.can_place_ship(ship, r, c, direction):
                        self.board_play.place_ship(ship, r, c, direction)
                        self.board_print.place_ship(name[0], r, c, direction, length)
                        break

    def validate_position(self, position: str) -> Union[bool, tuple]:
        """
        validate a position input:
        - return coordinate if success
        - otherwise return False
        """
        # restrictions
        fit = 1 < len(position) < 4
        alpha = position[0].isalpha()
        digit = position[1].isdigit()

        # coordinates
        r = ord(position[0].upper()) - ord('A')

        if len(position) == 3:
            c = int(position[1] + position[2]) - 1
        else:
            c = int(position[1]) - 1

        # convert restrictions to bool
        validate = sum([fit, alpha, digit, r >= 0, r < self.SIZE, c >= 0, c < self.SIZE])==7

        if validate:
            return r, c
        else:
            print('Invalid position. Please try again.')
            return False


    def place_ships_manually(self):
        """
        place ships manually:
        - ask for a cell to place a ship's bow + ship's direction
        - check if cells are available
        - repeat till get proper cells
        - tell how many ships left to place
        """
        ships_amount = sum([i[2] for i in self.ships_base])

        for ship_set in self.ships_base:
            name, length, amount = ship_set
            for _ in range(amount):
                ship = Ship(name, length)
                self.ships.append(ship)
                print(f'Place your {ship.name} ({ship.length} cells)')

                # try to place ships till all placed
                while True:
                    try:
                        position = input('Enter the position (e.g. A1): ')
                        try:
                            r, c = self.validate_position(position)
                        except Exception:
                            continue

                        direction = input('Enter the direction (H for horizontal, V for vertical): ')
                        if direction.upper() not in ['H', 'V']:
                            print('Invalid direction. Please try again.')
                            continue

                    except IndexError:
                        continue

                    if self.board_play.can_place_ship(ship, r, c, direction):
                        self.board_play.place_ship(ship, r, c, direction)
                        self.board_print.place_ship(name[0], r, c, direction, length)
                        self.print_boards()
                        break
                    else:
                        print('Cannot place the ship there. Please try again.')
                print(f'Ships left to place: {ships_amount - len(self.ships)}')
        print()

    def make_guess(self) -> tuple:
        """
        - ask for a guess
        - check if a guess fits a board
        - check if a guess does not hit same cell the second time
        - repeat till get a proper cell
        """
        while True:
            try:
                guess = input('Enter your guess (e.g. A1): ').upper()
                r, c = self.validate_position(guess)
            except Exception:
                continue

            print(f'You hit {chr(97 + r).upper()}{c + 1}')

            if self.board_guesses[r, c] != '.':
                print('You\'ve hit this cell before. Try again.')
                continue
            return r, c

    def has_lost(self) -> bool:
        return all(ship.is_sunk() for ship in self.ships)

    def print_boards(self):
        """ print boards after every Player's move"""
        print('Player\'s Ships               Player\'s Guesses')
        print('      ' + ' '.join(str(i + 1) for i in range(self.SIZE)) + '     ' + '   ' + ' '.join(
            str(i + 1) for i in range(self.SIZE)))
        print('    ---------------------    ------------------------')
        for i in range(self.SIZE):
            print('| ' + chr(ord('A') + i) + ' | ' + ' '.join(
                [self.board_print[i, j] for j in range(self.SIZE)]) + '   | ' + chr(
                ord('A') + i) + ' | ' + ' '.join([self.board_guesses[i, j] for j in range(self.SIZE)]))
        print()

class Game:
    """Class on behalf of a game"""
    def __init__(self):
        self.player = Player()
        self.computer = Player()

    def play(self):
        """
        a playing part:
        - players play in turns
        - comment each step
        - after each success hit show the achievements  in a table
        """
        print('Welcome to Battleship!')

        # Player makes a choice, Computer places ships randomly
        self.player.place_ships()
        self.computer.place_ships_randomly()

        # list of all choices (the board cell without duplicates)
        # the computer can make during a game
        computer_choice = list(product(range(Player.SIZE), repeat=2))

        while True:
            print("Player's turn:")
            self.player.print_boards()
            r, c = self.player.make_guess()
            ship = self.computer.board_play[r, c]
            hit = ship != '.'
            self.player.board_guesses.update_board(r, c, hit)

            if hit:
                print('Hit!')
                self.hit_ship(ship, 'You sank the')
            else:
                print('Miss!')
            print()

            if self.computer.has_lost():
                print('Congratulations! You won!')
                break

            print("Computer's turn:")
            r, c = choice(computer_choice)
            computer_choice.remove((r, c))
            print(f'Computer hit {chr(97 + r).upper()}{c + 1}. ')

            ship = self.player.board_play[r, c]
            hit = ship != '.'
            self.player.board_print.update_board(r, c, hit)

            if hit:
                print('Computer hit your ship!')
                self.hit_ship(ship, 'Computer sank your')
            else:
                print('Computer missed!')
            print()

            if self.player.has_lost():
                print('Sorry, you lost.')
                break

    def hit_ship(self, ship: Ship, frase: str):
        """  trace achievements """
        ship.hit += 1
        if ship.is_sunk():
            print(f'{frase} {ship.name}!')
            self.trace_achievements()

    def trace_achievements(self):
        """ print achievements"""
        players = [self.player.board_play.trace(), self.computer.board_play.trace()]
        trace = pd.DataFrame(players, index=['Computer', 'Player'])
        print('********************************************************')
        print('Achievements by now:')
        print(f'{trace}')
        print('********************************************************')

def before_release_check():
    """ test cases examples"""
    # ****** Ship ******
    # 1.
    ship = Ship('Destroyer', 2)
    ship.hit = 2
    assert ship.is_sunk() == True, '#1 expected answer: True'

    # ***** Board *****
    # 2. test a board access
    board = Board(0, 10)
    board[0, 7] = ship.name[0]
    for i in range(10):
        print('| ' + chr(ord('A') + i) + ' | ' + ' '.join(
            [board[i, j] for j in range(10)]))
    print()

    # ***** Player *****
    # 3. test inputs validation
    tester = Player()
    test_cases = ['a10', 'a12', 'u1', '11', 'c0', '/']

    for cell in test_cases:
        try:
            if cell == 'a10':
                assert tester.validate_position(cell) == (0, 9), \
                    f'#3. Expected answer for {cell}: (0, 9)'
            else:
                assert tester.validate_position(cell) == False, f'#3. Expected answer for {cell}: False'
        except IndexError as e:
            print(f'#3. {e} - IndexError is resolved in a try/except part -for input: {cell}')
    print()

    # 4. test printing boards
    guess = Board(1, 11)
    tester.place_ships_randomly()
    tester.print_boards()


if __name__ == '__main__':
    # before_release_check()
    game = Game()
    game.play()
