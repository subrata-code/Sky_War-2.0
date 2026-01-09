import pygame
import sys
import os
from pygame.locals import *
from enemys import *
from hero import *
from shield import Shield
from ultimateSkill import UltimateSkill

class AirCombatGame:
    """Sky War"""
    # Game State
    READY = 1           # Game Pending
    PLAYING = 2         # Game Playing
    OVER = 3            # Game Ended
    status = READY      # Initial State is set to READY
    frame = 0           # Frame Rate
    screen = None       # Game Window
    X_SIZE = 510        # Window Width
    Y_SIZE = 760        # Window Height
    enemies = []        # Enemies
    hero_bullets = []   # Bullet list for the Hero Aircraft
    rewards = []        # Loot or Collectable
    enemy_bullets = []  # Bullet list for the enemy
    our_hero = None     # Hero
    shield = None       # Sheild
    is_ultimate_skill = False # Ultimate status
    ultimate_skill = None  # Ultimate ability
    background = None       # Background picture
    bg_y_one = 0            # Background1 y-axis 
    bg_y_two = 0            # Background2 y-axis
    image_over = None       # Game Over Background
    bgm = None              # Background music
    has_boss = False        # Boss existence 
    boss_count = 0          # Number of bosses eliminated

    @classmethod
    def load_resources(cls):
        cls.image_over = pygame.image.load('../images/gameover.png')
        cls.background = pygame.image.load("../images/background.png")
        cls.bgm = pygame.mixer.music.load("../music/bgm.mp3")


    '''Generation Functions'''
    @classmethod
    def create_objects(cls):

        # Enemy Generation

        if cls.frame % 15 == 0:
            e = EnemyOne()
            e.x = random.randint(0, cls.X_SIZE - e.get_width())
            e.y = - e.get_height()
            cls.enemies.append(e)

        if cls.frame % 20 == 0:
            e = EnemyTwo()
            e.x = random.randint(0, cls.X_SIZE - e.get_width())
            e.y = - e.get_height()
            cls.enemies.append(e)

        if cls.frame % 30 == 0:
            e = EnemyThree()
            e.x = random.randint(0, cls.X_SIZE - e.get_width())
            e.y = - e.get_height()
            cls.enemies.append(e)

        # Generating Boss
        for each in cls.enemies:
            cls.has_boss = False
            if isinstance(each, Boss):
                cls.has_boss = True
                break

        if not cls.has_boss:
            cls.boss_count += 1

        if cls.boss_count == 200:
            cls.boss_count = 0
            boss = Boss()
            boss.x = random.randint(0, cls.X_SIZE - boss.get_width())
            boss.y = - boss.get_height() - 10
            cls.enemies.append(boss)

        # Generating Boss Missle
        if cls.frame % 100 == 0:
            for each in cls.enemies:
                if isinstance(each, Boss) and each.can_shoot:
                    b1 = BossBullet(each, 1, 1)
                    b2 = BossBullet(each, -1, 2)
                    b3 = BossBullet(each, 1, 3)
                    b4 = BossBullet(each, -1, 4)
                    cls.enemy_bullets.extend([b1, b2, b3, b4])

        # Generating Hero Bullet 
        if cls.frame % 3 == 0:
            # tilting bullet
            cls.hero_bullets.append(HeroBulletThree(cls.our_hero, 1))
            cls.hero_bullets.append(HeroBulletThree(cls.our_hero, -1))
            # tilting straight
            cls.hero_bullets.append(HeroBulletFour(cls.our_hero, 1))
            cls.hero_bullets.append(HeroBulletFour(cls.our_hero, -1))

            # Hero Ultimate Bullet
            if cls.is_ultimate_skill:
                # Sword Bullet
                cls.hero_bullets.append(HeroBulletTwo(cls.our_hero))
                # Purple Bullet
                cls.hero_bullets.append(HeroBulletFive(cls.our_hero, 1))
                cls.hero_bullets.append(HeroBulletFive(cls.our_hero, -1))
            else:
                # Fire Bullet
                cls.hero_bullets.append(HeroBulletOne(cls.our_hero))

        # Generating Hero Missle
        if cls.frame % 100 == 0:
            cls.hero_bullets.append(HeroMissileOne(cls.our_hero, -1))
            cls.hero_bullets.append(HeroMissileOne(cls.our_hero, 1))
            cls.hero_bullets.append(HeroMissileTwo(cls.our_hero, -1))
            cls.hero_bullets.append(HeroMissileTwo(cls.our_hero, 1))

        # Generating supply
        for each in cls.enemies:
            if each.destroy_count == 1:
                variable = random.random()
                if variable <= 0.5:
                    if isinstance(each, EnemyOne):
                        star = each.shoot_reward_star(6)
                        if star:
                            cls.rewards.append(star)
                    if isinstance(each, EnemyTwo):
                        star = each.shoot_reward_star(12)
                        if star:
                            cls.rewards.append(star)
                    if isinstance(each, EnemyThree):
                        star = each.shoot_reward_star(24)
                        if star:
                            cls.rewards.append(star)
                    if isinstance(each, Boss):
                        star = each.shoot_reward_star(100)
                        if star:
                            cls.rewards.append(star)
                else:
                    if isinstance(each, EnemyOne):
                        life = each.shoot_reward_life(4)
                        if life:
                            cls.rewards.append(life)
                    if isinstance(each, EnemyTwo):
                        life = each.shoot_reward_life(7)
                        if life:
                            cls.rewards.append(life)
                    if isinstance(each, EnemyThree):
                        life = each.shoot_reward_life(10)
                        if life:
                            cls.rewards.append(life)
                    if isinstance(each, Boss):
                        life = each.shoot_reward_life(100)
                        if life:
                            cls.rewards.append(life)


    '''Collision Detection'''
    @classmethod
    def collision_detection(cls):
        # Check contact of supply and hero
        for each in cls.rewards:
            iscollision = Rect.colliderect(each.get_rect(), cls.our_hero.get_rect())
            if iscollision and isinstance(each, RewardOne):
                each.can_clear = True
                current_mp = cls.our_hero.mp + each.value
                if current_mp >= cls.our_hero.max_mp:
                    cls.our_hero.mp = cls.our_hero.max_mp
                else:
                    cls.our_hero.mp = current_mp
            if iscollision and isinstance(each, RewardTwo):
                each.can_clear = True
                current_hp = cls.our_hero.hp + each.value
                if current_hp >= cls.our_hero.max_hp:
                    cls.our_hero.hp = cls.our_hero.max_hp
                else:
                    cls.our_hero.hp = current_hp

        # check collision of hero and enemy
        for each in cls.enemy_bullets:
            iscollision = Rect.colliderect(each.get_rect(), cls.our_hero.get_rect())
            # missle
            if iscollision and isinstance(each, BossBullet):
                if each.hp > 0:
                    current_hp = cls.our_hero.hp - each.hurt
                    if current_hp <= 0:
                        cls.our_hero.hp = 0
                    else:
                        cls.our_hero.hp = current_hp
                    each.hp = 0
            # normal enemy bullet
            elif iscollision:
                current_hp = cls.our_hero.hp - each.hurt
                if current_hp <= 0:
                    cls.our_hero.hp = 0
                else:
                    cls.our_hero.hp = current_hp
                each.can_clear = True

        # check collision
        for each in cls.enemies:
            iscollision = Rect.colliderect(each.get_rect(), cls.our_hero.get_rect())
            if iscollision and each.hp > 0:
                cls.our_hero.be_hit = True
                current_hp = cls.our_hero.hp - each.hurt
                if current_hp <= 0:
                    cls.our_hero.hp = 0
                else:
                    cls.our_hero.hp = current_hp
                each.hp = 0

        # check collision of hero bullet and enemy
        for each_bullet in cls.hero_bullets:
            for each_enemy in cls.enemies:
                iscollision = Rect.colliderect(each_enemy.get_rect(), each_bullet.get_rect())
                if iscollision and each_enemy.hp > 0:
                    each_bullet.can_clear = True
                    each_enemy.be_hit = True
                    each_enemy.hp -= each_bullet.hurt

        # check collission of hero bullet and boss missle

        for each_enemy_bullet in cls.enemy_bullets:
            if isinstance(each_enemy_bullet, BossBullet):
                for each_hero_bullet in cls.hero_bullets:
                    iscollision = Rect.colliderect(each_enemy_bullet.get_rect(), each_hero_bullet.get_rect())
                    if iscollision and each_enemy_bullet.hp > 0:
                        each_enemy_bullet.be_hit = True
                        each_enemy_bullet.hp -= each_hero_bullet.hurt
                        each_hero_bullet.can_clear = True

        # check hero ultimate and enemy
        if cls.is_ultimate_skill:
            for each in cls.enemies:
                iscollision = Rect.colliderect(each.get_rect(), cls.ultimate_skill.get_rect())
                if iscollision:
                    if isinstance(each, Boss):
                        each.hp -= cls.ultimate_skill.hurt
                    else:
                        each.hp = 0

        # check hero ultimate and boss missle
        if cls.is_ultimate_skill:
            for each in cls.enemy_bullets:
                if isinstance(each, BossBullet):
                    iscollision = Rect.colliderect(each.get_rect(), cls.ultimate_skill.get_rect())
                    if iscollision:
                        each.hp = 0



    '''Boundary Check'''
    @classmethod
    def boundary_detection(cls):
        # hero bullet boundary check 
        for each in cls.hero_bullets:
            if each.x < - 100 or each.x > 100 + cls.X_SIZE or each.y < - each.get_height():
                each.can_clear = True

        # enemy bullet boundary check 
        for each in cls.enemy_bullets:
            if each.y > cls.Y_SIZE:
                each.can_clear = True

        # enemy boundary check 
        for each in cls.enemies:
            if each.y > cls.Y_SIZE:
                each.can_clear = True

        # supply boundary check 
        for each in cls.rewards:
            if each.y > cls.Y_SIZE:
                each.can_clear = True



    '''deletion'''
    @classmethod
    def clear_all(cls):

        # deleting mana point
        if cls.is_ultimate_skill:
            cls.our_hero.mp -= 1
            if cls.our_hero.mp == 0:
                cls.is_ultimate_skill = False

        # deleting supply 
        temp = filter(lambda x: False if x.can_clear else True, cls.rewards)
        cls.rewards = list(temp)
        # deleting enemy
        temp = filter(lambda x: False if x.can_clear else True, cls.enemies)
        cls.enemies = list(temp)
        # deleting enemy bullet
        temp = filter(lambda x: False if x.can_clear else True, cls.enemy_bullets)
        cls.enemy_bullets = list(temp)
        # deleting hero bullet
        temp = filter(lambda x: False if x.can_clear else True, cls.hero_bullets)
        cls.hero_bullets = list(temp)


    '''location update'''
    @classmethod
    def update_position_all(cls):
        # update supply, enemy, bullet, and hero's location
        all_list = cls.rewards + cls.enemies + cls.enemy_bullets + cls.hero_bullets
        for each in all_list:
            each.update_position()

        # update ultimate location
        if cls.is_ultimate_skill:
            cls.ultimate_skill.update_position()
        # update sheild location
        if cls.is_ultimate_skill or cls.our_hero.be_hit:
            cls.shield.update_position()

        # update hero location
        x, y = pygame.mouse.get_pos()
        x -= cls.our_hero.get_width()/2
        y -= cls.our_hero.get_height()/2
        cls.our_hero.move_to(x,y)


    '''update pic'''
    @classmethod
    def update_image_all(cls):

        # update    supply   enemy    low level bullet     hero bullet    pic
        all_list = cls.rewards + cls.enemies + cls.enemy_bullets + cls.hero_bullets
        all_list.append(cls.our_hero)
        for each in all_list:
            each.update_image()

        # update sheild pic
        if cls.is_ultimate_skill or cls.our_hero.be_hit:
            cls.shield.update_image()

        # ultimate update image_rect
        if cls.is_ultimate_skill:
            cls.ultimate_skill.update_image_rect()


    '''Hitpoints and Manapoints'''
    @classmethod
    def draw_hero_value(cls):
        # draw hp and mp
        hp = 0
        mp = 0
        hp_percent = 0
        mp_percent = 0

        if cls.our_hero.hp >= 0:
            hp = cls.our_hero.hp
            hp_percent = hp / cls.our_hero.max_hp
        if cls.our_hero.mp >= 0:
            mp = cls.our_hero.mp
            mp_percent = mp / cls.our_hero.max_mp

        frame_width = 150
        frame_height = 14
        thickness = 3
        # hp frame
        pygame.draw.rect(cls.screen, [200, 200, 200], [30, 710, frame_width, frame_height], thickness)
        # mp frame
        pygame.draw.rect(cls.screen, [200, 200, 200], [30, 730, frame_width, frame_height], thickness)

        width_max = frame_width - 2 * thickness
        height_max = frame_height - 2 * thickness
        hp_width = width_max * hp_percent
        mp_width = width_max * mp_percent
        # hp 
        pygame.draw.rect(cls.screen, [238, 99, 99], [30 + thickness, 710 + thickness, hp_width, height_max], 0)
        # mp
        pygame.draw.rect(cls.screen, [0, 191, 255], [30 + thickness, 730 + thickness, mp_width, height_max], 0)
        # percentage
        my_font = pygame.font.SysFont("tempus sans itc", 17)

        hp_text = "HP               " + str(hp) + "/"+str(cls.our_hero.max_hp)
        hp_percent_text = ("%.2f" % (hp_percent * 100)) + "%"
        mp_text = "MP               " + str(mp) + "/"+str(cls.our_hero.max_mp)
        mp_percent_text = ("%.2f" % (mp_percent * 100)) + "%"

        hp_text_surface_one = my_font.render(hp_text, True, (255, 255, 255))
        hp_text_surface_two = my_font.render(hp_percent_text, True, (255, 255, 255))
        mp_text_surface_one = my_font.render(mp_text, True, (255, 255, 255))
        mp_text_surface_two = my_font.render(mp_percent_text, True, (255, 255, 255))

        cls.screen.blit(hp_text_surface_one, (7, 705))
        cls.screen.blit(hp_text_surface_two, (190, 705))
        cls.screen.blit(mp_text_surface_one, (5, 725))
        cls.screen.blit(mp_text_surface_two, (190, 725))

    '''Ordering'''
    @classmethod
    def draw_all(cls):
        # draw background
        cls.screen.blit(cls.background, (0, cls.bg_y_one))
        cls.screen.blit(cls.background, (0, cls.bg_y_two))

        # draw background
        if cls.is_ultimate_skill:
            cls.ultimate_skill.blit_me(cls.screen)
        # draw sheild
        if cls.is_ultimate_skill or cls.our_hero.be_hit:
            cls.shield.blit_me(cls.screen)
        # draw hero bullet
        for each in cls.hero_bullets:
            each.blit_me(cls.screen)

        # draw hero
        cls.our_hero.blit_me(cls.screen)

        # draw enemy bullet
        for each in cls.enemy_bullets:
            each.blit_me(cls.screen)

        # draw enemy
        for each in cls.enemies:
            each.blit_me(cls.screen)

        # draw supply 
        for each in cls.rewards:
            each.blit_me(cls.screen)

        # draw hp and mp
        cls.draw_hero_value()



    '''Main Prorgam'''
    @classmethod
    def main(cls):

        # Initializing pygame
        pygame.init()
        pygame.display.set_caption("Sky War")
        # Generate a window
        cls.screen = pygame.display.set_mode((cls.X_SIZE, cls.Y_SIZE), pygame.RESIZABLE, 32)

        # Loading
        cls.load_resources()


        # Timing
        clock = pygame.time.Clock()

        # Main loop
        # 1 handling events 2 update game state 

        # looping background music
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.05)


        # Initializng hero, shield, ultimate
        cls.our_hero = Hero()
        cls.our_hero.move_to(200, 500)
        cls.ultimate_skill = UltimateSkill(cls.our_hero, 120, 865, 123)
        cls.shield = Shield(cls.our_hero)


        while True:

            # check if game has ended
            if cls.our_hero.hp <= 0:
                cls.status = cls.OVER

            clock.tick(60)

            # framerate
            cls.frame += 1
            if cls.frame == 1000:
                cls.frame = 0


            '''Events'''
            for event in pygame.event.get():

                # if closed, quit the program
                if event.type == pygame.QUIT:
                    sys.exit()

                # mouse clicked
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if cls.status == cls.READY:
                        cls.status = cls.PLAYING
                    elif cls.status == cls.OVER:
                        cls.status = cls.READY

                # keyboard clicked
                if event.type == pygame.KEYDOWN and cls.status == cls.PLAYING:
                    key_down = event.key
                    # space clicked (ult)
                    if key_down == K_SPACE and cls.our_hero.mp >0:
                        cls.is_ultimate_skill = True


            if cls.status == cls.OVER:
                pass

            elif cls.status == cls.READY:
                cls.frame = 0    
                cls.enemies = []  
                cls.hero_bullets = []  
                cls.rewards = []  
                cls.enemy_bullets = []
                cls.bosses = []  
                # revive
                cls.our_hero.hp = cls.our_hero.max_hp
                cls.our_hero.mp = cls.our_hero.max_mp
                cls.our_hero.move_to(200, 500)

                # initialzie background
                cls.bg_y_one = - cls.background.get_height()
                cls.bg_y_two = 0

                # turn off ult
                cls.is_ultimate_skill = False

            # if game still in progress
            elif cls.status == cls.PLAYING:
                cls.bg_y_one += 10
                cls.bg_y_two +=  10
                if cls.bg_y_one >= 760:
                    cls.bg_y_one -= 2*cls.background.get_height()
                if cls.bg_y_two >= 760:
                    cls.bg_y_two -= 2 * cls.background.get_height()

                cls.collision_detection() 
                cls.boundary_detection() 
                cls.clear_all()                
                cls.create_objects()        
                cls.update_position_all()

            cls.update_image_all() 
            cls.draw_all() 
            # if game ended, then stop drawing anything
            if cls.status == cls.OVER:
                cls.screen.blit(cls.image_over, (0, 0))

            pygame.display.flip() 


if __name__ == "__main__":
    AirCombatGame.main()








