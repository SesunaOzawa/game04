import tkinter as tk
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('C:\東海5セメ\社会情報実践\production4-429001-14805d5e17b2.json', scope)
client = gspread.authorize(creds)
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1ch7GYCGyWXIHGcO06L0DdfI2z9XOE_aIPjMuSg7upT4/edit?usp=sharing').sheet1

class LeaderboardApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Leaderboard")
        self.canvas = tk.Canvas(master, width=400, height=600, bg="skyblue")
        self.canvas.pack()

        self.show_leaderboard()

    def show_leaderboard(self):
        scores = sheet.get_all_values()
        scores = sorted(scores[1:], key=lambda x: int(x[1]), reverse=True)[:10]

        title = self.canvas.create_text(200, 50, text="スコアランキング", font=("HG創英角ﾎﾟｯﾌﾟ体", 24), fill="orange")
        leaderboard_texts = []

        for i, (date, score) in enumerate(scores):
            color = "red" if i < 3 else "black"
            size = 25 if i < 3 else 20
            leaderboard_texts.append(self.canvas.create_text(200, 100 + (i + 1) * 40, text=f"{date}: {score}", font=("Arial", size), fill=color))

if __name__ == "__main__":
    root = tk.Tk()
    app = LeaderboardApp(root)
    root.mainloop()
