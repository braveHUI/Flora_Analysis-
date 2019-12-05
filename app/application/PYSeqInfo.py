import sys
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import (CHAR, DATE, DATETIME, FLOAT, INTEGER,
                                       JSON, SMALLINT, TEXT, TINYINT, VARCHAR,
                                       YEAR)
from sqlalchemy.pool import NullPool


class PYSeqCONFIG:
    DBUser = os.environ.get("dbuser")
    DBPassword = os.environ.get("dbpassword")
    DBHost = os.environ.get("dbhost")
    DBName = os.environ.get("dbname")
    DBTable = "PYSeq"
    DBURL = "mysql+pymysql://{user}:{password}@{dbhost}:3306/{dbname}".format(
        user=DBUser, password=DBPassword, dbhost=DBHost, dbname=DBName)
    PCRSOP = {"16S.V4", "16S.V4M", "16S.V3V4","16S.V4TM"}
    # PYBIOM = "/share/data3/PYProfile/SZ/"
    PYBIOM = os.environ.get("PYBIOM")


PYSeqConfig = {'PYSeqConfig': PYSeqCONFIG}

db = SQLAlchemy()
# PYSeq_engine = create_engine(config.PYSeqConfig.DBURL, poolclass=NullPool)
# PYSeqSession = sessionmaker(bind=PYSeq_engine)()


class PYSeqInfo(db.Model):
    __tablename__ = PYSeqCONFIG.DBTable
    SEQID = Column(VARCHAR(20), primary_key=True, nullable=False)
    PYID = Column(VARCHAR(20), nullable=False)
    LIBID = Column(VARCHAR(20))
    PCRSOP = Column(TEXT)
    RUNID = Column(VARCHAR(64))
    CloseRefTags = Column(INTEGER(4))

    def PYSeqInfo2dict(self):
        data = {
            'SEQID': self.SEQID,
            'PYID': self.PYID,
            'LIBID': self.LIBID,
            'PCRSOP': self.PCRSOP,
            'RUNID': self.RUNID,
            'CloseRefTags': self.CloseRefTags
        }
        return data

    def __repr__(self):
        return "PYSeqInfo(%s)" % self.__tablename__
