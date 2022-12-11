# -*- coding: utf-8 -*-
"""
Created the 11/12/2022

@author: Sebastien Weber
"""
from enum import Enum


class Error(Enum):
    ERR_SUCCESS                   = 0
    ERR_INVALID_PARAMETER         = -1
    ERR_OPERATION_NOT_SUPPORTED   = -2
    ERR_DEVICE_NOT_FOUND          = -3
    ERR_INVALID_DEVICE_ID         = -4
    ERR_OPERATION_PENDING         = -5
    ERR_TIMEOUT                   = -6
    ERR_INVALID_PASSWORD          = -7
    ERR_INVALID_MEAS_DATA         = -8
    ERR_INVALID_SIZE              = -9
    ERR_INVALID_PIXEL_RANGE       = -10
    ERR_INVALID_INT_TIME          = -11
    ERR_INVALID_COMBINATION       = -12
    ERR_INVALID_CONFIGURATION     = -13
    ERR_NO_MEAS_BUFFER_AVAIL      = -14
    ERR_UNKNOWN                   = -15
    ERR_COMMUNICATION             = -16
    ERR_NO_SPECTRA_IN_RAM         = -17
    ERR_INVALID_DLL_VERSION       = -18
    ERR_NO_MEMORY                 = -19
    ERR_DLL_INITIALISATION        = -20
    ERR_INVALID_STATE             = -21
    
#    // Return error codes DeviceData check
    ERR_INVALID_PARAMETER_NR_PIXELS   = -100
    ERR_INVALID_PARAMETER_ADC_GAIN    = -101
    ERR_INVALID_PARAMETER_ADC_OFFSET  = -102
    
#    // Return error codes PrepareMeasurement check
    ERR_INVALID_MEASPARAM_AVG_SAT2    = -110
    ERR_INVALID_MEASPARAM_AVG_RAM     = -111
    ERR_INVALID_MEASPARAM_SYNC_RAM    = -112
    ERR_INVALID_MEASPARAM_LEVEL_RAM   = -113
    ERR_INVALID_MEASPARAM_SAT2_RAM    = -114
    ERR_INVALID_MEASPARAM_FWVER_RAM   = -115 #//StoreToRAM in 0.20.0.0 and later
    ERR_INVALID_MEASPARAM_DYNDARK     = -116
    
 #   // Return error codes SetSensitivityMode check
    ERR_NOT_SUPPORTED_BY_SENSOR_TYPE  = -120
    ERR_NOT_SUPPORTED_BY_FW_VER       = -121
    ERR_NOT_SUPPORTED_BY_FPGA_VER     = -122
    
    UNCONFIGURED_DEVICE_OFFSET    = 256
    INVALID_AVS_HANDLE_VALUE     = 1000