import random

# to generate diferent environments from the same initial scenary
class Initial_Scenary:
    def __init__(self, rows, columns, dirtyness, obstacles, kids, change_t):
        self.rows = rows
        self.columns = columns
        self.dirtyness = dirtyness
        self.obstacles = obstacles
        self.kids = kids
        self.change_t = change_t
    
    def generate_environment(self):
        return Environment(self.rows, self.columns, self.dirtyness, self.obstacles, self.kids, self.change_t)


# usefull during direction traveling
drow = [-1, 0, 1, 0]
dcolumn = [0, 1, 0, -1]
rdrow = [1, 0, -1, 0]
rdcolumn = [0, -1, 0, 1]

# board is an integer matrix such as:
# - -1 means an obstacle
# - 0 means an empty cell
# - 1 means robot in the cell
# - 2 means kid in the cell
# - 3 means a dirty cell
# - 4 means a crib cell
# - 5 means a occupied crib
class Environment:
    # initialize all environment objects
    def __init__(self, rows, columns, dirtyness, obstacles, kids, change_t):

        global drow, dcolumn
        self.rows = rows
        self.columns = columns
        self.dirtyness_p = dirtyness
        self.obstacles_p = obstacles
        self.kids_t = kids
        
        # board generation
        self.board = []
        for i in range(0, rows):
            row = []
            for j in range(0, columns):
                row.append(0)
            self.board.append(row)

        # cribs placing
        i_crib_row = random.randint(0, rows - 1)
        i_crib_column = random.randint(0, columns - 1)
        self.cribs = []
        self.boolean_mask = {}
        self.place_cribs_recursivelly(i_crib_row, i_crib_column, kids - 1)

        # kids placing
        empty_positions = self.get_board_empty_positions()

        kids_left = kids
        self.kids = []
        while kids_left > 0:
            r = random.randint(0, len(empty_positions) - 1)
            row = empty_positions[r][0]
            column = empty_positions[r][1]
            self.board[row][column] = 2
            self.kids.append(Kid(row, column, self))
            empty_positions = empty_positions[0: r] + empty_positions[r + 1: len(empty_positions)]
            kids_left -= 1

        # obstacles placing
        empty_positions = self.get_board_empty_positions()

        obstacles_count = int(rows * columns * (obstacles / 100))
        self.obstacles = []
        while obstacles_count > 0:
            r = random.randint(0, len(empty_positions) - 1)
            row = empty_positions[r][0]
            column = empty_positions[r][1]
            self.board[row][column] = -1
            self.obstacles.append(Obstacle(row, column, self))
            empty_positions = empty_positions[0: r] + empty_positions[r + 1: len(empty_positions)]
            obstacles_count -= 1

        # dirty placing
        empty_positions = self.get_board_empty_positions()

        dirty_count = int(rows * columns * (dirtyness / 100))
        self.dirty = []
        while dirty_count > 0:
            r = random.randint(0, len(empty_positions) - 1)
            row = empty_positions[r][0]
            column = empty_positions[r][1]
            self.board[row][column] = 3
            self.dirty.append(Dirtyness(row, column, self))
            empty_positions = empty_positions[0: r] + empty_positions[r + 1: len(empty_positions)]
            dirty_count -= 1

        # robot placing
        empty_positions = self.get_board_empty_positions()

        r = random.randint(0, len(empty_positions) - 1)
        row = empty_positions[r][0]
        column = empty_positions[r][1]

        self.robot = Robot_Model_A(row, column, self)
        self.board[row][column] = 1

        # set time related variables
        self.change_t = change_t
        self.to_change_left = change_t
        self.turn_counter = 0
        self.turn_limit = change_t * 100
    
    
  
    # return a copy of self with alternate model
    def copy_with_alternate_model(self):
        result = Environment(self.rows, self.columns, self.dirtyness_p, self.obstacles_p, self.kids_t, self.change_t)
        
        for i in range(0, self.rows):
            for j in range(0, self.columns):
                result.board[i][j] = self.board[i][j]

        for i in range(0, len(self.cribs)):
            result.cribs[i] = Crib(self.cribs[i].row, self.cribs[i].column, result)

        for i in range(0, len(self.dirty)):
            result.dirty[i] = Dirtyness(self.dirty[i].row, self.dirty[i].column, result)

        for i in range(0, len(self.obstacles)):
            result.obstacles[i] = Obstacle(self.obstacles[i].row, self.obstacles[i].column, result)

        for i in range(0, len(self.kids)):
            result.kids[i] = Kid(self.kids[i].row, self.kids[i].column, result)

        result.robot = Robot_Model_B(self.robot.row, self.robot.column, result)

        return result
        

    def get_board_empty_positions(self):
        empty_positions = []
        for i in range(0, self.rows):
            for j in range(0, self.columns):
                if self.board[i][j] == 0:
                    empty_positions.append((i, j))
        return empty_positions

    # recursivelly and randomly place cribs
    # returns True if the current branch found a way to put all the cribs
    def place_cribs_recursivelly(self, last_row, last_column, remain):
        global drow, dcolumn

        if (last_row, last_column) in self.boolean_mask:
            return False

        self.boolean_mask[(last_row, last_column)] = True
        
        if remain == 0:
            self.board[last_row][last_column] = 4
            self.cribs.append(Crib(last_row, last_column, self))
            return True
        
        valid_directions = []
        
        for i in range(0, 4):
            
            new_row = last_row + drow[i]
            new_column = last_column + dcolumn[i]
            
            if self.valid_position(new_row, new_column) and self.board[new_row][new_column] == 0:
                valid_directions.append(i)
        
        random.shuffle(valid_directions)
        
        for i in valid_directions:
        
            if self.place_cribs_recursivelly(last_row + drow[i], last_column + dcolumn[i], remain - 1):
                self.board[last_row][last_column] = 4
                self.cribs.append(Crib(last_row, last_column, self))
                return True
        
        return False

    def perform_turn(self):

        self.robot.perform_action()
        
        for kid in self.kids:
            kid.perform_action()
        
        # lose condition
        if self.too_much_dirty():
            return "Too much dirty"
        
        # win condition
        if self.all_kids_in_crib() and self.floor_cleansed():
            return "Kids in cribs and floor cleaned"
        
        # also lose condition
        self.turn_counter += 1
        if self.turn_counter == self.turn_limit:
            return "Turn Limit Reached"
        
        # when t turns passed shuffle all environment objects
        self.to_change_left -= 1
        if self.to_change_left == 0:
            self.make_environment_shuffle()
            self.to_change_left = self.change_t
        
        return "Nothing happened"

    def kid_at(self, row, column):
        for kid in self.kids:
            kid_pos = kid.get_position()
            if kid_pos[0] == row and kid_pos[1] == column:
                return kid
        return None

    def obstacle_at(self, row, column):
        for obs in self.obstacles:
            obs_pos = obs.get_position()
            if obs_pos[0] == row and obs_pos[1] == column:
                return obs
        return None

    def dirty_at(self, row, column):
        for di in self.dirty:
            di_pos = di.get_position()
            if di_pos[0] == row and di_pos[1] == column:
                return di
        return None

    def crib_at(self, row, column):
        for crib in self.cribs:
            crib_pos = crib.get_position()
            if crib_pos[0] == row and crib_pos[1] == column:
                return crib
        return None

    # lose condition
    def too_much_dirty(self):
         return self.dirtyness_percentage() > 0.6

    # outputs the current dirtyness percentage
    def dirtyness_percentage(self):
        total_empty_cells = 0
        dirty_cells = 0

        for i in range(0, self.rows):
            for j in range(0, self.columns):
                if self.board[i][j] != -1 and self.board[i][j] != 4:
                    total_empty_cells += 1
                if self.board[i][j] == 3:
                    dirty_cells += 1

        return (dirty_cells / total_empty_cells)

    # one of the win conditions
    def floor_cleansed(self):
        return len(self.dirty) == 0

    # the other win condition
    def all_kids_in_crib(self):
        total_kids = 0
        in_crib_kids = 0
        for kid in self.kids:
            total_kids += 1
            if kid.in_crib:
                in_crib_kids += 1
        return total_kids == in_crib_kids

    # when t turns passed shuffle all environment objects
    def make_environment_shuffle(self):
        global drow, dcolumn

        # empty board
        for i in range(0, self.rows):
            for j in range(0, self.columns):
                self.board[i][j] = 0

        # shuffle crib positions
        n_cribs = len(self.cribs)
        
        i_crib_row = random.randint(0, self.rows - 1)
        i_crib_column = random.randint(0, self.columns - 1)
        self.cribs = []
        self.boolean_mask = {}
        self.place_cribs_recursivelly(i_crib_row, i_crib_column, n_cribs - 1)
        ind = 0
        # put in cribs the kids that already are in crib
        for k in self.kids:
            if k.in_crib:
                k.change_position(self.cribs[ind].row, self.cribs[ind].column)
                self.cribs[ind].occupied = True
                self.board[self.cribs[ind].row][self.cribs[ind].column] = 5
                ind += 1
            
        # shuffle obstacles
        empty_positions = self.get_board_empty_positions()

        for o in self.obstacles:
            r = random.randint(0, len(empty_positions) - 1)
            row = empty_positions[r][0]
            column = empty_positions[r][1]
            self.board[row][column] = -1
            o.change_position(row, column)
            empty_positions = empty_positions[0: r] + empty_positions[r + 1: len(empty_positions)]

        # shuffle dirty cells
        empty_positions = self.get_board_empty_positions()

        for d in self.dirty:
            r = random.randint(0, len(empty_positions) - 1)
            row = empty_positions[r][0]
            column = empty_positions[r][1]
            self.board[row][column] = 3
            d.change_position(row, column)
            empty_positions = empty_positions[0: r] + empty_positions[r + 1: len(empty_positions)]
                
        # shuffle robot position
        empty_positions = self.get_board_empty_positions()

        old_robot_pos = self.robot.get_position()
        
        r = random.randint(0, len(empty_positions) - 1)
        row = empty_positions[r][0]
        column = empty_positions[r][1]
        self.board[row][column] = 1
        self.robot.change_position(row, column)
  
        if self.robot.is_carrying_kid:
            self.kid_at(old_robot_pos[0], old_robot_pos[1]).change_position(self.robot.row, self.robot.column)
        
        # shuffle remain kids position
        empty_positions = self.get_board_empty_positions()

        for kid in self.kids:
            if kid.in_crib or kid.in_robot_arms:
                continue
            
            r = random.randint(0, len(empty_positions) - 1)
            row = empty_positions[r][0]
            column = empty_positions[r][1]
            self.board[row][column] = 2
            kid.change_position(row, column)
            empty_positions = empty_positions[0: r] + empty_positions[r + 1: len(empty_positions)]    
        
        # reset shuffle time variables
        self.to_change_left = self.change_t
        
    # return True when row and column are between valid limits in the board
    def valid_position(self, row, column):
        return row >= 0 and column >= 0 and row < self.rows and column < self.columns


