import json
import shutil
import logging
import sys
from pathlib import Path
from attrdict import AttrDict

from .simulation import TxRxFile, X3dXmlFile3_3, InSiteProject, object_move_rotate as omr, placement_rx

from .hmatrix import gen_database
from .hmatrix import gen_rays_dataset
from .hmatrix import gen_beam_output_file


def load_config(config_path: Path) -> AttrDict:
    """Loads configuration from a JSON file."""
    try:
        with config_path.open("r") as f:
            return AttrDict(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading configuration file: {e}")
        sys.exit(1)

def setup_results_dir(results_dir: Path, step: str):
    """Creates a clean results directory."""
    if results_dir.exists() and step == 1:
        try:
            shutil.rmtree(results_dir)
        except OSError as e:
            logging.error(f"Error removing directory {results_dir}: {e}")
            sys.exit(1)
    results_dir.mkdir(parents=True, exist_ok=True)

def process_step(step: int, pos: tuple, rot: tuple, base_object_path: Path, results_dir: Path,
                 obj_width: float, antenna, x3d_xml_file: X3dXmlFile3_3,
                 txrxFile: TxRxFile, insite_rx_name: str, dst_x3d_txrx_xpath: str):
    """Processes a single simulation step."""
    try:
        output_object_path = omr.moveTo_and_rotate(
            path_to_obj_file=str(base_object_path),
            output_dir=str(results_dir),
            current_step=step,
            position=pos,
            rotation=rot
        )
    except Exception as e:
        logging.error(f"Error processing step {step}: {e}")
        sys.exit(1)

    location = placement_rx(antenna, pos, obj_width)
    step_dir = results_dir / f"run{step}"
    project_output_dir = step_dir / 'study'
    xml_full_path = step_dir / 'model.study.xml'
    
    if project_output_dir.exists():
        try:
            shutil.rmtree(project_output_dir)
        except OSError as e:
            logging.error(f"Error removing directory {project_output_dir}: {e}")
            sys.exit(1)
    project_output_dir.mkdir(parents=True, exist_ok=True)
    
    x3d_xml_file.add_vertice_list(location, dst_x3d_txrx_xpath)
    x3d_xml_file.write(xml_full_path)
    txrxFile[insite_rx_name].location_list[0] = location
    txrxFile.write(step_dir / 'model.txrx')

    return step_dir

def run_simulation(cfg, run_path: Path):
    """Runs the simulation in Wireless InSite."""
    locale = ('LC_CTYPE=en_US.UTF-8 LC_NUMERIC=en_US.UTF-8 LC_TIME=en_US.UTF-8 ')
    wibatch_bin = (f"{locale}{cfg.insite_paths.REMCOMINC_LICENSE_FILE} "
                   f"LD_LIBRARY_PATH={cfg.insite_paths.insite_software_path}/OpenMPI/1.4.4/Linux-x86_64RHEL6/lib/ "
                   f"{cfg.insite_paths.insite_software_path}/WirelessInSite/3.3.0.4/Linux-x86_64RHEL6/bin/wibatch")
    
    logging.basicConfig(level=logging.INFO)
    project = InSiteProject()
    if run_path.is_dir():
        xml_full_path = run_path / 'model.study.xml'
        project_output_dir = run_path / 'study'
        project.run_x3d(xml_full_path, project_output_dir, wibatch_bin)

def main(positions: list, rotations: list,step: int):
    print(f"Running simulation for step {step} with positions: {positions} and rotations: {rotations}")
    if len(positions) != len(rotations):
        logging.error("Error: positions and rotations lists must have the same length.")
        sys.exit(1)
    
    working_directory = Path(__file__).resolve().parent
    cfg = load_config(working_directory / "config.json")
    
    base_insite_project_path = working_directory / "Bases_tests" / cfg.simulation.base_folder
    results_dir = working_directory / cfg.simulation.result_folder
    
    setup_results_dir(results_dir,step)

    base_txrx_file_name = base_insite_project_path / "model.txrx"
    base_x3d_xml_path = base_insite_project_path / f"model.{cfg.base_files_names.insite_study_area_name}.xml"
    base_object_path = base_insite_project_path / f"{cfg.simulation.template_file}.object"
    
    if not base_object_path.exists():
        logging.error(f"Error: Object file {base_object_path} does not exist.")
        sys.exit(1)
    
    with open(base_txrx_file_name) as infile:
        txrxFile = TxRxFile.from_file(infile)
    logging.info(f'Opened file with transmitters and receivers: {base_txrx_file_name}')
    
    x3d_xml_file = X3dXmlFile3_3(base_x3d_xml_path)
    antenna = txrxFile[cfg.base_files_names.insite_rx_name].location_list[0]
    
    run_path = process_step(step, positions, rotations, base_object_path, results_dir,
                    cfg.simulation.width_vehicle, antenna, x3d_xml_file,
                    txrxFile, cfg.base_files_names.insite_rx_name,
                    "./remcom__rxapi__Job/Scene/remcom__rxapi__Scene/TxRxSetList/"
                    "remcom__rxapi__TxRxSetList/TxRxSet/remcom__rxapi__PointSet/"
                    "OutputID/remcom__rxapi__Integer[@Value='2']/../../ControlPoints/"
                    "remcom__rxapi__ProjectedPointList")

    run_simulation(cfg, run_path)
    
    if gen_database(run_path,step):          #Create db if the receivers have rays information

        hdf5_rayInfo = gen_rays_dataset(run_path,step,cfg) #Create hdf5
        gen_beam_output_file(run_path,step,cfg, hdf5_rayInfo) #Create beam output file

    else:
        if run_path.exists():
            try:
                shutil.rmtree(run_path)
            except OSError as e:
                logging.error(f"Error removing run directory {run_path}: {e}")
                sys.exit(1)
        logging.warning(f"No rays information found for the receivers in scene {step}. Skipping database and dataset generation.")
if __name__ == "__main__":
    main()