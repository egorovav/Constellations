import json
import sqlalchemy as al
import constellation_model as m
from pyproj import Transformer

class ConstellationRepository:
    def __init__(self):
        self.engine = al.create_engine("sqlite:///Constellations/astradatabase.db")
        self.transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    
    def transform_4326_to_3857(self, lon, lat):
        """Преобразует координаты из EPSG:4326 (WGS84) в EPSG:3857 (Web Mercator)"""
        return self.transformer.transform(lon, lat)
    
    def get_constellation_by_abbr(self, abbr):
        with al.orm.Session(self.engine) as session:
            return session.query(m.ConstellationFigure).filter(m.ConstellationFigure.abbr == abbr).first()
    
    def get_hygdata_for_constellation(self, figure_id):
        with al.orm.Session(self.engine) as session:
            start_star = m.HygData.__table__.alias('start')
            end_star = m.HygData.__table__.alias('end')
        
            return session.query(start_star, end_star).select_from(
                m.Constellation
            ).join(
                start_star, m.Constellation.link_start == start_star.c.star_id
            ).join(
                end_star, m.Constellation.link_end == end_star.c.star_id
            ).filter(m.Constellation.figure_id == figure_id).all()
    
    def get_hygdata_by_abbr(self, abbr):
        with al.orm.Session(self.engine) as session:
            return session.query(m.HygData).filter(m.HygData.con == abbr).filter(m.HygData.bayer != None).all()
    
    def get_coordinates_for_constellation(self, figure_id):
        with al.orm.Session(self.engine) as session:
            start_star = m.HygData.__table__.alias('start')
            end_star = m.HygData.__table__.alias('end')
        
            rows = session.query(
                start_star.c.lon.label('start_lon'), 
                start_star.c.declination.label('start_declination'),
                end_star.c.lon.label('end_lon'), 
                end_star.c.declination.label('end_declination')
            ).select_from(
                m.Constellation
            ).join(
                start_star, m.Constellation.link_start == start_star.c.star_id
            ).join(
                end_star, m.Constellation.link_end == end_star.c.star_id
            ).filter(m.Constellation.figure_id == figure_id).all()
            
            result = []
            for row in rows:
                start_x, start_y = self.transform_4326_to_3857(row.start_lon, row.start_declination)
                end_x, end_y = self.transform_4326_to_3857(row.end_lon, row.end_declination)
                result.append(type('Row', (), {
                    'start_easting': start_x, 'start_northing': start_y,
                    'end_easting': end_x, 'end_northing': end_y
                })())
            return result

    def get_constellation_geojson(self, abbr):
        constellation = self.get_constellation_by_abbr(abbr)
        if not constellation:
            return None
            
        coordinates = self.get_coordinates_for_constellation(constellation.constellation_figure_id)
            
        return {
            "type": "Feature",
            "geometry": {
                "type": "MultiLineString",
                "coordinates": [[[row.start_easting, row.start_northing], [row.end_easting, row.end_northing]] for row in coordinates]
            },
            "properties": {
                "name": constellation.name,
                "nameLat": constellation.name_lat
            },
            "id": constellation.abbr
        }

    def get_all_constellations_geojson(self):
        with al.orm.Session(self.engine) as session:
            start_star = m.HygData.__table__.alias('start')
            end_star = m.HygData.__table__.alias('end')
            
            data = session.query(
                m.ConstellationFigure.constellation_figure_id.label('figure_id'),
                m.ConstellationFigure.name.label('name'),
                m.ConstellationFigure.abbr.label('abbr'),
                m.ConstellationFigure.name_lat.label('name_lat'),
                start_star.c.lon.label('start_lon'), 
                start_star.c.declination.label('start_declination'),
                end_star.c.lon.label('end_lon'), 
                end_star.c.declination.label('end_declination')
            ).select_from(
                m.ConstellationFigure
            ).join(
                m.Constellation, m.ConstellationFigure.constellation_figure_id == m.Constellation.figure_id
            ).join(
                start_star, m.Constellation.link_start == start_star.c.star_id
            ).join(
                end_star, m.Constellation.link_end == end_star.c.star_id
            ).all()
            
            constellations = {}
            for row in data:
                figure_id = row.figure_id
                if figure_id not in constellations:
                    constellations[figure_id] = {
                        "type": "Feature",
                        "geometry": {"type": "MultiLineString", "coordinates": []},
                        "properties": {"name": row.name, "nameLat": row.name_lat},
                        "id": row.abbr
                    }
                start_x, start_y = self.transform_4326_to_3857(row.start_lon, row.start_declination)
                end_x, end_y = self.transform_4326_to_3857(row.end_lon, row.end_declination)
                splitted = self.split_dateline_crossing([[start_x, start_y], [end_x, end_y]])
                for coordinates in splitted:
                    constellations[figure_id]["geometry"]["coordinates"].append(coordinates)
    
            return list(constellations.values())
        

    def split_dateline_crossing(self, coordinates):
        """Разделяет линии, пересекающие линию смены дат в проекции Меркатора"""
        start_x, start_y = coordinates[0]
        end_x, end_y = coordinates[1]
        
        # Границы проекции Web Mercator (EPSG:3857)
        mercator_max = 20037508.34  # ~180°
        mercator_min = -20037508.34  # ~-180°
        
        # Проверяем пересечение границ проекции
        if abs(end_x - start_x) > mercator_max:
            # Вычисляем точку пересечения с границей
            if start_x > 0:  # Переход с востока на запад
                y_intersect = start_y + (end_y - start_y) * (mercator_max - start_x) / (end_x - start_x + 2 * mercator_max)
                return [
                    [[start_x, start_y], [mercator_max, y_intersect]],
                    [[mercator_min, y_intersect], [end_x, end_y]]
                ]
            else:  # Переход с запада на восток
                y_intersect = start_y + (end_y - start_y) * (mercator_min - start_x) / (end_x - start_x - 2 * mercator_max)
                return [
                    [[start_x, start_y], [mercator_min, y_intersect]],
                    [[mercator_max, y_intersect], [end_x, end_y]]
                ]
        
        return [coordinates]
    
    def get_hygastra_by_magnitude_less_than(self, min_magnitude):
        with al.orm.Session(self.engine) as session:
            data = session.query(m.HygData).filter(m.HygData.mag < min_magnitude).all()
            points = []
            for row in data:
                x, y = self.transform_4326_to_3857(row.lon, row.declination)
                point = {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates":[x, y]},
                    "properties": {"name": row.name, "bayer": row.bayer_non_empty, "constellation": row.con},
                    "id": row.star_id
                }
                points.append(point)
            return points

    def get_all_constellations(self):
        with al.orm.Session(self.engine) as session:
            return session.query(m.ConstellationFigure).all()
        
    def get_constellation_links(self, abbr):
        with al.orm.Session(self.engine) as session:
            return session.query(m.Constellation
                        ).join(m.ConstellationFigure, m.Constellation.figure_id == m.ConstellationFigure.constellation_figure_id
                        ).filter(m.ConstellationFigure.abbr == abbr).all()
        
    def get_hygastra_by_page(self, page=1, per_page=30, order_by='star_id', desc=False):
        with al.orm.Session(self.engine) as session:
            query = session.query(m.HygData)
            order_column = getattr(m.HygData, order_by)
            query = query.order_by(order_column.desc() if desc else order_column)
            
            offset = (page - 1) * per_page
            items = query.offset(offset).limit(per_page).all()
            total = query.count()
            
            return {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }