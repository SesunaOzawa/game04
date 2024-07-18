import tkinter as tk
import random
import gspread
import subprocess
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 初期設定
WIDTH, HEIGHT = 800, 400
PLAYER_SIZE = 5
OBSTACLE_WIDTH = 5
INITIAL_OBSTACLE_HEIGHT = 800
OBSTACLE_SPEED = 7  # 障害物の速度
GRAVITY = 2  # 落下
JUMP_STRENGTH = -20
INITIAL_LIVES = 3

# Google Sheets設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('C:\東海5セメ\社会情報実践\production4-429001-14805d5e17b2.json', scope)
client = gspread.authorize(creds)
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1ch7GYCGyWXIHGcO06L0DdfI2z9XOE_aIPjMuSg7upT4/edit?usp=sharing').sheet1

class JumpGame:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=WIDTH, height=HEIGHT, bg="skyblue")
        self.canvas.pack()

        self.player = self.canvas.create_rectangle(50, HEIGHT - PLAYER_SIZE, 50 + PLAYER_SIZE, HEIGHT, fill="red")
        self.obstacles = []
        self.score = 0
        self.obstacle_speed = OBSTACLE_SPEED
        self.is_jumping = False
        self.jump_velocity = 0
        self.lives = INITIAL_LIVES
        self.game_started = False
        self.is_flashing = False

        self.score_text = self.canvas.create_text(10, 10, anchor='nw', text=f"Score: {self.score}", font=("HG創英角ﾎﾟｯﾌﾟ体", 16), fill="black")
        self.lives_texts = [self.canvas.create_text(WIDTH - (i * 30 + 10), 10, anchor='ne', text="♥", font=("HG創英角ﾎﾟｯﾌﾟ体", 16), fill="red") for i in range(INITIAL_LIVES)]

        self.start_text = self.canvas.create_text(WIDTH // 2, HEIGHT // 3, text="Spaceでスタート", font=("HG創英角ﾎﾟｯﾌﾟ体", 30), fill="white")

        self.master.bind("<space>", self.start_game)

        self.rank_button = tk.Button(master, text="スコアランキング", font=("HG創英角ﾎﾟｯﾌﾟ体", 16), command=self.show_leaderboard)
        self.rank_button.place(x=WIDTH//2 - 100, y=HEIGHT//2 - 30)
        
        self.start_button = tk.Button(master, text="ゲームスタート", font=("HG創英角ﾎﾟｯﾌﾟ体", 16), command=self.start_game)
        self.start_button.place(x=WIDTH//2 - 90, y=HEIGHT//2 + 30)

    def start_game(self, event=None):
        if not self.game_started:
            self.game_started = True
            self.canvas.delete(self.start_text)
            self.rank_button.place_forget()
            self.start_button.place_forget()
            self.master.bind("<space>", self.jump)
            self.update_game()
            self.create_obstacle()

    def jump(self, event):
        if self.game_started and not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = JUMP_STRENGTH

    def create_obstacle(self):
        if self.game_started:
            x = WIDTH
            height = random.randint(30, 100)
            y = HEIGHT - height
            obstacle = self.canvas.create_rectangle(x, y, x + OBSTACLE_WIDTH, HEIGHT, fill="green")
            self.obstacles.append(obstacle)
            
            # 障害物の生成間隔
            interval = random.randint(800, 1000)
            self.master.after(interval, self.create_obstacle)

    def update_game(self):
        if self.game_started:
            self.move_player()
            self.move_obstacles()
            self.check_collisions()
            self.update_score()
            self.master.after(30, self.update_game)

    def move_player(self):
        if self.is_jumping:
            self.canvas.move(self.player, 0, self.jump_velocity)
            self.jump_velocity += GRAVITY
            x0, y0, x1, y1 = self.canvas.coords(self.player)
            if y1 >= HEIGHT:
                self.canvas.coords(self.player, x0, HEIGHT - PLAYER_SIZE, x1, HEIGHT)
                self.is_jumping = False

    def move_obstacles(self):
        for obstacle in self.obstacles:
            self.canvas.move(obstacle, -self.obstacle_speed, 0)
        self.obstacles = [obs for obs in self.obstacles if self.canvas.coords(obs)[2] > 0]

    def check_collisions(self):
        player_coords = self.canvas.coords(self.player)
        for obstacle in self.obstacles:
            if self.hit_obstacle(player_coords, self.canvas.coords(obstacle)):
                self.lives -= 1
                self.canvas.delete(self.lives_texts[self.lives])
                self.obstacles.remove(obstacle)
                self.canvas.delete(obstacle)
                self.flash_screen()
                if self.lives == 0:
                    self.game_over()
                break

    def hit_obstacle(self, player_coords, obstacle_coords):
        if (player_coords[2] > obstacle_coords[0] and
            player_coords[0] < obstacle_coords[2] and
            player_coords[3] > obstacle_coords[1] and
            player_coords[1] < obstacle_coords[3]):
            return True
        return False

    def update_score(self):
        self.score += 1
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

    def flash_screen(self):
        if not self.is_flashing:
            self.is_flashing = True
            self.canvas.config(bg="red")
            self.master.after(100, self.reset_screen)

    def reset_screen(self):
        self.canvas.config(bg="skyblue")
        self.is_flashing = False

    def game_over(self):
        self.game_started = False
        self.save_score()
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text=f"Game Over\nScore: {self.score}\nSpaceで再挑戦", font=("HG創英角ﾎﾟｯﾌﾟ体", 30), fill="white")
        self.master.bind("<space>", self.reset_game)

    def save_score(self):
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sheet.append_row([date_str, self.score])

    def reset_game(self, event=None):
        self.canvas.delete("all")
        self.player = self.canvas.create_rectangle(50, HEIGHT - PLAYER_SIZE, 50 + PLAYER_SIZE, HEIGHT, fill="red")
        self.obstacles = []
        self.score = 0
        self.obstacle_speed = OBSTACLE_SPEED
        self.is_jumping = False
        self.jump_velocity = 0
        self.lives = INITIAL_LIVES
        self.game_started = False
        self.is_flashing = False

        self.score_text = self.canvas.create_text(10, 10, anchor='nw', text=f"Score: {self.score}", font=("HG創英角ﾎﾟｯﾌﾟ体", 16), fill="black")
        self.lives_texts = [self.canvas.create_text(WIDTH - (i * 30 + 10), 10, anchor='ne', text="♥", font=("HG創英角ﾎﾟｯﾌﾟ体", 16), fill="red") for i in range(INITIAL_LIVES)]

        self.start_text = self.canvas.create_text(WIDTH // 2, HEIGHT // 3, text="Spaceでスタート", font=("HG創英角ﾎﾟｯﾌﾟ体", 30), fill="white")

        self.rank_button = tk.Button(self.master, text="スコアランキング", font=("HG創英角ﾎﾟｯﾌﾟ体", 16), command=self.show_leaderboard)
        self.rank_button.place(x=WIDTH//2 - 100, y=HEIGHT//2 - 30)
        
        self.start_button = tk.Button(self.master, text="ゲームスタート", font=("HG創英角ﾎﾟｯﾌﾟ体", 16), command=self.start_game)
        self.start_button.place(x=WIDTH//2 - 90, y=HEIGHT//2 + 30)

        self.master.bind("<space>", self.start_game)

    def show_leaderboard(self):
        subprocess.run(["python", "C:\東海5セメ\社会情報実践\制作物No.4_2.py"])

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Jump Game")
    game = JumpGame(root)
    root.mainloop()
