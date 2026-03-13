import sqlite3
import os

# 全域變數，用來儲存資料庫連線
dbConn = None


def clear_screen():
    """清除終端機畫面，讓介面更乾淨"""
    os.system("cls" if os.name == "nt" else "clear")


def dbConnection():
    global dbConn
    try:
        if not os.path.exists("Database"):
            os.makedirs("Database")
        dbConn = sqlite3.connect("Database/test.db")
    except sqlite3.Error as e:
        print(f"資料庫連1線失敗: {e}")


def createTable():
    if dbConn is None:
        dbConnection()
    try:
        dbCursor = dbConn.cursor()
        sqlStr = """SELECT count(name) 
                    FROM sqlite_master 
                    WHERE type = 'table' AND name = 'Students';"""
        dbCursor.execute(sqlStr)

        if dbCursor.fetchone()[0] == 0:
            sqlStr = """CREATE TABLE Students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        gender TEXT NOT NULL,
                        department TEXT NOT NULL,
                        email TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        address TEXT);"""
            dbCursor.execute(sqlStr)
            dbConn.commit()
    except sqlite3.Error as e:
        print(f"建立資料表時發生錯誤: {e}")


# ==========================================
# 任務 A：重複註冊防護 (檢查 Email)
# ==========================================
def insert_student(name, gender, department, email, phone, address):
    if dbConn is None:
        dbConnection()
    try:
        dbCursor = dbConn.cursor()

        # 【任務 A 核心邏輯】：新增前先檢查 Email 是否已存在
        dbCursor.execute("SELECT email FROM Students WHERE email = ?", (email,))
        if dbCursor.fetchone():
            print(f"\n[錯誤] Email '{email}' 已經被註冊過，請確認後再試！")
            return  # 發現重複，直接結束函式，拒絕寫入

        # 若無重複，則執行新增
        dbCursor.execute(
            """INSERT INTO Students (name, gender, department, email, phone, address)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, gender, department, email, phone, address),
        )
        dbConn.commit()
        print(f"\n✅ 學生 {name} 的資料已成功新增！")
    except sqlite3.Error as e:
        print(f"\n❌ 新增資料失敗: {e}")


def list_all_students():
    if dbConn is None:
        dbConnection()
    try:
        dbCursor = dbConn.cursor()
        dbCursor.execute("SELECT * FROM Students")
        records = dbCursor.fetchall()

        print("\n" + "=" * 40 + " 學生資料列表 " + "=" * 40)
        header = f"{'ID':<4} | {'姓名':<8} | {'性別':<4} | {'系所':<10} | {'電話':<13} | {'電子信箱':<20} | {'地址'}"
        print(header)
        print("-" * 100)

        if not records:
            print("目前沒有任何學生資料。")
        else:
            for row in records:
                print(
                    f"{row[0]:<4} | {row[1]:<8} | {row[2]:<4} | {row[3]:<10} | {row[5]:<13} | {row[4]:<20} | {row[7]}"
                )
        print("-" * 100)
    except sqlite3.Error as e:
        print(f"\n❌ 查詢資料失敗: {e}")


def update_student():
    if dbConn is None:
        dbConnection()
    try:
        dbCursor = dbConn.cursor()
        student_id = input("\n請輸入要修改的學生 ID: ")

        dbCursor.execute("SELECT * FROM Students WHERE id = ?", (student_id,))
        record = dbCursor.fetchone()

        if not record:
            print(f"❌ 找不到 ID 為 {student_id} 的學生資料。")
            return

        print(f"\n--- 目前修改的學生：{record[1]} ---")
        print("請輸入新的資料 (若該欄位不修改，請直接按 Enter 略過)：")

        new_name = input(f"姓名 ({record[1]}): ") or record[1]
        new_gender = input(f"性別 ({record[2]}): ") or record[2]
        new_dept = input(f"系所 ({record[3]}): ") or record[3]
        new_email = input(f"電子信箱 ({record[4]}): ") or record[4]
        new_phone = input(f"電話號碼 ({record[5]}): ") or record[5]
        new_address = input(f"地址 ({record[7]}): ") or record[7]

        # 如果使用者有修改 email，一樣要檢查新 email 是否跟「別人」重複
        if new_email != record[4]:
            dbCursor.execute(
                "SELECT email FROM Students WHERE email = ? AND id != ?",
                (new_email, student_id),
            )
            if dbCursor.fetchone():
                print(f"\n[錯誤] Email '{new_email}' 已經被註冊過，修改失敗！")
                return

        sqlStr = """UPDATE Students 
                    SET name = ?, gender = ?, department = ?, email = ?, phone = ?, address = ? 
                    WHERE id = ?"""
        dbCursor.execute(
            sqlStr,
            (
                new_name,
                new_gender,
                new_dept,
                new_email,
                new_phone,
                new_address,
                student_id,
            ),
        )
        dbConn.commit()
        print("\n✅ 資料修改完成！")

    except sqlite3.Error as e:
        print(f"\n❌ 修改資料失敗: {e}")


def delete_student():
    if dbConn is None:
        dbConnection()
    try:
        dbCursor = dbConn.cursor()
        student_id = input("\n請輸入要刪除的學生 ID: ")

        dbCursor.execute("SELECT name FROM Students WHERE id = ?", (student_id,))
        record = dbCursor.fetchone()

        if not record:
            print(f"\n❌ 找不到 ID 為 {student_id} 的學生資料，無法刪除。")
            return

        student_name = record[0]

        while True:
            confirm = (
                input(
                    f"⚠️ 確定要刪除學生「{student_name}」(ID: {student_id}) 的資料嗎？(Y/N): "
                )
                .strip()
                .upper()
            )
            if confirm == "Y":
                dbCursor.execute("DELETE FROM Students WHERE id = ?", (student_id,))
                dbConn.commit()
                print(f"\n✅ 學生「{student_name}」的資料刪除成功！")
                break
            elif confirm == "N":
                print("\n已取消刪除操作。")
                break
            else:
                print("❌ 輸入錯誤，請明確輸入 'Y' 或 'N'。")
    except sqlite3.Error as e:
        print(f"\n❌ 刪除資料時發生資料庫錯誤: {e}")


# ==========================================
# 任務 B：系所人數統計 (GROUP BY)
# ==========================================
def count_by_department():
    if dbConn is None:
        dbConnection()
    try:
        dbCursor = dbConn.cursor()
        # 【任務 B 核心邏輯】：使用 GROUP BY 統計人數
        dbCursor.execute(
            "SELECT department, COUNT(*) FROM Students GROUP BY department"
        )
        records = dbCursor.fetchall()

        print("\n=== 📊 系所人數統計 ===")
        print(f"{'系所名稱':<15} | {'人數'}")
        print("-" * 30)

        if not records:
            print("目前沒有任何資料。")
        else:
            for row in records:
                print(f"{row[0]:<17} | {row[1]}")  # 寬度微調以對齊直線
        print("-" * 30)
    except sqlite3.Error as e:
        print(f"\n❌ 統計資料失敗: {e}")


# ==========================================
# 任務 C：模糊關鍵字搜尋 (LIKE)
# ==========================================
def search_student():
    if dbConn is None:
        dbConnection()
    try:
        dbCursor = dbConn.cursor()
        keyword = input("\n請輸入搜尋關鍵字: ")

        # 【任務 C 核心邏輯】：使用 LIKE 進行模糊搜尋 (%代表任意字元)
        search_pattern = f"%{keyword}%"
        sqlStr = "SELECT * FROM Students WHERE name LIKE ? OR address LIKE ?"
        dbCursor.execute(sqlStr, (search_pattern, search_pattern))
        records = dbCursor.fetchall()

        print(f"\n=== 🔍 搜尋結果 (關鍵字: '{keyword}') ===")
        if not records:
            print("找不到符合條件的學生資料。")
        else:
            for row in records:
                print(
                    f"ID: {row[0]:<3} | 姓名: {row[1]:<8} | 系所: {row[3]:<10} | 地址: {row[7]}"
                )
        print("=" * 60)
    except sqlite3.Error as e:
        print(f"\n❌ 搜尋資料失敗: {e}")


# ==========================================
# 任務 D：單筆資料查詢 (透過 ID)
# ==========================================
def query_single_student():
    if dbConn is None:
        dbConnection()
    try:
        dbCursor = dbConn.cursor()
        student_id = input("\n請輸入要查詢的學生 ID: ")

        # 【任務 D 核心邏輯】：使用 WHERE id = ? 查詢單筆
        sqlStr = "SELECT * FROM Students WHERE id = ?"
        dbCursor.execute(sqlStr, (student_id,))
        record = dbCursor.fetchone()

        if record:
            print(f"\n=== 📄 學生詳細資料 (ID: {record[0]}) ===")
            print(f"姓名     : {record[1]}")
            print(f"性別     : {record[2]}")
            print(f"系所     : {record[3]}")
            print(f"Email    : {record[4]}")
            print(f"電話     : {record[5]}")
            print(f"地址     : {record[7]}")
            print(f"建檔時間 : {record[6]}")
            print("=" * 40)
        else:
            print(f"\n❌ 找不到 ID 為 {student_id} 的學生資料。")
    except sqlite3.Error as e:
        print(f"\n❌ 查詢資料失敗: {e}")


# ==========================================
# 主程式選單
# ==========================================
def main_menu():
    clear_screen()
    createTable()

    while True:
        # 依照圖片重新設計的主選單排版
        print("\n=================================================")
        print(" 🏫 學生學籍管理系統 (v2.0)")
        print("=================================================")
        print("【基礎維護】")
        print(" 1. 新增學生資料")
        print(" 2. 列出所有學生")
        print(" 3. 修改學生資料 (電話/地址等)")
        print(" 4. 刪除學生資料")
        print("【進階功能】")
        print(" 5. 系所人數統計")
        print(" 6. 關鍵字模糊搜尋 (姓名/地址)")
        print(" 7. 查詢單筆詳細資料 (依 ID)")
        print("-------------------------------------------------")
        print(" 0. 登出並關閉系統")
        print("=================================================")

        choice = input("👉 請選擇功能操作 (0-7): ")

        if choice == "1":
            clear_screen()
            print("\n--- 新增學生資料 ---")
            name = input("輸入姓名: ").strip()
            gender = input("輸入性別: ")
            dept = input("輸入系所: ")
            mail = input("輸入 Email: ")
            tel = input("輸入電話: ")
            addr = input("輸入地址 (選填，可直接按 Enter): ")
            insert_student(name, gender, dept, mail, tel, addr)
            input("\n按 Enter 鍵返回主選單...")
            clear_screen()

        elif choice == "2":
            clear_screen()
            list_all_students()
            input("\n按 Enter 鍵返回主選單...")
            clear_screen()

        elif choice == "3":
            clear_screen()
            list_all_students()
            update_student()
            input("\n按 Enter 鍵返回主選單...")
            clear_screen()

        elif choice == "4":
            clear_screen()
            list_all_students()
            delete_student()
            input("\n按 Enter 鍵返回主選單...")
            clear_screen()

        elif choice == "5":
            clear_screen()
            count_by_department()
            input("\n按 Enter 鍵返回主選單...")
            clear_screen()

        elif choice == "6":
            clear_screen()
            search_student()
            input("\n按 Enter 鍵返回主選單...")
            clear_screen()

        elif choice == "7":
            clear_screen()
            query_single_student()
            input("\n按 Enter 鍵返回主選單...")
            clear_screen()

        elif choice == "0":
            print("\n系統登出，關閉連線，感謝使用！👋")
            if dbConn:
                dbConn.close()
            break

        else:
            print("\n[格式錯誤] 請輸入有效的數字格式 (例如: 1, 2, 3)！")
            input("按 Enter 鍵繼續...")
            clear_screen()


if __name__ == "__main__":
    main_menu()
