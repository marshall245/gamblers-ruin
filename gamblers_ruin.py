# Gambler's Ruin
import random
import argparse
import math


# Constants used in argparser below
N_PLAYERS = 1000
GAMES_PER_PLAYER = 52
PLAYER_BANK = 10000
BETSIZE = 10000
WIN_PROBABILITY = 0.5
WIN_MULTIPLIER = 1.5
LOSS_MULTIPLIER = 0.6


class Gambler:
    def __init__(self, bank=1000000):
        self.starting_bank = bank
        self.bank_ts = [bank]

    def update_bank(self, value):
        self.bank_ts.append(value)
    
    @property
    def bank(self):
        return self.bank_ts[-1]

class Game:
    def __init__(self, win_probability, win_multiplier, loss_multiplier):
        self._prob_win = win_probability
        self._win_multiplier = win_multiplier
        self._loss_multiplier = loss_multiplier
    
    def play(self, gambler, betsize):
        # NOTE : mutates gambler

        # gamblers cannot bet more than they have, will bet all if under betsize
        betsize = min(gambler.bank, betsize)

        flip = random.random()

        multiplier = None
        if flip < self._prob_win:
            multiplier = self._win_multiplier
        else:
            multiplier = self._loss_multiplier
        
        # bank - bet + bet * outcome_multiplier
        # if the whole bank is bet, this degenrates to bank * multiplier
        new_bank = gambler.bank + betsize * (multiplier - 1)
        if new_bank < 0.01:
            new_bank = 0

        gambler.update_bank(new_bank)


class Tournament:
    def __init__(self, n_players, games_per_player, player_bank, betsize, 
                 win_probability, win_multiplier, loss_multiplier):
        self._n_players = n_players
        self._win_probability = win_probability
        self._win_multiplier = win_multiplier
        self._loss_multiplier = loss_multiplier
        self.betsize = betsize
        self.games_per_player = games_per_player
        self._players_bank = player_bank
        self.game = Game(win_probability, win_multiplier, loss_multiplier)
        self.gamblers = [Gambler(player_bank) for ix in range(n_players)]
        
        # set post play
        self._post_game_holdings = None
        self._players_ahead = None
        self._players_ahead_percentage = None
        self._post_game_min = None
        self._post_game_max = None
        self._post_game_median = None
        self._post_game_avg = None

    def play(self):
        for _ in range(self.games_per_player):
            for gambler in self.gamblers:
                self.game.play(gambler, self.betsize)

        self._set_post_game_holdings()
        self._set_post_game_summary_numbers()

    def _set_post_game_holdings(self):
        self._post_game_holdings = [gambler.bank for gambler in self.gamblers]
        self._post_game_holdings.sort()

    def _set_post_game_summary_numbers(self):
        self._post_game_max = max(self._post_game_holdings)
        self._post_game_min = min(self._post_game_holdings)
        self._post_game_avg = sum(self._post_game_holdings) / float(len(self._post_game_holdings))
        
        # set post_game_median
        median_ix = math.ceil(len(self._post_game_holdings) / 2.0) - 1  # for len 8 take position 4, for length 9 position 5
        self._post_game_median = self._post_game_holdings[median_ix]

        # set players ahead and ahead percentage
        self._players_ahead = 0
        for val in self._post_game_holdings:
            if (val - self._players_bank) > 0:
                self._players_ahead += 1

        self._players_ahead_percentage = self._players_ahead / float(len(self._post_game_holdings)) * 100
        

    @property
    def post_game_holdings(self):
        if self._post_game_holdings is None:
            raise RuntimeError('games not played yet')
        return self._post_game_holdings

    def get_banner(self):
        banner_template = """
        Casino Setup
        ------------
        Player Count     :  {n_players}
        Games Per Player :  {games}
        Player Buy In    :  {bank}
        Betsize          :  {bet}
        Win Probability  :  {winprob}
        Win Multiplier   :  {win_mult}
        Loss Multiplier  :  {loss_mult}


        Outcomes
        --------
        Players Ending Ahead       : {ahead}
        Average Post Game Holdings : {avg_post_game}
        Median Post Game Holdings  : {med_post_game}
        Min Post Game Holdings     : {min_post_game}
        Max Post Game Holdings     : {max_post_game}
        """

        banner = banner_template.format(
            n_players=self._n_players,
            games=self.games_per_player,
            bank=self._players_bank,
            bet=self.betsize,
            winprob=self._win_probability,
            win_mult=self._win_multiplier,
            loss_mult=self._loss_multiplier,
            ahead=self._players_ahead,
            avg_post_game=self._post_game_avg,
            med_post_game=self._post_game_median,
            min_post_game=self._post_game_min,
            max_post_game=self._post_game_max
        )

        return banner

    def show_banner(self):
        banner = self.get_banner()
        print(banner)

    def show_end_of_game_holdings(self):
        banner = """
        

        End of Game Holdings Per Player
        -------------------------------"""

        print(banner)
        for bank in self._post_game_holdings:
            print('\t{0}'.format(bank))



if __name__ == "__main__":
    # parse commandline
    parser = argparse.ArgumentParser()

    parser.add_argument('--n-players', default=N_PLAYERS, type=int, dest='n_players')
    parser.add_argument('--games-per-player', default=GAMES_PER_PLAYER, type=int, dest='games_per_player')
    parser.add_argument('--player-bank', default=PLAYER_BANK, type=float, dest='player_bank')
    parser.add_argument('--betsize', default=BETSIZE, type=int, dest='betsize')
    parser.add_argument('--win-probability', default=WIN_PROBABILITY, type=float, dest='win_prob')
    parser.add_argument('--win-multiplier', default=WIN_MULTIPLIER, type=float, dest='win_multiplier')
    parser.add_argument('--loss-multiplier', default=LOSS_MULTIPLIER, type=float, dest='loss_multiplier')
    parser.add_argument('--show-eog-holdings', action='store_true', dest='show_eog_holdings')

    args = parser.parse_args()

    # play games
    tournament = Tournament(args.n_players, args.games_per_player, args.player_bank, args.betsize,
                            args.win_prob, args.win_multiplier, args.loss_multiplier)

    tournament.play()

    # report
    tournament.show_banner()

    if args.show_eog_holdings:
        tournament.show_end_of_game_holdings()