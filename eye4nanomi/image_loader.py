import os
import os.path as path
from logging import getLogger

import numpy as np

from panta_rhei.image_io import dm3reader_v3 as dm3
from panta_rhei.image_io import serReader as tia
from panta_rhei.image_io import mrcReader as mrc
from panta_rhei.image_io import dm4reader as dm4

from panta_rhei.gui.metadata_utils import convert_old_metadata

from panta_rhei.gui.calibration import DefaultCalibration
from panta_rhei.gui.calibration_rules import get_pixel_factor

import json

import glob
"""
This module contains functions to load data in many formats
from files.


Public functions:
* load_from_file(): The main access point for loading data
                  in all available formats.
* load_image: DEPRECATED, replaced by load_from_file().
* load_npz_with_data_model(): Additionally return data model info.

* make_meta_data(): Create default meta data (used in scan-procedures).
* mk_RBGA()
"""


class ImportException(Exception):
    pass


def make_meta_data(nda, name=None):
    return _create_default_meta_data(data=nda, filename=name)


def load_from_file(filepath: str, params: dict = None,
                   as_plot: bool = False, force_file_type: str = None):
    """
    Load data from file.

    The file format is guessed from the file extension,
    unless this guess is manually overwritten by defining
    `force_file_type`.

    :param filepath: The file path to the file which contains
        the data to be loaded.

    :param params: Optional arguments to be passed to the
        load methods.
    :param as_plot: If True, consider loaded data to be 1D data,
        if type is not explicitly defined in meta data.
    :param force_file_type: If not None, the data to be
        loaded is expected to be in this format.
        The file extension is ignored in this case.

    :return A tuple of (ndarray, meta_data: dict)
    """
    if params is None:
        data, meta = _load_data(filepath, force_file_type=force_file_type)
    else:
        data, meta = _load_data(filepath, force_file_type=force_file_type,
                                **params)

    if len(data.shape) == 1:
        data.reshape((1, data.shape[0]))

    # Create default meta data for the loaded data,
    # passed metadata will be merged with default meta data.
    if data is not None:
        if type(filepath) != type('str'):
            result_meta_data = _create_default_meta_data(data, metadata=meta,
                                                     as_plot=as_plot)
        else:
            result_meta_data = _create_default_meta_data(data, metadata=meta,
                                                     filename=filepath,
                                                     as_plot=as_plot)
    else:
        result_meta_data = meta
    return data, result_meta_data


def load_image(filepath, params=None, as_plot=None, force_raw=False):
    getLogger(__name__).warn("'load_image() is DEPRECATED. "
                             "Please use 'load_from_file()'  instead.")
    if force_raw:
        force_file_type = 'raw'
    else:
        force_file_type = None
    return load_from_file(filepath, params=params, as_plot=as_plot,
                          force_file_type=force_file_type)


def load_npz_with_data_model(fname, **kwargs):
    """
    Load a file in .prz format and return data, metadata and data model info.

    If data model is a group, meta data is returned as a list of dicts,
    otherwise as single dict.
    :param fname: The filename
    :return data: ndarray, metadata: dict or list of dicts, data_model_info:dict
    """
    data = None
    metadata = {}
    data_model_input = None
    with np.load(fname, allow_pickle=True) as npzdata:
        squeeze_data = True
        # Squeezing the data is needed to load older versions
        # of npz/prz-files, in which the structure of the data was
        # different.
        # In current versions of prz files squeezing is not allowed,
        # because data lists with one item are allowed
        # (for group data models).
        # Whether the currently loaded npz file is 'old' or 'new'
        # is determined with help of 'file_format_version' which
        # was introduced in the same PR version as the export function
        # for group data models.

        if 'file_format_version' in npzdata:
            squeeze_data = False
        # load image data
        # Use try/except to avoid calling `if 'data' in npzdata`
        # (which may be very time consuming if data is large).

        data = npzdata['data']
        # Don't squeeze data with dim=2
        # Otherwise plot data with only one line would be squeezed,
        # which causes undefined behaviour.
        if squeeze_data and len(data.shape) > 2:
            # Squeezing is only done for backward compatibility.
            # (There had been some PR versions which stored
            # the npz wrongly with dim+1)
            data = np.squeeze(data)

        # load data-model input
        # `data_model_input` is a Dictionary which includes the parameters of the DataModel
        data_model_input = npzdata['data_model'][0] \
                           if 'data_model' in npzdata else None
        # load meta data
        if data_model_input.get('is_group', False):
            # return list of meta data
            metadata = npzdata['meta_data']
        else:
            # Return only one meta data set
            metadata = npzdata['meta_data'][0] \
                       if 'meta_data' in npzdata else None

        # If input is a group, data and metadata are lists
        if data_model_input and data_model_input.get('is_group', False):
            new_meta_data = []
            for m, d in zip(metadata, data):
                m = _create_default_meta_data(d, metadata=m,
                                             filename=fname)
                m = convert_old_metadata(m, d.shape)
                new_meta_data.append(m)
            metadata = new_meta_data
        else:
            metadata = _create_default_meta_data(data,
                                                 metadata=metadata,
                                                 filename=fname)
            metadata = convert_old_metadata(metadata, data.shape)

        return data, metadata, data_model_input


