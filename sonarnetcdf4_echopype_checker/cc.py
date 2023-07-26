import os
from pathlib import Path

import netCDF4 as nc4
import pandas as pd
import xarray as xr


def _dtype_compare(var1, var2, dtype_strict=True):
    """Perform numpy array data type comparisons
    
    var1: xarray Dataarray
    var2: xarray Dataarray
    dtype_strict: If True, the comparison will be made on the specific data type returned by .dtype;
        if False, it will be a generalized comparison based on .dtype.kind 
        (eg, float rather than float64 or float32) or a string-type comparison that
        accounts for the case of string arrays represented as an object data type
    """
    if dtype_strict:
        return var1.dtype == var2.dtype
    else:
        if 'O' in (var1.dtype.kind, var2.dtype.kind):
            # Perform comparisons for string types where one is an object type potentially 
            # containing strings. Could also use np.issubdtype(var1.dtype, str).
            # In the return statement, I previously used the more verbose
            # var2[0].values.dtype.kind in ('U', 'S')
            if var1.dtype.kind in ('U', 'S'):
                return type(var2.values[0]) is str
            elif var2.dtype.kind in ('U', 'S'):
                return type(var1.values[0]) is str
            else:
                # Will return True if both are object type and neither contains string elements
                return var1.dtype.kind == var2.dtype.kind
        else:
            return var1.dtype.kind == var2.dtype.kind


