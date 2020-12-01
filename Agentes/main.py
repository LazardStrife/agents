from simulation_logic import Initial_Scenary
import copy as cpy

def run_simulations_with_robot_type_A():
    scenaries = [Initial_Scenary(5, 5, 40, 15, 4, 50),
                 Initial_Scenary(7, 9, 30, 10, 6, 100),
                 Initial_Scenary(8, 10, 25, 30, 8, 150),
                 Initial_Scenary(11, 11, 30, 15, 10, 200),
                 Initial_Scenary(13, 7, 37, 25, 9, 300),
                 Initial_Scenary(19, 16, 30, 15, 12, 400),
                 Initial_Scenary(15, 18, 38, 20, 9, 600),
                 Initial_Scenary(21, 19, 24, 35, 11, 500),
                 Initial_Scenary(12, 26, 50, 20, 12, 600),
                 Initial_Scenary(27, 20, 40, 36, 19, 700)]
                
    for i in range(0, len(scenaries)):
        s = scenaries[i]
        
        win_amount_A = 0
        lose_amount_A = 0
        dirtiness_percent_A = 0
        win_amount_B = 0
        lose_amount_B = 0
        dirtiness_percent_B = 0

        for j in range(0, 30):
            env_A = s.generate_environment()
            env_B = env_A.copy_with_alternate_model()

            result = ""

            while True:
                result = env_A.perform_turn()
                if result != "Nothing happened":
                    break
            if result == "Kids in cribs and floor cleaned":
                win_amount_A += 1
            else:
                lose_amount_A += 1
                dirtiness_percent_A += env_A.dirtyness_percentage()
            
            result = ""

            while True:
                result = env_B.perform_turn()
                if result != "Nothing happened":
                    break
            if result == "Kids in cribs and floor cleaned":
                win_amount_B += 1
            else:
                lose_amount_B += 1
                dirtiness_percent_B += env_B.dirtyness_percentage()

        dirtiness_percent_A /= 30
        dirtiness_percent_B /= 30
        
        print("Scenary #" + str(i + 1) + ":")
        print("Model A win amount: " + str(win_amount_A))
        print("Model A lose amount: " + str(lose_amount_A))
        print("Model A dirtyness mean: " + str(dirtiness_percent_A))
        print("Model B win amount: " + str(win_amount_B))
        print("Model B lose amount: " + str(lose_amount_B))
        print("Model B dirtyness mean: " + str(dirtiness_percent_B))
        print("")
        

def print_board(environment):
    for i in range(0, len(environment.board)):
        row_info = ""
        for j in range(0, len(environment.board[0])):
            if environment.board[i][j] == -1:
                row_info += str(environment.board[i][j]) + " "
            else:
                if environment.board[i][j] != 1 and environment.robot.row == i and environment.robot.column == j:
                    row_info += "-" + str(environment.board[i][j]) + " "
                else:
                    row_info += " " + str(environment.board[i][j]) + " "
        print(row_info)


def main():
    run_simulations_with_robot_type_A()


if __name__ == "__main__":
    main()