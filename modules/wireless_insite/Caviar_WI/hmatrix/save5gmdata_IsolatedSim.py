from sqlalchemy import create_engine, Column, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

import numpy as np
import os.path
from termcolor import colored

Base = declarative_base()

class Receiver(Base):
    __tablename__ = 'receivers'
    id = Column(Integer, primary_key=True)
    total_received_power = Column(Float)
    mean_time_of_arrival = Column(Float)
    total_rays = Column(Integer)
    rays = relationship("Ray", back_populates="receiver")

class Ray(Base):
    __tablename__ = 'rays'
    id = Column(Integer, primary_key=True)
    departure_elevation = Column(Float)
    departure_azimuth = Column(Float)
    arrival_elevation = Column(Float)
    arrival_azimuth = Column(Float)
    path_gain = Column(Float)
    time_of_arrival = Column(Float)
    interactions = Column(Text)
    phase_in_degrees = Column(Float)
    interactions_positions = Column(Text)
    receiver_id = Column(Integer, ForeignKey('receivers.id'))
    
    receiver = relationship("Receiver", back_populates="rays")

def create_database(dataBaseFileName='episodedata.db'):
    if os.path.isfile(dataBaseFileName):
        os.remove(dataBaseFileName)
        print(colored(f'Removed old database: {dataBaseFileName}', color='red'))
    else:
        print('Created a empty database: ', dataBaseFileName)
    print('##############################')
    engine = create_engine('sqlite:///' + dataBaseFileName)
    
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    return Session()

def open_database(dataBaseFileName='episodedata.db'):
    #engine = create_engine('sqlite:////tmp/episodedata.db')
    if os.path.isfile(dataBaseFileName):
        print(f'Found database file: {dataBaseFileName}')
    else:
        print(colored(f'File: {dataBaseFileName} no found', 'red'))
        exit(-1)
    print('##############################')
    engine = create_engine('sqlite:///' + dataBaseFileName)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    return Session()