# basic class of environment objects
class Environment_Object:
    def __init__(self, initial_row, initial_column, environment):
        self.row = initial_row
        self.column = initial_column
        self.environment = environment
    
    def change_position(self, new_row, new_column):
        self.row = new_row
        self.column = new_column

    def get_position(self):
        return (self.row, self.column)


# inmobile or static objects base class
class Static_Object(Environment_Object):
    pass


class Obstacle(Static_Object):
    pass


class Crib(Static_Object):
    def __init__(self, initial_row, initial_column, environment):
        super().__init__(initial_row, initial_column, environment)
        self.occupied = False


class Dirtyness(Static_Object):
    pass
        

# movable objects base class
class Movable_Object(Environment_Object):
    def perform_action():
        pass


class Kid(Movable_Object):
    def __init__(self, initial_row, initial_column, environment):
        super().__init__(initial_row, initial_column, environment)
        self.generate_next_move_counter()
        self.in_crib = False
        self.in_robot_arms = False

    # the kid moves each 1-10 turns, the probability is the same for each number
    def generate_next_move_counter(self):
        self.next_move_counter = random.randint(1, 10)

    # perform action is the way of interact with the environment
    def perform_action(self):
        
        if self.in_crib or self.in_robot_arms:
            return

        self.next_move_counter -= 1
        
        if self.next_move_counter == 0:
            old_pos = self.get_position()
            self.move()
            self.put_dirty(old_pos[0], old_pos[1])
            self.generate_next_move_counter()
    
    # kid moving logic
    def move(self):
        global drow, dcolumn
        global rdrow, rdcolumn

        direction = random.randint(0, 3)
        
        new_row = self.row + drow[direction]
        new_column = self.column + dcolumn[direction]
        
        environment = self.environment
        board = environment.board

        while not environment.valid_position(new_row, new_column):
            direction = random.randint(0, 3)
        
            new_row = self.row + drow[direction]
            new_column = self.column + dcolumn[direction]
        

        # if facing an empty cell then just move
        if board[new_row][new_column] == 0:
            board[new_row][new_column] = 2
            
            if environment.robot.get_position() != (self.row, self.column):
                board[self.row][self.column] = 0
            else:
                board[self.row][self.column] = 1

            self.change_position(new_row, new_column)
        
        # if facing to obstacles then prepare to move them
        elif board[new_row][new_column] == -1:
            
            search_row = new_row + drow[direction]
            search_column = new_column + dcolumn[direction]
            
            # find first empty cell in the facing direction
            while environment.valid_position(search_row, search_column):
                
                if board[search_row][search_column] == -1:
                    search_row += drow[direction]
                    search_column += dcolumn[direction]
                
                # when founded an empty cell then move all obstacles in the facing direction
                elif board[search_row][search_column] == 0:

                    reverse_row = search_row + rdrow[direction]
                    reverse_column = search_column + rdcolumn[direction]
    
                    while board[reverse_row][reverse_column] == -1:
                        
                        board[reverse_row][reverse_column] = 0
                        board[search_row][search_column] = -1
                        
                        environment.obstacle_at(reverse_row, reverse_column).change_position(search_row, search_column)
                        
                        search_row = reverse_row
                        search_column = reverse_column
                        
                        reverse_row += rdrow[direction]
                        reverse_column += rdcolumn[direction]
                    
                    if environment.robot.get_position() != (reverse_row, reverse_column):
                        board[reverse_row][reverse_column] = 0
                    else:
                        board[reverse_row][reverse_column] = 1

                    board[search_row][search_column] = 2

                    self.change_position(search_row, search_column)
                    break
                else:
                    break


    # gets the kid surrounding info of empty cells and other kids
    def get_surrounding_info(self, row, column):
        dir_9_row = [-1, -1, 0, 1, 1, 1, 0, -1]
        dir_9_column = [0, 1, 1, 1, 0, -1, -1, -1]

        empty_cells = []
        kid_cells = 0

        environment = self.environment
        board = environment.board
        
        if board[row][column] == 2:
            kid_cells += 1
        else:
            empty_cells.append((row, column))

        for i in range(0, 8):
            new_row = row + dir_9_row[i]
            new_column = column + dir_9_column[i]
            if environment.valid_position(new_row, new_column):
                if board[new_row][new_column] == 0:
                    empty_cells += [(new_row, new_column)]
                elif board[new_row][new_column] == 2:
                    kid_cells += 1
        
        return empty_cells, kid_cells

    # kids put dirty from time to time
    # each dirty hast 0.4 of probability to generate
    def put_dirty(self, row, column):
        
        empty_cells, kid_cells = self.get_surrounding_info(row, column)
        
        environment = self.environment
        board = environment.board
        
        # if one kid in the surroundings put one dirty
        if kid_cells == 1:
            put_dirty = random.randint(0, 1000)
            if put_dirty > 600 and len(empty_cells) > 0:
                dirty_pos = empty_cells[random.randint(0, len(empty_cells) - 1)]
                board[dirty_pos[0]][dirty_pos[1]] = 3
                environment.dirty.append(Dirtyness(dirty_pos[0], dirty_pos[1], environment))
                empty_cells.remove(dirty_pos)

        # if two kid in the surroundings put up to three dirtyes
        elif kid_cells == 2:
            for i in range(0, 3):
                put_dirty = random.randint(0, 1000)
                if put_dirty > 600 and len(empty_cells) > 0:
                    dirty_pos = empty_cells[random.randint(0, len(empty_cells) - 1)]
                    board[dirty_pos[0]][dirty_pos[1]] = 3
                    environment.dirty.append(Dirtyness(dirty_pos[0], dirty_pos[1], environment))
                    empty_cells.remove(dirty_pos)
                else:
                    break
                
        # if more than two kid in the surroundings put up to six dirtyes
        elif kid_cells > 2:
            for i in range(0, 6):
                put_dirty = random.randint(0, 1000)
                if put_dirty > 600 and len(empty_cells) > 0:
                    dirty_pos = empty_cells[random.randint(0, len(empty_cells) - 1)]
                    board[dirty_pos[0]][dirty_pos[1]] = 3
                    environment.dirty.append(Dirtyness(dirty_pos[0], dirty_pos[1], environment))
                    empty_cells.remove(dirty_pos)
                else:
                    break


