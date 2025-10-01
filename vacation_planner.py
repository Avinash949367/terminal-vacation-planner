import sqlite3
import datetime
import csv
import os

DB_PATH = 'vacation_planner.db'

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        secret_keyword TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        destination TEXT,
        start_date TEXT,
        end_date TEXT,
        budget REAL,
        status TEXT DEFAULT 'planned',
        notes TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transport (
        id INTEGER PRIMARY KEY,
        trip_id INTEGER,
        mode TEXT,
        cost REAL,
        FOREIGN KEY (trip_id) REFERENCES trips(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS accommodation (
        id INTEGER PRIMARY KEY,
        trip_id INTEGER,
        name TEXT,
        cost REAL,
        FOREIGN KEY (trip_id) REFERENCES trips(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY,
        trip_id INTEGER,
        name TEXT,
        cost REAL,
        FOREIGN KEY (trip_id) REFERENCES trips(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        trip_id INTEGER,
        category TEXT,
        amount REAL,
        FOREIGN KEY (trip_id) REFERENCES trips(id)
    )''')
    conn.commit()
    conn.close()

def register_user():
    username = input("Enter username: ")
    password = input("Enter password: ")
    secret = input("Enter secret keyword for password reset: ")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, secret_keyword) VALUES (?, ?, ?)", (username, password, secret))
        conn.commit()
        print("User registered successfully.")
    except sqlite3.IntegrityError:
        print("Username already exists.")
    conn.close()

def login_user():
    username = input("Enter username: ")
    password = input("Enter password: ")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        return user[0]
    else:
        print("Invalid credentials.")
        return None

def reset_password():
    username = input("Enter username: ")
    secret = input("Enter secret keyword: ")
    new_pass = input("Enter new password: ")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE username = ? AND secret_keyword = ?", (new_pass, username, secret))
    if c.rowcount > 0:
        conn.commit()
        print("Password reset successfully.")
    else:
        print("Invalid username or secret keyword.")
    conn.close()

def add_trip(user_id):
    dest = input("Destination: ")
    start = input("Start date (YYYY-MM-DD): ")
    end = input("End date (YYYY-MM-DD): ")
    budget = float(input("Budget: "))
    notes = input("Notes: ")
    now = datetime.datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO trips (user_id, destination, start_date, end_date, budget, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (user_id, dest, start, end, budget, notes, now, now))
    conn.commit()
    conn.close()
    print("Trip added.")

def view_trips(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, destination, start_date, end_date, budget, status FROM trips WHERE user_id = ?", (user_id,))
    trips = c.fetchall()
    conn.close()
    if not trips:
        print("No trips found.")
        return
    for trip in trips:
        print(f"ID: {trip[0]}, Dest: {trip[1]}, Dates: {trip[2]} to {trip[3]}, Budget: {trip[4]}, Status: {trip[5]}")

def edit_trip(user_id):
    trip_id = int(input("Trip ID to edit: "))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM trips WHERE id = ? AND user_id = ?", (trip_id, user_id))
    if not c.fetchone():
        print("Trip not found or not yours.")
        conn.close()
        return
    dest = input("New destination (leave blank to keep): ")
    if dest:
        c.execute("UPDATE trips SET destination = ? WHERE id = ?", (dest, trip_id))
    start = input("New start date: ")
    if start:
        c.execute("UPDATE trips SET start_date = ? WHERE id = ?", (start, trip_id))
    end = input("New end date: ")
    if end:
        c.execute("UPDATE trips SET end_date = ? WHERE id = ?", (end, trip_id))
    budget = input("New budget: ")
    if budget:
        c.execute("UPDATE trips SET budget = ? WHERE id = ?", (float(budget), trip_id))
    notes = input("New notes: ")
    if notes:
        c.execute("UPDATE trips SET notes = ? WHERE id = ?", (notes, trip_id))
    c.execute("UPDATE trips SET updated_at = ? WHERE id = ?", (datetime.datetime.now().isoformat(), trip_id))
    conn.commit()
    conn.close()
    print("Trip updated.")

def delete_trip(user_id):
    trip_id = int(input("Trip ID to delete: "))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM trips WHERE id = ? AND user_id = ?", (trip_id, user_id))
    if c.rowcount > 0:
        conn.commit()
        print("Trip deleted.")
    else:
        print("Trip not found.")
    conn.close()

def add_transport(user_id):
    trip_id = int(input("Trip ID: "))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
    trip_user = c.fetchone()
    if not trip_user or trip_user[0] != user_id:
        print("Invalid trip.")
        conn.close()
        return
    mode = input("Transport mode: ")
    cost = float(input("Cost: "))
    c.execute("INSERT INTO transport (trip_id, mode, cost) VALUES (?, ?, ?)", (trip_id, mode, cost))
    conn.commit()
    conn.close()
    print("Transport added.")

def view_transport(user_id):
    trip_id = int(input("Trip ID: "))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
    trip_user = c.fetchone()
    if not trip_user or trip_user[0] != user_id:
        print("Invalid trip.")
        conn.close()
        return
    c.execute("SELECT mode, cost FROM transport WHERE trip_id = ?", (trip_id,))
    trans = c.fetchall()
    conn.close()
    if not trans:
        print("No transport found.")
        return
    for t in trans:
        print(f"Mode: {t[0]}, Cost: {t[1]}")

def add_accommodation(user_id):
    trip_id = int(input("Trip ID: "))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
    trip_user = c.fetchone()
    if not trip_user or trip_user[0] != user_id:
        print("Invalid trip.")
        conn.close()
        return
    name = input("Accommodation name: ")
    cost = float(input("Cost: "))
    c.execute("INSERT INTO accommodation (trip_id, name, cost) VALUES (?, ?, ?)", (trip_id, name, cost))
    conn.commit()
    conn.close()
    print("Accommodation added.")

def view_accommodation(user_id):
    trip_id = int(input("Trip ID: "))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
    trip_user = c.fetchone()
    if not trip_user or trip_user[0] != user_id:
        print("Invalid trip.")
        conn.close()
        return
    c.execute("SELECT name, cost FROM accommodation WHERE trip_id = ?", (trip_id,))
    accoms = c.fetchall()
    conn.close()
    if not accoms:
        print("No accommodation found.")
        return
    for a in accoms:
        print(f"Name: {a[0]}, Cost: {a[1]}")

def add_activity(user_id):
    trip_id = int(input("Trip ID: "))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
    trip_user = c.fetchone()
    if not trip_user or trip_user[0] != user_id:
        print("Invalid trip.")
        conn.close()
        return
    name = input("Activity name: ")
    cost = float(input("Cost: "))
    c.execute("INSERT INTO activities (trip_id, name, cost) VALUES (?, ?, ?)", (trip_id, name, cost))
    conn.commit()
    conn.close()
    print("Activity added.")

def view_activities(user_id):
    trip_id = int(input("Trip ID: "))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
    trip_user = c.fetchone()
    if not trip_user or trip_user[0] != user_id:
        print("Invalid trip.")
        conn.close()
        return
    c.execute("SELECT name, cost FROM activities WHERE trip_id = ?", (trip_id,))
    acts = c.fetchall()
    conn.close()
    if not acts:
        print("No activities found.")
        return
    for a in acts:
        print(f"Name: {a[0]}, Cost: {a[1]}")

def add_expense(user_id):
    trip_id = int(input("Trip ID: "))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
    trip_user = c.fetchone()
    if not trip_user or trip_user[0] != user_id:
        print("Invalid trip.")
        conn.close()
        return
    category = input("Expense category: ")
    amount = float(input("Amount: "))
    c.execute("INSERT INTO expenses (trip_id, category, amount) VALUES (?, ?, ?)", (trip_id, category, amount))
    conn.commit()
    conn.close()
    print("Expense added.")

def view_expenses(user_id):
    trip_id = int(input("Trip ID: "))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
    trip_user = c.fetchone()
    if not trip_user or trip_user[0] != user_id:
        print("Invalid trip.")
        conn.close()
        return
    c.execute("SELECT category, amount FROM expenses WHERE trip_id = ?", (trip_id,))
    exps = c.fetchall()
    conn.close()
    if not exps:
        print("No expenses found.")
        return
    for e in exps:
        print(f"Category: {e[0]}, Amount: {e[1]}")

def budget_vs_spent(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, destination, budget FROM trips WHERE user_id = ?", (user_id,))
    trips = c.fetchall()
    for trip in trips:
        trip_id, dest, budget = trip
        c.execute("SELECT SUM(cost) FROM transport WHERE trip_id = ?", (trip_id,))
        trans = c.fetchone()[0] or 0
        c.execute("SELECT SUM(cost) FROM accommodation WHERE trip_id = ?", (trip_id,))
        accom = c.fetchone()[0] or 0
        c.execute("SELECT SUM(cost) FROM activities WHERE trip_id = ?", (trip_id,))
        act = c.fetchone()[0] or 0
        c.execute("SELECT SUM(amount) FROM expenses WHERE trip_id = ?", (trip_id,))
        exp = c.fetchone()[0] or 0
        total_spent = trans + accom + act + exp
        print(f"Trip {dest}: Budget {budget}, Spent {total_spent}, Difference {budget - total_spent}")
    conn.close()

def top_expensive(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT t.id, t.destination, (COALESCE(SUM(tr.cost),0) + COALESCE(SUM(a.cost),0) + COALESCE(SUM(ac.cost),0) + COALESCE(SUM(e.amount),0)) as total FROM trips t LEFT JOIN transport tr ON t.id = tr.trip_id LEFT JOIN accommodation a ON t.id = a.trip_id LEFT JOIN activities ac ON t.id = ac.trip_id LEFT JOIN expenses e ON t.id = e.trip_id WHERE t.user_id = ? GROUP BY t.id ORDER BY total DESC LIMIT 3", (user_id,))
    tops = c.fetchall()
    conn.close()
    if not tops:
        print("No trips found.")
        return
    for trip in tops:
        print(f"Dest: {trip[1]}, Total: {trip[2]}")

def favorite_destinations(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT destination, COUNT(*) as count FROM trips WHERE user_id = ? GROUP BY destination ORDER BY count DESC", (user_id,))
    favs = c.fetchall()
    conn.close()
    if not favs:
        print("No trips found.")
        return
    for fav in favs:
        print(f"{fav[0]}: {fav[1]} times")

def export_csv(user_id):
    filename = input("Export filename (without .csv): ") + ".csv"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM trips WHERE user_id = ?", (user_id,))
    trips = c.fetchall()
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'UserID', 'Destination', 'Start', 'End', 'Budget', 'Status', 'Notes', 'Created', 'Updated'])
        writer.writerows(trips)
    conn.close()
    print(f"Exported to {filename}")

def main():
    create_tables()
    current_user = None
    while True:
        if not current_user:
            print("\n1. Register")
            print("2. Login")
            print("3. Reset Password")
            print("4. Exit")
            choice = input("Choice: ")
            if choice == '1':
                register_user()
            elif choice == '2':
                current_user = login_user()
            elif choice == '3':
                reset_password()
            elif choice == '4':
                break
            else:
                print("Invalid choice.")
        else:
            print(f"\nLogged in as user {current_user}")
            print("1. Add Trip")
            print("2. View Trips")
            print("3. Edit Trip")
            print("4. Delete Trip")
            print("5. Manage Transport")
            print("6. Manage Accommodation")
            print("7. Manage Activities")
            print("8. Manage Expenses")
            print("9. Reports")
            print("10. Export")
            print("11. Logout")
            choice = input("Choice: ")
            if choice == '1':
                add_trip(current_user)
            elif choice == '2':
                view_trips(current_user)
            elif choice == '3':
                edit_trip(current_user)
            elif choice == '4':
                delete_trip(current_user)
            elif choice == '5':
                print("a. Add Transport")
                print("b. View Transport")
                sub = input("Subchoice: ")
                if sub == 'a':
                    add_transport(current_user)
                elif sub == 'b':
                    view_transport(current_user)
                else:
                    print("Invalid.")
            elif choice == '6':
                print("a. Add Accommodation")
                print("b. View Accommodation")
                sub = input("Subchoice: ")
                if sub == 'a':
                    add_accommodation(current_user)
                elif sub == 'b':
                    view_accommodation(current_user)
                else:
                    print("Invalid.")
            elif choice == '7':
                print("a. Add Activity")
                print("b. View Activities")
                sub = input("Subchoice: ")
                if sub == 'a':
                    add_activity(current_user)
                elif sub == 'b':
                    view_activities(current_user)
                else:
                    print("Invalid.")
            elif choice == '8':
                print("a. Add Expense")
                print("b. View Expenses")
                sub = input("Subchoice: ")
                if sub == 'a':
                    add_expense(current_user)
                elif sub == 'b':
                    view_expenses(current_user)
                else:
                    print("Invalid.")
            elif choice == '9':
                print("a. Budget vs Spent")
                print("b. Top Expensive")
                print("c. Favorite Destinations")
                sub = input("Subchoice: ")
                if sub == 'a':
                    budget_vs_spent(current_user)
                elif sub == 'b':
                    top_expensive(current_user)
                elif sub == 'c':
                    favorite_destinations(current_user)
                else:
                    print("Invalid.")
            elif choice == '10':
                export_csv(current_user)
            elif choice == '11':
                current_user = None
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    main()
