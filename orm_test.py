import sqlalchemy as al
from sqlalchemy import orm
import constellation_repository as cr


metadata = al.MetaData()
engine = al.create_engine("sqlite:///database.db")

stars = al.Table("hygdata", metadata, autoload_with=engine)

with al.orm.Session(engine) as session:
    rows = session.scalar(al.select(al.func.count(stars.c.id)))
    repository = cr.ConstellationRepository()
    print(repository.get_hygastra_by_page())

    

print(rows)

