from random import randint
from action_handler import *


class GameModel:
    def __init__(self):
        field_size = self.__input_int_param("Enter field size: ")
        self.__bomp_count = self.__input_int_param("Enter bomp count: ")

        self.__field_real_model = []
        self.__field_view_model = []
        self.__generate_field(field_size)

        self.__bomps_founs = 0
        self.__false_positive_bomps = 0
        self.__is_win = False

        self.__action_handler = CommandHandler(self.__field_real_model,
                                               self.__field_view_model,
                                               self)

    def reload(self, new_field_view_model, bomps_location):
        self.__bomp_count = len(bomps_location)
        self.__field_view_model = new_field_view_model
        self.__field_real_model = []

        for i in range(len(new_field_view_model)):
            line = []
            for j in range(len(new_field_view_model)):
                if (i, j) in bomps_location:
                    line.append(CELL_TYPE_BOMP)
                else:
                    line.append(CELL_TYPE_NONE)
            self.__field_real_model.append(line)

        return self.__field_real_model

    def __input_int_param(self, s):
        while True:
            try:
                return int(input(s))
            except:
                continue

    def __generate_field(self, field_size):
        for i in range(field_size):
            line1 = []
            line2 = []
            for j in range(field_size):
                line1.append(CELL_TYPE_NONE)
                line2.append(CELL_VIEW_TYPE_NONE)

            self.__field_real_model.append(line1)
            self.__field_view_model.append(line2)

        bomps_coordinates = []
        for i in range(self.__bomp_count):
            while True:
                x, y = randint(0, field_size-1), randint(0, field_size-1)
                #print("[bomp] " + str(x+1) + ' ' + str(y+1))
                if (x, y) not in bomps_coordinates:
                    break
            bomps_coordinates.append((x, y))

        for x, y in bomps_coordinates:
            self.__field_real_model[x][y] = CELL_TYPE_BOMP
            #self.__field_view_model[x][y] = '^'

    def __parse_command(self, s_command):
        command = Command()
        if s_command == "help":
            command.is_help = True
            return command
        elif s_command == "exit":
            command.is_exit = True
            return command
        elif s_command == "save":
            command.is_save = True
            return command
        elif s_command == "load":
            command.is_load = True
            return command

        spl = s_command.split(' ')
        try:
            command.action = spl[2]
            command.x = int(spl[0])
        except:
            if spl[0] == '*':
                command.all_column = True
            else:
                return None

        try:
            command.y = int(spl[1])
        except:
            if spl[1] == '*':
                command.all_line = True
            else:
                return None

        return command

    def __update_view(self):
        print('    ', end='')
        for i in range(len(self.__field_real_model)):
            if i < 8:
                print(i + 1, end='  ')
            else:
                print(i + 1, end=' ')
        print()
        print('    ', end='')
        for i in range(3 * len(self.__field_real_model)):
            print('_', end='')
        print()
        for i, line in enumerate(self.__field_view_model):
            if i < 9:
                print(i+1, end='  |')
            else:
                print(i+1, end=' |')

            for element in line:
                print(element, end='  ')
            print()

    def run_game(self):
        self.__update_view()
        print()

        while True:
            s = input("Sapper> ")

            command = self.__parse_command(s)
            if command is None:
                print('Error parsing command: ' + s)
                continue

            if command.all_column:
                for x in range(len(self.__field_real_model)):
                    command.x = x + 1
                    update, lose = self.__action_handler.handle(command)
            elif command.all_line:
                for y in range(len(self.__field_real_model)):
                    command.y = y + 1
                    update, lose = self.__action_handler.handle(command)
            else:
                update, lose = self.__action_handler.handle(command)

            if update:
                if lose:
                    return False

                self.__update_view()

            if self.__is_win:
                return True

    def __check_win(self):
        if (self.__bomp_count == self.__bomps_founs) and \
                (self.__false_positive_bomps == 0):
            self.__is_win = True

    def found_bomp(self):
        self.__bomps_founs += 1
        self.__check_win()

    def false_positive_bomp_inc(self):
        self.__false_positive_bomps += 1

    def false_positive_bomp_dec(self):
        self.__false_positive_bomps -= 1
        self.__check_win()

    def get_bomps_count(self):
        return self.__bomp_count

    def get_field_size(self):
        return len(self.__field_view_model)


