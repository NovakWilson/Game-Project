import sys
import pygame
import os
from glob import glob
import pygame.mixer
import time
import math


def load_image(name, colorkey=None):
    # Загрузка изображения.
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
        pygame.mixer.pre_init(44100, 16, 2, 4096)
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
        self.game_time = 0
        pygame.mixer.music.load('data/main_sounds.mp3')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.05)

    def terminate(self):
        pygame.quit()
        sys.exit()

    def generate_level(self, map):
        # создание карты
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
        # чтение и загрузка файла
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
        # отрисовка всего уровня
        self.screen.fill((0, 0, 0))
        self.tiles_group.draw(self.screen)
        self.player_group.draw(self.screen)

    def lose(self):
        # Отрисовка экрана поражения
        self.render_lvl()
        running = True
        v = 300
        clock = pygame.time.Clock()
        pause = 1000
        timer = 0
        pygame.mixer.music.load('data/mario_death.mp3')
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play()
        x_cord = -600
        y_cord = 0
        image = load_image('big_gameover2(small).png')
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
        # отрисовка экрана при победе
        running = True
        v = 300
        clock = pygame.time.Clock()
        x_cord = -600
        y_cord = 0
        image = load_image('big_win.png')
        self.screen.blit(image, (x_cord, y_cord))
        pygame.mixer.music.load('data/win_sounds.mp3')
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play()
        draw_count = True
        self.game_time = math.ceil(self.game_time)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if draw_count:
                if x_cord <= 0:
                    x_cord += (v * clock.tick() / 1000)
                    self.screen.blit(image, (int(x_cord), y_cord))
                else:
                    minute = self.game_time // 60
                    secund = self.game_time % 60

                    if minute % 10 == 1 and minute % 100 != 11:
                        minute_teg = 'минуту'
                    elif minute % 10 in [2, 3, 4] and minute % 100 not in [12, 13, 14]:
                        minute_teg = 'минуты'
                    else:
                        minute_teg = 'минут'

                    if secund % 10 == 1 and secund % 100 != 11:
                        second_teg = 'секунду'
                    elif secund % 10 in [2, 3, 4] and secund % 100 not in [12, 13, 14]:
                        second_teg = 'секунды'
                    else:
                        second_teg = 'секунд'

                    # Статистика прохождения игры:
                    font = pygame.font.Font(None, 50)
                    # Информация о собранных монетах.
                    text = font.render(str(self.coin_counter) + "/10 Монет собранно", 1, (255, 215, 0))
                    # Информация о времени прохождения игры.
                    if minute > 0:
                        text_time = font.render('За {} {} и {} {}'.format(minute, minute_teg, secund, second_teg), 1, (255, 215, 0))
                    else:
                        text_time = font.render('За {} {}'.format(secund, second_teg), 1, (255, 215, 0))
                    self.screen.blit(text, (120, 400))
                    self.screen.blit(text_time, (130, 450))

                    draw_count = False
                    x_cord = 0

                    # Очискта групп спрайтов
                    self.all_sprites.empty()
                    self.tiles_group.empty()
                    self.player_group.empty()

            pygame.display.flip()

    def level_screen(self):
        # Экран уровня
        t_start = time.time()
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

            # Работа с фоновой музыкой
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_1:
                    pygame.mixer.music.pause()
                elif event.key == pygame.K_2:
                    pygame.mixer.music.unpause()

            # Управление персонажем
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

            # Проверки на столкновения героя с тайлами
            if arrow_and_not_wall and tiles_collide is not None and tiles_types is not None:
                if 'bomb' in tiles_types and not self.extra_life:
                    self.player.kill()
                    for tile in tiles_collide:
                        if tile.tile_type == 'bomb':
                            sound = pygame.mixer.Sound("data/boom.ogg")
                            sound.set_volume(0.1)
                            sound.play()
                            tile.image = tile.tile_images["boom"]
                            self.lose()
                            self.game_over = True
                            return
                elif 'bomb' in tiles_types and self.extra_life == True:
                    for tile in tiles_collide:
                        if tile.tile_type == 'bomb':
                            tile.image = tile.tile_images["empty"]
                            self.extra_life = False
                            self.tiles_group.remove(tile)
                elif 'key' in tiles_types:
                    for tile in tiles_collide:
                        if tile.tile_type == 'key':
                            tile.image = tile.tile_images["empty"]
                            self.key = True
                            self.tiles_group.remove(tile)
                            sound = pygame.mixer.Sound("data/key_sound.ogg")
                            sound.set_volume(0.4)
                            sound.play()
                elif 'coin' in tiles_types:
                    for tile in tiles_collide:
                        if tile.tile_type == 'coin':
                            tile.image = tile.tile_images["empty"]
                            sound = pygame.mixer.Sound("data/coin_sounds.ogg")
                            sound.set_volume(0.1)
                            sound.play()
                            self.coin_counter += 1
                            self.tiles_group.remove(tile)
                elif 'door' in tiles_types and self.key == True:
                    self.key = False
                    self.all_sprites.empty()
                    self.tiles_group.empty()
                    self.player_group.empty()
                    self.map_pointer += 1
                    self.game_time += time.time() - t_start
                    sound = pygame.mixer.Sound("data/next_lvl.ogg")
                    sound.set_volume(0.2)
                    sound.play()
                    if self.map_pointer == len(self.maps):
                        self.win()
                        self.game_over = True
                    return
                elif "extra_life" in tiles_types:
                    for tile in tiles_collide:
                        if tile.tile_type == 'extra_life':
                            tile.image = tile.tile_images["empty"]
                            self.extra_life = True
                            sound = pygame.mixer.Sound("data/extra_life.ogg")
                            sound.set_volume(0.15)
                            sound.play()
                            self.tiles_group.remove(tile)

            # Движение камеры
            camera.update(self.player)
            for sprite in self.all_sprites:
                  camera.apply(sprite)

            self.render_lvl()
            clock.tick(400)
            pygame.display.flip()

    def start_screen(self):
        # Фоновое окно с правилами
        pygame.init()
        intro_text = ["Добро пожаловать в мир Mario!", "",
                      "Правила игры:",
                      "Подобрать ключ и найти дверь.",
                      "При задевании бомбы вы проигрываете.",
                      "Для продолжения нажмите ЛКМ или ПКМ"]
        # fon size: 2560 / 1440 = x / 600 (формула для высчитывания размеров фон экрана)
        fon = pygame.transform.scale(load_image('fon.jpg'), (1066, 600))
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
        # Работа с тайлами
        self.tile_images = {'wall': load_image('big_box.png'), 'empty': load_image('big_grass.png'), 'door': load_image('big_door.png', -1),
                       'key': load_image('big_key.png', -1), 'bomb': load_image('big_mario_bomb.png', -1), 'boom': load_image('big_boom.png', -1),
                       'extra_life': load_image('big_heart.png', -1), 'coin': load_image('big_coin3.png', -1)}
        tile_width = tile_height = 100
        super().__init__()
        self.tile_type = tile_type
        self.image = self.tile_images[self.tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        # работа с персонажем
        player_image = load_image('big_mario.png', -1)
        self.tile_width = self.tile_height = 100
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect().move(self.tile_width * pos_x + 15, self.tile_height * pos_y + 5)

    def move(self, direction):
        # перемещение персонажа
        if direction == "up":
            self.rect.y -= 1
        elif direction == "down":
            self.rect.y += 1
        elif direction == "left":
            self.rect.x -= 1
        elif direction == "right":
            self.rect.x += 1


class Camera:
    # Движение камеры в целом
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
    game = Game(600, 600)
    # Получение названия файла из командной строки и проверка его наличия в папке Data
    if os.path.exists("data/" + maps_dir):
        '''
        С помощью метода glob мы получаем все файлы с расширением txt из папки,
        находящейся в главной папке Data.
        '''
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
    '''
    Получение данных из командной строки.
    "len(sys.argv)" - длинна введенной строки (sys.argv) является списком данных.
    '''
    if len(sys.argv) == 2:
        maps_dir_name = sys.argv[1]
        main(maps_dir_name)
    else:
        print("Введите название папки с уровнями. Пример: python mario2.py maps")
