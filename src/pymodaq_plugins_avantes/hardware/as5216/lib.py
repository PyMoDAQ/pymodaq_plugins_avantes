# -*- coding: utf-8 -*-
"""
Created the 11/12/2022

@author: Sebastien Weber
"""
from . import consts
from .errors import Error
import ctypes
import numpy as np
import time
from pathlib import Path


dll = ctypes.WinDLL(r'C:\Program Files\AS5216x64-DLL_2.3\examples\Vcpp2008\as5216x64.dll')


class AvsIdentityType(ctypes.Structure):
    _fields_ = [('SerialNumber', ctypes.c_char * consts.AVS_SERIAL_LEN),
               ('UserFriendlyName', ctypes.c_char * consts.USER_ID_LEN),
               ('Status', ctypes.c_char)]


SensorType = ctypes.c_uint8


class ControlSettingsType(ctypes.Structure):
    _fields_ = [('m_StrobeControl', ctypes.c_uint16),
                ('m_LaserDelay', ctypes.c_uint32),
                ('m_LaserWidth', ctypes.c_uint32),
                ('m_LaserWaveLength', ctypes.c_float),
                ('m_StoreToRam', ctypes.c_uint16),]


class DarkCorrectionType(ctypes.Structure):
    _fields_ = [('m_Enable', ctypes.c_uint8),
                ('m_ForgetPercentage', ctypes.c_uint8),]


class DetectorType(ctypes.Structure):
    _fields_ = [('m_SensorType', SensorType),
                ('m_NrPixels', ctypes.c_uint16),
                ('m_aFit', ctypes.c_float * consts.NR_WAVELEN_POL_COEF),
                ('m_NLEnable', ctypes.c_bool),
                ('m_aNLCorrect', ctypes.c_double * consts.NR_NONLIN_POL_COEF),
                ('m_aLowNLCounts', ctypes.c_double),
                ('m_aHighNLCounts', ctypes.c_double),
                ('m_Gain', ctypes.c_float * consts.MAX_VIDEO_CHANNELS),
                ('m_Reserved', ctypes.c_float),
                ('m_Offset', ctypes.c_float * consts.MAX_VIDEO_CHANNELS),
                ('m_ExtOffset', ctypes.c_float),
                ('m_DefectivePixels', ctypes.c_uint16 * consts.NR_DEFECTIVE_PIXELS),
                ]


class SmoothingType(ctypes.Structure):
    _fields_ = [('m_SmoothPix', ctypes.c_uint16),
                ('m_SmoothModel', ctypes.c_uint8),]



class SpectrumCalibrationType(ctypes.Structure):
    _field_ = [('m_Smoothing', SmoothingType),
               ('m_CalInttime', ctypes.c_float),
               ('m_aCalibConvers', ctypes.c_float * consts.MAX_NR_PIXELS),]


class IrradianceType(ctypes.Structure):
    _field_ = [('m_IntensityCalib', SpectrumCalibrationType),
               ('m_CalibrationType', ctypes.c_uint8),
               ('m_FiberDiameter', ctypes.c_uint32),]


class TriggerType(ctypes.Structure):
    _fields_ = [('m_Mode', ctypes.c_uint8),
                ('m_Source', ctypes.c_uint8),
                ('m_SourceType', ctypes.c_uint8),]


class MeasConfigType(ctypes.Structure):
    _fields_ = [('m_StartPixel', ctypes.c_uint16),
                ('m_StopPixel', ctypes.c_uint16),
                ('m_IntegrationTime', ctypes.c_float),
                ('m_IntegrationDelay', ctypes.c_uint32),
                ('m_NrAverages', ctypes.c_uint32),
                ('m_CorDynDark', DarkCorrectionType),
                ('m_Smoothing', SmoothingType),
                ('m_SaturationDetection', ctypes.c_uint8),
                ('m_Trigger', TriggerType),
                ('m_Control', ControlSettingsType),]