def mk_RGBA(img):
    # for RGB(A) images, data shape will be (row, col, 3|4)
    rows, cols, depth = img.shape
    # channel indices in the image array
    RED, GREEN, BLUE, ALPHA = 0, 1, 2, 3

    # extract alpha channel (if any)
    if depth == 3:
        a = np.full((rows,cols), 0xFF, dtype=np.uint8)
    else:
        a = img[:,:, ALPHA]

    r = img[:,:, RED]
    g = img[:,:, GREEN]
    b = img[:,:, BLUE]

    # FIXME: this is specific for Little Endian (INTEL)
    imgType = 'ARGB'
    argb = np.stack([b, g, r, a], axis=2)
    # TODO: Explain this vvv
    img = argb.view(dtype=np.uint32).reshape((rows,cols))

    return img, imgType

def _get_default_calibration():
    """
    return a default calibration as dict.

    Defaults are:
    value: 1.0
    unit: empty string
    offset: 0.0
    pixel_factor = 1
    """
    return DefaultCalibration().as_dict()

def _load_mrc(mrcname, **kwargs):
    mrcdata = mrc.mrcReader(mrcname)

    if len(mrcdata)>1:
        img = np.stack(mrcdata)
    else:
        img = mrcdata[0]
    cx, cy, cz = mrcdata.pixel_spacing

    calibs = []
    calib_x = _get_default_calibration()
    calib_y = _get_default_calibration()

    calib_x['value'] = cx
    calib_y['value'] = cy

    calib_x['offset'] = 0.0
    calib_y['offset'] = 0.0
    calibs.append(calib_x)
    calibs.append(calib_y)
    t = '2D'
    if len(img.shape) > 2:
        calib_z = _get_default_calibration()
        calib_z['value'] = cz
        calibs.append(calib_z)
        t = 'Stack'

    meta = {'inherited.calib': calibs, 'type': t}
    getLogger(__name__).info('loaded MRC data with dtype = {} and shape = {}'.format(img.dtype, img.shape))
    return img, meta;

def _load_tia(sername,  **kwargs):
    serdata = tia.serReader(sername)
    img = serdata['imageData']

    meta = {}
    getLogger(__name__).info('loaded SER data with dtype = {} and shape = {}'.format(img.dtype, img.shape))
    return img, meta;

def _load_pgm(filename, **kwargs):
    """
    Read an grayscale pgm text file.

    we assume plain PGM 'P2' with pixel values given by whitespace separated ascii numbers
    more common is raw PGM 'P5' with pixel values a continuous uint8/uint16 binary block (FIXME)

    :param filename: name of the file to read
    :return: numpy array
    """
    header_lines = 3
    with open(filename, 'rb' ) as f:
        file_type = f.readline().strip().decode()
        assert file_type in ('P2','P5'), 'Unsupported file type'
        # skip comments
        line = f.readline()
        while line.strip().startswith(b'#'):
            header_lines += 1
            line = f.readline()
        width = int(line.split()[0])
        height = int(line.split()[1])
        maxval = int(f.readline())
        if maxval > 255:
            dtype = np.uint16
        else:
            dtype = np.uint8
        if file_type == 'P5':
            # format: one image in raw pgm (format allows for multiple images)
            # also check for bit-depth by hand as imagej can't be trusted to use the correct one
            array = np.frombuffer(f.read(),  dtype=np.uint8)
            nbytes = array.size//(width*height)
            if nbytes == 1:
                dtype = np.uint8
            elif nbytes == 2:
                dtype = np.uint16
            else:
                raise TypeError('Could not detect bit depth')
            # now correct bit depth and reshape
            array = array.view(dtype).reshape((width, height))
    if file_type == 'P2':
        # format: one image in native pgm
        array = np.loadtxt(filename, skiprows=header_lines, dtype=dtype)
    meta = _create_default_meta_data(array, filename=filename)
    return array.reshape((int(height), int(width))), meta


def _load_tiff(name, colors='argb', **kwargs):
    from tifffile import imread, TiffFile

    img = imread(name)

    # Obtain original type to determine whether this
    # is an ARGB image or a stack of images.

    orig_type = '2D'
    nr_tiff_pages = None
    with TiffFile(name) as tif:
        nr_tiff_pages = len(tif.pages)
        if "ImageDescription" in tif.pages[0].tags:
            try:
                img_description_str = tif.pages[0].tags["ImageDescription"].value
                ceos_meta = json.loads(img_description_str)
                orig_type = ceos_meta.get('type', '2D')
            except ValueError:
                # This .tiff-file was not created by PR
                pass

    # Force stack import
    if ((orig_type == 'Stack') or (nr_tiff_pages > 1)):
        colors = 'stack'

    imgType = None
    if colors == 'stack' and len(img.shape) == 3 and img.shape[2] in (3, 4):
        img = np.transpose(img, (2, 0, 1))
        imgType = 'Stack'
    elif colors == 'argb' and len(img.shape) > 2:
        img, imgType = mk_RGBA(img)
    meta = _create_default_meta_data(img, filename=name)
    if imgType is not None:
        meta['type'] = imgType

    with TiffFile(name) as tif:
        if "ImageDescription" in tif.pages[0].tags:
            img_description_str = tif.pages[0].tags["ImageDescription"].value
            try:
                ceos_meta = json.loads(img_description_str)
                for k in ceos_meta:
                    if k in meta:
                        if isinstance(meta[k], list):
                            ceos_meta[k] = tuple(ceos_meta[k])
                for k in ceos_meta:
                    if k in meta:
                        meta['orig-'+k] = meta[k]
                    meta[k] = ceos_meta[k]
            except ValueError:
                meta = _create_default_meta_data(img, filename=name)
                if img_description_str is not None and img_description_str !='META':
                    meta['description'] = img_description_str
        elif hasattr(tif, 'tvips_metadata') and isinstance(tif.tvips_metadata, dict):
            for k in tif.tvips_metadata:
                meta['tvips.'+k] = tif.tvips_metadata[k]
    getLogger(__name__).info('loaded TIFF data dtype: {} shape: {} meta: {}'
             .format(img.dtype, img.shape, meta))

    return img, meta

