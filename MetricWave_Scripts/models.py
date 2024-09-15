from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Dataset(Base):
    __tablename__ = 'datasets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, server_default='CURRENT_TIMESTAMP', nullable=False)
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    active = Column(Integer, default=1)
    afn = Column(String(50), nullable=False)
    day_type = Column(Integer, ForeignKey('day_type.id'), nullable=False)
    window_type = Column(String(16), nullable=False)

    rows = relationship("DatasetRow", back_populates="dataset")
    metrics = relationship("Metric", back_populates="dataset")
    predictions = relationship("Prediction", back_populates="dataset")


class DatasetRow(Base):
    __tablename__ = 'dataset_rows'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id'), nullable=False)
    day_type = Column(Integer, ForeignKey('day_type.id'), nullable=False)
    afn = Column(String(50), nullable=False)
    feature_0 = Column(Float)
    feature_1 = Column(Float)
    feature_2 = Column(Float)
    feature_3 = Column(Float)
    feature_4 = Column(Float)
    feature_5 = Column(Float)
    feature_6 = Column(Float)
    feature_7 = Column(Float)
    feature_8 = Column(Float)
    feature_9 = Column(Float)
    feature_10 = Column(Float)
    feature_11 = Column(Float)
    feature_12 = Column(Float)
    feature_13 = Column(Float)
    feature_14 = Column(Float)
    feature_15 = Column(Float)
    feature_16 = Column(Float)
    feature_17 = Column(Float)
    feature_18 = Column(Float)
    feature_19 = Column(Float)
    feature_20 = Column(Float)
    feature_21 = Column(Float)
    feature_22 = Column(Float)
    feature_23 = Column(Float)
    feature_24 = Column(Float)
    feature_25 = Column(Float)
    feature_26 = Column(Float)
    feature_27 = Column(Float)
    feature_28 = Column(Float)
    feature_29 = Column(Float)
    feature_30 = Column(Float)
    feature_31 = Column(Float)
    feature_32 = Column(Float)
    feature_33 = Column(Float)
    feature_34 = Column(Float)
    feature_35 = Column(Float)
    feature_36 = Column(Float)
    feature_37 = Column(Float)
    feature_38 = Column(Float)
    feature_39 = Column(Float)
    feature_40 = Column(Float)
    feature_41 = Column(Float)
    feature_42 = Column(Float)
    feature_43 = Column(Float)
    feature_44 = Column(Float)
    feature_45 = Column(Float)
    feature_46 = Column(Float)
    feature_47 = Column(Float)
    feature_48 = Column(Float)
    feature_49 = Column(Float)
    feature_50 = Column(Float)
    feature_51 = Column(Float)
    feature_52 = Column(Float)
    feature_53 = Column(Float)
    feature_54 = Column(Float)
    feature_55 = Column(Float)
    feature_56 = Column(Float)
    feature_57 = Column(Float)
    feature_58 = Column(Float)
    feature_59 = Column(Float)
    class_60 = Column(Float)
    class_day_time = Column(DateTime)

    dataset = relationship("Dataset", back_populates="rows")


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default='CURRENT_TIMESTAMP')
    updated_at = Column(DateTime, server_default='CURRENT_TIMESTAMP', onupdate='CURRENT_TIMESTAMP')


class DayType(Base):
    __tablename__ = 'day_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    day_type = Column(String(50), nullable=False, unique=True)


class Metric(Base):
    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id'), nullable=False)
    model_name = Column(String(100), nullable=False)
    mse = Column(Float)
    rmse = Column(Float)
    mae = Column(Float)
    mape = Column(Float)
    r2 = Column(Float)

    dataset = relationship("Dataset", back_populates="metrics")


class Prediction(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id'), nullable=False)
    day_time = Column(DateTime, nullable=False)
    predicted_class_60 = Column(Float, nullable=False)
    model_name = Column(String(100), nullable=False)

    dataset = relationship("Dataset", back_populates="predictions")