class AvaSpecLib:

    def __init__(self):
        self._handle = None
        self._n_pxls = None

    @staticmethod
    def init(port: int = 0):
        port = ctypes.c_short(port)
        ret = dll.AVS_Init(port)
        print(ret)
        return ret

    @staticmethod
    def done():
        ret = dll.AVS_Done()
        print(ret)
        ret

    @staticmethod
    def n_devices():
        ret = dll.AVS_GetNrOfDevices()
        print(ret)
        ret

    @staticmethod
    def get_list():
        list_size = ctypes.c_uint(256)
        required_size = ctypes.c_uint(1 * ctypes.sizeof(AvsIdentityType))
        id_list = AvsIdentityType()
        ret = dll.AVS_GetList(list_size,
                              ctypes.byref(required_size),
                              ctypes.byref(id_list))
        print(ret)
        return id_list

    def activate(self):
        id = self.get_list()

        ret = dll.AVS_Activate(ctypes.byref(id))
        print(ret)
        if ret != 1000:
            self._handle = ret
        return ret

    def deactivate(self):
        if self._handle is not None:
            dll.AVS_Deactivate(self._handle)

    def prepare_measure(self, start:int = 1, stop: int = 1024,
                        integration_time: float = 10., integration_delay: int = 0,
                        n_average: int = 1, ):
        """
        ('m_StartPixel', ctypes.c_uint16),
        ('m_StopPixel', ctypes.c_uint16),
        ('m_IntegrationTime', ctypes.c_float),
        ('m_IntegrationDelay', ctypes.c_uint32),
        ('m_NrAverages', ctypes.c_uint32),
        ('m_CorDynDark', DarkCorrectionType),
        ('m_Smoothing', SmoothingType),
        ('m_SaturationDetection', ctypes.c_uint8),
        ('m_Trigger', TriggerType),
        ('m_Control', ControlSettingsType),
        """
        measconfigtype = MeasConfigType(ctypes.c_uint16(start), ctypes.c_uint16(stop),
                                        ctypes.c_float(integration_time), ctypes.c_uint32(integration_delay),
                                        ctypes.c_uint32(n_average))
        err = None
        if self._handle is not None:
            ret = dll.AVS_PrepareMeasure(self._handle, ctypes.byref(measconfigtype))
            err = Error(ret).name
        return err

    def measure(self, n_measure=1):
        err = None
        if self._handle is not None:
            ret = dll.AVS_Measure(self._handle, None, ctypes.c_short(n_measure))
            err = Error(ret).name
        return err

    def get_lambda(self):
        err = None
        if self._handle is not None:
            data = np.zeros((self.get_n_pixels(), ), dtype=float)
            ret = dll.AVS_GetLambda(self._handle, data.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
            err = Error(ret).name
            if err == 'ERR_SUCCESS':
                return data
        return err

    def get_n_pixels(self):
        err = None
        if self._handle is not None:
            data = ctypes.c_short()
            ret = dll.AVS_GetNumPixels(self._handle, ctypes.byref(data))
            err = Error(ret).name
            if err == 'ERR_SUCCESS':
                self._n_pxls = data.value
                return data.value
        return err

    def poll(self):
        if self._handle is not None:
            return bool(dll.AVS_PollScan(self._handle))
        return False

    def get_data(self):
        err = None
        if self._handle is not None:
            time_label = ctypes.c_int()
            data = np.zeros((self.get_n_pixels(),), dtype=float)
            ret = dll.AVS_GetScopeData(self._handle, ctypes.byref(time_label),
                                       data.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
            err = Error(ret).name
            if err == 'ERR_SUCCESS':
                return data
        return err

    def get_info(self):
        err = None
        if self._handle is not None:
            fpga = ctypes.create_string_buffer(16)
            firmware = ctypes.create_string_buffer(16)
            dll_version = ctypes.create_string_buffer(16)
            ret = dll.AVS_GetVersionInfo(self._handle, ctypes.byref(fpga),
                                         ctypes.byref(firmware),
                                         ctypes.byref(dll_version))
            err = Error(ret).name
            if err == 'ERR_SUCCESS':
                return fpga.value.decode(), firmware.value.decode(), dll_version.value.decode()
        return err


if __name__ == '__main__':
    ava = AvaSpecLib()
    nspectro = ava.init()
    ndevices = ava.n_devices()
    device_info = ava.get_list()
    handle = ava.activate()
    print(ava.get_info())
    n_pxls = ava.get_n_pixels()
    wavelength = ava.get_lambda()
    ret = ava.prepare_measure()
    ret = ava.measure(1)
    timeout = 10
    start = time.perf_counter()
    while not ava.poll():
        time.sleep(0.01)
        if time.perf_counter() - start > timeout:
            break
    data = ava.get_data()
    ava.deactivate()
    release = ava.done()