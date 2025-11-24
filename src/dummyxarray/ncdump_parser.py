"""Parser for ncdump header output.

This module provides functionality to parse ncdump -h output and create
DummyDataset objects from NetCDF metadata.
"""

import re
from typing import Dict, List, Tuple, Optional, Any


def parse_ncdump_header(header_text: str) -> Dict[str, Any]:
    """Parse ncdump header output into a structured dictionary.
    
    Parameters
    ----------
    header_text : str
        Output from `ncdump -h filename.nc`
    
    Returns
    -------
    dict
        Structured metadata with keys:
        - 'dimensions': dict of dimension names to sizes
        - 'variables': dict of variable definitions
        - 'global_attrs': dict of global attributes
    
    Examples
    --------
    >>> header = '''
    ... netcdf example {
    ... dimensions:
    ...     time = 10 ;
    ...     lat = 64 ;
    ... variables:
    ...     double time(time) ;
    ...         time:units = "days since 2000-01-01" ;
    ... }
    ... '''
    >>> metadata = parse_ncdump_header(header)
    >>> metadata['dimensions']
    {'time': 10, 'lat': 64}
    """
    metadata = {
        'dimensions': {},
        'variables': {},
        'global_attrs': {}
    }
    
    # Parse dimensions
    dims_section = _extract_section(header_text, 'dimensions:')
    if dims_section:
        metadata['dimensions'] = _parse_dimensions(dims_section)
    
    # Parse variables
    vars_section = _extract_section(header_text, 'variables:')
    if vars_section:
        metadata['variables'] = _parse_variables(vars_section)
    
    # Parse global attributes
    global_attrs = _parse_global_attributes(header_text)
    if global_attrs:
        metadata['global_attrs'] = global_attrs
    
    return metadata


def _extract_section(text: str, section_name: str) -> Optional[str]:
    """Extract a section from ncdump output."""
    pattern = rf'{re.escape(section_name)}(.*?)(?=\n\w+:|// global attributes:|$)'
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else None


def _parse_dimensions(dims_text: str) -> Dict[str, Optional[int]]:
    """Parse dimensions section.
    
    Examples:
        time = UNLIMITED ; // (12 currently)
        lat = 64 ;
        lon = 128 ;
    """
    dimensions = {}
    
    for line in dims_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('//'):
            continue
        
        # Match: name = size ; or name = UNLIMITED ;
        match = re.match(r'(\w+)\s*=\s*(\w+)', line)
        if match:
            name, size = match.groups()
            if size == 'UNLIMITED':
                # Try to extract current size from comment
                current_match = re.search(r'//.*\((\d+)\s+currently\)', line)
                dimensions[name] = int(current_match.group(1)) if current_match else None
            else:
                dimensions[name] = int(size)
    
    return dimensions


def _parse_variables(vars_text: str) -> Dict[str, Dict[str, Any]]:
    """Parse variables section.
    
    Examples:
        double time(time) ;
            time:units = "days since 2000-01-01" ;
            time:calendar = "gregorian" ;
        float temperature(time, lat, lon) ;
            temperature:units = "K" ;
    """
    variables = {}
    current_var = None
    
    for line in vars_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('//'):
            continue
        
        # Variable declaration: type name(dims) ;
        var_match = re.match(r'(\w+)\s+(\w+)\s*\((.*?)\)', line)
        if var_match:
            dtype, name, dims_str = var_match.groups()
            dims = [d.strip() for d in dims_str.split(',') if d.strip()]
            current_var = name
            variables[name] = {
                'dims': dims,
                'dtype': dtype,
                'attrs': {}
            }
        # Attribute: var:attr = value ;
        elif current_var and ':' in line:
            attr_match = re.match(r'(\w+):(\w+)\s*=\s*(.+?)\s*;', line)
            if attr_match:
                var_name, attr_name, attr_value = attr_match.groups()
                if var_name == current_var:
                    variables[current_var]['attrs'][attr_name] = _parse_attribute_value(attr_value)
    
    return variables