def _load_pil(name, colors='argb', **kwargs):
    """
    load many image formats as ndarray (using PIL/pillow)
    """
    from PIL import Image
    print("load_pil_ address:", name)
    # PIL (pillow) reads many image formats: png, jpg, gif, ...
    pil_img = Image.open(name)
    if pil_img.mode == 'P':
        # GIF is always read as palette mode
        pil_img = pil_img.convert('RGB')
    # PIL.Image implements the array_interface
    img = np.array(pil_img)
    imgType = '2D'
    # for rgb(a) data shape will be (r,c,3|4), in this case return a stack
    if len(img.shape) > 2:
        if colors=='stack':
            img = np.transpose(img,(2,0,1))
            imgType = 'Stack'
        elif colors=='argb':
            img, imgType = mk_RGBA(img)

    if type(name) != type('str'):
        meta = _create_default_meta_data(img)
    else:
        meta = _create_default_meta_data(img, filename=name)
    meta['type'] = imgType
    getLogger(__name__).info('loaded PIL data dtype: {} shape: {} meta: {}'
             .format(img.dtype, img.shape, meta))
    pil_img.close()
    return img, meta

def _load_gif(name, colors='argb', **kwargs):
    """
    load many image formats as ndarray (using PIL/pillow)
    """
    from PIL import Image
    # PIL (pillow) reads many image formats: png, jpg, gif, ...
    pil_img = Image.open(name)
    n_frames = pil_img.n_frames
    if pil_img.n_frames == 1:
        data, meta = _load_pil(name, colors=colors, **kwargs)
    else:
        shape = *np.flip(pil_img.size), n_frames
        # GIF frame 1 is always read as palette mode
        data = np.zeros(shape, dtype = np.uint32)
        for i in range(n_frames):
            pil_img.seek(i)
            cimg = np.array(pil_img.convert('RGB'))
            # PIL.Image implements the array_interface
            img, imgType = mk_RGBA(cimg)
            data[:,:,i] = img
        if type(name) != type('str'):
            meta = _create_default_meta_data(img)
        else:
            meta = _create_default_meta_data(img, filename=name)
        meta['type'] = 'Stack'#imgType
        meta['display_axes'] = (1,0)
        getLogger(__name__).info('loaded PIL data dtype: {} shape: {} meta: {}'
                                 .format(img.dtype, img.shape, meta))
    print('loaded gif with shape: {}'.format(data.shape))
    return data, meta

def _load_fff(name, **kwargs):
    from panta_rhei.image_io.tvips_tools import read_header
    tvips_meta = read_header(name, include_metadata=True)
    slices, rows, cols = tvips_meta['ZDim'], tvips_meta['YDim'], tvips_meta['XDim']
    slices = max(slices, 1); rows = max(rows, 1); cols = max(cols, 1)
    nda, meta = _load_raw(name,
                          dtype=np.uint16,
                          rows=rows, cols=cols,
                          slices=slices, header=512,
                          **kwargs)
    for k in tvips_meta:
        meta['tvips.'+k] = tvips_meta[k]

    return nda, meta


def _load_raw(rawname, dtype=np.int16, rows=None, cols=None, slices=1, header=0, subheader=0, subfooter=0, **kwargs):
    if slices is None:
        slices = 1
    len_dtype = np.dtype(dtype=dtype).itemsize  # determine number of bytes of dtype
    with open(rawname, "rb") as f:
        size = os.path.getsize(rawname)  # this is now the bytesize of the file

        # calculate size of a single image in pixels
        img_size = int((size - (header + slices*(subheader + subfooter))) / len_dtype)

        if rows is None and cols is None:
            # If no number of rows and cols are given,
            # assume that the image is quadratic.
            cols = rows = int(np.sqrt(img_size))
        else:
            if cols is None:
                cols = img_size // rows
            if rows is None:
                rows = img_size // cols

        # create array to find starting point of each image in the file
        offset_array = _create_offset_array(slices, (rows*cols*len_dtype), header, subheader, subfooter)
        stack = np.zeros((slices, rows, cols), dtype=dtype)

        if size != (slices*rows*cols*len_dtype) + header + (slices * (subheader + subfooter)):
            getLogger(__name__).error('while reading <{}> size {} does not match shape {}x{}x{}'.
                      format(rawname, size, slices, rows, cols))
        for kk in range(0, slices):
            f.seek(offset_array[kk], 0)
            values = rows * cols
            dataValues = np.fromfile(f, dtype=dtype, count=values)
            dataValues = dataValues.reshape((rows, cols))

            stack[kk, :, :, ] = dataValues

        # remove redundant dimensions from final image
        stack = np.squeeze(stack)
        meta = _create_default_meta_data(stack, filename=rawname)
        getLogger(__name__).info('loaded RAW data with dtype = {} and shape = {}'.format(stack.dtype, stack.shape))

        return stack, meta


