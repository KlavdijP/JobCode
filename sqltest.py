from collections import defaultdict
import psycopg2
import csv

conn = psycopg2.connect(
    user = "openpg",
    host = "192.168.150.96",
    database = "morela11",
    password = "openpgpwd",
    port = '5432'
)

cursor = conn.cursor()

cursor.execute("select TRIM(p.koda), TRIM(p.skladisce), p.zaloga, p.mpcena, p.vrstams_naziv, p.vrstams  \
            from helios_zaloga_extended() p\
            where 1=1 and TRIM(p.koda) LIKE '716736193663' \
            order by p.koda")

data = cursor.fetchall()

seznam = defaultdict(lambda: defaultdict(dict))

for line in data:
    seznam[line[0]][line[1]] = line[2]

for i, j in enumerate(data):
    print("%d %-15s" % (i, j))
    if i > 100:
        break

with open("nova.txt", "w", encoding='utf-8', newline='\n') as file:
    for line in data:
        file.writelines(str(line) + "\n")

conn.close()
