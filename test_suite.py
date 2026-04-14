import sys

sys.argv = ['virtual','tests/cfg/test_cfg_flags_04.txt']
if(input('scene setup? [y/N] ') == 'y'):
    import tests.scene_setup
if(input('test_00 (Free ray)? [y/N] ') == 'y'):
    import tests.test_00
if(input('test_01 (Basic Snell\'s law test)? [y/N] ') == 'y'):
    import tests.test_01
if(input('test_02 (Rotations+scaling)? [y/N] ') == 'y'):
    import tests.test_02
if(input('test_03 (Spherical lens, thick)? [y/N] ') == 'y'):
    import tests.test_03
if(input('test_04 (Spherical lens, timing)? [y/N] ') == 'y'):
    import tests.test_04
if(input('test_05 (Mirror)? [y/N] ') == 'y'):
    import tests.test_05
if(input('test_06 (Parabaloid mirror)? [y/N] ') == 'y'):
    import tests.test_06
if(input('test_07 (Parabaloid lens, tilt)? [y/N] ') == 'y'):
    import tests.test_07
if(input('test_08 (Parabaloid lens, focus width)? [y/N] ') == 'y'):
    import tests.test_08
if(input('test_09 (Microscope)? [y/N] ') == 'y'):
    import tests.test_09
if(input('test_10 (Planoconvex, thin)? [y/N] ') == 'y'):
    import tests.test_10
if(input('test_11 (Chromatic aberration)? [y/N] ') == 'y'):
    import tests.test_11_chromatic
if(input('test_12 (Cooke triplet)? [y/N] ') == 'y'):
    import tests.test_12_cooke_triplet
