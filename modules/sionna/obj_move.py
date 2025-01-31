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

    try:
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

    except:
        # In case there is no <translate> grandchildren from a <shape> node with the desired "id"
        # then get the <shape> node with the desired "id" and add the <translate> grandchildren
        shape_to_be_translated = xml_tree.getroot().find(f"./shape[@id='{obj_name}']")
        transform_tag = ET.Element("transform")
        transform_tag.set("name", "to_world")
        transform_translate_tag = ET.SubElement(transform_tag, "translate")
        # Update the values in <translate> with the desired translation step
        transform_translate_tag.set(
            "value",
            f"{str(x_translation_step)} {str(y_translation_step)} {str(z_translation_step)}",
        )
        shape_to_be_translated.insert(0, transform_tag)

    # Write the modifications to disk
    xml_tree.write(mitsuba_file)


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
