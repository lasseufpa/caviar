def getFacesFromObjFile(pathToObjFile):
    """Reads an object file and returns a list containing the vertices points of
    each face composing the object.

    Args:
        pathToObjFile (String): path to the .object file

    Returns:
        faces (List): a list with one elements for each face, with each face element
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
    return faces


if __name__ == "__main__":
    getFacesFromObjFile("./simple_car.object")
