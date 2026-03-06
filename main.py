import tkinter as tk
from tkinter import messagebox
import random
import time

# 設定題目庫
WORD_BANKS = {
    "Normal": {
        "words": [
            "apple",
            "banana",
            "keyboard",
            "window",
            "mouse",
            "computer",
            "python",
            "coding",
            "practice",
            "example",
        ],
        "time": 10,
    },
    "Hard": {
        "words": [
            "binary search",
            "linked list",
            "cloud storage",
            "data structure",
            "machine learning",
            "user interface",
        ],
        "time": 10,
    },
    "Nightmare": {
        "words": [
            "Practice makes perfect.",
            "Accuracy is more important than speed.",
            "The quick brown fox jumps over the lazy dog.",
        ],
        "time": 15,
    },
}


class SpeedTypingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed Typing Challenge")
        self.root.geometry("600x550")
        self.root.configure(bg="#2E3440")

        # 遊戲變數初始化
        self.current_round = 0
        self.total_rounds = 0
        self.correct_count = 0
        self.total_typed_chars = 0  # 統計打對的總字元數
        self.current_word = ""
        self.time_limit = 0
        self.timer_job = None
        self.game_running = False
        self.start_time = 0

        self.selected_difficulty = "Normal"
        self.setup_initial_ui()

    def setup_initial_ui(self):
        """建立初始畫面（設定回合數與難度）"""
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="Speed Typing Challenge",
            font=("Helvetica", 24, "bold"),
            fg="white",
            bg="#2E3440",
        ).pack(pady=20)

        rounds_frame = tk.Frame(self.root, bg="#2E3440")
        rounds_frame.pack(pady=(15, 5))

        tk.Label(
            rounds_frame,
            text="Rounds:",
            font=("Helvetica", 14),
            fg="white",
            bg="#2E3440",
        ).pack(side=tk.LEFT)
        self.rounds_entry = tk.Entry(
            rounds_frame,
            width=5,
            font=("Helvetica", 14),
            bd=0,
            relief=tk.FLAT,
            justify=tk.CENTER,
        )
        self.rounds_entry.insert(0, "5")
        self.rounds_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(
            self.root,
            text="選擇難度:",
            font=("Helvetica", 14),
            fg="white",
            bg="#2E3440",
        ).pack(pady=5)

        difficulty_frame = tk.Frame(self.root, bg="#2E3440")
        difficulty_frame.pack(pady=10)

        self.difficulty_buttons = {}
        for difficulty in ["Normal", "Hard", "Nightmare"]:
            btn = tk.Button(
                difficulty_frame,
                text=difficulty,
                command=lambda d=difficulty: self.select_difficulty(d),
                font=("Helvetica", 12),
                width=10,
                bg="#4C566A",
                fg="white",
                relief=tk.RAISED,
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.difficulty_buttons[difficulty] = btn

        self.select_difficulty("Normal")

        self.start_button = tk.Button(
            self.root,
            text="Start Game",
            command=self.start_game,
            font=("Helvetica", 16, "bold"),
            bg="#A3BE8C",
            fg="black",
            padx=10,
            pady=5,
        )
        self.start_button.pack(pady=25)

    def select_difficulty(self, difficulty):
        """處理難度按鈕切換視覺效果"""
        self.selected_difficulty = difficulty
        for name, btn in self.difficulty_buttons.items():
            if name == difficulty:
                btn.config(bg="#8FBCBB", fg="black", relief=tk.SUNKEN)
            else:
                btn.config(bg="#4C566A", fg="white", relief=tk.RAISED)

    def start_game(self):
        """開始遊戲，初始化數據與計時器"""
        settings = WORD_BANKS[self.selected_difficulty]
        self.time_limit = settings["time"]
        self.current_word_bank = settings["words"]

        try:
            rounds = int(self.rounds_entry.get())
            if rounds <= 0:
                raise ValueError
            self.total_rounds = rounds
            self.current_round = 0
            self.correct_count = 0
            self.total_typed_chars = 0
            self.game_running = True
            self.start_time = time.time()  # 記錄整場遊戲開始時間
            self.setup_game_ui()
            self.next_round()
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的回合數。")

    def setup_game_ui(self):
        """建立遊戲中的介面"""
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="Speed Typing Challenge",
            font=("Helvetica", 20, "bold"),
            fg="white",
            bg="#2E3440",
        ).pack(pady=10)

        self.round_label = tk.Label(
            self.root,
            text=f"Round: 0/{self.total_rounds}",
            font=("Helvetica", 12),
            fg="#EBCB8B",
            bg="#2E3440",
        )
        self.round_label.pack()

        self.word_label = tk.Label(
            self.root,
            text="",
            font=("Courier New", 24, "bold"),
            fg="#8FBCBB",
            bg="#2E3440",
            wraplength=550,
        )
        self.word_label.pack(pady=(40, 10))

        self.time_label = tk.Label(
            self.root, text="", font=("Helvetica", 12), fg="#EBCB8B", bg="#2E3440"
        )
        self.time_label.pack(pady=5)

        self.input_entry = tk.Entry(
            self.root,
            width=30,
            font=("Helvetica", 18),
            bd=0,
            relief=tk.FLAT,
            insertbackground="white",
            fg="white",
            bg="#4C566A",
        )
        self.input_entry.pack(pady=10, padx=50, fill="x")
        self.input_entry.bind("<Return>", self.check_answer)

        # 反饋標籤：顯示正確或錯誤
        self.feedback_label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 14),
            fg="white",
            bg="#2E3440",
            justify=tk.CENTER,
        )
        self.feedback_label.pack(pady=10)

    def next_round(self):
        """切換到下一題，重置輸入框與計時器"""
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        if self.current_round < self.total_rounds:
            self.current_round += 1
            self.round_label.config(
                text=f"Round: {self.current_round}/{self.total_rounds}"
            )
            self.current_word = random.choice(self.current_word_bank)
            self.word_label.config(text=self.current_word)

            # 準備輸入框
            self.input_entry.config(state=tk.NORMAL)
            self.input_entry.delete(0, tk.END)
            self.input_entry.focus_set()

            self.feedback_label.config(text="")
            self.time_left = float(self.time_limit)
            self.update_time()
        else:
            self.show_final_score()

    def update_time(self):
        """倒數計時邏輯"""
        if not self.game_running:
            return

        self.time_label.config(text=f"Time: {self.time_left:.1f}s")

        if self.time_left <= 0:
            self.input_entry.config(state=tk.DISABLED)
            self.feedback_label.config(
                text=f"✘ 超時！正確答案是:\n'{self.current_word}'", fg="#BF616A"
            )
            self.timer_job = self.root.after(1500, self.next_round)
        else:
            self.time_left -= 0.1
            self.timer_job = self.root.after(100, self.update_time)

    def check_answer(self, event):
        """檢查玩家輸入的正確性，並給予回饋"""
        if not self.game_running or self.input_entry["state"] == tk.DISABLED:
            return

        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        typed_text = self.input_entry.get().strip()
        self.input_entry.config(
            state=tk.DISABLED
        )  # 暫時鎖定，不讓玩家在 1.5 秒內繼續打字

        if typed_text == self.current_word:
            self.correct_count += 1
            self.total_typed_chars += len(self.current_word)
            self.feedback_label.config(text="✔ 正確！", fg="#A3BE8C")
        else:
            # 顯示錯誤回饋，保留原本輸入的內容 1.5 秒
            error_msg = (
                f"✘ 錯誤！你打的是 '{typed_text}'\n正確應為 '{self.current_word}'"
            )
            self.feedback_label.config(text=error_msg, fg="#BF616A")

        # 停頓 1.5 秒後才進下一題
        self.root.after(1500, self.next_round)

    def show_final_score(self):
        """結算畫面，顯示 WPM 與正確率"""
        self.game_running = False
        total_time_seconds = time.time() - self.start_time
        total_time_minutes = total_time_seconds / 60

        # WPM 公式: (打對的總字元 / 5) / 分鐘
        if total_time_minutes > 0:
            wpm = (self.total_typed_chars / 5) / total_time_minutes
        else:
            wpm = 0

        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="Game Over",
            font=("Helvetica", 36, "bold"),
            fg="#D08770",
            bg="#2E3440",
        ).pack(pady=(40, 10))

        accuracy_percent = (self.correct_count / self.total_rounds) * 100

        tk.Label(
            self.root,
            text=f"Total Time: {total_time_seconds:.1f}s",
            font=("Helvetica", 14),
            fg="white",
            bg="#2E3440",
        ).pack(pady=5)
        tk.Label(
            self.root,
            text=f"Final Score: {self.correct_count}/{self.total_rounds} ({accuracy_percent:.0f}%)",
            font=("Helvetica", 18, "bold"),
            fg="#8FBCBB",
            bg="#2E3440",
        ).pack(pady=10)

        tk.Label(
            self.root,
            text=f"Typing Speed: {wpm:.1f} WPM",
            font=("Helvetica", 24, "bold"),
            fg="#EBCB8B",
            bg="#2E3440",
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Restart",
            command=self.setup_initial_ui,
            font=("Helvetica", 14),
            bg="#5E81AC",
            fg="white",
            padx=10,
            pady=5,
        ).pack(pady=30)


if __name__ == "__main__":
    root = tk.Tk()
    game = SpeedTypingGame(root)
    root.mainloop()
