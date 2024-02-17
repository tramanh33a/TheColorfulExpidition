from itertools import cycle
import sys
import random
import pygame
import math
from pygame.locals import *
from Component import Button

FRAME_RATE = 60.0
SCREEN_SIZE = (1366, 768)
IMAGE, SOUND, HITMASK = {}, {}, {}  # All the dictionaries that hold the items correspond to their name

COLOR = ('Yellow', 'Blue', 'Red', 'Green', 'Orange', 'Purple')  # the game involves colors, make a set of it
# Use a tuple since we don't need to change anything but still need the order
ENABILITY = ['Blue', 'Yellow']  # Disable the appearance of colors until reach a specific score
PLAYER_ENABILITY = ['Yellow']  # Color that the player is allowed to touch

# All the dictionaries assigning stuff


def pygame_modules_have_loaded():  # Check if anything doesn't load

    if not pygame.display.get_init():
        return False
    if not pygame.font.get_init():
        return False
    if not pygame.mixer.get_init():
        return False

    return True

pygame.mixer.pre_init(44100, -16, 2, 512)  # Change the initialization's default setting, in case we need to init again
pygame.init()

if pygame_modules_have_loaded():
    screen = pygame.display.set_mode(SCREEN_SIZE, pygame.SCALED)
    pygame.display.set_caption('The Colorful Expedition')    # Name here
    clock = pygame.time.Clock()
    # main font
    DefaultFont = pygame.font.Font('assets/fonts/Bebas-Regular.ttf', 20)

    # list of image
    IMAGE['logo'] = pygame.image.load('assets/sprites/logo.png').convert_alpha()
    IMAGE['player'] = pygame.image.load('assets/sprites/player_yellow.png').convert_alpha()
    IMAGE['power spike'] = pygame.image.load('assets/sprites/blue_power.png').convert_alpha()
    IMAGE['brick'] = (
        pygame.image.load('assets/sprites/yellow_brick.png').convert_alpha(),
        pygame.image.load('assets/sprites/blue_brick.png').convert_alpha(),
        pygame.image.load('assets/sprites/red_brick.png').convert_alpha(),
        pygame.image.load('assets/sprites/green_brick.png').convert_alpha(),
        pygame.image.load('assets/sprites/orange_brick.png').convert_alpha(),
        pygame.image.load('assets/sprites/purple_brick.png').convert_alpha(),
    )
    IMAGE['Recbutton'] = pygame.image.load(
        'assets/sprites/Recbutton.png').convert_alpha()
    IMAGE['ToLeft'] = pygame.image.load(
        'assets/sprites/ToLeft.png').convert_alpha()
    IMAGE['ToRight'] = pygame.image.load(
        'assets/sprites/ToRight.png').convert_alpha()
    IMAGE['pause'] = pygame.image.load(
        'assets/sprites/pause.png').convert_alpha()
    IMAGE['quit'] = pygame.image.load(
        'assets/sprites/quit.png').convert_alpha()
    IMAGE['setting'] = pygame.image.load(
        'assets/sprites/setting.png').convert_alpha()
    IMAGE['settingBg'] = pygame.image.load(
        'assets/sprites/setting_bg.png').convert_alpha()
    IMAGE['mainScreen'] = pygame.image.load(
        'assets/sprites/main_screen.png').convert_alpha()
    IMAGE['plane'] = pygame.image.load(
        'assets/sprites/plane.png').convert_alpha()
    IMAGE['cloud'] = (
        pygame.image.load('assets/sprites/cloud1.png').convert_alpha(),
        pygame.image.load('assets/sprites/cloud2.png').convert_alpha(),
        pygame.image.load('assets/sprites/cloud3.png').convert_alpha(),
    )
    IMAGE['buildings'] = pygame.image.load('assets/sprites/buildings.png').convert_alpha()
    # list of sounds
    SOUND['power'] = pygame.mixer.Sound('assets/audio/point.wav')
    SOUND['jump'] = pygame.mixer.Sound('assets/audio/jump.wav')
    SOUND['die'] = pygame.mixer.Sound('assets/audio/die.wav')

    pygame.mixer.music.load('assets/audio/bgm.mp3')

    # Basically Global variable, since some of these need to be accessed regularly, cannot be changed
    GravityStrength = 0.95
    PlayerMaxMovingSpeed = 12
    PlayerMaxDroppingSpeed = 30
    PlayerMinX = 0
    PlayerMaxX = 600

    DecoList = []  # List of purely decorative stuff
    BrickList = []  # List of brick that are loaded in the game currently (off-screen brick still count)
    ButtonList = []  # List of clickable thing
    DebugElement = []
    ResolutionList = [(1024, 600), (1280, 720), (1366, 768)]
    SkinList = ['player2', 'player']
    BlockList = ['brick', '3dbrick', 'ice']

    Bg = []

    # Also global variable, but need to be changed, and be accessed regularly
    Player = {'X': 0, 'Y': 50, 'W': IMAGE['player'].get_width(), 'H': IMAGE['player'].get_height(), 'VelocityX': 0,
               'VelocityY': 0, 'OnAir': 1, 'Rotation': 0, 'Orientation': 0, 'collision': 1}
    
    # GameInfo['State']: 0.MainLoop, 1.Lost, 2.Pause, 3.MainScreen, 4.Setting
    GameInfo = {'SkinCurrent': 1, 'BlockCurrent': 0, 'ResolutionCurrent': 2, 'DistanceTravelled': 0, 'State': 0,
                'countbrick': 0, 'Difficulty': 0, 't': 0, 'GameState': 0, 'HighScore': 0}
    Powerspike = {'X': ResolutionList[GameInfo['ResolutionCurrent']][0], 'Y': 400,
                  'W': IMAGE['power spike'].get_width(),
                  'H': IMAGE['power spike'].get_height(), 'Color': 'Blue', 'Enable': 1, 'timeleft': 10, 'touch': 0}

    def new_button(x, y, w, h, font, content, bg, func, arg=0):
        NewButton = Button(x, y, w, h, font, content, bg, func, arg)
        ButtonList.append(NewButton)
        
    def main_screen():
        GameInfo['State'] = 3

        ButtonList.clear()
        new_button(SCREEN_SIZE[0]/2 - 75, 300, 150, 70, DefaultFont, "New Game", IMAGE['Recbutton'], new_game)
        new_button(SCREEN_SIZE[0]/2 - 75, 400, 150, 70, DefaultFont, "Setting", IMAGE['Recbutton'], setting, "Main")
        new_button(SCREEN_SIZE[0]/1.1 - 75, SCREEN_SIZE[1] - 150, 70, 70, DefaultFont, "", IMAGE['quit'], quit_game)

    def setting(prev):
        GameInfo['State'] = 4

        ButtonList.clear()
        new_button(140, 100, 70, 70, DefaultFont, "", IMAGE['ToLeft'], change_volume_bgm, -0.1)
        new_button(340, 100, 70, 70, DefaultFont, "", IMAGE['ToRight'], change_volume_bgm, 0.1)
        new_button(140, 200, 70, 70, DefaultFont, "", IMAGE['ToLeft'], change_volume_vfx, -0.1)
        new_button(340, 200, 70, 70, DefaultFont, "", IMAGE['ToRight'], change_volume_vfx, 0.1)
        new_button(750, 200, 70, 70, DefaultFont, "", IMAGE['ToLeft'], skin_change, -1)
        new_button(1000, 200, 70, 70, DefaultFont, "", IMAGE['ToRight'], skin_change, 1)
        new_button(750, 300, 70, 70, DefaultFont, "", IMAGE['ToLeft'], block_change, -1)
        new_button(1000, 300, 70, 70, DefaultFont, "", IMAGE['ToRight'], block_change, 1)

        if prev == "Setting":
            new_button(70, 300, 150, 70, DefaultFont, 'Difficulty',
                       IMAGE['Recbutton'], nothing)
            new_button(70, 400, 150, 70, DefaultFont,
                       "Return", IMAGE['Recbutton'], pause)

        if prev == "Main":
            new_button(70, 300, 150, 70, DefaultFont, 'Difficulty',
                       IMAGE['Recbutton'], set_difficulty)
            new_button(70, 400, 150, 70, DefaultFont, "Return",
                       IMAGE['Recbutton'], main_screen)


    def set_difficulty():
        GameInfo['Difficulty'] = 1-GameInfo['Difficulty']

    def nothing():
        pass

    def pause():
        GameInfo["State"] = 2

        ButtonList.clear()

        # Volume button

        new_button(1200, 80, 70, 70, DefaultFont, "", IMAGE['pause'], resume)
        new_button(1200, 180, 70, 70, DefaultFont, "", IMAGE['setting'], setting, "Setting")
        new_button(1200, 280, 70, 70, DefaultFont, "", IMAGE['quit'], main_screen)

    def change_resolution():
        GameInfo['ResolutionCurrent'] += 1
        if GameInfo['ResolutionCurrent'] > 2:
            GameInfo['ResolutionCurrent'] = 0

        SCREEN_SIZE = ResolutionList[GameInfo['ResolutionCurrent']]

        pygame.display.set_mode(ResolutionList[GameInfo['ResolutionCurrent']], pygame.SHOWN)

    def change_volume_bgm(value):
        current = pygame.mixer.music.get_volume()
        if value < 0:
            if current - value > 0:
                pygame.mixer.music.set_volume(round(current + value, 1))
            else: 
                pygame.mixer.music.set_volume(0.0)

        else:
            if current + value < 1:
                pygame.mixer.music.set_volume(round(current + value, 1))
            else: 
                pygame.mixer.music.set_volume(1.0)

    def change_volume_vfx(value):
        current = SOUND['jump'].get_volume()
        new = 0.0

        if value < 0:
            if current - value > 0:
                new = round(current + value, 1)
            else: 
                new = 0.0

        else:
            if current + value < 1:
                new = round(current + value, 1)
            else: 
                new = 1.0

        for sound in SOUND:
            SOUND[sound].set_volume(new)

    def skin_change(value): 
        if value > 0:
            if GameInfo['SkinCurrent'] + 1 == len(SkinList):
                GameInfo['SkinCurrent'] = 0
            else:
                GameInfo['SkinCurrent'] += 1
        else:
            if GameInfo['SkinCurrent'] - 1 < 0:
                GameInfo['SkinCurrent'] = len(SkinList) - 1
            else:
                GameInfo['SkinCurrent'] -= 1

        IMAGE['player'] = pygame.image.load('assets/sprites/' + SkinList[GameInfo['SkinCurrent']] + '_yellow.png').convert_alpha()

    def block_change(value): 
        if value > 0:
            if GameInfo['BlockCurrent'] + 1 == len(BlockList):
                GameInfo['BlockCurrent'] = 0
            else:
                GameInfo['BlockCurrent'] += 1
        else:
            if GameInfo['BlockCurrent'] - 1 < 0:
                GameInfo['BlockCurrent'] = len(BlockList) - 1
            else:
                GameInfo['BlockCurrent'] -= 1

        print(GameInfo['BlockCurrent'])

        IMAGE['brick'] = (
            pygame.image.load('assets/sprites/yellow_' + BlockList[GameInfo['BlockCurrent']] + '.png').convert_alpha(),
            pygame.image.load('assets/sprites/blue_' + BlockList[GameInfo['BlockCurrent']] + '.png').convert_alpha(),
            pygame.image.load('assets/sprites/red_' + BlockList[GameInfo['BlockCurrent']] + '.png').convert_alpha(),
            pygame.image.load('assets/sprites/green_' + BlockList[GameInfo['BlockCurrent']] + '.png').convert_alpha(),
            pygame.image.load('assets/sprites/orange_' + BlockList[GameInfo['BlockCurrent']] + '.png').convert_alpha(),
            pygame.image.load('assets/sprites/purple_' + BlockList[GameInfo['BlockCurrent']] + '.png').convert_alpha(),
        )

    def new_game():
        ButtonList.clear()
        pre_main(0)
        GameInfo['State'] = 0
        GameInfo['GameState'] = 0
        new_button(1200, 80, 70, 70, DefaultFont, "", IMAGE['pause'], pause)

    def lose():
        ButtonList.clear()
        new_button(1200, 80, 70, 70, DefaultFont, "", IMAGE['pause'], pause)
        GameInfo['State'] = 1
        GameInfo['GameState'] = 1

        Point = round(GameInfo['DistanceTravelled'] / 50)

        Score = []
        Score.clear()

        f = open("score.txt", "a")
        f.write("\n")
        f.write(str(Point))
        f.close()
        f = open("score.txt", "r")

        for l in f:
           if not l == "":
               Score.append(int(float(l)))

        f.close()

        Score.append(Point)
        Score = list(dict.fromkeys(Score))
        Score.sort(reverse=True)

        GameInfo['HighScore'] = Score[0]

    def resume():
        ButtonList.clear()
        new_button(1200, 80, 70, 70, DefaultFont, "", IMAGE['pause'], pause)
        GameInfo['State'] = GameInfo['GameState']
    
    def quit_game():
        pygame.quit()
        sys.exit()

    # Check if the player touch any color (only brick for now)
    def color_collision(color):
        Gamestate = 0
        for i in range(len(PLAYER_ENABILITY)):
            if color == PLAYER_ENABILITY[i]:
                Gamestate = 1
        if len(PLAYER_ENABILITY) == 2 and color == 'Green' and PLAYER_ENABILITY[1]=='Blue':
                Gamestate = 1
        if len(PLAYER_ENABILITY) == 2 and color == 'Orange' and PLAYER_ENABILITY[1]=='Red':
                Gamestate = 1

        if Gamestate == 0:
            SOUND['die'].play()
            lose()

    # Check if the player touch anything (only brick for now)
    def check_collision():

        PlayerRect = pygame.Rect(Player['X'], Player['Y'], Player['W'], Player['H'])

        onGround = False

        for Brick in BrickList:  # Go through all the brick in the list

            PlayerRectNew = pygame.Rect(Player['X'] + Player['VelocityX'], Player['Y'] + Player['VelocityY'],
                                        Player['W'], Player['H'])

            BrickRect = pygame.Rect(Brick['X'], Brick['Y'], IMAGE['brick'][0].get_width(),
                                    IMAGE['brick'][0].get_height())
            # Create a rectangle of the brick's size and position
            CollisionRect = PlayerRectNew.clip(BrickRect)
            # Create a rectangle where PlayerRect and BrickRect clip or is on top of each other

            if CollisionRect.width != 0 and CollisionRect.height != 0:  # The size of 0 mean brick and player aren't on top of eachother
                if PlayerRect.bottom <= BrickRect.top:
                    Player['VelocityY'] -= PlayerRectNew.bottom - BrickRect.top
                    color_collision(Brick['Color'])
                elif PlayerRect.bottom <= BrickRect.top + 10:
                    Player['VelocityY'] -= PlayerRectNew.bottom - BrickRect.top
                    color_collision(Brick['Color'])
                else:
                    color_collision(Brick['Color'])
                    if (PlayerRect.right > BrickRect.left and PlayerRect.left < BrickRect.right):
                        Player['VelocityY'] -= PlayerRectNew.top - BrickRect.bottom
                        color_collision(Brick['Color'])
                    else:
                        if (PlayerRect.right <= BrickRect.left):
                            Player['VelocityX'] -= PlayerRectNew.right - BrickRect.left
                            color_collision(Brick['Color'])
                        elif (PlayerRect.left >= BrickRect.right):
                            Player['VelocityX'] -= PlayerRectNew.left - BrickRect.right
                            color_collision(Brick['Color'])

            PlayerRectNew = pygame.Rect(Player['X'] + Player['VelocityX'], Player['Y'] + Player['VelocityY'],
                                        Player['W'], Player['H'])

            if PlayerRectNew.right > BrickRect.left and PlayerRectNew.left < BrickRect.right and PlayerRectNew.bottom == BrickRect.top:
                onGround = True
                color_collision(Brick['Color'])

        Player['OnAir'] = not onGround

        # powerspike collision

        PlayerRectNew = pygame.Rect(Player['X'] + Player['VelocityX'], Player['Y'] + Player['VelocityY'], Player['W'],
                                    Player['H'])

        spikeRect = pygame.Rect(Powerspike['X'], Powerspike['Y'], IMAGE['power spike'].get_width(),
                                IMAGE['power spike'].get_height())
        # Create a rectangle of the spike's size and position
        CollisionSpike = PlayerRectNew.clip(spikeRect)
        # Create a rectangle where PlayerRect and spikeRect clip or is on top of eachother
        if Powerspike['Enable'] == 0:
            if CollisionSpike.width != 0 or CollisionSpike.height != 0:  # The size of 0 mean brick and player aren't on top of eachother
                SOUND['power'].play()
                PLAYER_ENABILITY.append(Powerspike['Color'])
                Powerspike['Enable'] = 1
                Powerspike['touch']=1
                Powerspike['X']=ResolutionList[GameInfo['ResolutionCurrent']][0]
            elif Powerspike['X']<=0:
                Powerspike['X'] = ResolutionList[GameInfo['ResolutionCurrent']][0]
        PlayerRectNew = pygame.Rect(Player['X'] + Player['VelocityX'], Player['Y'] + Player['VelocityY'], Player['W'],
                                    Player['H'])

        if PlayerRectNew.right > BrickRect.left and PlayerRectNew.left < BrickRect.right and PlayerRectNew.bottom == BrickRect.top:
            onGround = True
            color_collision(Brick['Color'])

    # The main movement + collision check. All player-movement related thing are running here to get the final destination
    def move_player():

        Player['VelocityY'] += GravityStrength

        check_collision()

        if Player['VelocityY'] > PlayerMaxDroppingSpeed:                # Cap the velocity to the terminal velocity of falling (50)
            Player['VelocityY'] = PlayerMaxDroppingSpeed

        if Player['X'] + Player['VelocityX'] < PlayerMinX:              # Case where the player go to the left most of the screen
            Player['VelocityX'] = PlayerMinX - Player['X']
            Player['X'] = PlayerMinX
            SOUND['die'].play()
            GameInfo['State'] = 1
            lose()

        if Player['X'] + Player['VelocityX'] > PlayerMaxX:            # Case where the player go to the right most of the screen
            move_map(-(Player['X'] + Player['VelocityX'] - PlayerMaxX))
            Player['X'] = PlayerMaxX

        else: Player['X'] += Player['VelocityX']
        Player['Y'] += Player['VelocityY']

        if not Player['OnAir']:
            Player['VelocityY'] = 0

        if Player['OnAir']: 
            Player['Rotation'] -= 4
        else: 
            Player['Rotation'] = round(Player['Rotation']/90)*90
        
    # Case where the player is about to move out of the screen, so the screen need to move backward
    def move_map(value):
        for i in range(len(BrickList)):
            BrickList[i]['X'] += value

        for decor in DecoList:
            decor['pos'][0] += round(value/3)

        for back in Bg:
            back['pos'][0] += round(value/3)

    def move_spike(value):
        if Powerspike['Enable'] == 0:
            Powerspike['X'] += value
    
    # Check for player's input obviously
    def obstacles():  # Map Stuff (Floor, Obstacles, etc.)
        DebugElement.append(Powerspike['timeleft'])
        points = GameInfo['DistanceTravelled'] / 50
        if (int(points)-400) % 200 == 0 and int(points) >= 400:
            Powerspike['Enable'] = 0
            Powerspike['Color'] = COLOR[random.randint(1,2)]

        if BrickList[0]['X'] + IMAGE['brick'][0].get_width() < 0:
            BrickList.pop(0)
        if BrickList[-1]['X'] + IMAGE['brick'][0].get_width() < SCREEN_SIZE[0]:
            if BrickList[0]['X'] + IMAGE['brick'][0].get_width() < 0:
                BrickList.pop(0)
            if BrickList[-1]['X'] + IMAGE['brick'][0].get_width() < SCREEN_SIZE[0]:
                if points <= 200:
                    if GameInfo['countbrick'] <= 2:
                        NewBrick = {'X': BrickList[-1]['X'] + 100, 'Y': 600,
                                    'Color': ENABILITY[random.randint(0, len(ENABILITY) - 1)]}
                        for i in range(len(PLAYER_ENABILITY)):
                            if NewBrick['Color'] != PLAYER_ENABILITY[i - 1]:
                                GameInfo['countbrick'] += 1
                    else:
                        NewBrick = {'X': BrickList[-1]['X'] + 100, 'Y': 600,
                                    'Color': PLAYER_ENABILITY[random.randint(0, len(PLAYER_ENABILITY) - 1)]}
                        GameInfo['countbrick'] = 0
                elif points <= 350.0:
                    if len(ENABILITY) == 2:
                        ENABILITY.append('Red')
                    if GameInfo['countbrick'] <= 1:
                        NewBrick = {'X': BrickList[-1]['X'] + 100, 'Y': 600,
                                    'Color': ENABILITY[random.randint(0, len(ENABILITY) - 1)]}
                        for i in range(len(PLAYER_ENABILITY)):
                            if NewBrick['Color'] != PLAYER_ENABILITY[i]:
                                GameInfo['countbrick'] += 1
                    else:
                        NewBrick = {'X': BrickList[-1]['X'] + 100, 'Y': 600,
                                    'Color': PLAYER_ENABILITY[random.randint(0, len(PLAYER_ENABILITY) - 1)]}
                        GameInfo['countbrick'] = 0
                elif points <= 500.0:
                    if len(ENABILITY) == 2:
                        ENABILITY.append('Red')
                    if GameInfo['countbrick'] <= 1:
                        NewBrick = {'X': BrickList[-1]['X'] + 100 + (random.randint(0, 2) % 2) * 75, 'Y': 600,
                                    'Color': ENABILITY[random.randint(0, len(ENABILITY) - 1)]}
                        for i in range(len(PLAYER_ENABILITY)):
                            if NewBrick['Color'] != PLAYER_ENABILITY[i]:
                                GameInfo['countbrick'] += 1
                    else:
                        GameInfo['countbrick'] = 0
                        NewBrick = {'X': BrickList[-1]['X'] + 100 + (random.randint(0, 2) % 2) * 75, 'Y': 600,
                                    'Color': PLAYER_ENABILITY[random.randint(0, len(PLAYER_ENABILITY) - 1)]}
                elif points <= 700.0:
                    if len(ENABILITY) == 2:
                        ENABILITY.append('Red')
                    if GameInfo['countbrick'] <= 1:
                        NewBrick = {'X': BrickList[-1]['X'] + 100 + (random.randint(0, 2) % 2) * 75,
                                    'Y': 600 - (random.randint(0, 2) % 2) * 50,
                                    'Color': ENABILITY[random.randint(0, len(ENABILITY) - 1)]}
                        for i in range(len(PLAYER_ENABILITY)):
                            if NewBrick['Color'] != PLAYER_ENABILITY[i]:
                                GameInfo['countbrick'] += 1
                    else:
                        NewBrick = {'X': BrickList[-1]['X'] + 100 + (random.randint(0, 2) % 2) * 75,
                                    'Y': 600 - (random.randint(0, 2) % 2) * 50,
                                    'Color': PLAYER_ENABILITY[random.randint(0, len(PLAYER_ENABILITY) - 1)]}
                        GameInfo['countbrick'] = 0
                elif points <= 1000.0:
                    if len(ENABILITY) == 2:
                        ENABILITY.append('Red')
                    if GameInfo['countbrick'] <= 1:
                        NewBrick = {'X': BrickList[-1]['X'] + 100 + (random.randint(0, 2) % 2) * 75,
                                    'Y': 600 - (random.randint(0, 2) % 2) * 50,
                                    'Color': ENABILITY[random.randint(0, len(ENABILITY) - 1)]}
                        for i in range(len(PLAYER_ENABILITY)):
                            if NewBrick['Color'] != PLAYER_ENABILITY[i]:
                                GameInfo['countbrick'] += 1
                    else:
                        NewBrick = {'X': BrickList[-1]['X'] + 100 + (random.randint(0, 2) % 2) * 75,
                                    'Y': 600 - (random.randint(0, 2) % 2) * 50,
                                    'Color': PLAYER_ENABILITY[random.randint(0, len(PLAYER_ENABILITY) - 1)]}
                        GameInfo['countbrick'] = 0
                else:
                    if GameInfo['countbrick'] <= 1:
                        NewBrick = {'X': BrickList[-1]['X'] + 100 + (random.randint(0, 2) % 2) * 75,
                                    'Y': 600 - (random.randint(0, 2) % 2) * 75,
                                    'Color': ENABILITY[random.randint(0, len(ENABILITY) - 1)]}
                        for i in range(len(PLAYER_ENABILITY)):
                            if NewBrick['Color'] != PLAYER_ENABILITY[i]:
                                GameInfo['countbrick'] += 1
                    else:
                        NewBrick = {'X': BrickList[-1]['X'] + 100 + (random.randint(0, 2) % 2) * 75,
                                    'Y': 600 - (random.randint(0, 2) % 2) * 75,
                                    'Color': PLAYER_ENABILITY[random.randint(0, len(PLAYER_ENABILITY) - 1)]}
                        GameInfo['countbrick'] = 0
                if GameInfo['State']==0 and int(GameInfo['t']) % 4 == 0 and GameInfo['Difficulty'] == 1:
                    BrickList[random.randint(9, 11)]['Color'] = COLOR[random.randint(0,5)]
                if len(PLAYER_ENABILITY)==1 and NewBrick['Color']=='Blue':
                    NewBrick['Color']=COLOR[random.randint(1,5)]
                elif len(PLAYER_ENABILITY)==1 and NewBrick['Color'] == 'Red':
                    NewBrick['Color']=COLOR[random.randint(1,5)]
                elif len(PLAYER_ENABILITY)==2 and NewBrick['Color'] == 'Blue' and PLAYER_ENABILITY[1]=='Blue':
                    NewBrick['Color']=COLOR[random.randint(0,1)*2+1]
                elif len(PLAYER_ENABILITY)==2 and NewBrick['Color'] == 'Red' and PLAYER_ENABILITY[1]=='Red':
                    NewBrick['Color']=COLOR[random.randint(1,2)*2]
                elif len(PLAYER_ENABILITY)==2 and NewBrick['Color'] == 'Blue' and PLAYER_ENABILITY[1]=='Red':
                    NewBrick['Color']=COLOR[random.randint(0,2)*2+1]
                elif len(PLAYER_ENABILITY)==2 and NewBrick['Color'] == 'Red' and PLAYER_ENABILITY[1]=='Blue':
                    NewBrick['Color']=COLOR[random.randint(1,2)*2]
                elif len(PLAYER_ENABILITY) == 2 and NewBrick['Color'] == 'Yellow' and PLAYER_ENABILITY[1]=='Blue':
                    NewBrick['Color'] = COLOR[0]
                elif len(PLAYER_ENABILITY) == 2 and NewBrick['Color'] == 'Yellow' and PLAYER_ENABILITY[1]=='Red':
                    NewBrick['Color'] = COLOR[0]
                BrickList.append(NewBrick)

    def deco():
        plane = random.randint(1,2000)
        cloud = random.randint(1,1000)

        for decor in DecoList:
            decor['pos'][0] -= decor['velocity'][0]
            decor['pos'][1] -= decor['velocity'][1]
            if decor['pos'][0] < -100: DecoList.pop(DecoList.index(decor))

        if plane == 1:
            DecoList.append( {'type': IMAGE['plane'], 'velocity': (random.randint(2,6), 0), 'pos': [SCREEN_SIZE[0],random.randint(100, 400)]})

        if cloud == 1:
            DecoList.append( {'type': IMAGE['cloud'][random.randint(0,2)], 'velocity': (random.randint(1,3), 0), 'pos': [SCREEN_SIZE[0],random.randint(200, 300)]})

    def background():
        lastBg = Bg[-1]

        if lastBg['pos'][0] + lastBg['image'].get_width() < SCREEN_SIZE[0]:
            Bg.append( {'image': IMAGE['buildings'], 'pos': [SCREEN_SIZE[0], SCREEN_SIZE[1] - IMAGE['buildings'].get_height()] } )

        firstBg = Bg[0]

        if firstBg['pos'][0] + firstBg['image'].get_width() < 0: Bg.pop(0)

    # For click in
    def handle_click():
        m = pygame.mouse.get_pos()
        for i in range(len(ButtonList)):
            B = ButtonList[i]
            if B.inRange(m):
                if B.arg == 0:
                    B.func()
                else:
                    B.func(B.arg)

                return

    # For input that should only be read once every keydown
    def handle_input_static(state):
        k = pygame.key.get_pressed()
        if state == 0:
            if k[pygame.K_ESCAPE]:
                pause()

        elif state == 1:
            if k[pygame.K_SPACE]:
                pre_main(0)

        elif state == 2:
            if k[pygame.K_ESCAPE]:
                resume()

    # For holdable input, or those that need continuous read
    def handle_input_continuous(state):
        k = pygame.key.get_pressed()
        if state == 0:
            # Left & Right movement
            if (k[pygame.K_d] and not k[pygame.K_a]) or (k[pygame.K_RIGHT] and not k[pygame.K_LEFT]):
                if Player['VelocityX'] + 1 <= PlayerMaxMovingSpeed:
                    Player['VelocityX'] += 1
                else:
                    Player['VelocityX'] = 10
                Player['Orientation'] = 1

            elif (k[pygame.K_a] and not k[pygame.K_d]) or (k[pygame.K_LEFT] and not k[pygame.K_RIGHT]):
                if abs(Player['VelocityX'] - 1) <= PlayerMaxMovingSpeed:
                    Player['VelocityX'] -= 1
                else:
                    Player['VelocityX'] = -10
                Player['Orientation'] = 0
            else:
                if Player['VelocityX'] != 0: Player['VelocityX'] -= 1 * (Player['VelocityX'] / abs(Player['VelocityX']))

            # Jump / Up Down movement
            if k[pygame.K_w] or k[pygame.K_UP]:
                if not Player['OnAir']:
                    Player['VelocityY'] -= 20
                    SOUND['jump'].play()

    def debug_text():
        location = [600,0]
        for text in DebugElement:
            debugLine = DefaultFont.render(str(text), True, (0,0,0))
            screen.blit(debugLine,(location[0], location[1]))
            location[1] += 16

    # Update run every tick
    def update(time,state):

        screen.fill((0, 178,255)) # Clear the whole thing first lol

        DebugElement.clear()

        handle_input_continuous(GameInfo['State'])

        if state == 0:
            move_player()

            # Map Stuff (Floor, Obstacles, etc.)
            obstacles()
            deco()
            background()

            if GameInfo['t'] >= 2:
                ease = GameInfo['DistanceTravelled'] / 50000 + 2
                Player['X'] -= ease
                if Powerspike['Enable'] == 0:
                    Powerspike['X'] -= ease
                move_map(-ease)
                move_spike(-ease)

            # Font & Text Stuff
            GameInfo['DistanceTravelled'] += Player['VelocityX']

        # Change to the screen (make sure to add all the position update stuff before this)
        if Powerspike['Enable'] == 0 and GameInfo['State']==0:
            IMAGE['power spike'] = pygame.image.load('assets/sprites/'+Powerspike['Color']+'_power.png').convert_alpha()
            screen.blit(IMAGE['power spike'], (Powerspike['X'], 400))
        if Powerspike['timeleft'] <= 0:
            Powerspike['Enable'] = 1
            Powerspike['touch'] = 0
            PLAYER_ENABILITY.pop()
            Powerspike['timeleft'] = 10
        else:
            if len(PLAYER_ENABILITY)==2 and PLAYER_ENABILITY[1]=='Blue':
                IMAGE['player'] = pygame.image.load('assets/sprites/'+ SkinList[GameInfo['SkinCurrent']] +'_green.png').convert_alpha()
            elif len(PLAYER_ENABILITY)==2 and PLAYER_ENABILITY[1]=='Red':
                pass
                IMAGE['player'] = pygame.image.load('assets/sprites/' + SkinList[GameInfo['SkinCurrent']] + '_orange.png').convert_alpha()
            elif len(PLAYER_ENABILITY)==1:
                pass
                IMAGE['player'] = pygame.image.load('assets/sprites/' + SkinList[GameInfo['SkinCurrent']] + '_yellow.png').convert_alpha()

        if state == 0 or state == 1 or state == 2: 
            debug_text()

            for back in Bg:
                screen.blit(back['image'], back['pos'])

            count = 0
            screen.blit(pygame.transform.flip(
                pygame.transform.rotate(pygame.transform.scale(IMAGE['player'], (30, 30)), Player['Rotation']),
                not Player['Orientation'], False), (Player['X'], Player['Y']))
            #if count<=3 and int(time) % 4 ==0 and GameInfo['Difficulty'] == 1:
                #BrickList[random.randint(9, 11)]['Color'] = ENABILITY[random.randint(0,len(ENABILITY)-1)]
                #count += 1
            for i in range(len(BrickList)):
                screen.blit(IMAGE['brick'][COLOR.index(BrickList[i]['Color'])], (BrickList[i]['X'],BrickList[i]['Y']))

            for decor in DecoList:
                screen.blit(pygame.transform.flip(pygame.transform.scale(decor['type'],(75,30)), True, False), decor['pos'])

            screen.blit( DefaultFont.render(str(round(GameInfo['DistanceTravelled']/50)), True, (0,0,0)) ,(0,0))
        if state == 0:
            screen.blit(DefaultFont.render(str(int(time)), True, (0, 0, 0)), (50, 0))

        #If pausing
        if state == 2:
            BigFont = pygame.font.SysFont('assets/fonts/Bebas-Regular.ttf', 48)
            screen.blit( BigFont.render(("Pause"), True, (0,0,0)) ,(60,60))

        # If lost
        if state == 1:
            Player.update({'VelocityX': 0, 'VelocityY': 0})
            ease = 0
            BigFont = pygame.font.SysFont('assets/fonts/Bebas-Regular.ttf', 120)
            score = round(GameInfo['DistanceTravelled'] / 50)
            LoseText = BigFont.render('You Lose!', True, (255,0,0))
            RestartText = DefaultFont.render('Press space to restart', True, (0, 0, 0))
            ScoreText = BigFont.render(str(score), True, (0,200,0))
            PLAYER_ENABILITY.clear()
            PLAYER_ENABILITY.append('Yellow')
            ENABILITY.clear()
            ENABILITY.append('Yellow')
            ENABILITY.append('Blue')
            screen.blit(LoseText,(100,100))
            screen.blit(ScoreText,(110,200))
            screen.blit(RestartText, (110, 300))

            screen.blit(pygame.font.SysFont('assets/fonts/Bebas-Regular.ttf', 60).render('High score: ' + str(GameInfo['HighScore']), True, (155,155,0)),(500,225))

        #if main screen
        if state == 3:
            screen.blit(pygame.transform.scale(
                IMAGE['mainScreen'], SCREEN_SIZE), (0, 0))
        # If in setting
        if state == 4:
            screen.blit( pygame.transform.scale(IMAGE['settingBg'], SCREEN_SIZE), (0,0))

            screen.blit( DefaultFont.render(("BGM"), True, (0,0,0)) ,(70,120))
            screen.blit( DefaultFont.render((str(round(pygame.mixer.music.get_volume() * 10))), True, (0,0,0)) ,(260,120))

            screen.blit( DefaultFont.render(("SFX"), True, (0,0,0)) ,(70,220))
            screen.blit( DefaultFont.render((str(round(SOUND['jump'].get_volume() * 10))), True, (0,0,0)) ,(260,220))
            if GameInfo['Difficulty'] == 1:
                screen.blit(DefaultFont.render(('Hard'), True, (0, 0, 0)), (260, 330))
            else:
                screen.blit(DefaultFont.render(('Easy'), True, (0, 0, 0)), (260, 330))

            screen.blit( DefaultFont.render(("Skin"), True, (0,0,0)) ,(900,130))

            screen.blit( DefaultFont.render(("Player"), True, (0,0,0)) ,(700,200))
            screen.blit( pygame.transform.scale(IMAGE['player'], (30,30)), (900, 210))

            screen.blit( DefaultFont.render(("Block"), True, (0,0,0)) ,(700,300))
            screen.blit( IMAGE['brick'][0], (860, 310))
        for B in ButtonList:
            B.blit(screen)
        # Add in code to be run during each update cycle.
        pygame.display.update()

    # Code for when the player(noob) lose
    def lose_screen():
        pass

    # For code that need to be run before the main game loop. Might be helpful for restarting
    def pre_main(state):
        Player.update({ 'X': 0, 'Y': 50, 'W': IMAGE['player'].get_width(), 'H': IMAGE['player'].get_height(),'VelocityX': 0, 'VelocityY': 0, 'OnAir': 1, 'Orientation': 1, 'Rotation': 90})
        GameInfo.update({'DistanceTravelled': 0, 'GameState': 0, 'State': 0, 't': 0})
        Powerspike.update({'X': ResolutionList[GameInfo['ResolutionCurrent']][0], 'Enable': 1, 'timeleft': 10,'touch': 0})

        if state == 3:
            main_screen()

        else:
            DecoList.clear()
            BrickList.clear()
            Bg.clear()
            Bg.append( {'image': IMAGE['buildings'], 'pos': [0, SCREEN_SIZE[1] - IMAGE['buildings'].get_height()] } )
            ENABILITY = ['Blue', 'Yellow']
            PLAYER_ENABILITY = ['Yellow', '']
            BrickInitLocationX = 0
            BrickinitLocationY = 600
            NewBrick = {'X': BrickInitLocationX, 'Y': BrickinitLocationY, 'Color': 'Yellow'}
            BrickList.append(NewBrick)
            BrickInitLocationX += 100
            while BrickInitLocationX < SCREEN_SIZE[0]:
                NewBrick = {'X': BrickInitLocationX, 'Y': BrickinitLocationY, 'Color': 'Yellow'}
                BrickList.append(NewBrick)
                BrickInitLocationX += 100

    def main():
        pygame.display.set_icon(IMAGE['logo'])
        pygame.mixer.music.unload()
        pygame.mixer.music.load('assets/audio/bgm.mp3')
        pygame.mixer.music.play(-1)

        pre_main(3)
        while True:

            if Player['Y'] > SCREEN_SIZE[1]:
                    GameInfo['State'] = 1

            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    handle_click()
                if event.type == KEYDOWN:
                    handle_input_static(GameInfo['State'])

                if event.type == QUIT:
                    quit_game()
            # Insanely confusing FPS Stuff
            

            milliseconds = clock.tick(FRAME_RATE) # How many milliseconds have passed since the last call
            seconds = milliseconds / 1000.0       # Convert to second
            if GameInfo['State'] ==0:
                GameInfo['t']+= seconds
                if Powerspike['timeleft']>=0 and Powerspike['touch']==1:
                    Powerspike['timeleft']-=seconds
            update(GameInfo['t'], GameInfo['State'])      # Update the game, add the second passed for future event code

            sleep_time = (1000.0 / FRAME_RATE) - milliseconds   # Since the game is locked to 60 fps, we check if the last time we called tick
                                                                # was not as far as it should be. adding sleeptime to make sure the game stay
                                                                # at the same FPS
            if sleep_time > 0.0:  # If the game need pausing, pause it (usually really smol)
                pygame.time.wait(int(sleep_time))
            else:
                pygame.time.wait(1) # else just sleep for 1 milli (not much) (pass might be bad for some reason)

    main()