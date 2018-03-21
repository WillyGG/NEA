import sqlite3 as sq3

"""
import matplotlib.pyplot as plt

# pass data as 2d array [ [x1, y1], [x2, y2] ]
def plot_data(data):
    x_vals = [d[0] for d in data]
    y_vals = [d[1] for d in data]
    plt.plot(x_vals, y_vals)

data = []
for x in range(100):
    to_append = [x, 0]
    y_val = x ** 2
    if x % 2 == 0:
        y_val = x**3
    to_append[1] = y_val
    data.append(to_append)

plot_data(data)
plt.show()
"""

connection = sq3.connect("test.sqlite")
cursor = connection.cursor()
cursor.execute("""
               CREATE TABLE IF NOT EXISTS thing (
               ID INTEGER PRIMARY KEY
               ) 
               """)

cursor.execute("""
               INSERT INTO thing (ID) VALUES (4);
               """)


cursor.execute("""
               SELECT * FROM thing;
               """)

cursor.execute("""
               INSERT INTO thing (ID) VALUES (5);
               """)

print(cursor.fetchone())


connection.commit()
connection.close()