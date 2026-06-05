import constellation_repository as repo
from math import sqrt

repository = repo.ConstellationRepository()

class AstraRouter:
    def __init__(self):
        self.all_coordinates = repository.get_all_coordinates()
        self.max_route_steps = 1000

    def get_route(self, origin_id, destination_id, max_step_length):
        origin = next((x for x in self.all_coordinates if x.star_id == origin_id), None)
        destination = next((x for x in self.all_coordinates if x.star_id == destination_id), None)
        route = [origin]
        self.find_route(origin, destination, max_step_length, self.all_coordinates, route)
        for point in self.all_coordinates:
            point.skip = 0
        return route
    
    def get_distance_by_id(self, origin_id, destination_id):
        origin = next((x for x in self.all_coordinates if x.star_id == origin_id), None)
        destination = next((x for x in self.all_coordinates if x.star_id == destination_id), None)
        return round(AstraRouter.get_distance(origin, destination), 4)

    @staticmethod
    def get_cube(coordinates, o, edge_size):
        return (p for p in coordinates if abs(p.x - o.x) < edge_size and abs(p.y - o.y) < edge_size and abs(p.z - o.z) < edge_size)

    @staticmethod
    def get_distance(astra1, astra2):
        return sqrt((astra1.x - astra2.x)**2 + (astra1.y - astra2.y)**2 + (astra1.z - astra2.z)**2)

    def find(self, coordinates, astra, destination, max_step_length):
        min_distance = max_step_length + self.get_distance(astra, destination)
        cube = self.get_cube(coordinates, astra, max_step_length)
        result = None
        for point in cube:
            d = self.get_distance(astra, point);
            if point.skip == 0 and d < max_step_length:
                distance = self.get_distance(point, destination)
                if distance < min_distance:
                    min_distance = distance
                    result = point
                    point.skip = 1
                    point.dist = round(d, 4)
        return result

    def find_route_r(self, origin, destination, max_step_length, coordinates, result):
        d = self.get_distance(origin, destination)
        if d < max_step_length:
            if len(result) < self.max_route_steps:
                destination.dist = round(self.get_distance(origin, destination), 4)
                result.append(destination)
            else:
                result.clear()
        else:
            anywhere = self.find(coordinates, origin, destination, max_step_length)
            if anywhere:
                if len(result) < self.max_route_steps:
                    result.append(anywhere)
                    self.find_route(anywhere, destination, max_step_length, coordinates, result)
                else:
                    result.clear()
            else: 
                if len(result) > 0:
                    a = result.pop()
                    self.find_route(a, destination, max_step_length, coordinates, result);
            
        return len(result) > 0
    
    def find_route(self, origin, destination, max_step_length, coordinates, result):
        res = 0
        astra = origin
        while res == 0 and self.get_distance(astra, destination) > max_step_length:
            astra = self.find(coordinates, astra, destination, max_step_length)
            if astra:
                if len(result) < self.max_route_steps - 1:
                    result.append(astra)
                else:
                    result.clear()
                    res = 1
            else: 
                if len(result) > 0:
                    astra = result.pop()
                else:
                    result.clear()
                    res = 2

        if res == 0:
            destination.dist = round(self.get_distance(astra, destination), 4)
            result.append(destination)
            
        return res

    @staticmethod
    def print_route(route):
        if len(route) > 0:
            prev = route[0]
            print(f"{prev}")
            for i in range(1, len(route)):
                current = route[i]
                print(f"{current}, {AstraRouter.get_distance(prev, current)}")
                prev = current



