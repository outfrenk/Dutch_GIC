#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 09:30:14 2019

@author: out
"""
from Dutch_GIC.dutchgic import GIC
import pytest
import os

string='/usr/people/out/Documents/380+220kV_extended' #change to your own location of powergrid csv files

def test_init(tmpdir):
    test=GIC(string,tmpdir,tmpdir)
    assert test.samples == 0
    assert test.date is test.qdate is None
    assert os.path.exists('topo.cpt') is True
    assert os.path.exists(f'{string}/spreadsheettrafo.csv') is True
    assert os.path.exists(f'{string}/spreadsheetcables.csv') is True
    os.system(f'rm -rf {tmpdir}')
    
def test_download(tmpdir):
    test=GIC(string,tmpdir,tmpdir,'31-12-2009')
    test.standard_download(['esk'])
    assert os.path.exists(f'{tmpdir}/31-12-2009/esk20091231dmin.min') is True
    assert os.path.exists(f'{tmpdir}/07-01-2010/esk20100107dmin.min') is True
    test=GIC(string,tmpdir,tmpdir,'1-1-2000')
    test.standard_download(['esk'])
    assert os.path.exists(f'{tmpdir}/01-01-2000/esk20000101dmin.min') is True
    assert os.path.exists(f'{tmpdir}/22-12-1999/esk19991222dmin.min') is True
    os.system(f'rm -rf {tmpdir}')
    
def test_magextract(tmpdir):
    test=GIC(string,tmpdir,tmpdir,'12-03-1997')
    test.standard_download(['esk'])
    assert test.qdate == "10-03-1997"
    assert os.path.exists(f'{tmpdir}/{test.qdate}') is True
    File=open(f'{test.quietpath}/esk19970310dmin.min','r')
    for counter,line in enumerate(File):
        words=line.split()
        if words[0]=='DATE':
            datastart=counter+2
            for counter2,letters in enumerate(words[3]):
                if counter2==3:
                    if letters=='H':
                        types=False
                        break
                    if letters=='X':
                        types=True
                        break
    assert datastart == 27
    assert types is False
    test.iteratestation()
    assert test.samples == 1440
    assert test.minute is True
    assert os.path.exists(f'{test.respath}/{test.date}/Eskdalemuir_{test.datevar}/allresults.csv') is True
    assert len([name for name in os.listdir(f'{test.respath}/{test.date}/Eskdalemuir_{test.datevar}')]) == 5
    os.system(f'rm -rf {tmpdir}')