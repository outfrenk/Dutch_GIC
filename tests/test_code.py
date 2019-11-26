#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 09:30:14 2019

@author: out
"""
from Dutch_GIC.dutchgic import GIC
import pytest
import os

def test_init(tmpdir):
    string='/usr/people/out/Documents/380+220kV_extended/' #change to your own location
    test=GIC(string,tmpdir,tmpdir)
    assert test.date is test.qdate is None
    assert os.path.exists('topo.cpt') is True
    assert os.path.exists(f'{string}/spreadsheettrafo.csv') is True
    assert os.path.exists(f'{string}/spreadsheetcables.csv') is True