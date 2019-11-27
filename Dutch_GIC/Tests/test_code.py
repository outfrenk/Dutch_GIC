#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 09:30:14 2019

@author: out
"""
from Dutch_GIC.dutchgic import GIC
import pytest
import os
string='/usr/people/out/Documents/380+220kV_extended/' #change to your own location

def test_init(tmpdir):
    test=GIC(string,tmpdir,tmpdir)
    assert test.date is test.qdate is None
    assert os.path.exists('topo.cpt') is True
    assert os.path.exists(f'{string}/spreadsheettrafo.csv') is True
    assert os.path.exists(f'{string}/spreadsheetcables.csv') is True
    
def test_download(tmpdir):
    test=GIC(string,tmpdir,tmpdir,'12-3-1997')
    test.standard_download(['esk'])
    assert os.path.exists(f'{tmpdir}/12-03-1997/esk19970312dmin.min') is True
    assert os.path.exists(f'{tmpdir}/10-03-1997/esk19970310dmin.min') is True
    os.system(f'rm -rf {tmpdir}')
    test=GIC(string,tmpdir,tmpdir,'31-12-2009')
    test.standard_download(['esk'])
    assert os.path.exists(f'{tmpdir}/31-12-2009/esk20091231dmin.min') is True
    assert os.path.exists(f'{tmpdir}/07-01-2010/esk20100107dmin.min') is True
    os.system(f'rm -rf {tmpdir}')
    test=GIC(string,tmpdir,tmpdir,'1-1-2000')
    test.standard_download(['esk'])
    assert os.path.exists(f'{tmpdir}/01-01-2000/esk20000101dmin.min') is True
    assert os.path.exists(f'{tmpdir}/22-12-1999/esk19991222dmin.min') is True
    os.system(f'rm -rf {tmpdir}')