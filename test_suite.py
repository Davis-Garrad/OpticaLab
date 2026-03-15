import sys

if(input('scene setup? [y/N] ') == 'y'):
    sys.argv = ['virtual','tests/cfg/test_cfg_flags_00.txt']
    import tests.scene_setup
if(input('test_00 (Free ray)? [y/N] ') == 'y'):
    sys.argv = ['virtual','tests/cfg/test_cfg_flags_00.txt']
    import tests.test_00
if(input('test_01 (Basic Snell\'s law test)? [y/N] ') == 'y'):
    sys.argv = ['virtual','tests/cfg/test_cfg_flags_00.txt']
    import tests.test_01
if(input('test_02 (Rotations+scaling)? [y/N] ') == 'y'):
    sys.argv = ['virtual','tests/cfg/test_cfg_flags_00.txt']
    import tests.test_02
if(input('test_03 (Spherical lens, thick)? [y/N] ') == 'y'):
    sys.argv = ['virtual','tests/cfg/test_cfg_flags_00.txt']
    import tests.test_03
if(input('test_04 (Spherical lens, timing)? [y/N] ') == 'y'):
    sys.argv = ['virtual','tests/cfg/test_cfg_flags_04.txt']
    import tests.test_04
if(input('test_05 (Mirror)? [y/N] ') == 'y'):
    sys.argv = ['virtual','tests/cfg/test_cfg_flags_00.txt']
    import tests.test_05
if(input('test_06 (Parabaloid mirror)? [y/N] ') == 'y'):
    sys.argv = ['virtual','tests/cfg/test_cfg_flags_00.txt']
    import tests.test_06
if(input('test_07 (Parabaloid lens, tilt)? [y/N] ') == 'y'):
    sys.argv = ['virtual','tests/cfg/test_cfg_flags_04.txt']
    import tests.test_07
if(input('test_08 (Parabaloid lens, focus width)? [y/N] ') == 'y'):
    sys.argv = ['virtual','tests/cfg/test_cfg_flags_04.txt']
    import tests.test_08
