### What is it
This utility works like Orcaslicer's build in flow rate calibration, except it calibrates z_offset by offseting individual objects in the g-code up/down by the set ammount to nail down that first layer.

It is written for Voron 2.4 and Orcaslicer, however as long as your printer is using Klipper this should still work as-is. If not, modifying the code to set the proper z offset should be easy enough.

### How to get it to work:

1. Use '9 piece set.3mf' Orcaslicer project to slice with 0.2mm layer height and your preferred settings/filament and export the gcode to a file (9_piece_test.gcode). This is a good time to take note which object is which (select Process/Objects).
2. Run the python script
    - `python offsets.py 9_piece_test.gcode -0.02 0.005 out.gcode`
    - This will offset z positions of each object by using `SET_GCODE_OFFSET Z_ADJUST` command.
3. Print and pick the one that looks the best (look for the adhesion, elephant foot, dimensions etc).
4. Use it's z offset to add to your z_offset in your printer.cfg file.
5. ???
6. Profit


### Command line parameters:
`offset.py <infile> <offset start> <offset step> [<outfile>]`
<br>

### Example

    $ python offsets.py 9_piece_test.gcode -0.02 0.005 out.gcode
    n_04 z offset -0.02
    n_03 z offset -0.015
    n_02 z offset -0.01
    n_01 z offset -0.005
    p_00 z offset 0.0
    p_01 z offset 0.005
    p_02 z offset 0.01
    p_03 z offset 0.015
    p_04 z offset 0.02
    
    Verifying file out.gcode
    Note: Object p_00 doesn't specify offset.
    OK

Let's say that **p_03** was the best of the bunch. p_03 has a z_offset of 0.015. You need to add that value to your existing z_offset:

Current value
   
    [probe]
    z_offset = -0.905

Add

    new value = -0.905 + 0.015 
    = -0.89

New value
   
    [probe]
    z_offset = -0.89

Save and restart.

This will bring the nozzle 0.015 mm closer to the bed. Likewise, negative values will move it up and away from the bed.

Your z_offset might be defined elsewhere if you're using Clicky or Euclid.
<br>

## Verify the number of zeros for offset and step size.
If you fatfinger incorrect values, there is a good chance you'll be buying a new build surface and/or nozzle. Program will print offsets it applies to the objects (those are also embedded in the output file), make sure those are ok before pushing 'Print' button. Good range for offset would be -0.04 to 0.04.
