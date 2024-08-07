# -----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2015-9-20
# Purpose: MeteoInfoLab layer module
# Note: Jython
# -----------------------------------------------------
import geoutil
import mipylib.miutil as miutil
import mipylib.numeric as np
from java.awt import Font
from java.time import LocalDateTime

from org.meteoinfo.data import TableUtil, XYListDataset
from org.meteoinfo.geo.layer import LayerTypes, VectorLayer
from org.meteoinfo.geometry.legend import LegendType
from org.meteoinfo.projection import ProjectionUtil, KnownCoordinateSystems
from org.meteoinfo.geometry.shape import PolygonShape, ShapeTypes
from org.meteoinfo.geo.analysis import GeometryUtil
from org.meteoinfo.geo.util import GeoProjectionUtil
from org.meteoinfo.geo.io import GeoJSONReader, GeoJSONWriter


class MILayer(object):
    """
    Map layer
    
    :param layer: (*MapLayer*) MapLayer object.
    :param shapetype: (*ShapeTypes*) Shape type ['point' | 'point_z' | 'line' | 'line_z' | 'polygon'
        | 'polygon_z']
    """

    def __init__(self, layer=None, shapetype=None):
        if layer is None:
            if shapetype is None:
                print('shapetype must be specified!')
            else:
                shapetype = shapetype.upper()
                if shapetype == 'LINE':
                    shapetype = 'POLYLINE'
                elif shapetype == 'LINE_Z':
                    shapetype = 'POLYLINE_Z'
                try:
                    type = ShapeTypes.valueOf(shapetype)
                except:
                    print('shapetype is not valid: {}'.foramt(shapetype))
                    type = ShapeTypes.POINT
                self._layer = VectorLayer(type)
                self.shapetype = type
                self.proj = KnownCoordinateSystems.geographic.world.WGS1984
        else:
            self._layer = layer
            self.shapetype = layer.getShapeType()
            self.proj = layer.getProjInfo()
        self._coord_array = None

    def __repr__(self):
        return self._layer.getLayerInfo()

    @property
    def visible(self):
        return self._layer.isVisible()

    @visible.setter
    def visible(self, val):
        self._layer.setVisible(val)

    @property
    def layer_type(self):
        return self._layer.getLayerType()

    @property
    def x_coord(self):
        """
        Get X coordinate array.
        :return: X coordinate array
        """
        if self.isvectorlayer():
            if self._coord_array is None:
                self._coord_array = GeometryUtil.getCoordinates(self._layer)
            return np.array(self._coord_array[0])
        else:
            return None

    @property
    def y_coord(self):
        """
        Get Y coordinate array.
        :return: Y coordinate array
        """
        if self.isvectorlayer():
            if self._coord_array is None:
                self._coord_array = GeometryUtil.getCoordinates(self._layer)
            return np.array(self._coord_array[1])
        else:
            return None

    @property
    def z_coord(self):
        """
        Get Z coordinate array.
        :return: Z coordinate array
        """
        if self.isvectorlayer():
            if self._coord_array is None:
                self._coord_array = GeometryUtil.getCoordinates(self._layer)
            return np.array(self._coord_array[2])
        else:
            return None

    @property
    def m_coord(self):
        """
        Get M coordinate array.
        :return: M coordinate array
        """
        if self.isvectorlayer():
            if self._coord_array is None:
                self._coord_array = GeometryUtil.getCoordinates(self._layer)
            return np.array(self._coord_array[3])
        else:
            return None

    def isvectorlayer(self):
        """
        Check this layer is VectorLayer or not.
        
        :returns: (*boolean*) Is VectorLayer or not.
        """
        return self._layer.getLayerType() == LayerTypes.VECTOR_LAYER

    def get_encoding(self):
        """
        Get encoding.
        
        :returns: (*string*) Encoding
        """
        return self._layer.getAttributeTable().getEncoding()

    @property
    def datatable(self):
        """
        Get attribute table.

        :return: Attribute table.
        """
        r = self._layer.getAttributeTable().getTable()
        return np.datatable(r)

    def gettable(self):
        """
        Get attribute table.
        
        :returns: (*PyTableData') Attribute table.
        """
        r = self._layer.getAttributeTable().getTable()
        return np.PyTableData(r)

    def cellvalue(self, fieldname, shapeindex):
        """
        Get attribute table cell value.
        
        :param fieldname: (*string*) Field name.
        :param shapeindex: (*int*) Shape index.
        
        :returns: The value in attribute table identified by field name and shape index.
        """
        v = self._layer.getCellValue(fieldname, shapeindex)
        if isinstance(v, LocalDateTime):
            dt = miutil.pydate(v)
            return dt
        else:
            return v

    def setcellvalue(self, fieldname, shapeindex, value):
        """
        Set cell value in attribute table.
        
        :param fieldname: (*string*) Field name.
        :param shapeindex: (*int*) Shape index.
        :param value: (*object*) Cell value to be assigned.
        """
        self._layer.editCellValue(fieldname, shapeindex, value)

    def setfieldvalue(self, fieldname, value, index=None):
        """
        Set field value.

        :param fieldname: (*str*) The field name.
        :param value: (*array*) The field data array.
        :param index: (*array*) Optional. Field data index. Default is `None`.
        """
        value = np.asarray(value)
        if index is None:
            self._layer.getAttributeTable().getTable().setColumnData(fieldname, value.jarray)
        else:
            index = np.asarray(index)
            self._layer.getAttributeTable().getTable().setColumnData(fieldname, value.jarray, index.jarray)

    @property
    def shapes(self):
        """
        Get shapes.
        """
        return self._layer.getShapes()

    def get_graphics(self, xshift=0, interpolation=None):
        """
        Get graphics.

        :param xshift: (*float*) X coordinate shift.
        :param interpolation: (*str*) Image interpolation.
        """
        if interpolation is None:
            return self._layer.getGraphics(xshift)
        else:
            return self._layer.getGraphics(xshift, interpolation)

    @property
    def shapenum(self):
        """
        Get shape number
        """
        return self._layer.getShapeNum()

    @property
    def legend(self):
        """
        Get legend scheme.
        """
        return self._layer.getLegendScheme()

    @legend.setter
    def legend(self, legend):
        """
        Set legend scheme.
        
        :param legend: (*LegendScheme*) Legend scheme.
        """
        self._layer.setLegendScheme(legend)

    def update_legend(self, ltype, fieldname):
        """
        Update legend scheme.
        
        :param ltype: (*string*) Legend type [single | unique | graduate].
        :param fieldname: (*string*) Field name.
        """
        if ltype == 'single':
            ltype = LegendType.SINGLE_SYMBOL
        elif ltype == 'unique':
            ltype = LegendType.UNIQUE_VALUE
        elif ltyp == 'graduate':
            ltype = LegendType.GRADUATED_COLOR
        else:
            raise ValueError(ltype)
        self._layer.updateLegendScheme(ltype, fieldname)
        return self._layer.getLegendScheme()

    def addfield(self, fieldname, dtype, values=None):
        """
        Add a field into the attribute table.
        
        :param fieldname: (*string*) Field name.
        :param dtype: (*string*) Field data type [string | int | float | double].
        :param values: (*array_like*) Field values.
        """
        dt = TableUtil.toDataTypes(dtype)
        self._layer.editAddField(fieldname, dt)
        if not values is None:
            n = self.shapenum()
            for i in range(n):
                if i < len(values):
                    self._layer.editCellValue(fieldname, i, values[i])

    def delfield(self, fieldname):
        """
        Delete a field from the attribute table.
        
        :param fieldname: (*string*) Filed name.
        """
        self._layer.editRemoveField(fieldname)

    def renamefield(self, fieldname, newfieldname):
        """
        Rename the field.
        
        :param fieldname: (*string*) The old field name.
        :param newfieldname: (*string*) The new field name.
        """
        self._layer.editRenameField(fieldname, newfieldname)

    def addshape(self, x, y, fields=None, z=None, m=None):
        """
        Add a shape.
        
        :param x: (*array_like*) X coordinates of the shape points.
        :param y: (*array_like*) Y coordinates of the shape points.
        :param fields: (*array_like*) Field values of the shape.
        :param z: (*array_like*) Optional, Z coordinates of the shape points.
        :param m: (*array_like*) Optional, M coordinates of the shape points.
        """
        shapes = geoutil.makeshapes(x, y, self.shapetype, z, m)
        if len(shapes) == 1:
            self._layer.editAddShape(shapes[0], fields)
        else:
            for shape, field in zip(shapes, fields):
                self._layer.editAddShape(shape, field)

    def del_shape(self, shape):
        """
        Delete a shape.

        :param shape: (*Shape or int*) The shape or shape index to be deleted.
        """
        self._layer.editRemoveShape(shape)

    def copy(self):
        """
        Copy the layer.

        :return: (*MILayer*) Copied layer.
        """
        return MILayer(layer=self._layer.clone())

    def move(self, xshift=0, yshift=0):
        """
        Move shapes.

        :param xshift: (*float*) X shift.
        :param yshift: (*float*) Y shift.
        """
        self._layer.move(xshift, yshift)

    def addlabels(self, fieldname, **kwargs):
        """
        Add labels
        
        :param fieldname: (*string*) Field name
        :param fontname: (*string*) Font name. Default is ``Arial``.
        :param fontsize: (*string*) Font size. Default is ``14``.
        :param bold: (*boolean*) Font bold or not. Default is ``False``.
        :param color: (*color*) Label color. Default is ``None`` with black color.
        :param xoffset: (*int*) X coordinate offset. Default is ``0``.
        :param yoffset: (*int*) Y coordinate offset. Default is ``0``.
        :param avoidcoll: (*boolean*) Avoid labels collision or not. Default is ``True``.
        :param decimals: (*int*) Number of decimals of labels.
        """
        labelset = self._layer.getLabelSet()
        labelset.setFieldName(fieldname)
        fontname = kwargs.pop('fontname', 'Arial')
        fontsize = kwargs.pop('fontsize', 14)
        bold = kwargs.pop('bold', False)
        if bold:
            font = Font(fontname, Font.BOLD, fontsize)
        else:
            font = Font(fontname, Font.PLAIN, fontsize)
        labelset.setLabelFont(font)
        color = kwargs.pop('color', None)
        if not color is None:
            color = miutil.getcolor(color)
            labelset.setLabelColor(color)
        xoffset = kwargs.pop('xoffset', 0)
        labelset.setXOffset(xoffset)
        yoffset = kwargs.pop('yoffset', 0)
        labelset.setYOffset(yoffset)
        avoidcoll = kwargs.pop('avoidcoll', True)
        labelset.setAvoidCollision(avoidcoll)
        decimals = kwargs.pop('decimals', None)
        if not decimals is None:
            labelset.setAutoDecimal(False)
            labelset.setDecimalDigits(decimals)
        self._layer.addLabels()

    def getlabel(self, text):
        """
        Get a label.
        
        :param text: (*string*) The label text.
        """
        return self._layer.getLabel(text)

    def movelabel(self, label, x=0, y=0):
        """
        Move a label.
        
        :param label: (*string*) The label text.
        :param x: (*float*) X shift for moving in pixel unit.
        :param y: (*float*) Y shift for moving in pixel unit.
        """
        self._layer.moveLabel(label, x, y)

    def add_charts(self, fieldnames, legend=None, **kwargs):
        """
        Add charts
        
        :param fieldnames: (*list of string*) Field name list.
        :param legend: (*LegendScheme*) Chart legend.
        :param charttype: (*string*) Chart type [bar | pie]. Default is ``bar``.
        :param minsize: (*int*) Minimum chart size. Default is ``0``.
        :param maxsize: (*int*) Maximum chart size. Default is ``50``.
        :param barwidth: (*int*) Bar width. Only valid for bar chart. Default is ``8``.
        :param xoffset: (*int*) X coordinate offset. Default is ``0``.
        :param yoffset: (*int*) Y coordinate offset. Default is ``0``.
        :param avoidcoll: (*boolean*) Avoid labels collision or not. Default is ``True``.
        :param align: (*string*) Chart align type [center | left | right | none], Default is ``center``.
        :param view3d: (*boolean*) Draw chart as 3D or not. Default is ``False``.
        :param thickness: (*int*) 3D chart thickness. Default is ``5``.
        :param drawlabel: (*boolean*) Draw label or not. Default is ``False``.
        :param fontname: (*string*) Label font name.
        :param fontsize: (*int*) Label font size.
        :param bold: (*boolean*) Font bold or not. Default is ``False``.
        :param labelcolor: (*color*) Label color.
        :param decimals: (*int*) Number of decimals of labels.
        """
        charttype = kwargs.pop('charttype', None)
        minsize = kwargs.pop('minsize', None)
        maxsize = kwargs.pop('maxsize', None)
        barwidth = kwargs.pop('barwidth', None)
        xoffset = kwargs.pop('xoffset', None)
        yoffset = kwargs.pop('yoffset', None)
        avoidcoll = kwargs.pop('avoidcoll', None)
        align = kwargs.pop('align', None)
        view3d = kwargs.pop('view3d', None)
        thickness = kwargs.pop('thickness', None)
        drawlabel = kwargs.pop('drawlabel', None)
        fontname = kwargs.pop('fontname', 'Arial')
        fontsize = kwargs.pop('fontsize', 12)
        bold = kwargs.pop('bold', False)
        if bold:
            font = Font(fontname, Font.BOLD, fontsize)
        else:
            font = Font(fontname, Font.PLAIN, fontsize)
        labelcolor = kwargs.pop('labelcolor', None)
        decimals = kwargs.pop('decimals', None)

        chartset = self._layer.getChartSet()
        chartset.setFieldNames(fieldnames)
        chartset.setLegendScheme(legend)
        if not charttype is None:
            chartset.setChartType(charttype)
        if not minsize is None:
            chartset.setMinSize(minsize)
        if not maxsize is None:
            chartset.setMaxSize(maxsize)
        if not barwidth is None:
            chartset.setBarWidth(barwidth)
        if not xoffset is None:
            chartset.setXShift(xoffset)
        if not yoffset is None:
            chartset.setYShift(yoffset)
        if not avoidcoll is None:
            chartset.setAvoidCollision(avoidcoll)
        if not align is None:
            chartset.setAlignType(align)
        if not view3d is None:
            chartset.setView3D(view3d)
        if not thickness is None:
            chartset.setThickness(thickness)
        if not drawlabel is None:
            chartset.setDrawLabel(drawlabel)
        chartset.setLabelFont(font)
        if not labelcolor is None:
            chartset.setLabelColor(miutil.getcolor(labelcolor))
        if not decimals is None:
            chartset.setDecimalDigits(decimals)
        self._layer.updateChartSet()
        self._layer.addCharts()
        return chartset

    def get_chartlegend(self):
        """
        Get legend of the chart graphics.
        """
        return self._layer.getChartSet().getLegendScheme()

    def get_chart(self, index):
        """
        Get a chart graphic.
        
        :param index: (*int*) Chart index.
        
        :returns: Chart graphic
        """
        return self._layer.getChartPoints()[index]

    def move_chart(self, index, x=0, y=0):
        """
        Move a chart graphic.
        
        :param index: (*int*) Chart index.
        :param x: (*float*) X shift for moving.
        :param y: (*float*) Y shift for moving.
        """
        s = self._layer.getChartPoints()[index].getShape()
        p = s.getPoint()
        p.X = p.X + x
        p.Y = p.Y + y
        s.setPoint(p)

    def set_avoidcoll(self, avoidcoll):
        """
        Set if avoid collision or not. Only valid for VectorLayer with Point shapes.
        
        :param avoidcoll: (*boolean*) Avoid collision or not.
        """
        self._layer.setAvoidCollision(avoidcoll)

    def project(self, toproj):
        """
        Project to another projection.
        
        :param toproj: (*ProjectionInfo*) The projection to be projected.
        """
        GeoProjectionUtil.projectLayer(self._layer, toproj)

    def buffer(self, dist=0, merge=False):
        """
        Get the buffer layer.
        
        :param dist: (*float*) Buffer value.
        :param merge: (*boolean*) Merge the buffered shapes or not.
        
        :returns: (*MILayer*) Buffered layer.
        """
        r = self._layer.buffer(dist, False, merge)
        return MILayer(r)

    def clip(self, clipobj):
        """
        Clip this layer by polygon or another polygon layer.
        
        :param clipobj: (*PolygonShape or MILayer*) Clip object.
        
        :returns: (*MILayer*) Clipped layer.
        """
        if isinstance(clipobj, PolygonShape):
            clipobj = [clipobj]
        elif isinstance(clipobj, MILayer):
            clipobj = clipobj._layer
        r = self._layer.clip(clipobj)
        return MILayer(r)

    def select(self, expression, seltype='new'):
        """
        Select shapes by SQL expression.
        
        :param expression: (*string*) SQL expression.
        :param seltype: (*string*) Selection type ['new' | 'add_to_current' |
            'remove_from_current' | 'select_from_current']
            
        :returns: (*list of Shape*) Selected shape list.
        """
        self._layer.sqlSelect(expression, seltype)
        return self._layer.getSelectedShapes()

    def clear_selection(self):
        """
        Clear shape selection.
        """
        self._layer.clearSelectedShapes()

    def clone(self):
        """
        Clone self.
        """
        return MILayer(self._layer.clone())

    def save(self, fn=None, encoding=None):
        """
        Save layer as shape file.
        
        :param fn: (*string*) Shape file name (.shp).
        :param encoding: (*string*) Encoding.
        """
        if fn is None:
            fn = self._layer.getFileName()

        if fn.strip() == '':
            print('File name is needed to save the layer!')
            raise IOError
        else:
            if encoding is None:
                self._layer.saveFile(fn)
            else:
                self._layer.saveFile(fn, encoding)

    def save_kml(self, fn):
        """
        Save layer as KML file.
        
        :param fn: (*string*) KML file name.
        """
        self._layer.saveAsKMLFile(fn)

    def save_bil(self, fn, proj=None):
        """
        Save layer as bil file.

        :param fn: (*str*) Bil file name.
        :param proj: (*ProjectionInfo*) Projection. Default is None.
        """
        if proj is None:
            self._layer.saveFile(fn)
        else:
            self._layer.saveFile(fn, proj)

    def save_geojson(self, fn):
        """
        Save layer as GeoJSON file.

        :param fn: (*str*) GeoJSON file name.
        """
        features = GeoJSONWriter.write(self._layer)
        with open(fn, 'w') as f:
            f.write("{\n")
            f.write(""""type": "FeatureCollection",\n""")
            f.write(""""features": [\n""")
            for i in range(features.getNumFeatures()):
                feature = features.getFeature(i)
                f.write(feature.toString())
                if i < features.getNumFeatures() - 1:
                    f.write(",\n")
                else:
                    f.write("\n")
            f.write("]\n")
            f.write("}")


class MIXYListData():
    def __init__(self, data=None):
        if data is None:
            self.data = XYListDataset()
        else:
            self.data = data

    def __getitem__(self, indices):
        if not isinstance(indices, tuple):
            inds = []
            inds.append(indices)
            indices = inds

        if isinstance(indices[0], int):
            if isinstance(indices[1], int):
                x = self.data.getX(indices[0], indices[1])
                y = self.data.getY(indices[0], indices[1])
                return x, y
            else:
                return self.data.getXValues(indices[0]), self.data.getXValues(indices[0])

    def size(self, series=None):
        if series is None:
            return self.data.getSeriesCount()
        else:
            return self.data.getItemCount(series)

    def addseries(self, xdata, ydata, key=None):
        if key is None:
            key = 'Series_' + str(self.size())
        if isinstance(xdata, list):
            self.data.addSeries(key, xdata, ydata)
        else:
            self.data.addSeries(key, xdata.asarray(), ydata.asarray())
