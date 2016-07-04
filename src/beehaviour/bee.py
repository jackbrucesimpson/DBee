#!/usr/bin/env python

class Bee:
    def __init__(self, bee_id, tag_id, length_tracked):
        self.bee_id = bee_id
        self.tag_id = tag_id
        self.length_tracked = length_tracked

        self.last_path_id = None
        self.path_length = None
        self.last_x = None
        self.last_y = None
        self.list_speeds = []
        self.list_angles = []
        self.cells_visited = {}

def main():
    pass

if __name__ == "__main__":
    main()
