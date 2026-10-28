import sys, cadquery as cq
OLD = sys.argv[1]   # v7.2 Pi STEP folder (rework-01)
AG = sys.argv[2]    # antigravity 02_CAD_AND_SOURCE
N13 = sys.argv[3]   # DC-notch STEP
ld = lambda p: cq.importers.importStep(p).val()
plain = ld(f"{OLD}/Rack_Faceplate_2U_10in.step")
final = ld(f"{AG}/Rack_Faceplate_2U_10in_final.step")
notch = ld(N13)
ups_tray = ld(f"{OLD}/Pi5_UPS_v3_ups_tray_pinned.step")
board = ld(f"{OLD}/Pi5_UPS_v3_board_tray_HDMIexit.step")
shelf = ld(f"{OLD}/Rack_Shelf_pinned.step")
ext = ld(f"{AG}/UPS_Switch_Extender.step")
def bb(s): b = s.BoundingBox(); return f"x {b.xmin:.1f}..{b.xmax:.1f}  y {b.ymin:.1f}..{b.ymax:.1f}  z {b.zmin:.1f}..{b.zmax:.1f}"
print("plain faceplate  ", bb(plain), f"vol {plain.Volume():.0f}")
print("final faceplate  ", bb(final), f"vol {final.Volume():.0f}")
print("DC-notch fp      ", bb(notch), f"vol {notch.Volume():.0f}")
print("UPS tray         ", bb(ups_tray))
print("board tray       ", bb(board))
print("shelf            ", bb(shelf))
rem = plain.cut(final)
print("removed by final vs plain:", f"{rem.Volume():.0f} mm3")
for s in rem.Solids(): print("   piece", bb(s), f"{s.Volume():.0f} mm3")
add = final.cut(plain); print("added by final vs plain:", f"{add.Volume():.1f} mm3")
remn = plain.cut(notch); print("removed by DC-notch vs plain:", f"{remn.Volume():.0f} mm3"); [print("   piece", bb(s)) for s in remn.Solids()]
# is the DC-notch opening present in the final faceplate?
nb = remn.BoundingBox()
probe = cq.Workplane().box(nb.xlen-0.2, nb.ylen-0.2, nb.zlen-0.2).translate((nb.center.x, nb.center.y, nb.center.z)).val()
print("final faceplate material inside the DC-notch opening:", f"{final.intersect(probe).Volume():.0f} mm3 (0 = notch present)")
# Through-holes vs blind: thickness left at the slit
for nm,(x,z) in {"switch window centre":(62.6,13.0),"slit (x101.5,z35)":(101.5,35.0),"slit (x101.5,z20)":(101.5,20.0)}.items():
    line = cq.Workplane("XZ").center(x,z).circle(0.3).extrude(-20).translate((0,105,0)).val()
    print(f"  material along y at {nm}: {final.intersect(line).Volume()/ (3.14159*0.09):.2f} mm of faceplate")
# what is directly behind the switch window (between UPS face y 80.6 and faceplate rear y 112.5)?
corr = cq.Workplane().box(10.0, 112.5-80.6, 6.0).translate((62.6, (80.6+112.5)/2, 13.0)).val()
for nm, s in [("UPS tray", ups_tray), ("board tray", board), ("shelf", shelf)]:
    print(f"  in the 10x6 corridor behind the switch window: {nm} {s.intersect(corr).Volume():.0f} mm3")
cb = ups_tray.intersect(corr).BoundingBox() if ups_tray.intersect(corr).Volume()>0 else None
if cb: print("   UPS tray wall in corridor at", f"y {cb.ymin:.1f}..{cb.ymax:.1f}")
