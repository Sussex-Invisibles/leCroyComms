#

from pyvisa.vpp43 import visa_library
from pyvisa.visa_exceptions import VisaIOError
visa_library.load_library("/Library/Frameworks/Visa.framework/VISA")
import visa
import sys
import time


class ScopeException(Exception):
    """Just an exception class
    """
    def __init__(self, error):
        Exception.__init__(self, error)


def chstr(channel):
    """Function to convert channel to the appropriate string.
    
    Only needed where a function can be used for either math/channel types.
    """
    if type(channel) is int:
        return "C%01d" % channel
    elif type(channel) is str:
        return "T%s" % channel
    else:
        raise ScopeException("Unknown channel type")


class LeCroy684(object):
    """LeCroy LC684DL Scope.
    Requires connection via GPIB.
    """
    
    def __init__(self, debug=False):
        self._dbg = debug
        self._conn = None
        self._conn = self._find_connection()
        self._measurements = {"area": "AREA",
                              "fall": "FALL",
                              "maximum": "MAX",
                              "minimum": "MIN",
                              "rise": "RISE",
                              "width": "WID"}

    def __del__(self):
        """Print any debug messages and clear logs.
        """        
        if self._dbg and self._conn:
#            self._write("GTL")
            try:
                print self._conn.ask("CHL? CLR")
            except VisaIOError:
                # timeout; fine.
                pass

    def _find_connection(self):
        """Find the appropriate GPIB connection
        """
        instrument_list = []
        print visa.get_instruments_list()        
        for instrument in visa.get_instruments_list():
            if instrument.startswith("GPIB"):
                temp_conn = visa.instrument(instrument)
                try:
                    response = temp_conn.ask("*IDN?")
                except VisaIOError:
                    # Need to release connection somehow!
                    print "Cannot connect with %s" % instrument
                    temp_conn.write("GTL")
                    raise
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

    def _ask(self, request):
        """A scope request.  But with some logging.
        """
        self._debug(request)
        return self._conn.ask(request)

    def _write(self, send):
        """A scope write.  But with some logging.
        """
        self._debug(send)
        self._conn.write(send)

    def reset_averaging(self, channel):
        """Reset averaging for the given (math) channel
        """
        self._write("T%s:FRST" % channel)

    def set_averaging(self, math_ch, scope_ch, nave):
        """Set channel T<math> to average T<scope>
        """
        self._write("T%s:DEF EQN,'AVGS(C%01d)',SWEEPS,%d" % (math_ch, scope_ch, nave))

    #def get_num_averages(self, math_ch):
    #    """Get the number of averages.
    #    """
    #    return self._ask("T%s?" % (math_ch))

    def set_trigger_mode(self, mode):
        """Set the trigger mode, options are single, normal
        """
        request = None
        if mode=="normal":
            request = "NORM"
        elif mode=="single":
            request = "SINGLE"
        else:
            raise scope.ScopeException("Unknown trigger mode %s" % mode)
        self._write("TRMD %s" % request)
        
    def set_trigger(self, channel, level, falling=False):
        """Set the trigger parameters for the scope.
        
        Still need to arm (enable_trigger).
        """
        request = ""
        request += "C%01d:TRLV %.3fV; " % (channel, level)
        if falling is False:
            request += "C%01d:TRSL POS" % channel
        else:
            request += "C%01d:TRSL NEG" % channel
        self._write(request)        

    def enable_trigger(self):
        """Just set the trigger
        """
        return self._write("ARM;")    

    def wait_triggered(self, channel):
        """Set the trigger on the scope and wait before acquiring waveform.
        """
        # TODO: add timeout
        return self._ask("ARM;WAIT;C%01d:WF?" % (channel))

    def get_waveform(self, channel):
        """Just get the waveform
        """
        return self._ask("%s:WAVEFORM? ALL" % chstr(channel))

    def save_waveform(self, channel, filename):
        """Get and save a waveform
        """
        f = open(filename, "w")
        f.write(self.get_waveform(channel))
        f.close()

    def set_x_scale(self, tdiv):
        """Set all channels to tdiv
        """
        self._write("TDIV %E" % (tdiv))

    def set_y_scale(self, channel, vdiv):
        """Set channel to vdiv
        """
        self._write("%s:VDIV %E" % (chstr(channel), vdiv))

    def set_y_position(self, channel, vpos):
        """Set the vertical position
        *** Math function positions must be set with DIVS! ***
        """
        if type(channel) is int:
            self._write("%s:OFST %f" % (chstr(channel), vpos))
        else:
            self._write("%s:VPOS %f" % (chstr(channel), vpos))            

    def set_cursor(self, axis, channel, pos1, pos2):
        """Set the cursors, must use div references.
        """
        if axis=="x" or axis=="X":
            csr = "HABS"
        elif axis=="y" or axis=="Y":
            csr = "VABS"
        else:
            raise ScopeException("Unknown axis %s" % axis)
        command = "%s:CRST %s,%f,%s,%f" % (chstr(channel), csr, pos1, csr, pos2)
        self._write(command)

    def measure(self, channel, parameter):
        """Make a measurement
        """
        if parameter in self._measurements:
            response = self._ask("%s:PAVA? %s" % (chstr(channel), self._measurements[parameter]))
            try:
                bits = response.split(",") # returns measurement, value unit, OK/NOTOK
                value = float(bits[1].split()[0])
                units = str(bits[1].split()[1])
                return value
            except:
                raise ScopeException("Could not parse measurement %s" % response)
        else:
            raise ScopeException("Unknown parameter type %s" % parameter)
    
