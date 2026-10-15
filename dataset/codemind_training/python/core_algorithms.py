from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import threading
from collections import deque
from pathlib import Path
from typing import Any, Callable, Generic, Iterable, TypeVar


T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def binary_search(sorted_values: list[T], target: T) -> int:
    """Return the index of target in an ascending list, or -1 when absent."""
    low = 0
    high = len(sorted_values) - 1
    while low <= high:
        middle = low + (high - low) // 2
        value = sorted_values[middle]
        if value == target:
            return middle
        if value < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1


def bubble_sort(values: Iterable[T]) -> list[T]:
    """Sort values in ascending order using the stable bubble-sort algorithm."""
    result = list(values)
    for end in range(len(result) - 1, 0, -1):
        swapped = False
        for index in range(end):
            if result[index] > result[index + 1]:
                result[index], result[index + 1] = result[index + 1], result[index]
                swapped = True
        if not swapped:
            break
    return result


def merge_sort(values: Iterable[T]) -> list[T]:
    """Return a stable O(n log n) sorted copy using merge sort."""
    items = list(values)
    if len(items) < 2:
        return items

    middle = len(items) // 2
    left = merge_sort(items[:middle])
    right = merge_sort(items[middle:])
    merged: list[T] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged


def dijkstra(
    graph: dict[K, dict[K, float]], start: K
) -> tuple[dict[K, float], dict[K, K | None]]:
    """Compute shortest paths for a directed graph with nonnegative weights."""
    if start not in graph:
        raise KeyError(f"Start node {start!r} is not present in the graph")

    distances = {node: float("inf") for node in graph}
    previous: dict[K, K | None] = {node: None for node in graph}
    unvisited = set(graph)
    distances[start] = 0.0

    while unvisited:
        current = min(unvisited, key=distances.__getitem__)
        if distances[current] == float("inf"):
            break
        unvisited.remove(current)

        for neighbor, weight in graph[current].items():
            if weight < 0:
                raise ValueError("Dijkstra's algorithm requires nonnegative weights")
            if neighbor not in graph:
                raise KeyError(f"Neighbor {neighbor!r} is not present in the graph")
            candidate = distances[current] + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = current

    return distances, previous


def reconstruct_path(previous: dict[K, K | None], target: K) -> list[K]:
    """Reconstruct a path from a Dijkstra predecessor map."""
    if target not in previous:
        raise KeyError(f"Target node {target!r} is not present in the predecessor map")
    path: list[K] = []
    current: K | None = target
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    return path


class LinkedNode(Generic[T]):
    def __init__(self, value: T, next_node: LinkedNode[T] | None = None) -> None:
        self.value = value
        self.next = next_node


class LinkedList(Generic[T]):
    def __init__(self) -> None:
        self.head: LinkedNode[T] | None = None
        self.tail: LinkedNode[T] | None = None
        self._length = 0

    def __len__(self) -> int:
        return self._length

    def __iter__(self):
        current = self.head
        while current is not None:
            yield current.value
            current = current.next

    def append(self, value: T) -> None:
        node = LinkedNode(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._length += 1

    def prepend(self, value: T) -> None:
        self.head = LinkedNode(value, self.head)
        if self.tail is None:
            self.tail = self.head
        self._length += 1

    def remove(self, value: T) -> bool:
        previous: LinkedNode[T] | None = None
        current = self.head
        while current is not None:
            if current.value == value:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                if self.tail is current:
                    self.tail = previous
                self._length -= 1
                return True
            previous, current = current, current.next
        return False


class BinarySearchTree(Generic[T]):
    class Node:
        def __init__(self, value: T) -> None:
            self.value = value
            self.left: BinarySearchTree.Node | None = None
            self.right: BinarySearchTree.Node | None = None

    def __init__(self) -> None:
        self.root: BinarySearchTree.Node | None = None

    def insert(self, value: T) -> None:
        if self.root is None:
            self.root = self.Node(value)
            return

        current = self.root
        while True:
            if value < current.value:
                if current.left is None:
                    current.left = self.Node(value)
                    return
                current = current.left
            else:
                if current.right is None:
                    current.right = self.Node(value)
                    return
                current = current.right

    def contains(self, value: T) -> bool:
        current = self.root
        while current is not None:
            if value == current.value:
                return True
            current = current.left if value < current.value else current.right
        return False

    def inorder(self) -> list[T]:
        result: list[T] = []

        def visit(node: BinarySearchTree.Node | None) -> None:
            if node is not None:
                visit(node.left)
                result.append(node.value)
                visit(node.right)

        visit(self.root)
        return result


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def __len__(self) -> int:
        return len(self._items)


class Queue(Generic[T]):
    def __init__(self) -> None:
        self._items: deque[T] = deque()

    def enqueue(self, item: T) -> None:
        self._items.append(item)

    def dequeue(self) -> T:
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()

    def __len__(self) -> int:
        return len(self._items)


class SingletonMeta(type):
    _instances: dict[type, object] = {}
    _lock = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        with SingletonMeta._lock:
            if cls not in SingletonMeta._instances:
                SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
            return SingletonMeta._instances[cls]


class ApplicationSettings(metaclass=SingletonMeta):
    def __init__(self, environment: str = "development") -> None:
        self.environment = environment
        self.values: dict[str, str] = {}


class Notification(Callable[[str], str]):
    def send(self, message: str) -> str:
        raise NotImplementedError


class EmailNotification:
    def send(self, message: str) -> str:
        return f"Email queued: {message}"


class SmsNotification:
    def send(self, message: str) -> str:
        return f"SMS queued: {message}"


class NotificationFactory:
    _builders: dict[str, Callable[[], Any]] = {
        "email": EmailNotification,
        "sms": SmsNotification,
    }

    @classmethod
    def create(cls, channel: str) -> Any:
        try:
            builder = cls._builders[channel.lower()]
        except KeyError as error:
            supported = ", ".join(sorted(cls._builders))
            raise ValueError(f"Unsupported channel {channel!r}; choose from {supported}") from error
        return builder()


class DataAccessError(RuntimeError):
    pass


def write_json_atomically(path: str | Path, data: Any) -> None:
    """Write JSON through a temporary file so partial writes do not replace valid data."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=destination.parent,
            prefix=f".{destination.name}.", suffix=".tmp", delete=False
        ) as temporary:
            temporary_name = temporary.name
            json.dump(data, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
        os.replace(temporary_name, destination)
    except (OSError, TypeError, ValueError) as error:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except OSError:
                pass
        raise DataAccessError(f"Could not write JSON file {destination}") from error


def read_json(path: str | Path) -> Any:
    try:
        with Path(path).open("r", encoding="utf-8") as source:
            return json.load(source)
    except (OSError, json.JSONDecodeError) as error:
        raise DataAccessError(f"Could not read valid JSON from {path}") from error


def create_task_database(path: str | Path) -> None:
    """Create a small SQLite task table with a stable schema."""
    try:
        with sqlite3.connect(path) as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1))
                )"""
            )
    except sqlite3.Error as error:
        raise DataAccessError("Could not initialize the task database") from error


def add_task(path: str | Path, title: str) -> int:
    normalized_title = title.strip()
    if not normalized_title:
        raise ValueError("Task title must not be empty")
    try:
        with sqlite3.connect(path) as connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title) VALUES (?)", (normalized_title,)
            )
            return int(cursor.lastrowid)
    except sqlite3.Error as error:
        raise DataAccessError("Could not add task to the database") from error


def list_tasks(path: str | Path) -> list[dict[str, Any]]:
    try:
        with sqlite3.connect(path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT id, title, completed FROM tasks ORDER BY id"
            ).fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as error:
        raise DataAccessError("Could not list tasks from the database") from error


def mark_task_completed(path: str | Path, task_id: int) -> bool:
    try:
        with sqlite3.connect(path) as connection:
            cursor = connection.execute(
                "UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,)
            )
            return cursor.rowcount == 1
    except sqlite3.Error as error:
        raise DataAccessError("Could not update the task") from error