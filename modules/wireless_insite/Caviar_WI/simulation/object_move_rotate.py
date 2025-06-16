import numpy as np
import os
import shutil
import pathlib
from pathlib import Path
from scipy.spatial.transform import Rotation as R_scipy


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


def generate_new_step_folder(path_to_obj_file: str, output_dir: str, current_step: int = 0) -> str:
    """Generates a new folder for the next step, copying all contents 
    from the current folder.

    Args:
        path_to_obj_file (str): Path to the object file.
        output_dir (str): Directory where the new folder will be created.
        current_step (int, optional): Step number. Default is 0.

    Returns:
        str: The path to the object file in the new folder.
    """
    filename = os.path.basename(path_to_obj_file)  # Get the file name

    path_to_next_step_file = os.path.join(output_dir, f"run{current_step}")

    os.makedirs(path_to_next_step_file, exist_ok=True)  # Create the folder if it doesn't exist

    path_to_next_obj_file = os.path.join(path_to_next_step_file, filename)

    shutil.copytree(os.path.dirname(path_to_obj_file), path_to_next_step_file, dirs_exist_ok=True)

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

    Returns:
        str: The path to the object file on the new folder
    """
    nparray_faces = np.array(getFacesFromObjFile(path_to_obj_file))

    nparray_faces[:, :, 0] = nparray_faces[:, :, 0] + x_translation_step
    nparray_faces[:, :, 1] = nparray_faces[:, :, 1] + y_translation_step
    nparray_faces[:, :, 2] = nparray_faces[:, :, 2] + z_translation_step

    path_to_next_obj_file = generate_new_step_folder(path_to_obj_file, current_step)

    modifyFacesOnObjFile(path_to_next_obj_file, nparray_faces)

    return path_to_next_obj_file


def moveTo_and_rotate(
    path_to_obj_file: str,
    output_dir: str,
    current_step: int = 0,
    position: tuple = (0, 0, 0),
    rotation: tuple = (0, 0, 0),
    rotation_quaternion: tuple = (0, 0, 0, 1)
):
    """Moves an object while applying rotation along all axes.

    Args:
        path_to_obj_file (str): Path to the object file.
        output_dir (str): Directory where the new step folder is created.
        current_step (int, optional): Step number for tracking. Defaults to 0.
        position (tuple, optional): New (x, y, z) position. Defaults to (0, 0, 0).
        rotation (tuple, optional): Rotation around (rot_x, rot_y, rot_z) in degrees. Defaults to (0, 0, 0).

    Returns:
        str: Path to the object file in the new folder.
    """

    if not Path(path_to_obj_file).exists():
        print(f"Error: Object file {path_to_obj_file} not found.")
        exit(1)

    # Load object faces
    nparray_faces = np.array(getFacesFromObjFile(path_to_obj_file))  # (N, 3)
    
    # if nparray_faces.ndim == 1 and nparray_faces.size % 3 == 0 : # e.g. [x1,y1,z1,x2,y2,z2...]
    #     nparray_faces = nparray_faces.reshape(-1,3)
    # elif nparray_faces.ndim != 2 or nparray_faces.shape[1] != 3:
    #     print(f"Error: Vertex array from {path_to_obj_file} has unexpected shape {nparray_faces.shape}. Expected (N, 3).")
    #     exit(1)

    # Convert  quaternion rotation to rotation matrix

    r_obj = R_scipy.from_quat(rotation_quaternion)
    R = r_obj.as_matrix()

    # theta_x, theta_y, theta_z = np.radians(rotation)

    # # Rotation matrix around X-axis
    # Rx = np.array([
    #     [1, 0, 0],
    #     [0, np.cos(theta_x), -np.sin(theta_x)],
    #     [0, np.sin(theta_x), np.cos(theta_x)]
    # ])

    # # Rotation matrix around Y-axis
    # Ry = np.array([
    #     [np.cos(theta_y), 0, np.sin(theta_y)],
    #     [0, 1, 0],
    #     [-np.sin(theta_y), 0, np.cos(theta_y)]
    # ])

    # # Rotation matrix around Z-axis
    # Rz = np.array([
    #     [np.cos(theta_z), -np.sin(theta_z), 0],
    #     [np.sin(theta_z), np.cos(theta_z), 0],
    #     [0, 0, 1]
    # ])

    # Calculate object center
    current_center = np.mean(nparray_faces.reshape(-1, 3), axis=0)

    # Center object before rotation
    centered_vertices = nparray_faces - current_center

    # Apply rotations in order: X → Y → Z
    # rotated_vertices = np.dot(centered_vertices, Rx.T)
    # rotated_vertices = np.dot(rotated_vertices, Ry.T)
    # rotated_vertices = np.dot(rotated_vertices, Rz.T)

    original_shape = centered_vertices.shape
    vertices_to_rotate = centered_vertices.reshape(-1, 3)
    rotated_flat_vertices = np.dot(vertices_to_rotate, R.T) # Usamos R.T porque os vértices são vetores linha
    rotated_vertices = rotated_flat_vertices.reshape(original_shape)

    # Translate to new position
    displacement = np.array(position)
    new_vertices = rotated_vertices + displacement

    # Create a new directory for the updated object
    path_to_next_obj_file = generate_new_step_folder(path_to_obj_file, output_dir, current_step)
    
    # Save the updated vertices to the new file
    modifyFacesOnObjFile(path_to_next_obj_file, new_vertices)

    return path_to_next_obj_file

if __name__ == "__main__":
    current_position_path = "/home/fritz/data/Caviar/caviar/examples/insite/Object_Step/random-line.object"

    # List of positions (x, y, z) and rotations (rot_x, rot_y, rot_z)
    positions = [(5, 8, 0), (7, 8, 0), (9, 8, 0), (11, 8, 0)]
    rotations = [(0, 0, 0), (30, 0, 0), (0, 45, 0), (0, 0, 90)]  # Rotation in degrees (X, Y, Z)

    for step, (position, rotation) in enumerate(zip(positions, rotations), start=1):
        current_position_path = moveTo_and_rotate(
            path_to_obj_file=current_position_path,
            output_dir=os.path.dirname(current_position_path),
            current_step=step,
            position=position,
            rotation=rotation
        )

        print(f"Step {step}: Object moved to {position} with rotation {rotation}.")