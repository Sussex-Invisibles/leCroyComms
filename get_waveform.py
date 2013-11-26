import os
import sys
import struct

def read_word(fin,address):
    fin.seek(address)
    return struct.unpack('>h',fin.read(2))[0]
def read_long(fin,address):
    fin.seek(address)
    return struct.unpack('>l',fin.read(4))[0]
    #return struct.unpack('i',fin.read(4))[0]
def read_float(fin,address):
    fin.seek(address)
    return struct.unpack('>f',fin.read(4))[0]
def read_double(fin,address):
    fin.seek(address)
    return struct.unpack('>d',fin.read(8))[0]
def read_string(fin,address):
    fin.seek(address)
    return fin.read(16)[0]
def read_timestamp(fin,address):
    fin.seek(address)
    seconds = struct.unpack('>d',fin.read(8))[0]
    minutes = struct.unpack('>b',fin.read(1))[0]
    hours = struct.unpack('>b',fin.read(1))[0]
    days = struct.unpack('>b',fin.read(1))[0]
    months = struct.unpack('>b',fin.read(1))[0]
    year = struct.unpack('>h',fin.read(2))[0]
    timestamp = "%s.%s.%s %s:%s:%s"%(days,months,year,hours,minutes,seconds)
    return timestamp
def read_timebase(fin,address):
    fin.seek(address)
    e = struct.unpack('>h',f.read(2))[0]
def read_array(fin,address,arr_length,var_type,read_length):
    fin.seek(address)
    arr = []
    for i in range(arr_length):
        arr.append(struct.unpack('>%s'%var_type,fin.read(read_length))[0])
    return arr

def get_waveform(fname):    
    f = open(fname,"rb")
    #get the descriptor junk
    fc = f.read(50)
    pos = fc.index("WAVEDESC")
    template_name_addr = pos+16
    comm_type_addr = pos+32
    comm_order_addr = pos+34
    wave_descriptor_addr = pos+36
    user_text_addr = pos+40
    trigtime_array_addr = pos+48
    wave_array_addr = pos+60
    instrument_name_addr = pos+76
    instrument_number_addr = pos+92
    trace_label_addr = pos+96
    wave_array_count_addr = pos+116
    subarray_count_addr = pos+144
    vertical_gain_addr = pos+156
    vertical_offset_addr = pos+160
    nominal_bits_addr = pos+172
    horiz_interval_addr = pos+176
    horiz_offset_addr = pos+180
    vertunit_addr = pos+196
    horunit_addr = pos+244
    trigger_time_addr = pos+296
    record_type_addr = pos+316
    processing_done_addr = pos+318
    timebase_addr = pos+324
    vert_coupling_addr = pos+326
    probe_att_addr = pos+328
    fixed_vert_gain_addr = pos+332
    bandwidth_limit_addr = pos+334
    vertical_vernier_addr = pos+336
    acq_vert_offset_addr = pos+340
    wave_source_addr = pos+344

    f.close()

    f = open(fname,"rb")
    instrument_name = read_string(f,instrument_name_addr)
    instrument_number = read_long(f,instrument_number_addr)
    trigger_time = read_timestamp(f,trigger_time_addr)
    
    comm_type = read_word(f,comm_type_addr)
    wave_descriptor = read_long(f,wave_descriptor_addr)
    user_text = read_long(f,user_text_addr)
    wave_array = read_long(f,wave_array_addr)
    wave_array_count = read_long(f,wave_array_count_addr)
    trigtime_array = read_long(f,trigtime_array_addr)
    nb_segments = read_long(f,subarray_count_addr)

    vertical_gain = read_float(f,vertical_gain_addr)
    vertical_offset = read_float(f,vertical_offset_addr)

    horiz_interval = read_float(f,horiz_interval_addr)
    
    y_address = pos+wave_descriptor+user_text+trigtime_array
    y_length = wave_array_count / nb_segments
    y_type = 'b'
    y_read_length = 1
    if comm_type!=0:
        y_type = 'h'
        y_read_length = 2
    adc_vals = read_array(f,y_address,y_length,y_type,y_read_length)
    
    xvals = []
    yvals = []
    for i in range(wave_array_count):
        xvals.append(i * horiz_interval)
        
    #convert y from adc to voltages
    for i in range(len(adc_vals)):
        yvals.append(adc_vals[i] * vertical_gain - vertical_offset)

    print vertical_gain,vertical_offset
    return xvals,yvals
