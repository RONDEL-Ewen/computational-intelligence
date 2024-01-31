import random
from game import Game, Move, Player
from copy import deepcopy


class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        return from_pos, move


class MyPlayer(Player):

    def __init__(
        self,
        depth = 2
    ):
        '''Initialize a player using Minimax algorithm with Alpha-Beta pruning'''

        super().__init__()
        self.depth = depth # Determine how many moves ahead the algorithm will evaluate


    def make_move(
        self,
        game: 'Game'
    ) -> tuple[tuple[int, int], Move]:
        '''Make a move'''

        # Call the Minimax algorithm to get the best move
        best_score, best_move = self.minimax(game, self.depth, -float('inf'), float('inf'), True)
        from_pos, move = best_move

        return (from_pos[1], from_pos[0]), move # Invert (x,y) into (y,x) because it is mixed up in Game.__move()


    def minimax(
        self,
        game: 'Game',
        depth: int,
        alpha: float,
        beta: float,
        maximizing_player: bool
    ):
        '''Choose the best possible move according to the Minimax algorithm with Alpha-Beta pruning'''

        # If the current player wins the game with this state
        winner = game.check_winner()
        if winner == game.get_current_player():
            return 10000, None
        # If the opponent wins the game with this state
        elif winner != -1:
            return -10000, None
        # If the desired depth has been reached
        elif depth == 0:
            return self.evaluate_game(game, game.get_current_player()), None

        # Get all possible moves from this state
        possible_moves = self.get_possible_moves(game)

        # If it's the turn of the player maximizing the score
        if maximizing_player:
            # Initialize the max evaluation score
            max_eval = -float('inf')
            # Initialize the list of the best moves (in case mutiple moves have the same best score)
            best_moves = []

            # Go through every possible moves
            for move in possible_moves:

                # Simulate the move from the current state
                new_game = self.simulate_move(deepcopy(game), move, game.get_current_player())
                # Recursive call of the Minimax algorithm until it reaches the desired depth
                eval = self.minimax(new_game, depth-1, alpha, beta, False)[0] # Switch to minimizing

                # If the move has a better score than the previous best move(s)
                if eval > max_eval:
                    max_eval = eval
                    best_moves = [move]
                # If the move has the same score than the previous best move(s)
                elif eval == max_eval:
                    best_moves.append(move)

                # Update alpha
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Alpha-Beta pruning

            # Return the best move with its score (or one random move if multiple moves have the same best score)
            return max_eval, random.choice(best_moves)

        # If it's the turn of the player minimizing the score
        else:
            # Initialize the min evaluation score
            min_eval = float('inf')
            best_moves = []

            for move in possible_moves:

                # Iterate over all possible moves
                new_game = self.simulate_move(deepcopy(game), move, game.get_current_player())
                eval = self.minimax(new_game, depth-1, alpha, beta, True)[0]  # Switch to maximizing

                if eval < min_eval:
                    min_eval = eval
                    best_moves = [move]
                elif eval == min_eval:
                    best_moves.append(move)

                # Update beta
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha-Beta pruning

            return min_eval, random.choice(best_moves)


    def get_possible_moves(
        self,
        game: 'Game',
        limit = 10      #Used only if there is a need to save computing resources -> return only the supposed X best moves (and not all)
    ):
        '''List all possible moves from the current state of the game'''

        moves = []
        # Try every coordinates
        for x in range(5):
            for y in range(5):
                # Try every direction
                for direction in [Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT]:
                    # Add the move to the list only if valid
                    if self.is_valid_move(game, (x, y), direction):
                        moves.append(((x, y), direction))

        # Evaluate briefly every move
        #evaluated_moves = [(self.evaluate_move(game, move), move) for move in moves]
        # Rank all the moves from 'best' to 'worst'
        #evaluated_moves.sort(key=lambda x: x[0], reverse=True)
        # Limit to X number of moves to only keep the 'best'
        #limited_moves = evaluated_moves[:limit]
        # Suffle the best kept moves
        #random.shuffle(limited_moves)
        # Return only the 'best' moves
        #return [move for score, move in limited_moves]

        return moves


    def simulate_move(
        self,
        simulated_game: 'Game',
        move: tuple[tuple[int, int], Move],
        player_id: int
    ) -> 'Game':
        '''Simulate a move on the board'''
        # This function is used because some functions in the Game class are private and can't be accessed from the MyPlayer class

        # Get move's coordinates and direction
        from_pos, slide = move
        # Invert (x,y) into (y,x) because it is mixed up in Game.__move()
        y, x = from_pos

        # Check if the move is valid before continuing
        if not self.is_valid_move(simulated_game, from_pos, slide):
            return simulated_game

        # Effectue la prise de la pièce si nécessaire
        if simulated_game._board[y, x] == -1 or simulated_game._board[y, x] == player_id:
            simulated_game._board[y, x] = player_id
        else:
            # Si le mouvement n'est pas valide, retourne le jeu sans modification
            return simulated_game

        # Slide to the left if this is the selected direction
        if slide == Move.LEFT:
            temp = simulated_game._board[y, 0]
            for i in range(0, x):
                simulated_game._board[y, i] = simulated_game._board[y, i + 1]
            simulated_game._board[y, x] = temp

        # Slide to the right if this is the selected direction
        elif slide == Move.RIGHT:
            temp = simulated_game._board[y, simulated_game._board.shape[1] - 1]
            for i in range(simulated_game._board.shape[1] - 1, x, -1):
                simulated_game._board[y, i] = simulated_game._board[y, i - 1]
            simulated_game._board[y, x] = temp

        # Slide to the top if this is the selected direction
        elif slide == Move.TOP:
            temp = simulated_game._board[0, x]
            for i in range(0, y):
                simulated_game._board[i, x] = simulated_game._board[i + 1, x]
            simulated_game._board[y, x] = temp

        # Slide to the bottom if this is the selected direction
        elif slide == Move.BOTTOM:
            temp = simulated_game._board[simulated_game._board.shape[0] - 1, x]
            for i in range(simulated_game._board.shape[0] - 1, y, -1):
                simulated_game._board[i, x] = simulated_game._board[i - 1, x]
            simulated_game._board[y, x] = temp

        # Update the player ID for the simulation
        simulated_game.current_player_idx = 1 - player_id

        return simulated_game


    def evaluate_game(
        self,
        game: 'Game',
        player_id: int
    ):
        '''Evaluate the board'''

        # Initialize the score
        score = 0
        # Get the board
        board = game.get_board()

        # Evaluate rows and columns for completion potential
        for i in range(5):
            row = board[i, :]
            column = board[:, i]
            score += self.evaluate_line(row, player_id)
            score += self.evaluate_line(column, player_id)

        # Evaluate the diagonals for completion potential
        first_diagonal = [board[i, i] for i in range(5)]
        second_diagonal = [board[i, 4 - i] for i in range(5)]
        score += self.evaluate_line(first_diagonal, player_id)
        score += self.evaluate_line(second_diagonal, player_id)

        # Other strategies could be added here

        return score


    def evaluate_line(
        self,
        line,
        player_id
    ):
        '''Evaluate the line (row, column or diagonal)'''

        # Initialize the score
        score = 0
        # Get the opponent ID
        opponent_id = 1 if player_id == 0 else 0

        # Count the number of pieces of each sort (current player, opponent, neutral)
        player_pieces = sum(piece == player_id for piece in line)
        neutral_pieces = sum(piece == -1 for piece in line)
        opponent_pieces = sum(piece == opponent_id for piece in line)

        # Scoring for the player's pieces
        if player_pieces == 5:
            return 10000
        if player_pieces == 4 and neutral_pieces == 1:
            score += 100
        elif player_pieces == 4 and opponent_pieces == 1:
            score += 50
        elif player_pieces == 3 and neutral_pieces == 2:
            score += 20
        elif player_pieces == 3 and opponent_pieces == 1:
            score += 15
        elif player_pieces == 3 and opponent_pieces == 2:
            score += 10
        elif player_pieces == 2 and neutral_pieces == 3:
            score += 5
        elif player_pieces == 2 and neutral_pieces == 2:
            score += 1

        # Penalize if the opponent is close to winning
        if opponent_pieces == 5:
            return -10000
        if opponent_pieces == 4 and neutral_pieces == 1:
            score -= 100
        elif opponent_pieces == 4 and player_pieces == 1:
            score -= 50
        elif opponent_pieces == 3 and neutral_pieces == 2:
            score -= 20
        elif opponent_pieces == 3 and neutral_pieces == 1:
            score -= 10

        return score


    def evaluate_move(
        self,
        game: 'Game',
        move: tuple[tuple[int, int], Move]
    ):
        '''Evaluate a simulated move'''

        # Simulate the move
        simulated_game = self.simulate_move(deepcopy(game), move, game.get_current_player())

        # Briefly evaluate the simulated move
        simulated_score = self.evaluate_game(simulated_game, game.get_current_player())

        return simulated_score


    def is_valid_move(
        self,
        game: 'Game',
        position: tuple[int, int],
        move: Move
    ):
        '''Check if a move is valid'''

        # Get the move coordinates
        x, y = position

        # Get the current state of the game
        board = game.get_board()
        # Get the current player ID
        player_id = game.get_current_player()

        # Check if the piece is on an edge
        is_on_edge = x in [0, 4] or y in [0, 4]
        # Check if the piece is neutral or owned by the current player
        is_free_or_own_piece = board[x, y] in [-1, player_id]
        if not is_on_edge or not is_free_or_own_piece:
            return False

        # Define the corners
        CORNERS = [(0, 0), (0, 4), (4, 0), (4, 4)]

        # If the piece is not in a corner
        if position not in CORNERS:
            # Define the possible directions for the different edges
            acceptable_top = (x == 0) and (move in [Move.BOTTOM, Move.LEFT, Move.RIGHT])
            acceptable_bottom = (x == 4) and (move in [Move.TOP, Move.LEFT, Move.RIGHT])
            acceptable_left = (y == 0) and (move in [Move.BOTTOM, Move.TOP, Move.RIGHT])
            acceptable_right = (y == 4) and (move in [Move.BOTTOM, Move.TOP, Move.LEFT])

        # If the piece is in a corner
        else:
            # Define the possible directions for the different corners
            acceptable_top = (position == (0, 0)) and (move in [Move.BOTTOM, Move.RIGHT])
            acceptable_left = (position == (4, 0)) and (move in [Move.TOP, Move.RIGHT])
            acceptable_right = (position == (0, 4)) and (move in [Move.BOTTOM, Move.LEFT])
            acceptable_bottom = (position == (4, 4)) and (move in [Move.TOP, Move.LEFT])

        # Check if the direction is possible
        acceptable = acceptable_top or acceptable_bottom or acceptable_left or acceptable_right

        return acceptable


if __name__ == '__main__':
    g = Game()
    g.print()
    player1 = MyPlayer()
    player2 = RandomPlayer()
    winner = g.play(player1, player2)
    g.print()
    print(f"Winner: Player {winner}")
