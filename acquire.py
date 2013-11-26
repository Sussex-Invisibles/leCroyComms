
import scope
import get_waveform
import os
import sys
import optparse

if __name__=="__main__":
    # Open the scope connection
    le_croy = scope.LeCroy684(debug=True)
    le_croy.save_waveform(1, "waveform_test")
    # Read the waveform
    x_vals, y_vals = get_waveform.get_waveform("waveform_test")
    print x_vals
    print y_vals
