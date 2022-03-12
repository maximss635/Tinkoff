from game_model import GameModel


if __name__ == "__main__":
    game = GameModel()
    game_result = game.run_game()

    if game_result:
        print('Congratulations, you win!!!')
    else:
        print('You lose(((')

    exit(0)
