import sqlite3

dbConn = None


def dbConnection():
    global dbConn
    dbConn = sqlite3.connect("Database/test.db")


def createTable():
    if dbConn is None:
        dbConnection()
    dbCursor = dbConn.cursor()
    sqlStr = """SELECT count( name )
    FROM sqlite_master
    WHERE type = 'table' AND name = 'Students';
    """
    dbCursor.execute(sqlStr)
    if dbCursor.fetchone()[0] == 1:
        print("Table 'Students' already exists.")
    else:
        sqlStr = """CREATE TABLE Students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            address TEXT); """
        dbCursor.execute(sqlStr)
        print("Table 'Students' created.")


def getStudentTableColumns():
    if dbConn is None:
        dbConnection()
    dbCursor = dbConn.cursor()
    dbCursor.execute("PRAGMA table_info( 'Students' )")
    columns = dbCursor.fetchall()
    for col in columns:
        print(col)


def insert_student(name, gender, department, email, phone, address):
    if dbConn is None:
        dbConnection()
    dbCursor = dbConn.cursor()
    dbCursor.execute(
        """INSERT INTO Students (name, gender, department, email, phone, address)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (name, gender, department, email, phone, address),
    )
    dbConn.commit()
    print(f"Student {name} inserted successfully.")


def main():
    createTable()
    getStudentTableColumns()
    student1 = {
        "name": "John Doe",
        "gender": "Male",
        "department": "AITA",
        "email": "test@gmail.com",
        "phone": "0912345678",
        "address": "No. 100, Wenhua Road, Xituan Dist., Taichung 40724",
    }
    insert_student(
        student1["name"],
        student1["gender"],
        student1["department"],
        student1["email"],
        student1["phone"],
        student1["address"],
    )
    dbConn.commit()
    dbConn.close()


if __name__ == "__main__":
    main()
