import pyxel


# シーン
SCENE_TITLE = 0 #連番にしてシーンの移動が分かりやすい
SCENE_PLAY = 1
SCENE_GAMEOVER = 2
SCENE_GAMECLEAR = 3

# キャラクターサイズ
CHAR_SIZE = 8
BOSS_SIZE = 16 # ボスのみ16x16

# イラストの座標
# プレイヤー、雑魚敵、ハートは8x8
IMG_PLAYER_X, IMG_PLAYER_Y = 0, 40
IMG_ENEMY1_X, IMG_ENEMY1_Y = 40, 40
IMG_ENEMY2_X, IMG_ENEMY2_Y = 8, 48
IMG_HEART_X, IMG_HEART_Y = 80, 48
# ボスは16x16
IMG_BOSS_X, IMG_BOSS_Y = 96, 72

# ゲームバランス
PLAYER_SPEED = 2
BULLET_SPEED = 4
BOSS_HP_MAX = 5

# 背景設定
NUM_STARS = 100 #星を何個描画するか
STAR_COLOR_HIGH = 12 #HIGH=速い 速い星を明るく
STAR_COLOR_LOW = 5 #LOW=遅い　遅い星を暗く


#classを使うことでグローベル変数を減らす updateもdrawも全部一つになると修正が大変
#背景
class Background:
    def __init__(self):
        self.stars = []
        for i in range(NUM_STARS):
            self.stars.append( #ランダムなx,y,speedで星を100個リストに入れる
                (pyxel.rndi(0, pyxel.width - 1), #0から画面右のどこか　0-239
                 pyxel.rndi(0, pyxel.height - 1), #0から画面下のどこか 0-159
                 pyxel.rndf(1, 2.5))
                )

    def update(self):
        for i, (x, y, speed) in enumerate(self.stars):
            x -= speed #星をspeedの値だけ左に移動させる
            if x <= 0: #星が左端に来たら右端に登場させる
                x += pyxel.width
            self.stars[i] = (x, y, speed)

    def draw(self): 
        for (x, y, speed) in self.stars: #星の表示
            #speedが1.8以上の速い星なら明るく、それ以外を暗く
            pyxel.pset(x, y, STAR_COLOR_HIGH if speed > 1.8 else STAR_COLOR_LOW)


#弾
class Bullet:
    def __init__(self, x, y, dx, dy, is_enemy=False):
        self.x = x #弾の座標
        self.y = y 
        self.dx = dx #弾の速度（変化量）　1フレームにどのくらい動くのか
        self.dy = dy #d=difference
        self.is_enemy = is_enemy #自分の弾か敵の弾か
        self.is_active = True #弾が存在するか（当たったらor画面に行ったら消える）
        self.w = 2 #弾の幅
        self.h = 4 #弾の高さ

    def update(self): #弾の移動
        self.x += self.dx #横
        self.y += self.dy #縦
        
        # 画面外判定
        if (self.y < 0 or self.y > pyxel.height or #画面外で削除
            self.x < 0 or self.x > pyxel.width):
            self.is_active = False

    def draw(self): #弾の描画
        color = 8 if self.is_enemy else 10 # 敵弾は赤、自分は黄色
        pyxel.rect(self.x, self.y, self.w, self.h, color) #弾は四角なのでrect


#雑魚敵とボス
class Enemy: 
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind # 1:Stage1 2:Stage2 3:ボス
        self.w = BOSS_SIZE if kind == 3 else CHAR_SIZE #ボス以外の大きさはCHAR_SIZE
        self.h = BOSS_SIZE if kind == 3 else CHAR_SIZE
        self.dir = 1 # 1:右 -1:左
        self.hp = BOSS_HP_MAX if kind == 3 else 1 #ボスの体力はBOSS_HP_MAX
        self.is_active = True #生きてるか
        self.move_timer = 0 #敵の移動を管理する

    def update(self): #移動の処理
        if self.kind == 3: #ボスは1フレームに1ピクセル移動
            self.x += self.dir #右に移動
            if self.x <= 0 or self.x >= pyxel.width - self.w: #右端に到達したら
                self.dir *= -1 #左に移動
                
        else: 
            self.move_timer += 1 #雑魚敵は2フレームに1ピクセル移動
            if self.move_timer % 2 == 0:
                self.x += self.dir #右に移動
                if self.x <= 0 or self.x >= pyxel.width - self.w: #右端に到達したら
                    self.dir *= -1 #左に移動

    def draw(self): #敵の種類ごとに画像を変える
        u, v = 0, 0
        
        if self.kind == 1: #STAGE1
            u, v = IMG_ENEMY1_X, IMG_ENEMY1_Y
        elif self.kind == 2: #STAGE2
            u, v = IMG_ENEMY2_X, IMG_ENEMY2_Y
        elif self.kind == 3: #STAGE3
            u, v = IMG_BOSS_X, IMG_BOSS_Y
            
        #bltのw,hはそれぞれのサイズを使用 ボス16x16 それ以外8x8    
        pyxel.blt(self.x, self.y, 0, u, v, self.w, self.h, 0)

        if self.kind == 3:
            #ボスの体力バー
            bar_width = 30
            bar_height = 3
            bar_x = self.x + BOSS_SIZE//2 - bar_width // 2 #ボスの中心に表示 rectは左端のxから始まる ボスの左端x+ボスの横幅の半分-バーの半分
            bar_y = self.y + BOSS_SIZE + 2 #ボスより少し下
            
            #赤色バーを下地に上に緑色バーをのせて、緑色バーを短くすることで体力の減少を表現
            #減少体力（赤色）　そのまま表示
            pyxel.rect(bar_x, bar_y, bar_width, bar_height, 8)
            
            #現在体力（緑色） ボスの体力に応じて長さを変える
            #現在体力の割合に応じて長さを決める
            current_width = int(bar_width * (self.hp / BOSS_HP_MAX))
            if current_width > 0:
                pyxel.rect(bar_x, bar_y, current_width, bar_height, 11) #11:緑色


