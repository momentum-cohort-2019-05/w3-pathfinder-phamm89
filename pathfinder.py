import random
from PIL import Image, ImageColor, ImageDraw


def read_of_line_of_ints(text):
    """Given a string with integers in it, return a list of those integers."""
    ints = []
    ints_as_strs = split_line(text)

    for int_as_str in ints_as_strs:
        ints.append(int(int_as_str))
    return ints

def split_line(line):
    return line.split()

def read_file_into_list(filename):
    """Given a file, return a list of each line in the file as a string."""
    with open(filename) as file:
        return file.readlines()

def read_file_into_ints(filename):
    """Given a filename, read that file and then convert it to a list of lists of ints. Example: 

    We have a file with these contents: 
    1 2 
    3 4

    The return value would be [[1, 2], [3, 4]]"""
    lines = read_file_into_list(filename)

    list_of_lists = []
    for line in lines:
        list_of_lists.append(read_of_line_of_ints(line))
    return list_of_lists

class ElevationMap:
    """
    ElevationMap is a class that takes a matrix (list of lists, 2D)
    of integers and can be used to generate an image of those elevations like a 
    standard elevation map.
    """

    def __init__(self, elevations):
        self.elevations = elevations

    def elevation_at_coordinate(self, x, y):
        return self.elevations[y][x]
    
    def min_elevation(self):
        return min([min(row) for row in self.elevations])

    def max_elevation(self):
        return max([max(row) for row in self.elevations])
    
    def intensity_at_coordinate(self, x, y, min_elevation, max_elevation):
        """Given an x, y coordinate, return the intensity level
        (used for grayscale in image) of the elevation at that coordinate."""
        elevation = self.elevation_at_coordinate(x, y)
    
        return ((elevation - min_elevation) / (max_elevation - min_elevation)) * 255

    def draw_grayscale_gradient(self, filename, width, height):
        image = Image.new(mode = 'L', size=(width, height))
        min_elevation = self.min_elevation()
        max_elevation = self.max_elevation()
        
        for x in range(width):
            for y in range(height):
                intensity = int(self.intensity_at_coordinate(x, y, min_elevation, max_elevation))
                image.putpixel((x, y), (intensity))
        return image.save(filename)


class Pathfinder:
    """Class to find optimal path across the mountain"""

    def __init__(self, map, filename, y=0, x=0):
        self.map = map
        self.im = Image.open(filename)
        self.current_position = (x, y)
    
    def greedy_path(self, x):
        """Determines the potential options for next steps and chooses the step smallest elevation change."""
        y = self.current_position[1]

        # Account for beginning index
        if y - 1 < 0:
            y = 0
        current_elevation = self.map.elevation_at_coordinate(x, y)
        up_path = self.map.elevation_at_coordinate((x+1), (y-1))
        straightforward_path = self.map.elevation_at_coordinate((x+1), y)
        
        # Account for ending index
        if y + 1 > len(self.map.elevations):
            y = len(self.map.elevations) - 1
        down_path = self.map.elevation_at_coordinate((x+1), (y+1))

        # Find the least difference in elevation change
        self.up_difference = abs(up_path - current_elevation)
        self.straight_difference = abs(straightforward_path - current_elevation)
        self.down_difference = abs(down_path - current_elevation)

        self.path_options = [self.up_difference, self.straight_difference, self.down_difference]

        self.minimum_difference = min(self.path_options)

        # Account for elevations up, down, or straight being equal to each other and choosing the path
        if self.up_difference == self.minimum_difference and self.up_difference == self.down_difference and self.up_difference != self.straight_difference:
            if random.randint(0, 1) == 0:
                y -= 1
            else:
                y += 1
        elif self.up_difference == self.minimum_difference and self.up_difference != self.straight_difference:
            y -= 1
        elif self.down_difference == self.minimum_difference and self.down_difference != self.straight_difference:
            y += 1
        x += 1
        self.current_position = (x, y)

        return y
    
    def draw_path(self):
        """Draw path of least elevation change"""
        y = self.current_position[1]
        
        for x in range(len(self.map.elevations[0])-1):
            self.im.putpixel((x,y), 255)
            y = self.greedy_path(x)
        self.im.save('map_path.png')



if __name__ == "__main__":
    elevations = read_file_into_ints('elevation_small.txt')

    e_map = ElevationMap(elevations)

    e_map.draw_grayscale_gradient('basic_map.png', 600, 600)

    y = 100

    mapped_path = Pathfinder(e_map, 'basic_map.png', y, x=0)
    mapped_path.draw_path()