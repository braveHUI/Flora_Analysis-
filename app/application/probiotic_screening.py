# -*- coding: utf-8 -*-
import os
from sys import argv
import pandas as pd
import numpy as np
from optparse import OptionParser
import json, time, sys
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from docxtpl import DocxTemplate
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

def test():
    print("test is running")
    current_path = '/'.join(os.path.abspath(__file__).split('/')[:-1])
    usage = "usage: %prog [options] arg1 arg2"
    parser = OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("-i", "--sampleid", dest="sampleid",
                      help="sampleid", metavar="FILE", default="SA1901109")
    parser.add_option("-k", "--outfile", dest="outfile", help="output prefix, the default is .", metavar="FILE",
                      default=".")
    parser.add_option("-b", "--biom", dest="biom_path", help="biom path", metavar="FILE",
                      )
    (options, args) = parser.parse_args()
    qimme_path = os.environ.get('qiime_base_path')
    activate_path = os.environ.get('activate_path')
    shstr = '''
export PATH=%s:$PATH
source activate %s
single_rarefaction.py -i otu_table.biom -o $workdir/otu_table_even10000.biom -d 10000
filter_otus_from_otu_table.py -i $workdir/otu_table_even10000.biom -o $workdir/otu_table_no_singletons.biom -n 2
biom convert -i $workdir/otu_table_no_singletons.biom --to-json -o $workdir/no_singletons.json
summarize_taxa.py -L 6,7 -i $workdir/otu_table_no_singletons.biom -o $workdir/
perl %s/configure/profile2taxlast.pl -i $workdir/otu_table_no_singletons_L6.txt -o $workdir/otu_table_no_singletons_L6.shortax
perl %s/configure/profile2taxlast.pl -i $workdir/otu_table_no_singletons_L7.txt -o $workdir/otu_table_no_singletons_L7.shortax
perl %s/configure/defined_species2profile.pl -i $workdir/otu_table_no_singletons_L6.shortax -p $genus_type -o $workdir/defined_L6.prof
perl %s/configure/defined_species2profile.pl -i $workdir/otu_table_no_singletons_L7.shortax -p $species_type -o $workdir/defined_L7.prof
normalize_by_copy_number.py -i $workdir/no_singletons.json -o $workdir/no_singletons.normalize
predict_metagenomes.py -i $workdir/no_singletons.normalize -o $workdir/no_singletons.ko
categorize_by_function.py -i $workdir/no_singletons.ko -c KEGG_Pathways -l 3 -o $workdir/no_singletons.pathway -f
perl %s/configure/profile2equalize.pl -i $workdir/no_singletons.pathway -o $workdir/no_singletons.pathway.prof
perl %s/configure/defined_species2profile.pl -i $workdir/no_singletons.pathway.prof -p $metabolism_type -o $workdir/no_singletons.metabolism
alpha_diversity.py -i $workdir/otu_table_even10000.biom -m observed_species -o $workdir/otu_table_no_singletons.obs''' % (
    activate_path, qimme_path, current_path, current_path, current_path, current_path, current_path, current_path)

    #a,b = getone(options.infilename, shstr, options.outfile, current_path)
    getshai(options.sampleid, shstr, options.outfile, current_path, options.biom_path)


def getone(file0, shstr, outpath, current_path):#file0:SGC0200919      /share/douhy/shuguo/SGC0200919.biom
    print("getone is running")
    filename = outpath + '/' + file0.split('/')[-1].replace('.biom','')
    littlefilename = file0.split('/')[-1].replace('.biom','')
    biompath = file0
    otu_table_even10000 = littlefilename + '_10000.biom'
    otu_table_no_singletons = littlefilename + '_no_singletons.biom'
    begi = 'mkdir -p ' + filename + '\n'
    no_singletons_L6 = littlefilename + '_no_singletons_L6.txt'
    no_singletons_L7 = littlefilename + '_no_singletons_L7.txt'

    shstr = begi + shstr

    shstr = shstr.replace('otu_table.biom', biompath)
    shstr = shstr.replace('$workdir', filename)
    shstr = shstr.replace('otu_table_even10000.biom', otu_table_even10000)
    shstr = shstr.replace('otu_table_no_singletons.biom', otu_table_no_singletons)
    a = '%s/configure/metabolism_type' % (current_path)
    shstr = shstr.replace('$metabolism_type', a)
    b = '%s/configure/genus.define.type' % (current_path)
    shstr = shstr.replace('$genus_type', b)
    c = '%s/configure/species.define.type' % (current_path)
    shstr = shstr.replace('$species_type', c)
    shstr = shstr.replace('otu_table_no_singletons_L6.txt', no_singletons_L6)
    shstr = shstr.replace('otu_table_no_singletons_L7.txt', no_singletons_L7)
    os.system(shstr)
    outfile = filename + '/result.json'
    dfrefile = filename + '/dfre.csv'
    dfre = getfulltable(littlefilename, filename, current_path)
    # print dfre.head()
    dfre.to_csv(dfrefile)

    rejson, ddict = getjson(dfre)

    with open(outfile, 'w') as f:
        f.write(rejson)
    # with open(outfile+'_dict.txt','w') as g:
    #    g.write(str(ddict))
    srtest = pd.Series(ddict)
    print(srtest)
    srtest = srtest.drop(["password", "username"])
    srtestfile = filename+'/'+littlefilename + '_wanted.result'  # srtestfile = filename +'/'+filename+'_wanted.result'
    srtest.to_csv(srtestfile, sep='\t')
    print(rejson)

    return rejson, ddict