#プレイヤー
class Player:
    def __init__(self):
        self.x = pyxel.width // 2 - CHAR_SIZE // 2 #ゲーム開始時にプレイヤーを中央に
        self.y = pyxel.height - 16 #プレイヤーを画面下から少し上
        self.w = CHAR_SIZE #大きさ
        self.h = CHAR_SIZE
        self.hp = 3 #残機3
        
    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT): #左端よりいかない
            self.x = max(self.x - PLAYER_SPEED, 0)
        if pyxel.btn(pyxel.KEY_RIGHT): #右端よりいかない
            self.x = min(self.x + PLAYER_SPEED, pyxel.width - self.w)
            
    def draw(self): #プレイヤー描画
        pyxel.blt(self.x, self.y, 0, IMG_PLAYER_X, IMG_PLAYER_Y, self.w, self.h, 0)


#アプリケーション本体
class App:
    def __init__(self):
        pyxel.init(240, 160, title="Pyxel Invader Game")
        pyxel.load("sample.pyxres")

        self.background = Background() #背景
        self.reset_game() #ゲームを初期化
        
        pyxel.playm(0, loop=True)  # BGM再生
        
        pyxel.run(self.update, self.draw) #ゲームを動かす

    def reset_game(self): #ゲームを初期化
        self.scene = SCENE_TITLE
        self.stage = 1
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.game_frame_count = 0

    def start_stage(self): #敵を配置
        self.enemies = []
        self.bullets = []
        
        spacing = 20 #間隔を適当に20ピクセル開ける
        
        if self.stage == 1: #STAGE1
            #敵3体を横一列
            start_x = (pyxel.width - (3 * spacing)) // 2 + (spacing - CHAR_SIZE)//2
            for i in range(3):
                self.enemies.append(Enemy(start_x + i * spacing, 40, 1))
                
        elif self.stage == 2: #STAGE2
            # 上段5体
            start_x_top = (pyxel.width - (5 * spacing)) // 2 + (spacing - CHAR_SIZE)//2
            for i in range(5):
                self.enemies.append(Enemy(start_x_top + i * spacing, 20, 2))
            
            # 下段3体
            start_x_bot = (pyxel.width - (3 * spacing)) // 2 + (spacing - CHAR_SIZE)//2
            for i in range(3):
                self.enemies.append(Enemy(start_x_bot + i * spacing, 40, 1))
                
        elif self.stage == 3: #STAGE3
            self.enemies.append(Enemy(pyxel.width // 2 - BOSS_SIZE // 2, 30, 3))

    def update(self): #フレーム処理
        self.background.update() #星の移動
        
        if self.scene == SCENE_TITLE: #タイトル画面
            if pyxel.btnp(pyxel.KEY_R): #Rキーでスタート
                self.scene = SCENE_PLAY #ゲーム画面
                self.stage = 1 
                self.player.hp = 3
                self.start_stage() #敵を配置
                
        elif self.scene == SCENE_PLAY: #ゲーム画面
          #プレイヤー、弾、敵などのゲーム全体のフレーム処理
          self.update_play() 
          
        #ゲームクリアorゲームオーバー画面
        elif self.scene == SCENE_GAMEOVER or self.scene == SCENE_GAMECLEAR:
            if pyxel.btnp(pyxel.KEY_R): #Rキーでリスタート
                self.reset_game() #ゲームを初期化
                self.scene = SCENE_PLAY #ゲーム画面
                self.start_stage() #敵を配置

    def update_play(self): #プレイヤー、弾、敵などのゲーム全体のフレーム処理
        self.game_frame_count += 1 #1フレームずつ
        
        #プレイヤー処理
        self.player.update()
        
        #発射スペースキー、画面上に5発まで
        #自分の弾のみ発射
        player_bullets = [b for b in self.bullets if not b.is_enemy]
        if pyxel.btnp(pyxel.KEY_SPACE) and len(player_bullets) < 5: #5発まで
            #弾の発射位置（中心）
            self.bullets.append(Bullet(self.player.x + CHAR_SIZE//2 - 1, self.player.y - 4, 0, -BULLET_SPEED, False))

        #敵処理
        for enemy in self.enemies:
            enemy.update()
            
            #敵の弾の発射位置（中心）
            bullet_start_x = enemy.x + enemy.w // 2 - 1
            bullet_start_y = enemy.y + enemy.h
            
            if enemy.kind == 3: #ボス
                #60フレームに1回必ず発射
                if self.game_frame_count % 60 == 0:
                    # 3方向 左下、真下、右下）
                    self.bullets.append(Bullet(bullet_start_x, bullet_start_y, -2, 2, True))
                    self.bullets.append(Bullet(bullet_start_x, bullet_start_y, 0, 2, True))
                    self.bullets.append(Bullet(bullet_start_x, bullet_start_y, 2, 2, True))
                    
            else: #雑魚敵
                #60フレームに1回ランダムに弾を打つ
                if self.game_frame_count % 60 == 0:
                    if pyxel.rndi(0, 1) == 0: #50%の確率
                        self.bullets.append(
                        Bullet(bullet_start_x, bullet_start_y, 0, 2, True)
                        )
          
        #弾と当たり判定
        active_bullets = [] 
        for b in self.bullets: #生きている弾を処理　それ以外はスキップ
            b.update()
            if not b.is_active:
                continue

            #プレイヤーの弾が敵に命中したとき
            if not b.is_enemy: #自分の弾
                hit_enemy = None #まず命中してないと仮定
                for enemy in self.enemies: #命中したか判定　AABB
                    if (b.x < enemy.x + enemy.w and b.x + b.w > enemy.x and
                        b.y < enemy.y + enemy.h and b.y + b.h > enemy.y):
                        hit_enemy = enemy #命中
                        break
                
                if hit_enemy: #敵に命中時
                    b.is_active = False #弾消滅
                    if hit_enemy.kind == 3: #ボス
                        hit_enemy.hp -= 1
                        if hit_enemy.hp <= 0: #ボス撃破
                            self.enemies.remove(hit_enemy) #ボス削除
                            self.scene = SCENE_GAMECLEAR #ゲームクリア
                            
                    else: #雑魚敵
                        self.enemies.remove(hit_enemy) #雑魚敵削除
                
                if b.is_active: #当たってない弾はそのままリストに追加
                    active_bullets.append(b)

            #敵の弾がプレイヤーに命中したとき
            elif b.is_enemy: #敵の弾
                if (b.x < self.player.x + self.player.w and b.x + b.w > self.player.x and #AABB
                    b.y < self.player.y + self.player.h and b.y + b.h > self.player.y):
                    b.is_active = False #弾消滅
                    self.player.hp -= 1 #残機減少
                    if self.player.hp <= 0: #残機0の時
                        self.scene = SCENE_GAMEOVER #ゲームオーバー
                
                if b.is_active: #当たってない弾はそのままリストに追加
                    active_bullets.append(b)

        self.bullets = active_bullets #弾のリストを更新（いらない弾は消滅）

        #ステージのクリア判定
        if len(self.enemies) == 0 and self.scene == SCENE_PLAY: #画面上に敵がいないandゲーム中
            if self.stage < 3: #STAGE3以下の時進む
                self.stage += 1
                self.start_stage()

    def draw(self): #描画処理
        pyxel.cls(0) #黒で塗りつぶす
        self.background.draw() #流れ星の背景を描写
        
        if self.scene == SCENE_TITLE: #タイトル画面
            pyxel.text(95, 70, "INVADER GAME", 7)
            pyxel.text(85, 90, "Start to Push R", 13)
            
        elif self.scene == SCENE_PLAY: #ゲーム中
            self.player.draw() #プレイヤー
            for enemy in self.enemies: #敵
                enemy.draw()
            for b in self.bullets: #弾
                b.draw()
            
            #UI描画
            #右上にSTAGE
            pyxel.text(190, 5, f"STAGE {self.stage}", 7)
            
            #その下残りENEMY
            total = 0
            if self.stage == 1: total = 3 #STAGE1 3体
            elif self.stage == 2: total = 8 #STAGE2 8体
            elif self.stage == 3: total = 1 #STAGE3 1体
            pyxel.text(190, 15, f"ENEMY {len(self.enemies)}/{total}", 7)
            
            #左上に残機表示（ハート）
            for i in range(self.player.hp):
                pyxel.blt(5 + i * 10, 5, 0, IMG_HEART_X, IMG_HEART_Y, CHAR_SIZE, CHAR_SIZE, 0)
                
        elif self.scene == SCENE_GAMEOVER: #ゲームオーバー画面
            pyxel.text(100, 70, "GAME OVER!", 8)
            pyxel.text(85, 90, "Restart to Push R", 13)
            
        elif self.scene == SCENE_GAMECLEAR: #ゲームクリア画面
            pyxel.text(95, 70, "GAME CLEAR!", 11)
            pyxel.text(85, 90, "Restart to Push R", 13)

App()