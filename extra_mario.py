import sys
import pygame
import os
from glob import glob
import pygame.mixer


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Game:
    def __init__(self, width=650, height=550):
        pygame.init()
        pygame.mixer.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.tiles_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.maps = None
        self.map_pointer = 0
        self.player = None
        self.map = None
        self.game_over = False
        self.key = False
        self.extra_life = False
        self.coin_counter = 0
        pygame.mixer.music.load('data/main_sounds.mp3')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.05)

    def terminate(self):
        pygame.quit()
        sys.exit()

    def generate_level(self, map):
        self.load_level(map)
        new_player, x, y = None, None, None
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                if self.map[y][x] == '.':
                    tile = Tile('empty', x, y)
                    tile.add(self.tiles_group, self.all_sprites)
                elif self.map[y][x] == '#':
                    tile = Tile('wall', x, y)
                    tile.add(self.tiles_group, self.all_sprites)
                elif self.map[y][x] == 'd':
                    tile = Tile('empty', x, y)
                    tile.add(self.tiles_group, self.all_sprites)
                    tile = Tile('door', x, y)
                    tile.add(self.tiles_group, self.all_sprites)
                elif self.map[y][x] == 'h':
                    tile = Tile('empty', x, y)
                    tile.add(self.tiles_group, self.all_sprites)
                    tile = Tile('extra_life', x + 0.15, y + 0.2)
                    tile.add(self.tiles_group, self.all_sprites)
                elif self.map[y][x] == 'c':
                    tile = Tile('empty', x, y)
                    tile.add(self.tiles_group, self.all_sprites)
                    tile = Tile('coin', x + 0.2, y + 0.25)
                    tile.add(self.tiles_group, self.all_sprites)
                elif self.map[y][x] == 'k':
                    tile = Tile('empty', x, y)
                    tile.add(self.tiles_group, self.all_sprites)
                    tile = Tile('key', x, y)
                    tile.add(self.tiles_group, self.all_sprites)
                elif self.map[y][x] == 'b':
                    tile = Tile('empty', x, y)
                    tile.add(self.tiles_group, self.all_sprites)
                    tile = Tile('bomb', x, y)
                    tile.add(self.tiles_group, self.all_sprites)
                elif self.map[y][x] == '@':
                    tile = Tile('empty', x, y)
                    tile.add(self.tiles_group, self.all_sprites)
                    new_player = Player(x, y)
                    new_player.add(self.player_group, self.all_sprites)
        return new_player, x, y

    def load_level(self, filename):
        filename = "data/" + filename
        # читаем уровень, убирая символы перевода строки
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        # и подсчитываем максимальную длину
        max_width = max(map(len, level_map))
        # дополняем каждую строку пустыми клетками ('.')
        self.map = list(map(lambda x: x.ljust(max_width, '.'), level_map))
        return self.map

    def render_lvl(self):
        self.screen.fill((0, 0, 0))
        self.tiles_group.draw(self.screen)
        self.player_group.draw(self.screen)

    def lose(self):
        self.render_lvl()
        running = True
        v = 200
        clock = pygame.time.Clock()
        pause = 1000
        timer = 0
        x_cord = -300
        y_cord = 0
        #pygame.mixer.music.load('data/mario_death.mp3')
        #pygame.mixer.music.play()
        p = os.path.abspath('data/test.wav')
        sound = pygame.mixer.Sound(p)
        image = load_image('gameover2(small).png')
        self.screen.blit(image, (x_cord, y_cord))
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if timer < pause:
                timer += clock.tick()
            else:
                if x_cord <= 0:
                    x_cord += (v * clock.tick() / 1000)
                    self.screen.blit(image, (int(x_cord), y_cord))
                else:
                    x_cord = 0
                    self.screen.blit(image, (int(x_cord), y_cord))
            pygame.display.flip()

    def win(self):
        running = True
        v = 200
        clock = pygame.time.Clock()
        x_cord = -300
        y_cord = 0
        image = load_image('win.png')
        self.screen.blit(image, (x_cord, y_cord))
        pygame.mixer.music.load('data/win_sounds.mp3')
        pygame.mixer.music.play()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if x_cord <= 0:
                x_cord += (v * clock.tick() / 1000)
                self.screen.blit(image, (int(x_cord), y_cord))
            else:
                x_cord = 0
                self.screen.blit(image, (int(x_cord), y_cord))
                self.all_sprites.empty()
                self.tiles_group.empty()
                self.player_group.empty()
            pygame.display.flip()

    def level_screen(self):
        map = self.maps[self.map_pointer]
        camera = Camera(self.width, self.height)
        self.player = self.generate_level(map)[0]
        self.render_lvl()
        clock = pygame.time.Clock()
        look_left = True
        while True:
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
            arrow_and_not_wall = False
            tiles_types = None
            tiles_collide = None
            if keys[pygame.K_DOWN]:
                self.player.move("down")
                tiles_collide = pygame.sprite.spritecollide(self.player, self.tiles_group, False)
                tiles_types = [tile.tile_type for tile in tiles_collide]
                if "wall" in tiles_types:
                    self.player.move("up")
                else:
                    arrow_and_not_wall = True

            if keys[pygame.K_UP]:
                self.player.move("up")
                tiles_collide = pygame.sprite.spritecollide(self.player, self.tiles_group, False)
                tiles_types = [tile.tile_type for tile in tiles_collide]
                if "wall" in tiles_types:
                    self.player.move("down")
                else:
                    arrow_and_not_wall = True

            if keys[pygame.K_RIGHT]:
                self.player.move("right")
                tiles_collide = pygame.sprite.spritecollide(self.player, self.tiles_group, False)
                tiles_types = [tile.tile_type for tile in tiles_collide]
                if look_left:
                    self.player.image = pygame.transform.flip(self.player.image, True, False)
                    look_left = False
                if "wall" in tiles_types:
                    self.player.move("left")
                else:
                    arrow_and_not_wall = True

            if keys[pygame.K_LEFT]:
                self.player.move("left")
                tiles_collide = pygame.sprite.spritecollide(self.player, self.tiles_group, False)
                tiles_types = [tile.tile_type for tile in tiles_collide]
                if not look_left:
                    self.player.image = pygame.transform.flip(self.player.image, True, False)
                    look_left = True
                if "wall" in tiles_types:
                    self.player.move("right")
                else:
                    arrow_and_not_wall = True

            if arrow_and_not_wall and tiles_collide is not None and tiles_types is not None:
                if 'bomb' in tiles_types and not self.extra_life:
                    self.player.kill()
                    for tile in tiles_collide:
                        if tile.tile_type == 'bomb':
                            tile.image = tile.tile_images["boom"]
                            self.lose()
                            self.game_over = True
                            return
                elif 'bomb' in tiles_types and self.extra_life == True:
                    for tile in tiles_collide:
                        if tile.tile_type == 'bomb':
                            tile.image = tile.tile_images["empty"]
                            self.extra_life = False
                elif 'key' in tiles_types:
                    for tile in tiles_collide:
                        if tile.tile_type == 'key':
                            tile.image = tile.tile_images["empty"]
                            self.key = True
                elif 'coin' in tiles_types:
                    for tile in tiles_collide:
                        if tile.tile_type == 'coin':
                            tile.image = tile.tile_images["empty"]
                            self.coin_counter += 1
                elif 'door' in tiles_types and self.key == True:
                    self.key = False
                    self.all_sprites.empty()
                    self.tiles_group.empty()
                    self.player_group.empty()
                    self.map_pointer += 1
                    if self.map_pointer == len(self.maps):
                        self.win()
                        self.game_over = True
                    return
                elif "extra_life" in tiles_types:
                    for tile in tiles_collide:
                        if tile.tile_type == 'extra_life':
                            tile.image = tile.tile_images["empty"]
                            self.extra_life = True

            camera.update(self.player)
            for sprite in self.all_sprites:
                  camera.apply(sprite)

            self.render_lvl()
            clock.tick(200)
            pygame.display.flip()

    def start_screen(self):
        pygame.init()
        intro_text = ["Добро пожаловать в мир Mario!", "",
                      "Правила игры:",
                      "Подобрать ключ и найти дверь.",
                      "При задевании бомбы вы проигрываете.",
                      "Для продолжения нажмите ЛКМ или ПКМ"]

        fon = pygame.transform.scale(load_image('fon.jpg'), (930, 550))
        self.screen.blit(fon, (-200, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return
            pygame.display.flip()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        self.tile_images = {'wall': load_image('box.png'), 'empty': load_image('grass.png'), 'door': load_image('door.png', -1),
                       'key': load_image('key.png', -1), 'bomb': load_image('mario_bomb.png', -1), 'boom': load_image('boom.png', -1),
                       'extra_life': load_image('heart.png', -1), 'coin': load_image('coin3.png', -1)}
        tile_width = tile_height = 50
        super().__init__()
        self.tile_type = tile_type
        self.image = self.tile_images[self.tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        player_image = load_image('mario.png', -1)
        self.tile_width = self.tile_height = 50
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect().move(self.tile_width * pos_x + 15, self.tile_height * pos_y + 5)

    def move(self, direction):
        if direction == "up":
            self.rect.y -= 1
        elif direction == "down":
            self.rect.y += 1
        elif direction == "left":
            self.rect.x -= 1
        elif direction == "right":
            self.rect.x += 1


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, width, height):
        self.dx = 0
        self.dy = 0
        self.width = width
        self.height = height

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - self.width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - self.height // 2)


def main(maps_dir):
    game = Game(300, 300)
    if os.path.exists("data/" + maps_dir):
        maps = glob("data/" + maps_dir + '/*.txt')
        for i in range(len(maps)):
            maps[i] = maps[i].replace('\\', '/')
            maps[i] = maps[i].replace('data/', '')
        game.maps = maps
        game.start_screen()
        while not game.game_over:
            game.level_screen()
    else:
        print("Папка с уровнями data/" + maps_dir + " не найдена.")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        maps_dir_name = sys.argv[1]
        main(maps_dir_name)
    else:
        print("Введите название папки с уровнями. Пример: python mario2.py maps")
