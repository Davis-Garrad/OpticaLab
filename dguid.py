'''A custom UUID/GUID module, so that I can name things for debugging and don't have to use an external library. Yeah, it's a terrible implementation. No, I'm not writing a proper UUID system for this. Sue me.'''

import time

def get_uuid():
    return hex(time.time_ns())[2:] # It'll never be the same!
