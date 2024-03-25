Voron 2.4 using Orcaslicer

Tool to move individual objects in g-code up/down by set ammount to nail down the first layer offset.

1. Use '9 piece set.3mf' Orcaslicer project to slice with the preferred settings and 
export the gcode to a file.
2. Run the python script
    - python offsets.py 9_piece_test.gcode -0.02 0.005 out.gcode
    - This will offset z positions of each object by using SET_GCODE_OFFSET Z_ADJUST command.
3. Print and pick the one that looks the best.
4. Use it's z offset to add to your z_offset in your printer.cfg file.
5. ???
6. Profit
