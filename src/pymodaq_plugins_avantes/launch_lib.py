# -*- coding: utf-8 -*-
"""
Created the 12/12/2022

@author: Sebastien Weber
"""
import time

from pymodaq_plugins_avantes.hardware.as5216.lib import AvaSpecLib


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