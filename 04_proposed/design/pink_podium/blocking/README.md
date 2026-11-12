# Pink podium: 3D blocking of the preferred design (08_park_B)

`build_blocking.py` builds the massing of `../08_park_B.png` in Blender and renders 10 clay views.
`pink_podium_blocking.blend` is the saved scene; `renders/` holds the clay views, a contact sheet and
`compare_view0_vs_08_park_B.jpg` (concept image above, blocking below).

What is modelled (all dimensions ASSUMED, read off the concept image and scaled to the 71 m front-slab slot):
- Plan 71 x 32 m overall, footprint about 1,350 m2: a wide rounded head, a slimmer curved body, a tail.
- Head: 4 storeys (16.5 m) with a taller, flared lattice crown and the round lookout deck.
- Roof descends continuously from the head to a low lawn (3.6 m), which falls to the ground toward the back and the tip.
- In front of the cafe the roof edge comes down to the ground (the "pinch"); from there a lattice arch
  (5.8 m crown) spans to the tip over a set-back glazed cafe, with the terrace in front.
- Fin screen with an open portal in the front, floor slabs, glazing.
- Roof park: serpentine main path that runs out to the ground at the back of the tail, a loop path, stream,
  small deck, picnic lawn, tree groups, people.

Cameras: 10 views, all 130 m from the building centre, 40 mm lens. Views 0–7 every 45° at 35° elevation
(view 0 = the camera of 08_park_B), view 8 overhead, view 9 at 10° elevation.

    .venv/bin/python 04_proposed/design/pink_podium/blocking/build_blocking.py [--views view0,view4] [--samples 24]

`../views_blocked/` was generated from the earlier L-shaped blocking and does NOT match this model.
