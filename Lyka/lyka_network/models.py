from django.db import models

class PriorityQueue:
    def __init__(self):
        self.heap = []

    def parent(self, node):
        return (node - 1) // 2

    def left(self, node):
        return (2 * node) + 1

    def right(self, node):
        return (2 * node) + 2

    def heapify_up(self, index):
        parent_index = self.parent(index)
        while index > 0 and self.heap[index]["priority"] < self.heap[parent_index]["priority"]:
            self._swap(index, parent_index)
            index = parent_index
            parent_index = self.parent(index)

    def heapify_down(self, index):
        left_child_index = self.left(index)
        right_child_index = self.right(index)
        smallest = index

        if left_child_index < len(self.heap) and self.heap[left_child_index]["priority"] < self.heap[smallest]["priority"]:
            smallest = left_child_index

        if right_child_index < len(self.heap) and self.heap[right_child_index]["priority"] < self.heap[smallest]["priority"]:
            smallest = right_child_index

        if smallest != index:
            self._swap(index, smallest)
            self.heapify_down(smallest)

    def enqueue(self, item):
        self.heap.append(item)
        self.heapify_up(len(self.heap) - 1)

    def dequeue(self):
        if not self.is_empty():
            self._swap(0, len(self.heap) - 1)
            minimum_element = self.heap.pop()
            self.heapify_down(0)
            return minimum_element
        else:
            raise IndexError("Priority queue is empty")

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def is_empty(self):
        return len(self.heap) == 0


class ServiceLocation(models.Model):
    name = models.CharField(max_length=30)


class Hub(models.Model):
    LEVEL_CHOICES = [
        ('A', "NATIONAL"),
        ('B', "STATE")
    ]
    location = models.ForeignKey(ServiceLocation, on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length = 30)
    city = models.CharField(max_length = 30)
    level = models.CharField(max_length = 1, choices=LEVEL_CHOICES)


class Distance(models.Model):
    source = models.ForeignKey(ServiceLocation, on_delete=models.CASCADE)
    destination = models.ForeignKey(ServiceLocation, on_delete=models.CASCADE)
    distance = models.IntegerField()

    def shortest_path(self, source, destination):
        visited = []
        distances = {}
        priority_queue = PriorityQueue()

        for location in ServiceLocation.objects.all():
            if location.id == source.id:
                distances[location] = 0
            else:
                distances[location] = float('inf')

        priority_queue.enqueue({
            "priority": 0,
            "source": source
        })

        while not priority_queue.is_empty():
            smallest_element = priority_queue.dequeue()
            visited.append(smallest_element)

            if smallest_element["source"].name == destination.name:
                return visited, distances[smallest_element["source"]]

            tentative_distances = Distance.objects.filter(source=smallest_element["source"])
            for d in tentative_distances:
                tentative = distances[smallest_element["source"]] + d.distance

                if tentative < distances[d.destination]:
                    distances[d.destination] = tentative
                    priority_queue.enqueue({
                        "priority": tentative,
                        "source": d.destination
                    })


