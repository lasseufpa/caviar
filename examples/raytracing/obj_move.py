import numpy as np
import os
import shutil
import pathlib


def getFacesFromObjFile(path_to_obj_file: str) -> list[list[float]]:
    """Reads an object file and returns a list containing the vertices points of
    each face composing the object.

    Args:
        path_to_obj_file (str): path to the object file

    Returns:
        faces (list[list[float]]): a list with one elements for each face, with each face element
        containing a list for the vertice points
    """
    with open(path_to_obj_file, encoding="utf-8") as file:
        obj_lines = file.readlines()
        startReadingVertices = False  # Indicates if the line above was 'nVertices'
        initialVerticeIdx = 0  # Indicates the initial line of the vertice descrpt.
        nVertices = 0
        faces = []
        vertices = []

        for line_idx, line in enumerate(obj_lines):
            # Start reading vertices from a face
            if startReadingVertices and line_idx <= initialVerticeIdx + nVertices:
                # Clean the line first
                if line.find("\n"):
                    line.replace("\n", "")
                vertices.append(
                    [float(vertice_point) for vertice_point in line.split(" ")]
                )

            # Finished reading vertices from a face
            if startReadingVertices and line_idx > initialVerticeIdx + nVertices:
                faces.append(vertices)
                vertices = []
                startReadingVertices = False

            # Get number of vertices from each face
            if line.find("nVertices") != -1:  # Check if line contains 'nVertices'
                startReadingVertices = True
                initialVerticeIdx = line_idx
                nVertices = int(line[line.find(" ") : -1])
    file.close()

    return faces


def modifyFacesOnObjFile(path_to_obj_file: str, nparray_faces):
    """Writes the modified vertice values back on an object file.

    Args:
        path_to_obj_file (str): path to the object file
        nparray_faces (ndarray):holds the modified vertices values in a
                                numpy array in a structure similar to the
                                output obtained from getFacesFromObjFile()
    """
    with open(path_to_obj_file, "r", encoding="utf-8") as file_read:
        obj_lines = file_read.readlines()
        startReadingVertices = False  # Indicates if the line above was 'nVertices'
        initialVerticeIdx = 0  # Indicates the initial line of the vertice descrpt.
        nVertices = 0
        nVertices = 0
        current_face = 0
        current_vertice = 0

        for line_idx, line in enumerate(obj_lines):
            # Start reading vertices from a face
            if startReadingVertices and line_idx <= initialVerticeIdx + nVertices:
                modified_text = ""
                for point in nparray_faces[current_face, current_vertice, :]:
                    modified_text = modified_text + str(point) + " "
                modified_text = modified_text[:-1] + "\n"
                obj_lines[line_idx] = modified_text
                current_vertice = current_vertice + 1

            # Finished reading vertices from a face
            if startReadingVertices and line_idx > initialVerticeIdx + nVertices:
                current_vertice = 0
                current_face = current_face + 1
                startReadingVertices = False

            # Get number of vertices from each face
            if line.find("nVertices") != -1:  # Check if line contains 'nVertices'
                startReadingVertices = True
                initialVerticeIdx = line_idx
                nVertices = int(line[line.find(" ") : -1])
    file_read.close()

    # Loop to write modifications from 'modified_lines' list to file
    with open(path_to_obj_file, "w", encoding="utf-8") as file_write:
        file_write.writelines(obj_lines)
    file_write.close()


def generateNewStepFolder(path_to_obj_file: str, current_step: int = 0) -> str:
    """Generates a new folder to hold the next step by copying all the contents
    from the current step folder.

    Args:
        path_to_obj_file (str): path to the object file
        current_step (int, optional): number to identify new step folder.
                                      Defaults to 0.

    Returns:
        str: The path to the object file on the new folder
    """
    [path_to_current_step_file, filename] = os.path.split(path_to_obj_file)

    path_to_next_step_file = os.path.join(
        pathlib.Path(path_to_current_step_file).parents[0],
        f"run{current_step}",
    )

    path_to_next_obj_file = os.path.join(path_to_next_step_file, filename)

    shutil.copytree(
        src=path_to_current_step_file,
        dst=path_to_next_step_file,
    )

    return path_to_next_obj_file


def translate(
    path_to_obj_file: str,
    current_step: int = 0,
    x_translation_step: float = 0,
    y_translation_step: float = 0,
    z_translation_step: float = 0,
):
    """Makes an object execute a translation movement on a given axis or axes.

    Args:
        path_to_obj_file (str): path to the object file
        current_step (int, optional): number to identify new step folder. Defaults to 0.
        x_translation_step (float, optional): the step size for x. Defaults to 0.
        y_translation_step (float, optional): the step size for y. Defaults to 0.
        z_translation_step (float, optional): the step size for z. Defaults to 0.
    """
    nparray_faces = np.array(getFacesFromObjFile(path_to_obj_file))

    nparray_faces[:, :, 0] = nparray_faces[:, :, 0] + x_translation_step
    nparray_faces[:, :, 1] = nparray_faces[:, :, 1] + y_translation_step
    nparray_faces[:, :, 2] = nparray_faces[:, :, 2] + z_translation_step

    path_to_next_obj_file = generateNewStepFolder(path_to_obj_file, current_step)

    modifyFacesOnObjFile(path_to_next_obj_file, nparray_faces)


def moveTo(
    path_to_obj_file: str,
    current_step: int = 0,
    new_x: float = 0,
    new_y: float = 0,
    new_z: float = 0,
):
    """Makes an object move to a given point.

    Args:
        path_to_obj_file (str): path to the object file
        current_step (int, optional): number to identify new step folder. Defaults to 0.
        new_x (float, optional): new x value. Defaults to 0.
        new_y (float, optional): new y value. Defaults to 0.
        new_z (float, optional): new z value. Defaults to 0.
    """
    nparray_faces = np.array(getFacesFromObjFile(path_to_obj_file))

    nparray_faces[:, :, 0] = new_x
    nparray_faces[:, :, 1] = new_y
    nparray_faces[:, :, 2] = new_z

    path_to_next_obj_file = generateNewStepFolder(path_to_obj_file, current_step)

    modifyFacesOnObjFile(path_to_next_obj_file, nparray_faces)


if __name__ == "__main__":
    translate(
        "./run0/simple_car.object",
        current_step=1,
        x_translation_step=-0.1727235913,
        y_translation_step=0.8878211975,
        z_translation_step=-2.7066750526,
    )

    # moveTo(
    #     "./run0/simple_car.object",
    #     current_step=1,
    #     new_x=0,
    #     new_y=0,
    #     new_z=0,
    # )
