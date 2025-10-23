import numpy as np
from qtpy.QtCore import Signal
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport, DataRaw
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, \
    comon_parameters, main
from pymodaq.utils.parameter import Parameter
from pymodaq_plugins_avantes.hardware.AvaSpec_ULS2048CL_EVO_Controller \
    import AvantesController


class DAQ_1DViewer_Avantes(DAQ_Viewer_base):
    """ Avantes Spectrometer Instrument plugin class for a 1D viewer.
    Besides acquiring spectral data, the Avantes device may control ten digital
    output lines. They are exposed to PyMoDAQ as parameters. Acquisition on
    digital and analog input lines is not yet supported.
    """

    # define controller type for easy autocompletion
    controller_type = AvantesController

    params = comon_parameters+[
        {'title': 'Integration time:', 'name': 'integration_time',
         'type': 'float', 'min': 0.001, 'value': 0.1,
         'tip': 'Integration time in seconds'},
    ] + [ {'title': 'Output %d:' % (i + 1), 'name': 'output_%d' % (i + 1),
           'type': 'led_push', 'value': False,
           'tip': 'Logic level on putput %d' % (i + 1) } \
          for i in range(10)
         ]

    def ini_attributes(self):
        self.controller: self.controller_type = None
        self.x_axis = None

    def commit_settings(self, param: Parameter):
        if param.name() == "integration_time":
            self.controller.set_integration_time(param.value() * 1000)
        elif param.name()[:7] == 'output_':
            # Note: digital outputs are not really parameters. However and
            # for the time being, this seems to come closest to PyMoDAQ's
            # functionallity.
            self.controller.set_digital_output(int(param.name()[7:]),
                                               param.value())

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only 
            one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        self.ini_detector_init(slave_controller=controller)

        if self.is_master:
            self.controller = self.controller_type()
            if self.controller.open_communication():
                info = "Avantes Spectro initilialized"
            else:
                info = "No Avantes Spectro detected"
                return info, False

            wavelengths = self.controller.wavelengths
            self.x_axis = Axis(label='Wavelength', units='nm',
                                data=wavelengths, index=0)
            dfp = DataFromPlugins(name='Avantes',
                                  data=[np.zeros(len(wavelengths))],
                                  dim='Data1D', axes=[self.x_axis],
                                  labels=['Avantes-Signal'])
            self.dte_signal_temp.emit(DataToExport(name='Avantes', data=[dfp]))
            self.controller.set_default_config()
        else:
            self.controller = controller

        initialized = True

        return info, initialized

    def close(self):
        """Terminate the communication protocol"""

        self.controller.close_communication()
        initialized = False

        return initialized

    def grab_data(self, Naverage=1, **kwargs):
        """Start grabbing from the detector
        Use a synchrone acquisition (blocking function)

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging.
        """

        data,timestamp = self.controller.grab_spectrum()

        dwa0D_timestamp = \
            DataRaw('timestamp', units='dimensionless',
                    data=np.array([timestamp]))

        dfp = DataFromPlugins(name='Avantes', data=data, dim='Data1D',
                              labels=['data'], axes=[self.x_axis])
        self.dte_signal.emit(DataToExport(name='spectrum',
                                          data=[dfp, dwa0D_timestamp]))
 
    def stop(self):
        self.controller.abort_measurement()

    def has_dark_shutter(self):
        return False

    def has_reference_shutter(self):
        return False

if __name__ == '__main__':
    main(__file__)