def getfulltable(littlefilename, filename, current_path):
    print("getfulltable is running")
    a = '%s/configure/metabolism_type' % (current_path)
    b = '%s/configure/genus.define.type' % (current_path)
    c = '%s/configure/species.define.type' % (current_path)
    dfgenus = pd.read_table(b, header=None)
    dfspecies = pd.read_table(c, header=None)
    dfmetabolism = pd.read_table(a, header=None)
    allindex = dfgenus[1].tolist()
    allindex.extend(dfspecies[1].tolist())
    allindex.extend(dfmetabolism[1].unique().tolist())
    dfre = pd.DataFrame(np.zeros((len(allindex), 1)), index=allindex)
    L6name = filename + '/defined_L6.prof'
    df6 = pd.read_table(L6name, index_col=0)
    # print df6.head()
    L7name = filename + '/defined_L7.prof'
    df7 = pd.read_table(L7name, index_col=0)
    # print df7.head()
    Metaname = filename + '/no_singletons.metabolism'
    dfmeta = pd.read_table(Metaname, index_col=0)
    # print dfmeta.head()
    obs = filename + '/otu_table_no_singletons.obs'
    dfobs = pd.read_table(obs, index_col=0)
    dfobs = dfobs.T
    # print dfobs

    for i in range(df6.shape[0]):
        h = list(df6.index)[i]
        dfre.loc[h] = df6.iloc[i, 0]

    for j in range(df7.shape[0]):
        w = list(df7.index)[j]
        dfre.loc[w] = df7.iloc[j, 0]

    for k in range(dfmeta.shape[0]):
        p = list(dfmeta.index)[k]
        dfre.loc[p] = dfmeta.iloc[k, 0]

    for l in range(dfobs.shape[0]):
        q = list(dfobs.index)[l]
        dfre.loc[q] = dfobs.iloc[l, 0]

    dfre.columns = [littlefilename]
    dfre.index = map(lambda x: x.replace(' ', ''), list(dfre.index))
    return dfre


def chulikongge(sstr):
    b = ""
    if " " in sstr:
        a = sstr.split(" ")
        b = "".join([i.capitalize() for i in a])
    else:
        b = sstr
    return b


def getjson(dfre):
    print("getjson is running")
    dfredict = dfre.to_dict()
    print("dfredict : {}".format(dfredict))
    ddict = list(dfredict.values())[0]
    databasic = {'username': 'puyuan', 'password': 'puyuan2017', 'pyid': str(list(dfre.columns)[0])}
    ddict.update(databasic)
    zuolist = "Acinetobacter;Akkermansia;Amino Acid Metabolism;Bacteroides;Bifidobacterium;BifidobacteriumBifidum;BifidobacteriumLongum;Bilophila;Blautia;Butyricimonas;Carbohydrate Metabolism;Clostridium;Collinsella;Coprococcus;Dorea;Enterococcus;Haemophilus;HaemophilusInfluenzae;Klebsiella;Lachnospira;Lactobacillus;Lipid Metabolism;Neisseria;observed_species;Oscillospira;Prevotella;Roseburia;Salmonella;Serratia;Shigella;Streptococcus;Sutterella;Veillonella".split(
        ";")
    minlist = "0;0;0.112149;0.000323;0.128076;0.000783;0.067149;0;0.000334;0;0.102729;0.000335;0.000346;3.80E-05;4.00E-05;0;3.80E-05;0;0;0;0.002418;0.026551;0;119;0;0.000823;0;0;0;0;0.006637168;1.00E-05;0.000393".split(
        ";")
    minlist = [round(float(i), 6) for i in minlist]
    maxlist = "0;3.00E-06;0.118762;0.013155;0.504183;0.024605;0.414732;1.70E-05;0.029496;0;0.109995;0.003036;0.007505;0.007182;0.003788;0.002115;0.002381;0;0;0.000722;0.065066;0.028547;0;224;0.00251;0.350845;0.000237;0;0;0;0.081730327;0.002884;0.010286".split(
        ";")
    maxlist = [round(float(i), 6) for i in maxlist]
    for i in range(len(zuolist)):
        ddict[(chulikongge(zuolist[i]) + "_min")] = minlist[i]
        ddict[(chulikongge(zuolist[i]) + "_max")] = maxlist[i]
    for k in ddict:
        try:
            ddict[k] = round(ddict[k], 6)
        except:
            pass
    return json.dumps(ddict, indent=4), ddict


