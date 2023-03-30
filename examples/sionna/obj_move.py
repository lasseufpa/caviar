import mitsuba as mi
import drjit as dr
import xml.etree.ElementTree as ET

mi.set_variant("cuda_ad_rgb")


def getParams(mitsuba_file):
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
    xml_tree = ET.parse(mitsuba_file)

    # Get the <translate> grandchildren from a <shape> node with the desired "id"
    translation_element = (
        xml_tree.getroot()
        .findall(f"./shape[@id='{obj_name}']/transform/translate")[0]
        .attrib
    )
    # Update the values in <translate> with the desired translation step
    translation_element[
        "value"
    ] = f"{str(x_translation_step)} {str(y_translation_step)} {str(z_translation_step)}"

    # Write the modifications to disk
    xml_tree.write(mitsuba_file)


# Currently deprecated
def moveTo(
    mitsuba_file: str,
    obj_name: str,
    x_translation_step: float = 0,
    y_translation_step: float = 0,
    z_translation_step: float = 0,
):
    params = getParams(mitsuba_file)
    object = dr.unravel(mi.Point3f, params[f"{obj_name}.vertex_positions"])
    object.x = x_translation_step
    object.y = y_translation_step
    object.z = z_translation_step
    params[f"{obj_name}.vertex_positions"] = dr.ravel(object)
    params.update()


mitsuba_file = "/home/joao/codes/caviar/examples/sionna/simple_street_canyon/simple_street_canyon.xml"
translate(mitsuba_file, "mesh-Cube", -741, 0, 0)