def _load_hspy(name):
    """
    Load hyperspy file (experimental).

    :param name: file name
    """
    import h5py

    def flip_energy_axes(axis_info, data):
        """
        If an axis labelled with 'Energy' is found in axis info, flip the data of this axis.

        :return tuple of (flipped_axes, data)
            flipped_axes: a list of indices of flipped axes.
            data: the data with the flipped axes.

        """
        flipped_axes = []
        for i in axes_info:
            axis_label = axes_info[i]['name']
            if axis_label == 'Energy':
                data = np.flip(data, i)
                flipped_axes.append(i)
        return flipped_axes, data

    def get_metadata_from_axes_info(axes_info, pixel_factors, flipped_axes):
        """
        Return a dict with meta data obtained from the passed axes info.

        :param axes_info: A list of dicts containing axis information.
            The list is sorted by the axis index.
            Each item in the list refers to one axis.
        :param pixel_factors: A list of pixel factors.
            If the .hspy-file to be imported was originally exported by PR,
            the pixel factor will be re-created from meta data
            when calibration rules are applied.
            So, the pixel factor must be taken into
            account when importing calibrations from the
            hspy-axis-information.

        """
        axis_name_to_content_type = {'Energy loss': 'Energy'}
        nr_axes = len(axes_info)
        imported_calibs = [None] * nr_axes
        content_types = [None] * nr_axes
        navigate_axes = [None] * nr_axes
        for i in axes_info:
            # Add content types if axes names are known.
            axis_info = axes_info[i]
            axis_label = None
            if 'name' in axis_info: # name is not always present
                axis_label = axis_info['name']

            if axis_label in axis_name_to_content_type:
                content_types[i] = axis_name_to_content_type[axis_label]

            imported_calib_dict = {'scale': None,
                                   'offset': None,
                                   'units': None}
            for key in ('scale', 'offset', 'units'):
                if key in axis_info:
                    imported_calib_dict[key] = axis_info[key]
            # If any part of a calibration is given
            # -> Create a default calibration and
            # set all available information.
            if any([v for k, v in imported_calib_dict.items()]):

                # TODO: pixel factor???
                calib = DefaultCalibration()

                if imported_calib_dict['scale'] is not None:
                    calib.value = imported_calib_dict['scale']
                    # Apply pixel factor as calculated from meta data.
                    if pixel_factors:
                        calib.value /= pixel_factors[i]
                if imported_calib_dict['offset'] is not None:
                    calib.offset = imported_calib_dict['offset']
                    if i in flipped_axes:
                        if ('size' in axis_info) and ('scale' in imported_calib_dict):
                            imported_offset = imported_calib_dict['offset']
                            scaled_size = (axis_info['size'] - 1) * imported_calib_dict['scale']
                            calib.offset = - imported_offset - scaled_size

                    # PR expects offset in image pixels
                    # not in calibrated values.
                    calib.offset = calib.offset / calib.value
                if imported_calib_dict['units'] is not None:
                    imported_unit = imported_calib_dict['units']
                    # unit may be in SI unit *with* prefix
                    allowed_base_units = ['m', 'A', 'V', 'rad', 's', 'eV']
                    calib.value, calib.unit = _guess_from_unit(
                        calib.value, imported_unit,
                        allowed_base_units=allowed_base_units)
                    if calib.unit in allowed_base_units:
                        calib.use_prefix = True

                imported_calibs[i] = calib.as_dict()
            # Get information whether axis is navigate axis
            # (which means 'display axis' in our terms).
            if 'navigate' in axis_info:
                navigate_axes[i] = axis_info['navigate']
            display_axes = [i for i, is_display
                            in enumerate(navigate_axes) if is_display]
        axes_meta_data = {}
        # Calibrations and content types must be in reversed order,
        # because hyperspy uses numpy order,
        # while PR expects image order.
        if any(imported_calibs):
            axes_meta_data['inherited.calib'] = imported_calibs[::-1]
        if any(content_types):
            axes_meta_data['content.types'] = content_types[::-1]
        if display_axes:
            # Only add display axes tag, if not all axes are displayed
            # (which means that data is 3D or 4D data).
            # If only one display axis is defined, ignore it,
            # because using plots as navigation tool for cubes
            # is currently not supported.
            if nr_axes > len(display_axes) and len(display_axes) > 1:
                axes_meta_data['display_axes'] = tuple(display_axes[::-1])

        return axes_meta_data

    with h5py.File(name, 'r') as hspy_data:

        experiments = hspy_data['Experiments']
        if len(experiments) < 1:
            getLogger(__name__).warn(
                "Could not load {}. "
                "File seems to contain no data.".format(name))
            return
        # Get arbitrarily first dataset.
        # Loading multiple data sets is currently not supported.
        for experiment_name in experiments:
            experiment = experiments[experiment_name]
            # break after first, ignore more data sets
            break
        dataset = None
        axes_data = []
        original_metadata = None
        imported_metadata = None
        for item_name in experiment:
            item = experiment[item_name]
            # We assume that there is only one dataset per experiment
            if isinstance(item, h5py._hl.dataset.Dataset):
                dataset = item
            else:
                if item_name.startswith('axis-'):
                    _, axis_index = item_name.split('-')
                    axes_data.append((axis_index, item))
                if item_name == 'original_metadata':
                    original_metadata = item
                if item_name == 'metadata':
                    imported_metadata = item
        if dataset:
            data = dataset[:]
            if data.ndim == 1:
                isplot = True
                data = data.reshape(1, data.shape[0])
        else:
            getLogger(__name__).warn(
                "Could not load {}. "
                "File seems to contain no data.".format(name))
            return

        axes_info = {int(index): dict(axis.attrs)
                     for index, axis in sorted(axes_data)}

        if original_metadata is not None:
            original_metadata_dict = dict(original_metadata.attrs)

            for k, v in original_metadata_dict.copy().items():
                try:
                    # Original metadata maybe stored as json (= from PR)
                    # or not -> Try to load as json
                    # and ignore if this is not possible
                    original_metadata_dict[k] = json.loads(v)
                except Exception as e:
                    getLogger(__name__).warn(
                        "Could not load  original meta data '{}' "
                        "from hyperspy file: {}".format(k, e))

        if original_metadata_dict.get('filter.mode', None) == 'EELS':
            flipped_axes, data = flip_energy_axes(axes_info, data)
        else:
            flipped_axes = ()

        if original_metadata:
            # Iterate over the axes in reversed order
            # (the axes are in numpy order in .hspy file)
            # and get the pixel factors as defined by the original metadata.
            # Note, that the pixel factors will be 1.0,
            # if the metadata needed to calculate them is not available.
            # This is the case for all files that had not been generated
            # by the PR software.
            pixel_factors = [get_pixel_factor(data.shape,
                                              original_metadata_dict, axis)
                             for axis in range(len(axes_info) - 1, -1, -1)]
        else:
            pixel_factors = None

        assert all([v != 0 for v in pixel_factors])
        # 1. set the metadata generated from axes information
        metadata = get_metadata_from_axes_info(axes_info, pixel_factors,
                                               flipped_axes)
            
        # TODO: Set is_binned in axis_info,
        # type (from shape of data?), filename (from metadata)
        # and comment (from metadata)

        # TODO: What to do with imported metadata?
        # Can we use some of the information contained in there?

        # 2. overwrite with original_metadata
        if original_metadata is not None:
            metadata.update(original_metadata_dict)
        
        # Ensure that data that's only a plot will display as a plot
        if 'isplot' in locals():
            metadata['type'] = '1D'

        # Return extracted data and metadata
        return data, metadata


