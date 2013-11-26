#

from pyvisa.vpp43 import visa_library
visa_library.load_library("/Library/Frameworks/Visa.framework/VISA")
import visa
import sys


class ScopeException(Exception):
    """Just an exception class
    """
    def __init__(self, error):
        Exception.__init__(self, error)


class LeCroy684(object):
    """LeCroy LC684DL Scope.
    Requires connection via GPIB.
    """
    
    def __init__(self, debug=False):
        self._dbg = debug
        self._conn = self._find_connection()

    def _find_connection(self):
        """Find the appropriate GPIB connection
        """
        instrument_list = []
        print visa.get_instruments_list()        
        for instrument in visa.get_instruments_list():
            if instrument.startswith("GPIB"):
                temp_conn = visa.instrument(instrument)
                response = temp_conn.ask("*IDN?")
                if response.startswith("*IDN LE"):
                    instrument_list.append(instrument)
        if len(instrument_list)==0:
            raise ScopeException("Cannot find LeCroy684 GPIB")
        elif len(instrument_list)==1:
            return visa.instrument(instrument_list[0])
        else:
            print "Select instrument:"
            for i, instrument in enumerate(instrument_list):
                temp_conn = visa.instrument(instrument)
                print "\t%s:\t%s" % (i, temp_conn.ask("*IDN?"))
            number = raw_input("Make selection [number]: ")
            return visa_instrument(instrument_list[number])

    def _debug(self, info):
        """Basic logging
        """
        if self._dbg is True:
            print info

    def _request(self, request):
        """A scope request.  But with some logging.
        """
        self._debug(request)
        return self._conn.ask(request)

    def get_waveform(self, channel):
        """Just get the waveform
        """
        return self._request("C%01d:WAVEFORM? ALL" % (channel))

    def save_waveform(self, channel, filename):
        """Get and save a waveform
        """
        f = open(filename, "w")
        f.write(self.get_waveform(channel))
        f.close()
