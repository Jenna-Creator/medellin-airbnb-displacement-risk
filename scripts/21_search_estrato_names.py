import pandas as pd

estrato = pd.read_csv('data/raw/barranquilla_barrio_estrato.csv')
names = sorted(estrato['barrio'])

search_terms = ['SANTO', 'DOMINGO', 'ANGEL', 'LIMON', 'LIMÓN', 'JULIO', 'ABRIL', 'AGOSTO', 'HOYOS', 'BETANIA']
for term in search_terms:
    matches = [n for n in names if term in n.upper()]
    print(f"{term}: {matches if matches else '(nothing at all)'}")