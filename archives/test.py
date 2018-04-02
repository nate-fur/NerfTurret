
def generate_values(grid):
    """ Function to fill in the empty squares using linear approximations of the coordinates
    found in the calibration function"""
    # Generate values for even columns
    for row in range(1,4,2):
        for col in range(0,5,2):
            grid[row][col][0] = (grid[row-1][col][0] + grid[row+1][col][0]) / 2
            grid[row][col][1] = (grid[row-1][col][1] + grid[row+1][col][1]) / 2

    # Generate values for odd columns
    for row in range(5):
        for col in range(1,4,2):
            grid[row][col][0] = (grid[row][col+1][0] + grid[row][col-1][0]) / 2
            grid[row][col][1] = (grid[row][col+1][1] + grid[row][col-1][1]) / 2

grid = [[],[],[],[],[]]
grid[0] = [[1.0,1.0],[0,0],[3.0,3.0],[0,0],[5.0,5.0]]
grid[1] = [[0,0],[0,0],[0,0],[0,0],[0,0]]
grid[2] = [[1.0,1.0],[0,0],[4.0,4.0],[0,0],[5.0,5.0]]
grid[3] = [[0,0],[0,0],[0,0],[0,0],[0,0]]
grid[4] = [[1.0,1.0],[0,0],[3.0,3.0],[0,0],[5.0,5.0]]

for i in range(5):
    for j in range(5):
        print(str(grid[i][j][0]) + "," + str(grid[i][j][1]), end=' ')
    print()
print()
generate_values(grid)

for i in range(5):
    for j in range(5):
        print(str(grid[i][j][0]) + "," + str(grid[i][j][1]), end=' ')
    print()