def getall(ff, shstr, outpath, current_path):
    for i in ff:
        shstra, filename = getone(i, shstr, outpath, current_path)
        # print shstra
        os.system(shstra)
        outfile = filename + '/result.json'
        dfrefile = filename + '/dfre.csv'
        dfre = getfulltable(i, filename, current_path)
        # print dfre.head()
        dfre.to_csv(dfrefile)
        rejson, ddict = getjson(dfre)

        with open(outfile, 'w') as f:
            f.write(rejson)
        print(rejson)

        srtest = pd.Series(ddict)
        srtest = srtest.drop(["password", "username"])
        srtestfile = filename + '_wanted.result'  # srtestfile = filename +'/'+filename+'_wanted.result'
        srtest.to_csv(srtestfile, sep='\t')


def select_sql(sampleid):
    print("select_sql is running")
    content = {}
    user = os.environ.get('dbuser')
    pwd = os.environ.get('dbpassword')
    dbaddress = "127.0.0.1"
    DBName = os.environ.get("pycustome_name")
    DB_CONNECT = 'mysql+pymysql://{}:{}@{}/{}'.format(user, pwd, dbaddress, DBName)
    print(DB_CONNECT)
    engine = create_engine(DB_CONNECT, echo=True)
    conn = engine.connect()
    metadata = MetaData(engine, reflect=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    TubeInfor = metadata.tables['TubeInfor']
    sample = session.query(TubeInfor).filter_by(Sample_ID=sampleid).first()
    if sample:
        print("sample : {}".format(sample))
        content["name"] = sample[-3]
        content["age"] = sample[4]
        content["sex"] = "男" if int(sample[3]) == 1 else "女"
        content["pyid"] = sampleid
    else:
        print("数据库中查不到改样品编号：{}".format(sampleid))
    return content


def render_report(ddict, content, outpath, sampleid):
    print("render_report is running")
    Bifidobacterium_min = ddict["Bifidobacterium_min"]
    Bifidobacterium_max = ddict["Bifidobacterium_max"]
    Bifidobacterium = ddict["Bifidobacterium_max"]
    Lactobacillus_max = ddict["Lactobacillus_max"]
    Lactobacillus_min = ddict["Lactobacillus_min"]
    Lactobacillus = ddict["Lactobacillus"]
    if Bifidobacterium <= Bifidobacterium_max and Bifidobacterium >= Bifidobacterium_min :
        content["Bifidobacterium_result"] = "正常"
        content['btip'] = 0
    elif Bifidobacterium > Bifidobacterium_max:
        content["Bifidobacterium_result"] = "偏高"
        content['btip'] = 1
    elif Bifidobacterium < Bifidobacterium_min:
        content["Bifidobacterium_result"] = "偏低"
        content['btip'] = 2

    if Lactobacillus <= Lactobacillus_max and Lactobacillus >= Lactobacillus_min:
        content["Lactobacillus_result"] = "正常"
        content["ltip"] = 0
    elif Lactobacillus > Lactobacillus_max:
        content["Lactobacillus_result"] = "偏高"
        content['ltip'] = 1
    elif Lactobacillus < Lactobacillus_min:
        content["Lactobacillus_result"] = "偏低"
        content['ltip'] = 2
    base_path = os.path.dirname(os.path.abspath(__file__))
    print("content:{}".format(content))
    print("base_path:{}".format(base_path))
    old_temple = os.path.join(base_path, 'PY_probiotics_report.docx')
    # old_temple = os.path.join(base_path, 'test.docx')
    print(old_temple)
    tpl = DocxTemplate(old_temple)
    tpl.render(content)
    outfile = os.path.join(outpath, sampleid + "/PY_probiotics_report.docx")
    tpl.save(outfile)
    print("render_report is done")


def getshai(sampleid, shstr, outpath, current_path, biom_path):  # shaixuanban
    print("getshai is running")
    content = select_sql(sampleid)
    rejson, ddict = getone(biom_path, shstr, outpath, current_path)
    render_report(ddict, content, outpath, sampleid)
    selist = {'username', 'password', 'pyid', 'Bifidobacterium', 'Lactobacillus'}

    rejson2 = {key: ddict[key] for key in selist}
    for h in rejson2.keys():
        if isinstance(rejson2[h], float):
            rejson2[h] = round(np.sqrt(rejson2[h]), 4)
    rejson2['bi'] = rejson2.pop('Bifidobacterium')
    rejson2['la'] = rejson2.pop('Lactobacillus')
    rejson3 = json.dumps(rejson2, indent=4)
    print(rejson3)



test()

