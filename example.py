#!/usr/bin/env python
# 
# example.py
#
# An example of reading LeCroy scope waveforms
# and plotting with ROOT.
#
# Assumes you have ROOT installed and correct
# environment for PyROOT.
#

import get_waveform
import ROOT
import os
import sys
import optparse

if __name__=="__main__":
    parser = optparse.OptionParser("Usage: python example.py <file>")
    (options,args) = parser.parse_args()
    fname = sys.argv[1]
    #read the file:
    x_vals,y_vals = get_waveform.get_waveform(fname)
    x_diff = x_vals[1]-x_vals[0]
    tg = ROOT.TGraph()
    for i,x in enumerate(x_vals):
        tg.SetPoint(i,x_vals[i],y_vals[i])
    can = ROOT.TCanvas()
    tg.Draw("alp")
    raw_input("Exit on RTN")
