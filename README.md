# MetaForge

This is an attempt to reconcile font creation using visual editors like [FontForge](https://fontforge.org/en-US/) with parametric, programming based font creation software like [MetaFont](https://ctan.org/pkg/metafont?lang=de). It is a Python plugin for FontForge that allows introducing variables that can be used to specify coordinates of points. As an example, the wide and thin stroke widths can be turned into variables, ensuring consistent design of the glyphs and minimal effort to change these dimensions.

## Installation

Put the file `metaforge.py` into the folder where FontForge looks for scripts, according to the documentation this should be either `$(PREFIX)/share/fontforge/python` and `~/.FontForge/python`, but in my case on Linux, `~/.config/fontforge/python` works as well. The `fontforge` Python module is required.

## Usage

In MetaForge, you can create parameters and assign some parametric expression to any point you have created in the glyph window. However, I would recommend writing down the constraints in a different file, of type `mfg` explained below, and import that file rather than entering all the constraints over the user interface of FontForge. Sometimes, it is necessary to do `Tools>MetaForge>Update all glyph parametrizations` in the font view window to make changes go into effect, especially when messing with `em` sizes and the like.

### Creating parameters

Go to `Tools>MetaForge>View/edit parameters...`. A crude interface for editing the list of current parameters is displayed; you can insert a new parameter, remove or update existing ones. For each new parameter, you will be asked for an identifier, which should consist only of letters and numbers, without spaces (this is currently not checked). Then, you can specify a value using arithmetic expressions, and including parameters that have already been defined. MetaForge **will not resolve equations** the way MetaFont does that, so it is your responsibility to check that each new variable is defined entirely in terms of existing ones or constants. This is important to consider when updating a value, as in this case, the order of the definitions is not changed, so you can only use values in the new expression that you could use in the old expression.

Note that MetaForge uses `eval` to evaluate the expression you type there. Numpy's functions are available as `np` and the FontForge Python extension as `ff`. The current font (as a Python variable) is available as `font`. Furthermore, a few special variables can be used, namely the font's em size as `em`, the ascent as `asc` and the descent as `desc`. These values will be read before any other parameter definition, so they are always available. You can also insert them as new parameters, which will actually set the font parameters to the respective values. In this case, even though they are displayed below the parameters defined before, they will be evaluated first.

### Parametrizing points

After selecting one or more points, you can choose `Parametrize selected points...` from the MetaForge menu, which will ask you for a name (which all selected points will receive), an x and y coordinate as well as incoming and outgoing radii and angles (refering to the control points of the curve). You can then also `View/edit parametrized points...` similar to the parameters. Again, the order of the definition matters, and you can use already defined coordinates as references. Additionally, the current glyph attributes are available under `glyph`, and `wd`, `lft` and `rt` correspond to the width, the left and the right side bearing, respectively. Note that when setting `lft`, the individual points in the glyph are **not shifted** as usual, but the width will be changed to accommodate for the new value. Thus, you will still have to set the x coordinate of your leftmost point to `lft`.

When adding a new coordinate, MetaForge will not create a new point. In fact, MetaForge **will never add or remove existing points**. Adding a new coordinate only has an effect if afterwards a point with a corresponding name is created (and parametrizations are updated). This can be abused to create "local parameters", by adding a new "coordinate" that does not end in `_x`, `_y`, etc. Similarly, removing a coordinate only removes the constraint, so that the point can be moved and will not be updated anymore. `Deparametrize selected points...` does that for all the coordinates of selected points.

### Importing and exporting parametrizations

The parametrizations for a specific glyph or the whole font can be exported using `Export parametrizations...` in the respective MetaForge menu. Importing is currently only possible for the whole font (i.e., it will always update all glyphs for which parametrizations are specified). This functionality is implemented using the `mfg` file format, which is described here.

To declare a parameter `foo` with value `bar`, write

```
* foo: bar
```

on a new line. Whitespace does not matter except at the beginning of the line, which must be `*`. The assignment is global, no matter where it is carried out, and again, the order matters and later reassignments do not change the order.

To start definitions for a new glyph, say `S`, type

```
/S
```

on a new line. Everything between `/` and the line end will be interpreted as a FontForge glyph name. Now, new coordinate constraints can be added with a `+`, like

```
+ a_x: 0.3*em
+ a_y: 0.2*em
+ a_phii: 60
+ a_phio: a_phii + 180
```

etc. Any line not beginning with `*`, `/` or `+` is ignored, allowing for a nice and literal documentation of the code. An example of this can be found at `basic-shapes.mfg`. Currently it only contains parametrizations of the letter `O`, but I might expand it in the future.

## Vim

You can put the file `mfg.vim` into your user `syntax` folder to enable syntax highlighting of `mfg` files. Note that you will also need to create a file in `ftdetect` if you want to automatically set the filetype to `mfg` for `*.mfg` files.

