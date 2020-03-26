import pint


registry = pint.UnitRegistry([
    # prefixes
    "µ- = 1e-6  = micro- = u-",
    "m- = 1e-3  = milli-",
    "c- = 1e-2  = centi-",
    "d- =  1e-1  = deci-",

    # base units
    "pt = [length] = points",
    # "% = [fraction] = pc = percent

    # derived units
    "\" = 72 * pt = inch = in",
    "m = inch / 0.0254 = meter = metre",

    # area
    "[area] = [length] ** 2",
])

c = registry("")

pt = registry.pt

mm = registry.mm
cm = registry.cm
dm = registry.dm
m = registry.m

inch = registry.inch


def as_mm(qty):
    return qty.to(mm).magnitude


def as_pt(qty):
    return qty.to(pt).magnitude
