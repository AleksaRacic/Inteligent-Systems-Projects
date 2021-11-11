import pygame
import os
import config
import math


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, row, col, file_name, transparent_color=None):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (col * config.TILE_SIZE, row * config.TILE_SIZE)
        self.row = row
        self.col = col


class Agent(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Agent, self).__init__(row, col, file_name, config.DARK_GREEN)

    def move_towards(self, row, col):
        row = row - self.row
        col = col - self.col
        self.rect.x += col
        self.rect.y += row

    def place_to(self, row, col):
        self.row = row
        self.col = col
        self.rect.x = col * config.TILE_SIZE
        self.rect.y = row * config.TILE_SIZE

    # game_map - list of lists of elements of type Tile
    # goal - (row, col)
    # return value - list of elements of type Tile
    def get_agent_path(self, game_map, goal):
        pass

    @staticmethod
    def check_bounds(position, bounds):
        if(all([x >= 0 for x in position])):
            if(position[0]<bounds[0] and position[1]<bounds[1]):
                return True
        else:
            return False


class ExampleAgent(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        row = self.row
        col = self.col
        while True:
            if row != goal[0]:
                row = row + 1 if row < goal[0] else row - 1
            elif col != goal[1]:
                col = col + 1 if col < goal[1] else col - 1
            else:
                break
            path.append(game_map[row][col])
        return path

class Aki(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]
        directions = { 'west': [0, -1] , 'south' : [1, 0], 'east' : [0, 1], 'north': [-1, 0]}
        bounds = [len(game_map), len(game_map[0])]
        row = self.row
        col = self.col
        position = [row, col]
        check_point = 0
        while True:
            next_move_cost = 1500
            next_move = None
            for direction in directions.values():
                move = [pos+mov for pos,mov in zip(position, direction)]
                if(Agent.check_bounds(move, bounds) ):
                    tile = game_map[move[0]][move[1]]
                    if(tile not in path and tile.cost() <= next_move_cost):
                        next_move = tile
                        next_move_cost = tile.cost()
                    
            if(next_move == None):
                next_move = path[check_point]
                check_point -= 1
            else:
                check_point = len(game_map)
            row = next_move.row
            col = next_move.col 
            position = [row, col]
            path.append(game_map[row][col])
            if(row == goal[0] and col == goal[1]):
                break
        return path

class Jocke(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    @staticmethod
    def calculate_surrounding_cost(tile, game_map):
        directions = { 'west': [0, -1] , 'south' : [1, 0], 'east' : [0, 1], 'north': [-1, 0]}
        position = [tile.row, tile.col]
        bounds = [len(game_map), len(game_map[0])]
        cost = 0
        count = 0
        for direction in directions.values():
            move = [pos+mov for pos,mov in zip(position, direction)]
            if(Agent.check_bounds(move, bounds)):
                tile = game_map[move[0]][move[1]]
                cost +=tile.cost()
                count += 1
        if count == 0:
            return 1500
        return cost//count

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]
        tiles_heap = [game_map[self.row][self.col]]
        directions = { 'west': [0, -1] , 'south' : [1, 0], 'east' : [0, 1], 'north': [-1, 0]}
        bounds = [len(game_map), len(game_map[0])]
        row = self.row
        col = self.col
        position = [row, col]
        cursor = 1
        prev_cursor = 0
        prev_tile = game_map[self.row][self.col]
        while True:
            tile_surrounding = []
            #get neigbours
            for direction in directions.values():
                move = [pos + mov for pos,mov in zip(position, direction)]
                if(Agent.check_bounds(move, bounds)):
                    tile = game_map[move[0]][move[1]]
                    if(tile not in path and tile not in tiles_heap):
                        tile_surrounding.append(tile)
                    
            t_len = len(tile_surrounding)
            #Sort the tile_surrounding
            for i in range(0,t_len-1):
                for j in range(i+1,t_len):
                    if(Jocke.calculate_surrounding_cost(tile_surrounding[i], game_map) > Jocke.calculate_surrounding_cost(tile_surrounding[j], game_map)):
                        tmp = tile_surrounding[i]
                        tile_surrounding[i] = tile_surrounding[j]
                        tile_surrounding[j] = tmp

            #Adding surrounding to heap
            for tl in tile_surrounding:
                tiles_heap.append(tl)
            for _ in range(4-len(tile_surrounding)):
                tiles_heap.append(None)
            print("heap", len(tiles_heap))

            
            #Skipping empty branches
            while(tiles_heap[cursor] == None):
                for _ in range(4):
                    tiles_heap.append(None)
                cursor += 1
                print("heap", len(tiles_heap))
            
            next_tile  = tiles_heap[cursor]

            #Finding antsestors
            next_antsestors = []
            next_antsestor = (cursor - 1) // 4
            while(prev_cursor != next_antsestor):
                if(prev_cursor < next_antsestor):
                    next_antsestors.insert(0, tiles_heap[next_antsestor])
                    next_antsestor = (next_antsestor - 1) // 4
                else:
                    if(path[-1] != tiles_heap[prev_cursor] and tiles_heap[prev_cursor] != None):
                        path.append(tiles_heap[prev_cursor])
                    prev_cursor = (prev_cursor - 1) // 4

            if(path[-1] != tiles_heap[prev_cursor] and tiles_heap[prev_cursor] != None):
                path.append(tiles_heap[prev_cursor])

            for i in next_antsestors:
                if(path[-1] != i and i != None):
                    path.append(i)

            row = next_tile.row
            col = next_tile.col 
            position = [row, col]
            path.append(game_map[row][col])

            prev_tile = next_tile
            prev_cursor = cursor
            cursor += 1
            
            if(row == goal[0] and col == goal[1]):
                break
        return path

class Draza(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    @staticmethod
    def __get_cost(path_dict):
        return path_dict['cost']

    def get_agent_path(self, game_map, goal):
        directions = { 'west': [0, -1] , 'south' : [1, 0], 'east' : [0, 1], 'north': [-1, 0]}
        bounds = [len(game_map), len(game_map[0])]
        paths = [{'cost': 0, 'path' : [game_map[self.row][self.col]], 'last_pos': (self.row, self.col)}]

        while True:
            #sort path
            paths.sort(key=Draza.__get_cost)
            
            #take first and return if the goal is reached
            path = paths.pop(0)
            if path['last_pos'] == goal:
                return path['path']

            #branch(reevaluate costs)

            #find neigbours
            for direction in directions.values():
                move = [pos + mov for pos,mov in zip(list(path['last_pos']), direction)]
                if(Agent.check_bounds(move, bounds)):
                    tile = game_map[move[0]][move[1]]
                    if(tile not in path['path']):
                        #Add new path to paths
                        new_path = dict(path)
                        new_path['cost'] += tile.cost()
                        new_path['path'] = path['path'].copy()
                        new_path['path'].append(tile)
                        new_path['last_pos'] = (tile.row, tile.col)
                        paths.append(new_path)

class Bole(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)
    #Heuristika: da li se prelaskom u cvor priblizavamo ili udaljavamo cilju
    @staticmethod
    def __heuristics(new_position, old_position, goal):
        return (sum([abs(x-y) for x, y in zip(new_position, list(goal))]) - sum([abs(x-y) for x, y in zip(old_position, list(goal))])) * 100

        
    @staticmethod
    def __get_cost(path_dict):
        return path_dict['cost'] + path_dict['heuristic']

    def get_agent_path(self, game_map, goal):
        directions = { 'west': [0, -1] , 'south' : [1, 0], 'east' : [0, 1], 'north': [-1, 0]}
        bounds = [len(game_map), len(game_map[0])]
        paths = [{'cost': 0, 'path' : [game_map[self.row][self.col]], 'last_pos': (self.row, self.col), 'heuristic' : 0}]

        row = self.row
        col = self.col
        while True:
            #sort path
            paths.sort(key=Bole.__get_cost)
            
            #take first and return if the goal is reached
            path = paths.pop(0)
            if path['last_pos'] == goal:
                return path['path']

            #branch(reevaluate costs)

            #find neigbours
            for direction in directions.values():
                move = [pos + mov for pos,mov in zip(list(path['last_pos']), direction)]
                if(Agent.check_bounds(move, bounds)):
                    tile = game_map[move[0]][move[1]]
                    if(tile not in path['path']):
                        #Add new path to paths
                        new_path = dict(path)
                        new_path['cost'] += tile.cost()
                        new_path['path'] = path['path'].copy()
                        new_path['path'].append(tile)
                        new_path['heuristic'] = Bole.__heuristics(move, list(path['last_pos']), goal)
                        new_path['last_pos'] = (tile.row, tile.col)
                        paths.append(new_path)

class Tile(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Tile, self).__init__(row, col, file_name)

    def position(self):
        return self.row, self.col

    def cost(self):
        pass

    def kind(self):
        pass


class Stone(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'stone.png')

    def cost(self):
        return 1000

    def kind(self):
        return 's'


class Water(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'water.png')

    def cost(self):
        return 500

    def kind(self):
        return 'w'


class Road(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'road.png')

    def cost(self):
        return 2

    def kind(self):
        return 'r'


class Grass(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'grass.png')

    def cost(self):
        return 3

    def kind(self):
        return 'g'


class Mud(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'mud.png')

    def cost(self):
        return 5

    def kind(self):
        return 'm'


class Dune(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'dune.png')

    def cost(self):
        return 7

    def kind(self):
        return 's'


class Goal(BaseSprite):
    def __init__(self, row, col):
        super().__init__(row, col, 'x.png', config.DARK_GREEN)


class Trail(BaseSprite):
    def __init__(self, row, col, num):
        super().__init__(row, col, 'trail.png', config.DARK_GREEN)
        self.num = num

    def draw(self, screen):
        text = config.GAME_FONT.render(f'{self.num}', True, config.WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
