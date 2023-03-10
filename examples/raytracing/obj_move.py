import numpy as np


def getFacesFromObjFile(pathToObjFile: str) -> list[list[float]]:
    """Reads an object file and returns a list containing the vertices points of
    each face composing the object.

    Args:
        pathToObjFile (str): path to the object file

    Returns:
        faces (list[list[float]]): a list with one elements for each face, with each face element
        containing a list for the vertice points
    """
    with open(pathToObjFile, encoding="utf-8") as file:
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


def modifyFacesOnObjFile(pathToObjFile: str, nparray_faces):
    """Writes the modified vertice values back on an object file.

    Args:
        pathToObjFile (str): path to the object file
        nparray_faces (ndarray):holds the modified vertices values in a
                                numpy array in a structure similar to the
                                output obtained from getFacesFromObjFile()
    """
    with open(pathToObjFile, "r", encoding="utf-8") as file_read:
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
    with open(pathToObjFile, "w", encoding="utf-8") as file_write:
        file_write.writelines(obj_lines)
    file_write.close()


def move(
    pathToObjFile: str,
    x_movement_step: float = 0,
    y_movement_step: float = 0,
    z_movement_step: float = 0,
):
    """Makes an object execute a movement on a given axis or axes.

    Args:
        pathToObjFile (str): path to the object file
        x_movement_step (float): the step size for x
        y_movement_step (float): the step size for y
        z_movement_step (float): the step size for z
    """
    nparray_faces = np.array(getFacesFromObjFile(pathToObjFile))

    nparray_faces[:, :, 0] = nparray_faces[:, :, 0] + x_movement_step
    nparray_faces[:, :, 1] = nparray_faces[:, :, 1] + y_movement_step
    nparray_faces[:, :, 2] = nparray_faces[:, :, 2] + z_movement_step

    modifyFacesOnObjFile(pathToObjFile, nparray_faces)


if __name__ == "__main__":
    move(
        "./simple_car.object",
        x_movement_step=-0.1727235913,
        y_movement_step=0.8878211975,
        z_movement_step=-2.7066750526,
    )
