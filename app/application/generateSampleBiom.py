# ==============================================================================
#
#         FILE: generateReportJson.py
#
#        USAGE: ./generateReportJson.py
#
#  DESCRIPTION:
#
#      OPTIONS: ---
# REQUIREMENTS: ---
#         BUGS: ---
#        NOTES: ---
#       AUTHOR: ZHOU Yuanjie (ZHOU YJ), libranjie@gmail.com
# ORGANIZATION: R & D Department
#      VERSION: 1.0
#      CREATED: Tue May 22 16:14:31 CST 2018
#     REVISION: 2018.May22-16.14
# ==============================================================================
import os
import re
import stat
import sys
from datetime import datetime

from app import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .PYSeqInfo import PYSeqConfig, PYSeqInfo

PYSeqCONF = PYSeqConfig['PYSeqConfig']

PYSeq_engine = create_engine(PYSeqCONF.DBURL, poolclass=NullPool)
DBSession = sessionmaker(bind=PYSeq_engine)
PYSeqSession = DBSession()


class PYConfigPath(config['development']):
    minimalTags = 1000
    scp = "/usr/bin/scp"
    # scp = "scp"
    scplogin = "profile"
    scphostname = "192.168.1.15"
    # scphostname = "59.111.94.145"
    scpheader = "{login}@{hostname}".format(
        login=scplogin, hostname=scphostname)


ReportConfig = {
    "PYConfigPath": PYConfigPath
}

PYReportCONF = ReportConfig['PYConfigPath']


def SampleBIOM(Tube_ID, PriSID):
    #seqinfo = PYSeqSession.query(PYSeqInfo).filter_by(
    #    PYID=Tube_ID, PCRSOP=PYSeqCONF.PCRSOP).order_by(
    print("SampleBIOM is running")

    seqinfo = PYSeqSession.query(PYSeqInfo).filter_by(
        PYID=Tube_ID).filter(
        PYSeqInfo.PCRSOP.in_(PYSeqCONF.PCRSOP)).order_by(
        -PYSeqInfo.CloseRefTags).first()
    print(f"seqinfo.CloseRefTags: {seqinfo.CloseRefTags}")
    if None == seqinfo:
        PYSeqSession.close()
        print("None == seqinfo")
        return False
    elif None == seqinfo.CloseRefTags:
        PYSeqSession.close()
        print("None == seqinfo.CloseRefTags")
        return False
    elif PYReportCONF.minimalTags > seqinfo.CloseRefTags:
        PYSeqSession.close()
        print("PYReportCONF.minimalTags > seqinfo.CloseRefTags")
        print(seqinfo.CloseRefTags)
        return False
    else:
        PYSeqSession.close()

        biompath = PYReportCONF.scpheader + ":" + BIOMPATH(seqinfo)
        subfold = str(int(PriSID / 1000))
        path2sample = os.path.join(PYReportCONF.PYReport, subfold, Tube_ID)
        if False == os.path.exists(path2sample):
            os.makedirs(path2sample, mode=0o751)
        path4biom = os.path.join(path2sample, "CloseRef.biom")
        biompath = biompath.replace(PYReportCONF.scpheader + ":", "")
        cp_shstr = " ".join(["ln -s", biompath, path4biom])
        print(cp_shstr)
        code = os.system(cp_shstr)
        if code == 0:
            return True
        else:
            return False


def SCPBIOM(biompath, path2sample):
    exe = PYReportCONF.scp
    path4biom = os.path.join(path2sample, "CloseRef.biom")
    if os.path.exists(path4biom):
        os.chmod(path4biom, stat.S_IRUSR + stat.S_IWUSR)
        return True

    cmd = [exe, biompath, path4biom]
    shell = " ".join(cmd)
    print(shell)
    if os.system(shell):
        return False
    else:
        os.chmod(path4biom, stat.S_IRUSR + stat.S_IWUSR)
        return True


def BIOMPATH(seqinfo):
    runpath = RUNPATH(seqinfo.RUNID)
    biompath = os.path.join(runpath, seqinfo.SEQID, "CloseRef.biom")
    return biompath


def RUNPATH(runid):
    info = re.split(r"_", runid)
    date = info[0]
    machine = info[1]
    [year, month, day] = re.compile(r"\d\d").findall(date)
    year = "20" + year
    seqtype = "MiSeq"
    if "MN00302" == machine:
        seqtype = "MiniSeq"

    runpath = os.path.join(PYSeqCONF.PYBIOM, seqtype,
                           year, month, machine, runid)
    return runpath