def _parse_global_attributes(text: str) -> Dict[str, Any]:
    """Parse global attributes section.
    
    Examples:
        // global attributes:
                :Conventions = "CF-1.8" ;
                :title = "Example Data" ;
    """
    global_attrs = {}
    
    # Find global attributes section
    match = re.search(r'// global attributes:(.*?)(?=\n\}|$)', text, re.DOTALL)
    if not match:
        return global_attrs
    
    attrs_text = match.group(1)
    
    for line in attrs_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('//'):
            continue
        
        # Match: :attr = value ;
        attr_match = re.match(r':(\w+)\s*=\s*(.+?)\s*;', line)
        if attr_match:
            attr_name, attr_value = attr_match.groups()
            global_attrs[attr_name] = _parse_attribute_value(attr_value)
    
    return global_attrs


def _parse_attribute_value(value_str: str) -> Any:
    """Parse attribute value from string.
    
    Handles:
    - Quoted strings: "value"
    - Numbers: 1.5, 42
    - Arrays: 1.0, 2.0, 3.0
    """
    value_str = value_str.strip()
    
    # String (quoted)
    if value_str.startswith('"') and value_str.endswith('"'):
        return value_str[1:-1]
    
    # Array (contains comma)
    if ',' in value_str:
        parts = [p.strip() for p in value_str.split(',')]
        return [_parse_single_value(p) for p in parts]
    
    # Single value
    return _parse_single_value(value_str)


def _parse_single_value(value_str: str) -> Any:
    """Parse a single value (number or string)."""
    value_str = value_str.strip()
    
    # Try integer
    try:
        return int(value_str)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value_str)
    except ValueError:
        pass
    
    # Return as string
    return value_str


def from_ncdump_header(header_text: str, record_history: bool = True):
    """Create a DummyDataset from ncdump header output.
    
    Parameters
    ----------
    header_text : str
        Output from `ncdump -h filename.nc`
    record_history : bool, optional
        Whether to record construction history (default: True)
    
    Returns
    -------
    DummyDataset
        Dataset constructed from the header metadata
    
    Examples
    --------
    >>> header = open('header.txt').read()
    >>> ds = from_ncdump_header(header)
    >>> print(ds.dims)
    >>> print(ds.coords.keys())
    
    Notes
    -----
    This function parses the output of `ncdump -h` and creates a DummyDataset
    with the same structure. Data arrays are not populated - use
    `populate_with_random_data()` if you need sample data.
    
    The parser handles:
    - Dimensions (including UNLIMITED)
    - Variables with dimensions and attributes
    - Global attributes
    - Common NetCDF data types
    """
    # Import here to avoid circular dependency
    from dummyxarray import DummyDataset
    
    # Parse the header
    metadata = parse_ncdump_header(header_text)
    
    # Create dataset
    ds = DummyDataset(_record_history=record_history)
    
    # Add global attributes
    if metadata['global_attrs']:
        ds.assign_attrs(**metadata['global_attrs'])
    
    # Add dimensions
    for dim_name, dim_size in metadata['dimensions'].items():
        if dim_size is not None:
            ds.add_dim(dim_name, dim_size)
    
    # Separate coordinates from variables
    # A variable is a coordinate if it has the same name as its only dimension
    coords = {}
    variables = {}
    
    for var_name, var_info in metadata['variables'].items():
        if len(var_info['dims']) == 1 and var_info['dims'][0] == var_name:
            coords[var_name] = var_info
        else:
            variables[var_name] = var_info
    
    # Add coordinates
    for coord_name, coord_info in coords.items():
        ds.add_coord(
            coord_name,
            dims=coord_info['dims'],
            attrs=coord_info['attrs']
        )
    
    # Add variables
    for var_name, var_info in variables.items():
        ds.add_variable(
            var_name,
            dims=var_info['dims'],
            attrs=var_info['attrs']
        )
    
    return ds