class Robot(Movable_Object):
    def __init__(self, initial_row, initial_column, environment):
        super().__init__(initial_row, initial_column, environment)
        self.is_carrying_kid = False
        self.current_task = "None"
        self.carrying_kid = None

    def perform_action(self):
        pass

    # only called if robot is in dirty cell with no kid in arms
    def clean_dirty(self):
        env = self.environment
        board = env.board
        board[self.row][self.column] = 1
        env.dirty.remove(env.dirty_at(self.row, self.column))

    # only called if robot in a cell with a kid
    def pick_up_kid(self):
        env = self.environment
        board = env.board
        self.is_carrying_kid = True
        self.carrying_kid = env.kid_at(self.row, self.column)
        board[self.row][self.column] = 1
        self.carrying_kid.in_robot_arms = True
        
    # only called when robot has a kid in his arms and is in a crib cell
    def put_kid_in_crib(self):
        env = self.environment
        board = env.board
        self.is_carrying_kid = False
        self.carrying_kid.in_robot_arms = False
        self.carrying_kid.in_crib = True
        env.crib_at(self.row, self.column).occupied = True
        self.carrying_kid = None
        board[self.row][self.column] = 5

    # only called if robot has a kid in his arms
    def drop_kid(self):
        env = self.environment
        board = env.board
        self.is_carrying_kid = False
        self.carrying_kid.in_robot_arms = False
        self.carrying_kid = None
        board[self.row][self.column] = 2

    # sets robot current task from dirty or kid proximity
    def find_nearest_task(self):
        global drow, dcolumn

        queue = [self.get_position()]
        visited = []
        
        env = self.environment
        board = env.board
        
        while len(queue) > 0:
            curr_pos = queue[0]
            queue = queue[1:len(queue)]
            
            if curr_pos in visited:
                continue
            
            visited += [curr_pos]
            
            if  board[curr_pos[0]][curr_pos[1]] == 2:
                self.current_task = "Kid"
                break
            
            if board[curr_pos[0]][curr_pos[1]] == 3:
                self.current_task = "Dirty"
                break
            
            for i in range(0, 4):
                new_row = curr_pos[0] + drow[i]
                new_column = curr_pos[1] + dcolumn[i]

                if env.valid_position(new_row, new_column) and board[new_row][new_column] != -1 and board[new_row][new_column] != 5:
                   queue += [(new_row, new_column)]

    # move robot to the next objects of tipe object_type (BFS)
    # returns True if there is a valid path to any object of object_type type
    def move_to_next(self, object_type):
        global drow, dcolumn

        queue = [self.get_position()]
        
        if object_type == "Empty":
            object_id = 0
        
        elif object_type == "Kid":
            object_id = 2
        
        elif object_type == "Dirty":
            object_id = 3
        
        elif object_type == "Crib":
            object_id = 4
        
        visited = []
        # to store the path
        trail = [""]
        
        env = self.environment
        board = env.board

        curr_pos = (-1, -1)
        curr_trail = ""
        
        while len(queue) > 0:
            curr_pos = queue[0]
            curr_trail = trail[0]
            
            queue = queue[1:len(queue)]
            trail = trail[1:len(trail)]
            
            if curr_pos in visited:
                continue
            
            visited += [curr_pos]
            
            if board[curr_pos[0]][curr_pos[1]] == object_id:
                break
            
            for i in range(0, 4):
                new_row = curr_pos[0] + drow[i]
                new_column = curr_pos[1] + dcolumn[i]
                
                if env.valid_position(new_row, new_column) and board[new_row][new_column] != -1 and board[new_row][new_column] != 5:
                   queue += [(new_row, new_column)]
                   
                   if i == 0:
                       trail += [curr_trail + "U"]
                   elif i == 1:
                       trail += [curr_trail + "R"]
                   elif i == 2:
                       trail += [curr_trail + "D"]
                   else:
                       trail += [curr_trail + "L"]
        
        if curr_trail == "" or (len(queue) == 0 and not (board[curr_pos[0]][curr_pos[1]] == object_id)):
            return False
        
        move_direction = curr_trail[0:1]
        
        direction = 0
        if move_direction == "U":
            direction = 0
        elif move_direction == "R":
            direction = 1
        elif move_direction == "D":
            direction = 2
        else:
            direction = 3
        
        new_row = self.row + drow[direction]
        new_column = self.column + dcolumn[direction]
        
        if board[self.row][self.column] == 1:
            board[self.row][self.column] = 0
        
        if board[new_row][new_column] == 0:
            board[new_row][new_column] = 1
        
        self.row = new_row
        self.column = new_column
        
        return True


