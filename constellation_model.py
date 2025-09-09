from sqlalchemy import Column, Integer, String, Float, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class HygData(Base):
    __tablename__ = 'hygdata'
    
    id = Column(String(50))
    # Henry Draper catalog Id
    hd = Column(String(10))
    proper = Column(String(50))
    # right ascension
    ra = Column(Float)
    declination = Column(Float)
    dist = Column(Float)
    mag = Column(Float)
    bayer = Column(String(10))
    con = Column(String(10))
    lon = Column(Float)
    star_id = Column(BigInteger, primary_key=True)
    
    @property
    def lon_rounded(self):
        return round(self.lon, 5) if self.lon else None
    
    @property
    def bayer_non_empty(self):
        return self.bayer if self.bayer else ""
    
    @property
    def hd_non_empty(self):
        return self.hd if self.hd else ""
    
    @property
    def name(self):
        return self.proper if self.proper else ""
    
    @property
    def hh_mm(self):
        hh = (18000 - round(self.lon * 100)) // 1500
        mm = ((18000 - round(self.lon * 100)) % 1500) // 25
        return f"({hh:02d}:{mm:02d})"


class ConstellationFigure(Base):
    __tablename__ = 'constellation_figure'
    
    constellation_figure_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    abbr = Column(String(3))
    name_lat = Column(String(50))

class Constellation(Base):
    __tablename__ = 'constellation'
    
    constellation_link_id = Column(BigInteger, primary_key=True)
    link_start = Column(BigInteger, ForeignKey('hygdata.star_id'))
    link_end = Column(BigInteger, ForeignKey('hygdata.star_id'))
    figure_id = Column(Integer, ForeignKey('constellation_figure.constellation_figure_id'))
    
    start_star = relationship('HygData', foreign_keys=[link_start])
    end_star = relationship('HygData', foreign_keys=[link_end])
    figure = relationship('ConstellationFigure')

