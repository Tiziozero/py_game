import enum
from typing import List, Tuple, Union, overload
import pygame, uuid, sys
from random import randint

from pygame.mixer_music import play

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
FPS = 60

class Body:
    def __init__(self, width: float, height: float, x: float =0, y: float =0):
        self.__id = uuid.uuid4()
        self.__width = width
        self.__height = height
        self.__coords: pygame.Vector2 = pygame.Vector2(x,y)
        self.__body = pygame.Rect(x,y, width, height);
        self.__color: Tuple[int, int, int] = (randint(55, 255), randint(55, 255),randint(55, 255))
        ...

    def get_id(self):
        return self.__id

    def get_width(self):
        return self.__width

    def get_height(self):
        return self.__height

    def get_body(self):
        return self.__body
    def get_coords(self):
        return self.__coords
    def get_color(self):
        return self.__color

    def set_width(self, new_value: float):
        self.__width = new_value

    def set_height(self, new_value: float):
        self.__height = new_value

    def set_body(self, new_value: pygame.Rect):
        self.__body = new_value
        self.__coords = pygame.Vector2(self.__body.center)

    def set_color(self, new_value: Tuple[int,int,int]):
        self.__color = new_value

    def _move(self, x: Union[float, None] = None, y: Union[float, None] = None):
        if x is not None:
            self.__coords.x = x
        if y is not None:
            self.__coords.y = y
        self.update_body()

    def _move_v(self, new_coords: pygame.Vector2):
        self.__coords = new_coords
        self.update_body()

    def _translate(self, dx: Union[float, None] = None, dy: Union[float, None] = None):
        if dx is not None:
            self.__coords.x += dx
        if dy is not None:
            self.__coords.y += dy
        self.update_body()

    def _translate_v(self, delta: pygame.Vector2):
        self.__coords += delta
        self.update_body()
    def update_body(self):
        self.__body.center = (int(self.__coords.x), int(self.__coords.y))


class Entity(Body):
    def __init__(self, health:float = 300, attack: float = 300):
        super().__init__(40, 40)
        self.__speed = 300
        self.__health: float = health
        self.__attack: float = attack

    def move(self, dx: Union[float, None] = None, dy: Union[float, None] = None, dt: Union[float, None] = None):
        if dt is not None:
            if dx is not None: dx *= self.__speed * dt
            if dy is not None: dy *= self.__speed * dt
        else:
            if dx is not None: dx *= self.__speed
            if dy is not None: dy *= self.__speed
        super()._translate(dx, dy)


global_item_count = 0
class Interactable:
    def __init__(self) -> None:
        pass
class Item(Interactable):
    counter = 0
    def __init__(self, id=None):
        if id is None:
            id = Item.counter
            Item.counter += 1
        self.__id = id
        self.body = pygame.Rect(0,0, 10,10)
        print("New Item:", self.__id);
    def copy(self):
        return Item(id=self.__id)
    def drop(self):
        print(f"Dropped Item: {self.__id}")
        ...
    def __repr__(self) -> str:
        return f"Item: {self.__id}"

class Weapon(Item):
    def __init__(self) -> None:
        super().__init__()
    def attack(self, *args, **kwargs):
        ...
class Sword(Weapon):
    def __init__(self) -> None:
        super().__init__()
    def attack(self, *args, **kwargs):
        ...


class Camera:
    def __init__(self, screen_width: int, screen_height: int):
        # Camera offset (what gets applied to world coords to map to screen coords)
        self.offset = pygame.Vector2(0, 0)
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, target: Body):
        """
        Update camera offset based on target (usually the player).
        Centers the target on the screen.
        """
        # Center the camera on the target
        target_coords = target.get_coords()
        self.offset.x = target_coords.x - self.screen_width // 2
        self.offset.y = target_coords.y - self.screen_height // 2

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """
        Return a new rect shifted by the camera offset for drawing.
        """
        return rect.copy().move(-self.offset.x, -self.offset.y)


class Player(Entity):
    def __init__(self):
        super().__init__()
        self.id = "player"
        self.__inventory: List[Item|None] = [ None for _ in range(40) ]
        self.interface_items: List[Interactable] = []
        self.__direction: float = 0 # angle from the vertical/bearing?
        self.__relative_to_screen_position: pygame.Vector2 = pygame.Vector2(0,0)
    def get_inventory(self):
        return [item.copy() if item is not None else None for item in self.__inventory.copy()]

    def add_to_inventory(self, item:Item|None, position:int|None=None):
        if item is None: raise Exception("Item can not be none")
        if position is not None:
            current = item
            while current != None and position < len(self.__inventory):
                t_ = self.__inventory[position]
                self.__inventory[position] = current
                current = t_
                position += 1
            if current is None:
                return
            if position >= len(self.__inventory):
                current.drop()
                return
        else:
            for i,v in enumerate(self.__inventory):
                if v is None:
                    self.__inventory[i] = item
                    return
    def __check_for_items(self, world_items:List[Item]):
        items = []
        for item in world_items:
            if self.get_body().colliderect(item.body):  # Check if the current item's rect collides
                items.append(item);
        return items

    def update(self, *args, **kwargs):
        return
        self.__direction = 0

        pygame.mouse.get_pos()
        self.interface_items = self.__check_for_items(kwargs["items"]);
            




def sort_bodies(bodies: list[Body]) -> list[Body]:
    for b in bodies:
        print(f"{b.get_id}: {b.get_coords().y}, {b.get_body().y}")
    return sorted(bodies, key=lambda b: b.get_coords().y)

if __name__ == "__main__":
    pygame.init()
    player = Player()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()


    bodies: List[Body] = [player, Body(30, 30, 200,200)]

    running = True
    cam = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    while running:
        dt = clock.tick(FPS) / 1000  # Get time passed in seconds (convert ms to seconds)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        p_direction = pygame.Vector2(0,0)
        # Check each key and move the player accordingly
        if keys[pygame.K_a]:
            p_direction.x += -1
        if keys[pygame.K_d]:
            p_direction.x += 1
        if keys[pygame.K_w]:
            p_direction.y += -1
        if keys[pygame.K_s]:
            p_direction.y += 1
        if p_direction.magnitude() > 0:p_direction = p_direction.normalize()
        player.move(p_direction.x, p_direction.y, dt)
        player.update()
        cam.update(player)


        screen.fill((0,0,0))
        bodies = sort_bodies(bodies)
        for e in bodies:
            pygame.draw.rect(screen, e.get_color(), cam.apply(e.get_body()))

        pygame.display.flip()
    pygame.quit()
    sys.exit()