class Robot_Model_A(Robot):
    # perform action is the way of interact with the environment
    def perform_action(self):
        # if environment shuffled then check for new task if not carrying kid
        if self.environment.to_change_left == self.environment.change_t:
            if self.current_task == "Dirty" or (self.current_task == "Kid" and not self.is_carrying_kid):
                self.current_task = "None"
        
        # if has no task then find one
        if self.current_task == "None":
            self.find_nearest_task()
        
        # if doing a collect-kid task
        if self.current_task == "Kid":
            # if already carrying kid
            if self.is_carrying_kid:
                # if current cell has a crib then put the kid in the crib
                if self.environment.board[self.row][self.column] == 4:
                    self.put_kid_in_crib()
                    self.current_task = "None"
                # else move to the nearest crib
                else:
                    if not self.move_to_next("Crib"):
                        # if there is no valid path to a crib then drop kid in an empty cell 
                        # and change to clean-dirty tasks
                        if self.environment.board[self.row][self.column] == 0 or self.environment.board[self.row][self.column] == 1:
                            self.drop_kid()
                            self.current_task = "Dirty"
                        else:
                            if self.move_to_next("Empty"):
                                self.carrying_kid.change_position(self.row, self.column)
                    else:
                        self.carrying_kid.change_position(self.row, self.column)
                    # second move since carrying a kid
                    if not (self.environment.board[self.row][self.column] == 4):
                        if not self.move_to_next("Crib"):
                            self.current_task = "None"
                        else:
                            self.carrying_kid.change_position(self.row, self.column)
            # if not carrying a kid
            else:
                # if current cell has a kid then pick him up
                if self.environment.board[self.row][self.column] == 2:
                    self.pick_up_kid()
                    # but if no way to reach a crib then change to dirty-clean tasks
                    if not self.move_to_next("Crib"):
                        self.drop_kid()
                        self.current_task = "Dirty"
                        return
                    else:
                        self.carrying_kid.change_position(self.row, self.column)
                    
                    if not self.environment.board[self.row][self.column] == 4:
                        if not self.move_to_next("Crib"):
                            self.drop_kid()
                            self.current_task = "Dirty"
                        else:
                            self.carrying_kid.change_position(self.row, self.column)
                # find the nearest kid
                else:
                    if not self.move_to_next("Kid"):
                        self.current_task = "None"

        # dirty-clean tasks
        elif self.current_task == "Dirty":
            # if carrying_kid drop him
            if self.is_carrying_kid:
                self.drop_kid()
            # if current cell has a dirty then clean it and find next task
            elif self.environment.board[self.row][self.column] == 3:
                self.clean_dirty()
                self.current_task = "None"
            # else move towards the next dirty
            else:
                if not self.move_to_next("Dirty"):
                    self.current_task = "None"


