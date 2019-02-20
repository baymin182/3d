OPENMVG_SFM_BIN = "/home/SENSETIME/baixu/openMVG_Build/Linux-x86_64-RELEASE"

CAMERA_SENSOR_WIDTH_DIRECTORY = "/home/SENSETIME/baixu/openMVG/src/software/SfM" + "/../../openMVG/exif/sensor_width_database"

OPENMVS_BIN_PATH = "/home/SENSETIME/baixu/openMVS_build/bin"

FOCAL_LENGTH = 3391.5
import os
import subprocess
import sys

def get_parent_dir(directory):
    return os.path.dirname(directory)


input_image_dir = os.path.abspath("./S0000")
output_dir = os.path.join(get_parent_dir(input_image_dir), "out")
if not os.path.exists(output_dir):
  os.mkdir(output_dir)

matches_dir = os.path.join(output_dir, "matches")
camera_file_params = os.path.join(CAMERA_SENSOR_WIDTH_DIRECTORY, "sensor_width_camera_database.txt")

# Create the ouput/matches folder if not present
if not os.path.exists(matches_dir):
  os.mkdir(matches_dir)

print ("1. Intrinsics analysis")
pIntrisics = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"),  "-i", input_image_dir, "-o", matches_dir,"-f",str(FOCAL_LENGTH),"-d", camera_file_params, "-c", "3"] )
pIntrisics.wait()

print ("2. Compute features")
pFeatures = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeFeatures"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-m", "SIFT", "-f" , "1","-p","HIGH"] )
pFeatures.wait()

print ("3. Compute matches")
pMatches = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-f", "1", "-n", "ANNL2"] )
pMatches.wait()

reconstruction_dir = os.path.join(output_dir,"reconstruction")

if not os.path.exists(reconstruction_dir):
    os.mkdir(reconstruction_dir)
print ("4. Do Incremental/Sequential reconstruction") #set manually the initial pair to avoid the prompt question
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_IncrementalSfM"),  "-i", matches_dir+"/sfm_data.json", "-m", matches_dir, "-o", reconstruction_dir] )
pRecons.wait()

print ("5. Colorize Structure")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/sfm_data.bin", "-o", os.path.join(reconstruction_dir,"colorized.ply")] )
pRecons.wait()

print ("6. Structure from Known Poses (robust triangulation)")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeStructureFromKnownPoses"),  "-i", reconstruction_dir+"/sfm_data.bin","-f", matches_dir+"/matches.f.bin", "-m", matches_dir, "-o", os.path.join(reconstruction_dir,"robust.ply")] )
pRecons.wait()

print ("7. openMVG2openMVS")
pMvs = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_openMVG2openMVS"), "-i", reconstruction_dir+"/sfm_data.bin", "-o", reconstruction_dir+"/scene.mvs", "-d", reconstruction_dir])
pMvs.wait()

print ("8. DensifyPointCloud")
pDense = subprocess.Popen( [os.path.join(OPENMVS_BIN_PATH,"DensifyPointCloud"), "scene.mvs", "-w",  reconstruction_dir])
pDense.wait()

print ("9. ReconstructMesh")
pRecon = subprocess.Popen( [os.path.join(OPENMVS_BIN_PATH,"ReconstructMesh"), "scene_dense.mvs", "-w", reconstruction_dir])
pRecon.wait()

print ("10. Mesh Refinement")
pMesh = subprocess.Popen( [os.path.join(OPENMVS_BIN_PATH,"RefineMesh"), "scene_dense_mesh.mvs","--resolution-level=4","-w", reconstruction_dir])
pMesh.wait()

print ("11. Mesh Texturing")
pTexture = subprocess.Popen( [os.path.join(OPENMVS_BIN_PATH,"TextureMesh"), "scene_dense_mesh_refine.mvs","-w", reconstruction_dir])
pTexture.wait()

print("Done")