class ConventionCDL:
    def __init__(self, group):
        self._process_cdl(group)
        self.group = group
        
        # Optional filters
        self.obligation = None
        self.echopype_mods = None

    def _process_cdl(self, group):
        """_summary_

        Args:
            group (_type_): _description_

        Returns:
            _type_: _description_
        """
        get_attr_value = lambda v, attr: v[attr] if attr in v else None
        
        if group == 'Platform':
            cdl_filename = "CDLsource-Platform-D20211005-T001612.cdl"
        elif group in ("Sonar", "Sonar/Beam_group1"):
            cdl_filename = "CDLsource-Sonar-Beam_group1-D20211005-T001612.cdl"
        else:
            # Not implemented yet
            return None, None
        
        # TODO: Use of moduledir won't be needed once this module becomes a package
        # May be able to replace this with importlib.resources, but will then probably
        # have to use StringIO
        # https://dev.to/bowmanjd/easily-load-non-python-data-files-from-a-python-package-2e8g
        # https://stackoverflow.com/questions/58520128/how-to-use-importlib-resources-pathpackage-resource
        moduledir = os.path.dirname(os.path.realpath(__file__))
        cdl_path = Path(moduledir) / "cdls" / cdl_filename
        # cdl_path = Path("./cdls") / cdl_filename
        
        nc4_ds = nc4.Dataset.fromcdl(cdl_path, ncfilename=None, format="NETCDF4")

        # If the group parameter is not used, the Top-level (root) group is returned
        cdl_ds = xr.load_dataset(xr.backends.NetCDF4DataStore(nc4_ds, group=group))
        # nc4_ds.close() # Not needed, apparently?

        # TODO: nc files are being created by fromcdl, despite the ncfilename=None.
        #       Delete them here
        
        # Create dataframe compiling the properties attributes "obligation" and "echopype_mods"
        # for each variable
        variables_attrs = []
        for v in sorted(cdl_ds.variables):
            v_attrs = cdl_ds[v].attrs
            var_attr_tup = (
                v, 
                v_attrs["obligation"], 
                get_attr_value(v_attrs, "echopype_mods"),
                cdl_ds.variables[v].dtype.name, 
                get_attr_value(v_attrs, "long_name"),
                get_attr_value(v_attrs, "units"),
                get_attr_value(v_attrs, "standard_name"),
                get_attr_value(v_attrs, "valid_min"),
                get_attr_value(v_attrs, "valid_range"),
                get_attr_value(v_attrs, "comment"),
            )
            variables_attrs.append(var_attr_tup)

        cdl_variables_df = pd.DataFrame(
            variables_attrs, 
            columns=[
                'variable_name', 
                'obligation', 
                'echopype_mods',
                'data_type', 
                'long_name',
                'units',
                'standard_name',
                'valid_min',
                'valid_range',
                'comment',
            ]
        )
        
        self.cdl_ds = cdl_ds
        self.cdl_variables_df = cdl_variables_df

    def set_obligation(self, obligation, exclude=False):
        """_summary_

        Args:
            obligation (_type_): _description_. Can be None
            exclude (bool, optional): _description_. Defaults to False.
        """
        obligations_all = set(["M", "MA", "R", "O", "NA"])
        
        if isinstance(obligation, (list, tuple)):
            obligation = set(obligation)
        elif obligation is None:
            obligation = obligation
        else:
            obligation = set([obligation])

        if exclude and obligation is not None:
            obligation = obligations_all.difference(obligation)
        
        self.obligation = obligation
    
    def set_echopype_mods(self, echopype_mods):
        # TODO: implement exclude=False later 
        if isinstance(echopype_mods, (list, tuple)):
            echopype_mods = set(echopype_mods)
        elif echopype_mods is None:
            echopype_mods = echopype_mods
        else:
            echopype_mods = set([echopype_mods])

        self.echopype_mods = echopype_mods
    
    def set_ed_group_ds(self, ds):
        self.ed_group_ds = ds
    
    def _get_common_variables(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return (
            set(self._get_obligation_vars()) 
            & set(self._get_echopype_mods_vars()) 
            & set(self.ed_group_ds.variables)
        )

    def _get_obligation_vars(self):
        if self.obligation:
            return (
                self.cdl_variables_df[
                    self.cdl_variables_df.obligation.isin(self.obligation)
                ]
                ["variable_name"].values
            )
        else:
            return self.cdl_variables_df["variable_name"].values

    def _get_echopype_mods_vars(self):
        # TODO: echopype_mods attr can be a comma-separated list, right?
        #       If so, will need to account for that
        if self.echopype_mods:
            return (
                self.cdl_variables_df[
                    self.cdl_variables_df.echopype_mods.isin(self.echopype_mods)
                ]
                ["variable_name"].values
            )
        else:
            return self.cdl_variables_df["variable_name"].values

    def test_vars_presence(self, test_type="expected"):
        """Presence of expected and unexpected variables

        Args:
            test_type (str, optional): _description_. Defaults to "expected".
        """

        cdl_variables = self._get_obligation_vars()

        if test_type == "expected":
            print("****Expected variables not found in the EchoData object:")
            for v in cdl_variables:
                if v not in self.ed_group_ds.variables:
                    print(v)
        elif test_type == "unexpected":
            print("****EchoData variables not found in the CDL:")
            for v in self.ed_group_ds.variables:
                if v not in self.cdl_ds.variables:
                    print(v)

    def test_vars_datatype(self, dtype_strict=True):
        """Test variable data type
        
        Use two types of data type comparisons: strict (specific) vs generalized.

        Args:
            dtype_strict (bool, optional): _description_. Defaults to True.
        """

        print("****Variables with different data type from what is expected:")
        for v in self._get_common_variables():
            if not _dtype_compare(
                self.ed_group_ds.variables[v], 
                self.cdl_ds.variables[v], 
                dtype_strict
            ):
                print(f"{v}: EchoData type: {self.ed_group_ds.variables[v].dtype}, CDL type: {self.cdl_ds.variables[v].dtype}")

    def test_vars_dimensionality(self):
        """Test variable dimensionality
        """

        print("****EchoData variables with dimensionality different from the CDL:")
        for v in self._get_common_variables():
            if self.ed_group_ds.variables[v].dims != self.cdl_ds.variables[v].dims:
                print(f"{v}: EchoData dims: {self.ed_group_ds.variables[v].dims}, CDL dims: {self.cdl_ds.variables[v].dims}")

    def test_attrs_presence(self, global_attrs=False):
        """Test attribute presence
        """

        def _attr_check(cdl_source, ed_source, global_attrs):
            cdl_attrs_keys = [
                k for k in cdl_source.attrs.keys() if k not in ('obligation', 'echopype_mods')
            ]
            ed_group_attrs_keys = ed_source.attrs.keys()
            if set(ed_group_attrs_keys) != set(cdl_attrs_keys):
                missing_attrs = set(cdl_attrs_keys).difference(set(ed_group_attrs_keys))
                source = "global" if global_attrs else v
                print(f"{source}: Missing EchoData attrs: {missing_attrs}")

        print("****Variable or global missing convention attributes:")
        if global_attrs:
            _attr_check(self.cdl_ds, self.ed_group_ds, global_attrs)
        else:
            for v in self._get_common_variables():
                _attr_check(self.cdl_ds.variables[v], self.ed_group_ds.variables[v], global_attrs)

    def test_attrs_value(self, global_attrs=False):
        """Test for attribute values.
        Initially, test only for CDL attributes missing in the echodata group
        
        This will be trickier b/c of values that are not defined as static
        """
        def _attr_value_check(cdl_source, ed_source, global_attrs):
            cdl_attrs_keys = [
                k for k in cdl_source.attrs.keys() if k not in ('obligation', 'echopype_mods')
            ]
            ed_group_attrs_keys = ed_source.attrs.keys()
            for attr in cdl_attrs_keys & ed_group_attrs_keys:
                if attr != 'valid_range':
                    # TODO: For now, excluding value_range b/c it entails
                    #   comparing lists or arrays, not scalars
                    if ed_source.attrs[attr] != cdl_source.attrs[attr]:
                        source = "global" if global_attrs else v
                        print(f"{source}.{attr}: EchoData value: {ed_source.attrs[attr]}")

        print("****Variable or global attribute with different values:")
        if global_attrs:
            _attr_value_check(self.cdl_ds, self.ed_group_ds, global_attrs)
        else:
            for v in self._get_common_variables():
                _attr_value_check(self.cdl_ds.variables[v], self.ed_group_ds.variables[v], global_attrs)
