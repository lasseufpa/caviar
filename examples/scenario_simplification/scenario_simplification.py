import bpy

classes = {
    "1": {"min_faces": 1, "max_faces": 10, "decimate_ratio": 0.8},
    "2": {"min_faces": 30, "max_faces": 40, "decimate_ratio": 0.5},
    "3": {"min_faces": 400, "max_faces": 600, "decimate_ratio": 0.1},
}


def getAllObjectsNumberOfFaces():
    for OBJ_NAME in bpy.data.objects.keys():
        OBJ = bpy.data.objects[OBJ_NAME]
        try:
            number_of_faces = len(OBJ.data.polygons)
            print(f"{OBJ_NAME}: {number_of_faces}")
        except:
            print(f"{OBJ_NAME}: Data unavailable")


def getDecimateRatioFromNumberOfFaces(number_of_faces: int, classes: dict):
    for key in classes:
        if (
            number_of_faces >= classes[key]["min_faces"]
            and number_of_faces <= classes[key]["max_faces"]
        ):
            return classes[key]["decimate_ratio"]


def simplifyObjects():
    for OBJ_NAME in bpy.data.objects.keys():
        OBJ = bpy.data.objects[OBJ_NAME]
        try:
            number_of_faces = len(OBJ.data.polygons)
            decimate_ratio = getDecimateRatioFromNumberOfFaces(number_of_faces, classes)
            OBJ.modifiers.new("Decimate", "DECIMATE")
            OBJ.modifiers["Decimate"].ratio = decimate_ratio
        except:
            print("Decimate unavailable")


if __name__ == "__main__":
    print(getDecimateRatioFromNumberOfFaces(15, classes))
