import subprocess
import logging
import os
import shutil
import json
import attrdict

def add_opt(opt, formatter):
    if opt is not None:
        return formatter.format(opt=opt)
    else:
        return ''

class InSiteProject:
    
    '''
    Pedro had a constructor in class InSiteProject that would keep the same files for running all simulations.
    Better to first copy the files to the run folder and then invoke from there.
    def __init__(self, setup_path, xml_path, output_dir, project_name='model', calcprop_bin=CALCPROP_BIN,
                 wibatch_bin=None):
        """InSite project
        :param setup_path: path to the .setup file
        :param xml_path: path to the X3D xml path
        :param output_dir: where the .setup will store the results (normally the Study Area name)
        :param calcprop_bin: the path to InSite's calcprop binary
        """
        self._setup_path = setup_path
        self._xml_path = xml_path
        self._output_dir = output_dir
        self._project_name = project_name
        self._calcprop_bin = calcprop_bin
        self._wibatch_bin = wibatch_bin
    '''

    def __init__(self, project_name='model'):
        """InSite project
        :param calcprop_bin: the path to InSite's calcprop binary
        """
        self._project_name = project_name
        


    def run_x3d(self, xml_path, output_dir,wibatch_bin):
        '''
        :param setup_path: path to the .setup file
        :param xml_path: path to the X3D xml path
        :param output_dir: where the .setup will store the results (normally the Study Area name)
        '''
        cmd = ''
        cmd += wibatch_bin
        cmd += add_opt(output_dir, ' -out {opt}')
        cmd += add_opt(xml_path, ' -f {opt}')
        cmd += add_opt(self._project_name, ' -p {opt}')
        logging.info('Running CMD: "{}"'.format(cmd))
        subprocess.run(cmd, shell=True, check=True)


if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'NewYork', 'model.setup')
    project_output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                      'NewYork', 'study')
    output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              'Results')
    project = InSiteProject()
    
    xml_full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 'NewYork', 'model.study.xml')

    with open("config.json","r") as f:
        cfg=attrdict.AttrDict(json.load(f))

    locale = 'LC_CTYPE=en_US.UTF-8 LC_NUMERIC=en_US.UTF-8 LC_TIME=en_US.UTF-8 '

    wibatch_bin = (locale + '{} '.format(cfg.insite_paths.REMCOMINC_LICENSE_FILE) +
               'LD_LIBRARY_PATH={}/OpenMPI/1.4.4/Linux-x86_64RHEL6/lib/ '.format(cfg.insite_paths.insite_software_path) +
               '{}/WirelessInSite/3.3.0.4/Linux-x86_64RHEL6/bin/wibatch'.format(cfg.insite_paths.insite_software_path))

    project.run_x3d(xml_full_path,project_output_dir,wibatch_bin)