#!/usr/bin/env python

class Bee:
    def __init__(self, bee_id, tag_id, path_length):
        self.bee_id = bee_id
        self.tag_id = tag_id
        self.path_length = path_length

        self.last_path_id = None
        self.last_x = None
        self.last_y = None
        self.list_speeds = []
        self.list_angles = []
        self.cells_visited = {}

def main():
    pass

if __name__ == "__main__":
    main()
