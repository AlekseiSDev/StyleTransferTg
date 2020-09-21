import sqlite3
import pandas as pd
from sqlalchemy import MetaData, create_engine

# инициализируем движок
sqllite_engine = create_engine('sqlite:///data/bandit.db')
meta = MetaData(bind=sqllite_engine, reflect=True)

# посмотрим че в ней щас
for t in meta.sorted_tables:
    print(t.name)

# делаем чето с БД
df = pd.DataFrame(data = {'int': [1, 2], 'str' : ['op', 'hop',], 'float':[1.1, 2.2]})
df.to_sql(con=sqllite_engine, name='df')

for t in meta.sorted_tables:
    print(t.name)