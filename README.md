# Animaide 1.0.38

In contrast to modeling, when animating there are not that many options to manipulate keys on an f-curve like you can
with the vertices on a geometry. That is where **AnimAide** comes in.

There are some Blender options to manipulate keys, but **AnimAide** open the door to new possibilities. Not only has a
wider range of tools but when working with a group of f-curves each one will have their local space.

This kind of tools is standard in the game and film industry.

![Shortcut Troubleshoot](https://github.com/aresdevo/animaide/blob/gh-pages/images/animaide.jpg)

> **Note:** 
> *AnimOffset is on the headers by default now, but that can be changed in the addon preferences*
> ![AnimOffset header](https://github.com/aresdevo/animaide/blob/gh-pages/images/anim_offset_header.jpg)

**Tested with Blender 2.93 and up.**

At the moment, Animaide has Three main panels:

## curveTools

![Shortcut Troubleshoot](https://github.com/aresdevo/animaide/blob/gh-pages/images/local_space.gif)

These panel gives you helpful tools to simultaneously manipulate keys across
multiple f-curves from either animated objects or animated bones in an armature.

## animOffset

![AnimOffset](https://github.com/aresdevo/animaide/blob/gh-pages/images/anim_offset_basic.gif)

With this tool you can modify any animated object, and the change will propagate to the animation range. It can be
filter by a mask. You can find the panel in all the animation editors, but the mask option just in the GraphEditor.

![AnimOffset panel](https://github.com/aresdevo/animaide/blob/gh-pages/images/anim_offset_panel.gif)

The mask has the option of adding a blending border that fades the effect of the tool. The interpolation can be adjusted
in the preferences with the interpolation options.

![Mask Creation](https://github.com/aresdevo/animaide/blob/gh-pages/images/anim_offset_mask.gif)

## KeyManager:

![Key Manager](https://github.com/aresdevo/animaide/blob/gh-pages/images/key_manager_panel.jpg)

This toolbox mostly aims to speedup some tasks you already can do by adding extra options to some Blender Tools.

It has three main sections:
- **Move-Insert**
  ![Move Keys](https://github.com/aresdevo/animaide/blob/gh-pages/images/move_keys.gif)
  ![Move Keys](https://github.com/aresdevo/animaide/blob/gh-pages/images/insert_keys.gif)
- **Type**
  ![Key Type](https://github.com/aresdevo/animaide/blob/gh-pages/images/key_type.gif)
- **Interpolation**
  ![Handle type and selection](https://github.com/aresdevo/animaide/blob/gh-pages/images/handle_type_and_selection.gif)

  
### New on this version:

**In General:**
- *Bug fixes*
- Some settings were moved to the addon preferences. By being there your options will persist even after the Blender 
session is over.
- A new group of tools called **KeyManager** has been added to its own panel.
- Some panels can now be moved to the animation views headers.
- Animaide menu has been organized better.
- Menus and panels are now smarter. Tools are available just where they make sense. That simplifies the interface.
 
**CurveTools:**
- A new "Infinite" tool has been added.
- The "Noise" has been renamed "Wave-Noise". It now adds a wave when sliding to the left.
- Tools are now grouped in the "expand" mode for ease of use.
- Overshoot option button is now available next to the curveTool.
- If keys are not selected the tools will act on the keys under the cursor.
- If auto-key is on most tools will add a keyframe if no key under the cursor and no key is selected.
- Time-Offset works with cycles now.

**AnimOffset:**
- Panels can now be moved to the animation views headers to make them more accessible. On this version they
are in panels by default not to confuse the users, but in a future version will be on the headers by default.
- Interactive mask creation. New edit button appears after a mask has been created to make the process easier. The
new edit button is persistent
- AnimOffset is turned off automatically now if autokey is selected (because they can not be active at the same time).
- There is a new pie menu for AnimOffset on the Animaide menu.
 
**KeyManager:**
- This panel can be moved to the animation views headers to make it more accessible.
- Has three main sections:
- Move-insert:
  - *Move* keys in time by a specified amount. If some keys are selected just those will be affected.
  If non are selected the key under the cursor will.
  - *Inset* frames between keys by a specified amount. If some keys are selected, frames will be inserted
  between those. If non is selected frames will be inserted where the cursor is.
- Type:
     
  Uses the colored Blender key types (Keyframe, Breakdown, Jitter, Extreme), and lets you "assign", "select",
  "unselect" and "delete" them by type.
  It also incorporates a Blender option that lets you select the key type that auto-key will use.
- Interpolation:

  Lets you quickly assign interpolation types to key handles, just like Blender does, but with the added benefit of
  been able to assign it to every key in the selected object with the click of a button.
- When dealing with "Bezier" curves, it lets you select the left or right handles of every selected key to 
  easily interact with a group of handles at once.


### Enjoy the addon :)