class Robot_Model_B(Robot):
    # returns True if there is a dirty near the robot (distance of 1)
    def dirty_near(self):
        global drow, dcolumn

        env = self.environment
        board = env.board

        for i in range(0, 4):
            row = self.row + drow[i]
            column = self.column + dcolumn[i]
            if env.valid_position(row, column) and board[row][column] == 3:
                return True

        return False

    # perform action is the way of interact with the environment
    def perform_action(self):
        # if environment shuffled then check for new task if not carrying kid
        if self.environment.to_change_left == self.environment.change_t:
            if self.current_task == "Dirty" or (self.current_task == "Kid" and not self.is_carrying_kid):
                self.current_task = "None"
        
        # if dirty percentage is greater than 55% turn into clean fury
        if self.current_task != "Dirty Priority" and self.environment.dirtyness_percentage() > 0.55:
            if self.is_carrying_kid:
                if self.environment.board[self.row][self.column] == 0 or self.environment.board[self.row][self.column] == 1:
                    self.drop_kid()
                    self.current_task = "Dirty Priority"
                else:
                    if self.move_to_next("Empty"):
                        self.carrying_kid.change_position(self.row, self.column)  
            else:
                self.current_task = "Dirty Priority"

        # if has no task then find one
        if self.current_task == "None":
            self.find_nearest_task()
        
        # if doing a collect-kid task
        if self.current_task == "Kid":
            # if already carrying kid
            if self.is_carrying_kid:
                # if current cell has a crib then put the kid in the crib
                if self.environment.board[self.row][self.column] == 4:
                    self.put_kid_in_crib()
                    self.current_task = "None"
                # else move to the nearest crib
                else:
                    if not self.move_to_next("Crib"):
                        # if there is no valid path to a crib then drop kid in an empty cell 
                        # and change to clean-dirty tasks
                        if self.environment.board[self.row][self.column] == 0 or self.environment.board[self.row][self.column] == 1:
                            self.drop_kid()
                            self.current_task = "Dirty"
                        else:
                            if self.move_to_next("Empty"):
                                self.carrying_kid.change_position(self.row, self.column)
                    else:
                        self.carrying_kid.change_position(self.row, self.column)
                    # second move since carrying a kid
                    if not (self.environment.board[self.row][self.column] == 4):
                        if not self.move_to_next("Crib"):
                            self.current_task = "None"
                        else:
                            self.carrying_kid.change_position(self.row, self.column)
            # if not carrying a kid
            else:

                # if current cell has a kid then pick him up
                if self.environment.board[self.row][self.column] == 2:
                    self.pick_up_kid()
                    # but if no way to reach a crib then change to dirty-clean tasks
                    if not self.move_to_next("Crib"):
                        self.drop_kid()
                        self.current_task = "Dirty"
                        return
                    else:
                        self.carrying_kid.change_position(self.row, self.column)
                    
                    if not self.environment.board[self.row][self.column] == 4:
                        if not self.move_to_next("Crib"):
                            self.drop_kid()
                            self.current_task = "Dirty"
                        else:
                            self.carrying_kid.change_position(self.row, self.column)
                # find the nearest kid
                else:
                    # if comes near a dirty just generated clean it
                    if self.dirty_near():
                        self.current_task = "Dirty"
                        self.move_to_next("Dirty")
                    elif not self.move_to_next("Kid"):
                        self.current_task = "None"

        # dirty-clean tasks
        elif self.current_task == "Dirty" or self.current_task == "Dirty Priority":
            # if carrying_kid drop him
            if self.is_carrying_kid:
                self.drop_kid()
            # if current cell has a dirty then clean it and find next task
            elif self.environment.board[self.row][self.column] == 3:
                self.clean_dirty()
                self.current_task = "None"
            # else move towards the next dirty
            else:
                if not self.move_to_next("Dirty"):
                    self.current_task = "None"
            
            # if dirtyness percentage is below 50% shut down clean fury
            if self.current_task == "Dirty Priority" and self.environment.dirtyness_percentage() < 0.5:
                self.current_task = "None"