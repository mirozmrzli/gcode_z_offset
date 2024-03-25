Voron 2.4 using Orcaslicer

Tool to move individual objects in g-code up/down by set ammount to nail down the first layer offset.

1. Use '9 piece set.3mf' Orcaslicer project to slice with the preferred settings and 
export the gcode to a file (9_piece_test.gcode).
2. Run the python script
    - **python offsets.py 9_piece_test.gcode -0.02 0.005 out.gcode**
    - This will offset z positions of each object by using SET_GCODE_OFFSET Z_ADJUST command.
3. Print and pick the one that looks the best.
4. Use it's z offset to add to your z_offset in your printer.cfg file.
5. ???
6. Profit

<br>

Command line parameters: <br>
`offset.py <infile> <offset start> <offset step> [<outfile>]`

<br>
Here's the example of the output:

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

<br>

## Verify the number of digits for offset and step size.
If you fatfinger incorrect values, there is a good chance you'll be buying a new build surface and/or nozzle. Program will print offsets it applies to the objects (those are also embedded in the output file), make sure those are ok before pushing 'Print' button. Good range for offset would be -0.04 to 0.04
