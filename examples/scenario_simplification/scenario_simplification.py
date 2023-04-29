import bpy

classes = {
    "1": {"min_faces": 1, "max_faces": 10, "decimate_ratio": 0.8},
    "2": {"min_faces": 11, "max_faces": 20, "decimate_ratio": 0.3},
}


def getAllObjectsNumberOfFaces():
    for OBJ_NAME in bpy.data.objects.keys():
        OBJ = bpy.data.objects[OBJ_NAME]
        try:
            number_of_faces = len(OBJ.data.polygons)
            print(number_of_faces)
        except:
            print("Data unavailable")


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