def _create_offset_array(slices, size, header=0, subheader=0, subfooter=0):
    return np.linspace(header, ((slices-1) * (size + subheader + subfooter))+header,
                       num=slices, dtype='int') + subheader


def _get_meta_data_dm3(dm3tags, dm3root):
    tagnames = [('DigiScan.Flyback', 'flyback time', float),
                ('DigiScan.TimeStamp','time stamp', str),
                ('DigiScan.Sample Time','pixel time', float)]
    meta = {}
    for tagname, metaname, typecast in tagnames:
        dm3tag = dm3root+'.'+tagname
        tagdata = dm3tags.get(dm3tag, None)
        getLogger(__name__).info('found dm3 tag {}: {}'.format(dm3tag, tagdata))
        if tagdata is not None:
            meta[metaname] = typecast(tagdata)
    return meta


def _guess_from_unit(scale, unit, allowed_base_units=None):
    """
    Guess the base unit according to the passed unit (with possible prefix).

    :param scale: the calibration value as given by the imported format
    :param unit: the calibration unit as given by the imported format
        as string. May start with a unit prefix (like 'm', 'u', etc.)
    :param allowed_base_units: An optional list of allowed base units.
        If None is passed, all units that start with 'm', 'n', 'p' or 'u'
        are assumed to be units with prefixes.
    :return a tuple of (value, unit) which contains the base unit
        and the calibration value scaled with the prefix-factor.
    """
    prefixes = {'m': 1e-3, 'u': 1e-6, 'µ': 1e-6, 'n': 1e-9, 'p': 1e-12}
    if len(unit) > 1 and unit[0] in prefixes:
        if allowed_base_units is None or (unit[1:] in allowed_base_units):
            scale *= prefixes[unit[0]]
            unit = unit[1:]
    return scale, unit


def _get_calib_from_dm3_tags(dm3tags, prefix, axis):
    """
    Create a calibration according to the passed dm3 tags.

    Read the passed dm3 tags and search for calibration values for the
    passed axis.
    If required tags are missing, use default values.

    :param prefix: A prefix for the tag name

    :return a calibration as dict
    """
    calib = {}
    scale_tag_name = prefix + ".Calibrations.Dimension.{}.Scale".format(axis)
    unit_tag_name = prefix + ".Calibrations.Dimension.{}.Units".format(axis)
    offset_tag_name = prefix + ".Calibrations.Dimension.{}.Origin".format(axis)
    dm3scale = float(dm3tags.get(scale_tag_name, 1.0))
    dm3origin = float(dm3tags.get(offset_tag_name, 0.0))
    dm3unit = dm3tags.get(unit_tag_name, 'px')
    dm3scale, dm3unit = _guess_from_unit(dm3scale, dm3unit)

    calib = _get_default_calibration()
    calib['value'] = dm3scale
    # Is there a dm3-tag for origin?
    calib['offset'] = dm3origin * -1
    calib['unit'] = dm3unit
    return calib


