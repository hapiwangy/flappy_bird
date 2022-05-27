# 之後要補鍵盤操作
import pygame, neat, time, os, random

pygame.font.init()
WIN_WIDTH = 500
WIN_HEIGHT = 800

# scale2x:把圖片變成兩倍大，比較容易檢視
BIRDS_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMGS = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMGS = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMGS = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
STAT_FONT = pygame.font.SysFont("comicsnas", 50)
OVER_IMG = pygame.image.load(os.path.join("imgs","gameover.png"))
OVER_IMG = pygame.transform.scale(OVER_IMG, (500, 800))
START_IMG = pygame.image.load(os.path.join("imgs", "get_start.png"))
START_IMG = pygame.transform.scale(START_IMG, (500, 800))

class bird:
    IMGS = BIRDS_IMGS
    # 鳥在上下移動的時候頭朝上、下的傾斜角度
    MAX_ROTATION = 25
    # 每次rotate多少(應該是每次鳥會移動多少(包括掉下來跟往上跳))
    ROT_VEL = 20
    # 鳥拍動翅膀的頻率
    ANIMATION_TIME = 5

    def __init__(self, x:int, y:float) -> None:
            self.x = x
            self.y = y 
            # 傾斜角度
            self.tilt = 0
            # 距離上一次跳經過了多久
            self.tickcount = 0
            self.vel = 0
            self.height = self.y
            # 控制現在應該是哪張圖
            self.img_count = 0
            # 決定圖片  
            self.img = self.IMGS[0]
    # 跳
    def jump(self):
        # 因為0, 0是左上角，要往上的話y-axis要-，反之要+
        self.vel = -10.5
        # 追蹤我們上一次跳的時候(每次跳就會重製這個數字)
        self.tickcount = 0
        # 根據當前的高度和跳的次數
        self.height = self.y
    # 這樣寫出來之後就可以在while迴圈之中呼叫這個function就會自動算每次應該要移動的距離了

    def move(self):
        self.tickcount += 1

        # decide要移動多少(根據上一次跳經過了多久來決定要掉多少)
        # 也就是要模擬越跳越快的感覺
        d = self.vel*self.tickcount + 1.5 * self.tickcount ** 2

        # 避免掉落速度太快
        if d >= 16:
            d = 16
        
        # 決定跳高高會跳多少
        if d < 0:
            d -= 2
        
        # 根據計算調整y的高度
        self.y = self.y + d

        # bird傾斜
        # 判斷我們的鳥正在上升，下一個瞬間也是要做上升的行為
        if d <= 0 or self.y  < self.height + 50:
            # 確定鳥不會翻過去
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        # 如果不是的話，讓鳥往下傾斜
        else:
            if self.tilt  >= -90:
                self.tilt -= self.ROT_VEL
    # 這裡不斷刷新鳥的三張圖讓他有拍翅膀的感覺
    def draw(self, win):
        # 判斷已經刷新幾張圖片了
        self.img_count += 1

        if self.img_count  < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]

        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # 如果鳥要掉下去了就不能拍動翅膀
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2
        
        # 這裡寫如何去翻轉鳥鳥
        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        #但只有上面這樣會讓圖片以左上角為中心去旋轉
        # 加入下面這個可以讓旋轉的中心在中間
        new_rect = rotated_img.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        
        # 最後再把調整好的東西畫出來
        win.blit(rotated_img, new_rect.topleft)
    # 這個方法可以回傳鳥的mask(用在碰撞判斷)
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    # 兩個之間的差距
    GAP = 200
    # 每次會移動的距離
    VEL = 5
    def __init__(self, x) -> None:
        self.x = x
        self.height = 0

        #決定top 跟bottom要畫在哪裡

        self.top = 0
        self.bottom = 0
        # 因為我們的pipe圖案是由兩個pipe(一正一反)組成的，所以要用一個正的，一個返的
        self.pipe_top = pygame.transform.flip(PIPE_IMGS, False, True)
        self.pipe_bottom = PIPE_IMGS  

        # 判斷鳥有沒有通過
        self.passed = False
        # 設定pipe的高度、間隔等等
        self.set_hight()

    def set_hight(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.pipe_top.get_height()
        self.bottom = self.height + self.GAP
    
    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.pipe_top, (self.x, self.top))
        win.blit(self.pipe_bottom, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.pipe_top)
        bot_mask = pygame.mask.from_surface(self.pipe_bottom)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bot_offset = (self.x - bird.x, self.bottom - round(bird.y))
        
        # 告訴我們低一個重疊的點(鳥跟pipe)(如果沒有重疊的話回傳None)
        bot_point = bird_mask.overlap(bot_mask, bot_offset)
        top_point = bird_mask.overlap(top_mask, top_offset)

        # 重疊的畫return True
        if bot_point or top_point:
            return True
        return False    
    
class Base:
    # 要跟pipe依樣，不然看起來是以不同速度在動
    VEL = 5
    WIDTH = BASE_IMGS.get_width()
    IMG = BASE_IMGS
    
    def __init__(self, y) -> None:
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # 把已經超出遊戲畫面的圖片放到現在正在顯示中的圖片的後面
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, window):
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))
# 把所有的東西畫到window上面
def draw_window(window, bird, pipes, base, score):
    window.blit(BG_IMGS, (0,0))
    for pipe in pipes:
        pipe.draw(window)
    text = STAT_FONT.render("Scores :" + str(score), 1, (255, 255, 255))
    window.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    base.draw(window)
    # bilt代表把東西畫到前面的那個window上面
    bird.draw(window)
    pygame.display.update()

def show_over(window):
    window.blit(OVER_IMG, (0, 0))
    pygame.display.update()
def show_start(window):
    window.blit(START_IMG, (0, 0))
    pygame.display.update()


def main():

    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    #使用clock物件來控制執行的速度
    clock = pygame.time.Clock()
    run1 = False
    show_start(window)
    #遊戲起點
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    run1 = True
        #mbird.move()
        # rem用來儲存即將要remove的pipe
        # add_pipe用來判斷是否要新Pipe
        mbird = bird(230, 350)
        base = Base(630)
        pipes = [Pipe(700)]
        score = 0
        over = False
        while run1:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_KP_ENTER:
                        run1 = False
                        time.sleep(1)
                        over = True
                    elif event.key == pygame.K_SPACE:
                        mbird.jump()
            mbird.move()
            add_pipe = False
            rem = []
            for pipe in pipes:
                if pipe.collide(mbird):
                    # 撞到鳥要結束
                    while mbird.y < 730:
                        mbird.y +=30
                        mbird.move()
                        draw_window(window, mbird, pipes, base, score)
                    run1 = False
                    over = True
                 
                # if pipe超出螢幕
                if pipe.x + pipe.pipe_top.get_width() < 0:
                    rem.append(pipe)
                # 如果鳥飛過去pipe而且已經超過pipe了
                if not pipe.passed and pipe.x < mbird.x:
                    pipe.passed = True
                    add_pipe = True
                pipe.move()
            # 新增pipe並+1分
            if add_pipe:
                score += 1
                pipes.append(Pipe(600))
            # 把要刪除的pipe移除
            for r in rem:
                pipes.remove(r)

            if mbird.y + mbird.img.get_height() >= 730:
                run1 = False
                over = True
            base.move()
            draw_window(window, mbird, pipes, base, score)
            if over:
                show_over(window)

        
    pygame.quit()
    quit()

main( )