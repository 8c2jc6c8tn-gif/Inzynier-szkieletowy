import json

# 1. Wczytanie stałych (Standardy)
with open('stale.json', 'r') as f:
    stale = json.load(f)

# 2. Wczytanie zmiennych (Konkretny projekt)
with open('projekt.json', 'r') as f:
    projekt = json.load(f)

# 3. Logika (Silnik inżynierski)
for sciana in projekt['wymiary_scian']:
    ilosc_slupkow = (sciana['dlugosc'] / stale['standardy']['rozstaw_belek']) + 1
    print(f"Projekt: {projekt['nazwa_projektu']} | {sciana['nazwa']}: {int(ilosc_slupkow)} słupków")