def _load_dm3(dm3name, dm3index=1, **kwargs):
    # parse DM3 file

    dm3tags = dm3.parseDM3(dm3name)

    if dm3tags == 0:
        raise ImportException("Could not read DM3 file '{}'.".format(dm3name))

    # get tags for image index
    prefixImageData = 'root.ImageList.{0}.ImageData'.format(dm3index)
    prefixImageTags = 'root.ImageList.{0}.ImageTags'.format(dm3index)

    # print('=== DM3 image <1> === BEGIN')
    # for k, v in dm3tags.items():
    #     print('  {} : {}'.format(k,v))
    # print('=== DM3 image <1> === END')

    # TODO: Are these tags mandantory? If yes, pass exception to user,
    # if they are missing.
    try:
        dm3offset = int(dm3tags[prefixImageData+'.Data.Offset'])
        dm3width = int(dm3tags[prefixImageData+'.Dimensions.0'])
        if prefixImageData+'.Dimensions.1' in dm3tags:
            dm3height = int(dm3tags[prefixImageData+'.Dimensions.1'])
        else:
            dm3height = None
        dm3slices = int(dm3tags.get(prefixImageData+'.Dimensions.2',1))
        dm3length = int(dm3tags[prefixImageData+'.Data.Size'])
        dm3type = int(dm3tags[prefixImageData+'.DataType'])
        dm3size = int(dm3tags[prefixImageData+'.PixelDepth'])
    except Exception as e:
        getLogger(__name__).error("Exception: {}".format(e))

    # get optional meta data
    optmeta = _get_meta_data_dm3(dm3tags, prefixImageTags)
    # print("optmeta: {}".format(optmeta))
    dm3file = open(dm3name, 'rb')

    # DM3 data types,
    # see http://www.microscopy.cen.dtu.dk/~cbb/info/dmformat/
    dm3DataTypes = {
        1 : np.int16,
        2 : np.float32,
        3 : np.complex64,
        10: np.uint16,
        7 : np.int32,
        9 : np.int8,
        6 : np.uint8,
        11: np.uint32,
        12: np.uint64
        };

    if (dm3type in dm3DataTypes):
        dm3dtype = dm3DataTypes[dm3type]
    else:
        getLogger(__name__).debug("unsupported DM3 DataType: {0}\n".format(dm3type))
        return _load_dm3(dm3name, dm3index=0, **kwargs)

    calib_x = _get_calib_from_dm3_tags(dm3tags, prefixImageData, 0)

    if dm3height is None:
        calibs = [calib_x]
    else:
        calib_y = _get_calib_from_dm3_tags(dm3tags, prefixImageData, 1)
        calibs = [calib_x, calib_y]

    # read data from file
    dm3file.seek(dm3offset);
    dm3data = np.fromfile(dm3file,dtype=dm3dtype,count=dm3length//dm3size)
    dm3file.close();

    # 1D data:
    if dm3height is None:
        meta_data = {'inherited.calib': calibs,
                     'type': '1D'}
        dm3data = dm3data.reshape((1, dm3width))
    # Stacked data
    elif dm3slices > 1:
        # print("input stack : {}x{}x{}@{}byte [RAM: {}kB]"
        #      .format(dm3height, dm3width, dm3slices, dm3size, dm3length//1024))
        dm3data = dm3data.reshape(dm3slices,dm3height,dm3width)
        calib_z = _get_calib_from_dm3_tags(dm3tags, prefixImageData, 2)
        calibs.append(calib_z)
        meta_data = {'inherited.calib': calibs,
                     'type': 'Stack'}
    # 2D data
    else:
        # print("input image : {}x{}@{}byte [RAM: {}kB]"
        #       .format(dm3height, dm3width, dm3size, dm3length//1024));
        dm3data = dm3data.reshape(dm3height,dm3width)
        meta_data = {'inherited.calib': calibs,
                     'type': '2D'}
    meta_data.update(optmeta)

    return dm3data, meta_data

def _load_npy(fname, **kwargs):
    nda = np.load(fname)
    shape = nda.shape
    if (len(shape) > 2 and shape[0]==1):
        nda = nda.reshape(shape[1:])
    getLogger(__name__).info('loaded NPY data with dtype = {} and shape = {}'.format(nda.dtype, nda.shape))
    meta = {}
    return nda, meta

def _load_npz(fname, **kwargs):
    """
    Load .prz/.npz file and return data and metadata.

    Data model info is ignored.
    For getting the data model info as well,
    use `load_npz_with_datamodel`

    :param fname: The filename

    :return data:ndarray, metadata:dict
    """
    nda, metadata, _ = load_npz_with_data_model(fname, **kwargs)
    if isinstance(metadata, (list, tuple)):
        # If data model is a group,
        # return the first item of meta data only.
        # TODO:
        # Meta data of all items should be merged.
        metadata = metadata[0]
    return nda, metadata

def _load_txt(fname, dtype=np.float, **kwargs):
    txt_file = open(fname, "r")
    file_content = txt_file.read()
    if '# type: 2D' in file_content:
        is_image = True
    else:
        is_image = False
    nda = np.transpose(np.loadtxt(fname, dtype=dtype))

    getLogger(__name__).info('loaded TXT data with dtype = {} and shape = {}'.format(nda.dtype, nda.shape))
    # Data of type '1D' must have dimension 2
    # (one dimension for number of plots and one for actual data)
    # If .txt file contains more than one column,
    # dimension of resulting ndarray is already 2.
    if len(nda.shape) == 1:
        nda = np.expand_dims(nda, axis=0)
    # TODO: Maybe readout more meta data from file?
    if is_image:
        meta = {'type': '2D'}
    else:
        meta = {'type': '1D', 'ref_size': [nda.shape[1]]}
    return nda, meta

def _parse_msa_info(fname):
    import re
    meta = {}
    p = re.compile(r'\s*#\s*([A-Z]+)\s*:\s*([^$]*)')
    with open(fname,'r') as f:
        for line in f:
            m = p.match(line)
            if m:
                key = m.group(1).strip()
                val = m.group(2).strip()
                if key == 'FORMAT' and val != 'EMSA/MAS Spectral Data File':
                    getLogger(__name__).info('MSA file FORMAT \'{}\' is unexpected '
                             'interpretation of data could be wrong.'.format(val))
                elif key == 'TITLE':
                    meta['comment']= val
                elif key == 'XUNITS':
                    meta['unit']= val
                elif key == 'YUNITS':
                    meta['intens. unit']= val
                elif key == 'NCOLUMS' and val>1:
                    getLogger(__name__).info('MSA file has NCOLUMNS {}, '
                             'extra columns are interpreted as extra graphs.'.format(val))
                elif key == 'DATATYPE' and val!='XY':
                    getLogger(__name__).info('MSA file has unexpected DATATYPE {}, '
                             'interpretation of data could be wrong.'.format(val))
                elif key == 'XPERCHAN':
                    meta['calib'] = float(val)
                elif key == 'OFFSET':
                    meta['origin'] = float(val)
                else:
                    getLogger(__name__).info('Extra MSA info tag {} : {} ignored.'.format(key, val))
            else: break
    # correct scaling since unit of origin is image pixel'
    if ('calib' in meta) and ('origin' in meta):
        meta['origin'] /= meta['calib']
    else:
        getLogger(__name__).info('Scaling could not be derived from MSA info.')

    return meta


def _load_msa(fname, dtype=np.float, **kwargs):
    msa_info = _parse_msa_info(fname)
    nda = np.transpose(np.loadtxt(fname, delimiter=',', comments='#', dtype=dtype))
    # first column is equidistant energy axis, discard this according to '1D' data concept

    calib = _get_default_calibration()
    calib['value'] = msa_info.get('calib', 1.0)
    calib['offset'] = msa_info.get('origin', 0.0)
    # msa files are always (?) spectra.
    calib['unit'] = 'eV'
    getLogger(__name__).info('loaded MSA data with dtype = {} and shape = {}'.format(nda.dtype, nda.shape))
    meta = {'type': '1D', 'inherited.calib': [calib]}
    meta.update(msa_info)

    return nda[1:], meta


def _load_csv(fname, dtype=np.float, skip_rows=1, **kwargs):
    nda = np.transpose(np.loadtxt(fname, dtype=dtype, skiprows=skip_rows, delimiter=','))

    getLogger(__name__).warn('loaded CSV data with dtype = {} '
             'and shape = {}'.format(nda.dtype, nda.shape))
    meta = {'type': '1D', 'ref_size': [nda.shape[0]]}
    return nda, meta

def _load_dm4(dm4name, **kwargs):

    # DM data types,
    # see http://www.microscopy.cen.dtu.dk/~cbb/info/dmformat/
    # note: image data type number is different from tag data type number for some data type
    dm4DataTypes = {
        1 : np.int16,
        2 : np.float32,
        10: np.uint16,
        7 : np.int32,
        9 : np.int8,
        6 : np.uint8,
        11: np.uint32,
        12: np.uint64
        };

    dm4file = dm4.DM4File.open(dm4name)
    dm4tags = dm4file.read_directory()

    datatag = dm4tags.named_subdirs['ImageList'].unnamed_subdirs[1].named_subdirs['ImageData'].named_tags['Data']
    typetag = dm4tags.named_subdirs['ImageList'].unnamed_subdirs[1].named_subdirs['ImageData'].named_tags['DataType']
    dimstag = dm4tags.named_subdirs['ImageList'].unnamed_subdirs[1].named_subdirs['ImageData'].named_subdirs['Dimensions']

    dims = []
    dm4type = dm4DataTypes[dm4file.read_tag_data(typetag)]
    for tag in dimstag.unnamed_tags:
        dims.append(dm4file.read_tag_data(tag))

    if len(dims) == 1:
        cols, = dims
        rows = None
        slices = 1
    if len(dims) == 2:
        cols, rows = dims
        slices = 1
    elif len(dims) == 3:
        cols, rows, slices = dims

    # print('-- Begin DM4 Info Tags --')
    # print(dm4tags.named_subdirs['ImageList'].unnamed_subdirs[1].named_subdirs['ImageData'].named_tags.keys())
    # print('shape: ', dims)
    # print('dtype: ', dm4type)
    # print('-- End DM4 Info Tags--')
    nda = np.array(dm4file.read_tag_data(datatag), dtype=dm4type)
    meta = {}

    if slices > 1:
        nda = nda.reshape(slices, rows, cols)
    elif rows is not None:
        nda = nda.reshape(rows, cols)
    else:
        nda = nda.reshape((1, cols))
        meta['type'] = '1D'

    Calibration_data_input = dm4tags.named_subdirs['ImageList'].unnamed_subdirs[1].named_subdirs['ImageData'].named_subdirs['Calibrations'].named_subdirs['Dimension'].unnamed_subdirs

    Calibration_data_output = []
    for line in Calibration_data_input:
        output_dic = {}
        output_dic['name'] = 'Default'
        value_input = dm4file.read_tag_data(line.named_tags['Scale'])
        unit_ascii = dm4file.read_tag_data(line.named_tags['Units'])
        unit_input = ''
        for asc in unit_ascii:
            unit_input += chr(asc)
        value, unit = _guess_from_unit(value_input, unit_input, allowed_base_units= ['m', 'A', 'V', 'rad', 's', 'eV'])
        output_dic['value'] = value
        output_dic['unit'] = unit
        output_dic['use_prefix'] = True
        output_dic['offset'] = dm4file.read_tag_data(line.named_tags['Origin'])
        output_dic['pixel_factor'] = 1.0
        output_dic['fixed_prefix'] = None
        Calibration_data_output.append(output_dic)

    meta['inherited.calib'] = Calibration_data_output
    dm4file.close()

    getLogger(__name__).info('loaded DM4 data with dtype = {} and shape = {}'.format(nda.dtype, nda.shape))

    return nda, meta

# define recognized file extensions and input data formats
DataFormatByExtension = [ ('dm3', ['.dm3',]),
                          ('dm4', ['.dm4',]),
                          ('tif', ['.tif', '.tiff']),
                          ('tia', ['.ser',]),
                          ('mrc', ['.mrc',]),
                          ('fff', ['.fff',]),
                          ('npy', ['.npy',]),
                          ('npz', ['.npz',]),
                          ('prz', ['.prz',]),
                          ('txt', ['.txt','.dat']),
                          ('csv', ['.csv']),
                          ('pgm', ['.pgm']),
                          ('msa', ['.msa']),
                          ('hspy', ['.hspy']),
                          ('pil', ['.png', '.jpg', '.jpeg', '.bmp' ]),
                          ('gif', ['.gif']),
                          ('raw', ['.raw',]) ]

# define loaders for all recognized input data formats
DataLoader = { 'dm3': _load_dm3,
               'dm4': _load_dm4,
               'raw': _load_raw,
               'fff': _load_fff,
               'tif': _load_tiff,
               'tiff': _load_tiff,
               'tia': _load_tia,
               'mrc': _load_mrc,
               'npy': _load_npy,
               'npz': _load_npz,  # This is used in some scripts in playground
               'txt': _load_txt,
               'csv': _load_csv,
               'pgm': _load_pgm,
               'pil': _load_pil,
               'gif': _load_gif,
               'msa': _load_msa,
               'prz': _load_npz,  # This is used in some scripts in playground
               'hspy': _load_hspy}

def _get_data_format(filepath):
    fileName, fileExt = path.splitext(filepath)
    fileExt = fileExt.lower()
    for fmt, extensions in DataFormatByExtension:
        if fileExt in extensions:
            break
    return fmt

def _load_data(filepath, force_file_type=None, **kwargs):
    if type(filepath) != type('str'):
        dataFormat = 'pil'
    elif force_file_type is None:
        dataFormat = _get_data_format(filepath)
    else:
        dataFormat = force_file_type
    getLogger(__name__).info('trying to load {} with format {}'.format(filepath, dataFormat))
    nda,  meta = DataLoader[dataFormat](filepath, **kwargs)
    return nda, meta

def _create_default_meta_data(data, metadata=None, data_type=None,
                              filename=None, as_plot=False):
    """Return a dict of default meta data.

    The returned dict contains
    * all metadata from the input dict 'metadata',
    * default values for the mandantory meta data keys,
    if they are missing in the input.
    Mandantory keys are:
    'ref_size', 'repo_id', 'comment' and 'type'.
    The default value for the size is data.shape[::-1],
    unless data is considered to be a plot.

    :param as_plot: If True, consider data as plot if the type is not
        explicitly defined in meta data.
    """
    result_meta_data = {}
    result_meta_data['repo_id'] = ''

    if metadata is None or 'type' not in metadata:
        if data_type is None:
            if len(data.shape) == 1 or as_plot:
                data_type = '1D'
            elif len(data.shape) == 2:
                data_type = '2D'
            elif len(data.shape) == 3:
                data_type = 'Stack'
        result_meta_data['type'] = data_type
    else:
        result_meta_data['type'] = metadata['type']

    if result_meta_data['type'] == '1D':
        if len(data.shape) > 2:
            # This is a plot stack:
            # shape[0] is the number of slices,
            # shape[1] is the number of plots in one graph
            # shape[2] is the number of x-values in one plot.
            # The size is defined for the number of slices
            # and the number of x-values, *not* for the
            # number of plots in a graph.
            result_meta_data['ref_size'] = [data.shape[0], data.shape[2]]
        else:
            # This is a single plot:
            # shape[0] is the number of plots in one graph,
            # shape[1] is the number of x-values.
            # Size is defined for the number of x-values only.
            result_meta_data['ref_size'] = [data.shape[-1]]
    else:
        result_meta_data['ref_size'] = data.shape[::-1]

    if metadata is not None:
        if 'size' in metadata:
            # Remove old key 'size' and replace by new key 'ref_size'
            metadata['ref_size'] = metadata['size']
            del metadata['size']
        result_meta_data.update(metadata)

    if filename is not None:
        # Overwrite the old filename from meta data
        # with the current one.
        # 'filename' should always contain the name of the
        # file from which the data was actually loaded.
        # See T3404
        result_meta_data['filename'] = path.basename(filename)
    # If 'comment' contains an old filename and this filename is
    # the same as the current one,
    # -> delete 'comment', because filename is already stored
    # in its own meta data item.
    if ('comment' in result_meta_data) and ('filename' in result_meta_data):
        if result_meta_data['comment'] == '<{}>'.format(
                result_meta_data['filename']):
            del result_meta_data['comment']

    return result_meta_data
