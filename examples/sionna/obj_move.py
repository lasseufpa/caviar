import mitsuba as mi
import drjit as dr
import xml.etree.ElementTree as ET

mi.set_variant("cuda_ad_rgb")


def getPositionParams(mitsuba_file):
    scene = mi.load_file(mitsuba_file)
    params = mi.traverse(scene)
    return params


def translate(
    mitsuba_file: str,
    obj_name: str,
    x_translation_step: float = 0,
    y_translation_step: float = 0,
    z_translation_step: float = 0,
):
    params = getPositionParams(mitsuba_file)
    root = ET.parse(mitsuba_file).getroot()
    # selected_object = root.findall(f"./shape[@id='{obj_name}']/transform/translate")
    for translation in root.findall(f"./shape[@id='{obj_name}']/transform/translate"):
        print(translation.attrib)
    print("END")


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


mitsuba_file = "/home/joao/codes/caviar/examples/sionna/simple_street_canyon/simple_street_canyon.xml"
translate(mitsuba_file, "mesh-Cube", -100, 0, 0)
