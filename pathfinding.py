from queue import PriorityQueue


class Node:
    # node class that adds parent instance variable to retrace the final path
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.g_cost = None
        self.f_cost = None
        self.h_cost = None
        self.neighbors = []

def setup(rows, columns, snake_body):
    nodes = []
    for row in range(rows):
        for column in range(columns):
            node = Node(row, column)
            node.neighbors.append(Node(row + 1, column))
            node.neighbors.append(Node(row - 1, column))
            node.neighbors.append(Node(row, column + 1))
            node.neighbors.append(Node(row, column - 1))

    return nodes


def get_distance(current, start, end, rows, columns):
    h_teleport_distance_to_start = rows - max(current.x, start.x) + min(current.x, start.x)
    h_distance_to_start = abs(current.x - start.x)
    v_distance_to_start = abs(current.y - start.y)
    v_teleport_distance_to_start = columns - max(current.y, start.y) + min(current.y, start.y)

    h_teleport_distance_to_end = rows - max(current.x, end.x) + min(current.x, end.x)
    h_distance_to_end = abs(current.x - end.x)
    v_teleport_distance_to_end = columns - max(current.y, end.y) + min(current.y, end.y)
    v_distance_to_end = abs(current.y - end.y)

    g_cost = min(h_teleport_distance_to_start, h_distance_to_start) + min(v_distance_to_start, v_teleport_distance_to_start)
    h_cost = min(h_teleport_distance_to_end, h_distance_to_end) + min(v_teleport_distance_to_end, v_distance_to_end)
    f_cost = g_cost + h_cost

    return g_cost, h_cost, f_cost


def find_path(snack_pos, rows, columns, snake_body):
    snake_body = [part[:2] for part in snake_body]
    path_is_safe = snack_path_is_safe(snack_pos, rows, columns, snake_body)

    # if path is not save start circling around the edges (or parts of the snake) until the path becomes safe, once it is safe generate the path to it and follow it.
    if path_is_safe:
        start_pos = Node(snake_body[0][0], snake_body[0][1])
        snack_pos = Node(snack_pos[0], snack_pos[1])
        start_node = Node(snake_body[0][0], snake_body[0][1])
        curr_g_cost, curr_h_cost, curr_f_cost = get_distance(start_node, start_pos, snack_pos, rows, columns)
        start_node.g_cost = curr_g_cost
        start_node.h_cost = curr_h_cost
        start_node.f_cost = curr_f_cost

        visited = {(start_pos.x, start_pos.y)}
        queue = PriorityQueue()
        entry = 0
        queue.put((curr_f_cost, curr_h_cost, entry, start_node))

        count = 0
        while not queue.empty():
            count += 1
            current_f_cost, current_h_cost, _, current = queue.get()
            visited.add((current.x, current.y))

            if (current.x, current.y) == (snack_pos.x, snack_pos.y):
                path = reconstruct_path(current)
                print(count)
                return path

            neighbors = [Node(current.x - 1, current.y) if current.x - 1 >= 0 else Node(rows - 1, current.y),
                         Node(current.x + 1, current.y) if current.x + 1 < rows else Node(0, current.y),
                         Node(current.x, current.y - 1) if current.y - 1 >= 0 else Node(current.x, columns - 1),
                         Node(current.x, current.y + 1) if current.y + 1 < columns else Node(current.x, 0)]

            for neighbor in neighbors:
                _, neighbor_h_cost, neighbor_f_cost = get_distance(neighbor, start_pos, snack_pos, rows, columns)
                if neighbor_collides_snake(neighbor, snake_body) is False:
                    if (neighbor.x, neighbor.y) not in visited or neighbor_f_cost < current_f_cost:# or\
                            #(neighbor_f_cost == current_f_cost and neighbor_h_cost < current_h_cost):

                        entry += 1
                        queue.put((neighbor_f_cost, neighbor_h_cost, entry, neighbor))
                        neighbor.parent = current
                        neighbor.g_cost = _
                        neighbor.h_cost = neighbor_h_cost
                        neighbor.f_cost = neighbor_f_cost


# def snack_path_is_safe(snack_pos, rows, columns, snake_body):
#     # check if currently the snack is safe to get
#     snack_neighbors = [[snack_pos[0]-1, snack_pos[1]] if snack_pos[0]-1 >= 0 else [rows, snack_pos[1]],
#                        [snack_pos[0]+1, snack_pos[1]] if snack_pos[0]+1 < rows else [0, snack_pos[1]],
#                        [snack_pos[0], snack_pos[1]-1] if snack_pos[1]-1 >= 0 else [snack_pos[0], columns],
#                        [snack_pos[0], snack_pos[1]+1] if snack_pos[1]+1 < columns else [snack_pos[0], 0]
#                        ]
#     unoccupied_squares = 0
#     for snack_neighbor in snack_neighbors:
#         if snack_neighbor not in snake_body:
#             unoccupied_squares += 1
#
#     if unoccupied_squares >= 2:
#         return True
#     return False