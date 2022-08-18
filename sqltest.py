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

cursor.execute("select TRIM(koda), TRIM(p.skladisce), p.zaloga \
            from helios_zaloga_extended() p\
            where 1=1 and koda SIMILAR TO '[0-9]+' \
            and ((vrstams='401' and vrstams_naziv='Sončna očala') or (vrstams='200' and vrstams_naziv='Korekcijski okvirji')) \
            order by koda")

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
