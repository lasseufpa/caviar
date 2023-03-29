import mitsuba as mi
import drjit as dr

mi.set_variant("cuda_ad_rgb")


def getPositionParams(scene):
    # scene = mi.load_file(mitsuba_file)
    params = mi.traverse(scene)
    return params


def translate(
    scene,
    obj_name: str,
    x_translation_step: float = 0,
    y_translation_step: float = 0,
    z_translation_step: float = 0,
):
    params = getPositionParams(scene)
    object = dr.unravel(mi.Point3f, params[f"{obj_name}.vertex_positions"])
    object.x += x_translation_step
    object.y += y_translation_step
    object.z += z_translation_step
    params[f"{obj_name}.vertex_positions"] = dr.ravel(object)
    params.update()


def moveTo(
    mitsuba_file: str,
    obj_name: str,
    x_translation_step: float = 0,
    y_translation_step: float = 0,
    z_translation_step: float = 0,
):
    params = getPositionParams(mitsuba_file)
    object = dr.unravel(mi.Point3f, params[f"{obj_name}.vertex_positions"])
    object.x = x_translation_step
    object.y = y_translation_step
    object.z = z_translation_step
    params[f"{obj_name}.vertex_positions"] = dr.ravel(object)
    params.update()


scene = mi.load_file("simple_street_canyon/simple_street_canyon.xml")
translate(scene, "mesh-Cube", 0, 0, 100)
