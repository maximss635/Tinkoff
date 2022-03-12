from constants import *
from my_rsa import *

import re

bfs_queue = []

class Command:
    def __init__(self):
        self.is_help = False
        self.is_exit = False
        self.is_save = False
        self.is_load = False

        self.x, self.y = -1, -1
        self.action = str()

        self.all_line = False
        self.all_column = False


class CommandHandler:
    def __init__(self, field_real_model, field_view_model, game_model):
        self.__field_real_model = field_real_model
        self.__field_view_model = field_view_model
        self.__cells_queue = set()
        self.__game_model = game_model

    # return 1) need show field / 2) is user lose

    def handle(self, command):
        if command.is_help:
            self.__help()
            return False, False

        if command.is_exit:
            exit(0)

        if command.is_save:
            self.__backup()
            return False, False

        if command.is_load:
            res = self.__load()
            return res, False

        if command.x <= 0 or command.x > len(self.__field_real_model):
            print("Wrong x param: " + str(command.x))
            return False, False

        if command.y <= 0 or command.y > len(self.__field_real_model):
            print("Wrong y param: " + str(command.y))
            return False, False

        if command.action == "Flag":
            self.__action_flag(command)

        elif command.action == "Open":
            if self.__action_open(command.x, command.y, []) == -1:
                return True, True

        else:
            print("Unknown command: " + command.action)
            return False, False

        return True, False

    def __action_open(self, x, y, visited):
       #print('__action_open {} {}'.format(x, y))

        if self.__field_real_model[x - 1][y - 1] == CELL_TYPE_BOMP:
            return -1

        global bfs_queue
        bfs_queue.append((x, y))
        visited.append((x, y))

        while bfs_queue:
            x, y = bfs_queue.pop()

            #print('pop {} {}'.format(x, y))
            #print(bfs_queue)

            if self.__field_view_model[x - 1][y - 1] == CELL_VIEW_TYPE_MARK_BOMP:
                self.__game_model.false_positive_bomp_dec()

            neighbours = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
                          (x - 1, y - 1), (x + 1, y + 1), (x - 1, y + 1), (x + 1, y - 1)]
            bomps_near_count = 0

            # Count bomps near
            for x_, y_ in neighbours:
                if (x_ <= 0) or (y_ <= 0) \
                        or (x_ > len(self.__field_real_model)) \
                        or (y_ > len(self.__field_real_model)):
                    continue
                if self.__field_real_model[x_ - 1][y_ - 1] == CELL_TYPE_BOMP:
                    bomps_near_count += 1

            self.__field_view_model[x - 1][y - 1] = bomps_near_count

            if bomps_near_count != 0:
                continue

            for x_, y_ in neighbours:
                if (x_ <= 0) or (y_ <= 0) \
                        or (x_ > len(self.__field_real_model)) \
                        or (y_ > len(self.__field_real_model)):
                    continue
                if (x_, y_) not in visited:
                    #print('append {} {}'.format(x_, y_))
                    visited.append((x_, y_))
                    bfs_queue.append((x_, y_))

    def __action_flag(self, command):
        self.__field_view_model[command.x - 1][command.y - 1] = CELL_VIEW_TYPE_MARK_BOMP

        if self.__field_real_model[command.x - 1][command.y - 1] == CELL_TYPE_BOMP:
            self.__game_model.found_bomp()
        else:
            self.__game_model.false_positive_bomp_inc()

    def __help(self):
        print("Commands:")
        print("\t<x> <y> <action>", end=', ')
        print("x, y - coordinates", end=', ')
        print("\taction = [Open, Flag]")
        print("\thelp - show this message")
        print("\tsave - make backup to file")
        print("\tload - load backup from file")
        print("\texit")

    def __backup(self):
        buffer = ''
        buffer += 'field_size={}, bomps_count={}\n'.format(
            self.__game_model.get_field_size(),
            self.__game_model.get_bomps_count()
        )

        bomps_location = []
        for i, line in enumerate(self.__field_real_model):
            for j, elem in enumerate(line):
                if elem == CELL_TYPE_BOMP:
                    bomps_location.append((i, j))

        for i, j in bomps_location:
            buffer += 'Bomp: {}, {}\n'.format(i, j)

        for line in self.__field_view_model:
            for element in line:
                buffer += str(element)
            buffer += '\n'

        crypted_buffer = my_rsa_encrypt(buffer, (1594536295583, 2321726850343)) # Open key - (e, d)

        file = open(BACKUP_FILE_NAME, 'wb')
        file.write(crypted_buffer)
        file.close()

    def __load(self):
        try:
            file = open(BACKUP_FILE_NAME, 'rb')
        except FileNotFoundError:
            print('Backup file not found: {}'.format(BACKUP_FILE_NAME))
            return False

        crypted_bytes = file.read()
        file.close()

        file_data = my_rsa_decrypt(crypted_bytes, (34862323487, 2321726850343)) # Private key - (d, n), e*d = 1(mod n)

        new_field_view_model, bomps_location = self.__parse_backup_data(file_data)

        self.__field_view_model = new_field_view_model
        self.__field_real_model = self.__game_model.reload(new_field_view_model, bomps_location)

        return True

    def __parse_backup_data(self, data):
        new_field_view_model = []
        line_array = data.split('\n')

        matches = re.search('field_size=(\\d+), bomps_count=(\\d+)', line_array[0])
        new_field_size = int(matches.group(1))
        new_bomps_count = int(matches.group(2))

        bomps_location = []
        for i in range(new_bomps_count):
            line = line_array[1 + i]
            matches = re.search('Bomp: (\\d+), (\\d+)', line)
            bomps_location.append((int(matches.group(1)), int(matches.group(2))))

        for i in range(new_field_size):
            model_line = []
            line = line_array[1 + new_bomps_count + i]
            for c in line:
                if c != '\n':
                    model_line.append(c)
            new_field_view_model.append(model_line)

        return new_field_view_model, bomps_location


