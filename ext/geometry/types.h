#include "Python.h"
#include "structmember.h"

typedef struct {
    PyObject_HEAD
    PyObject *X;
    PyObject *Y;
} point;

typedef struct {
    PyObject_HEAD
    PyObject *line_set;
} polygon;

typedef struct {
  PyObject_HEAD
  PyObject *X0;
  PyObject *Y0;
  PyObject *X1;
  PyObject *Y1;
  PyObject *X2;
  PyObject *Y2;
  PyObject *X3;
  PyObject *Y3;


} bezier;


// Points "Class"
static int        point_init(point *self, PyObject *args, PyObject *kwds);
static void       point_dealloc(point* self);
static PyObject  *point_new(PyObject* self_, PyObject *args, PyObject *kwds);
static PyObject  *point_linepoint(point *self, PyObject *args);


// Polygon Class
static int        polygon_init(polygon *self, PyObject *args, PyObject *kwds);
static void       polygon_dealloc(polygon* self);
static PyObject  *polygon_new(PyObject *self_, PyObject *args, PyObject *kwds);
static PyObject  *polygon_addLine(polygon* self, PyObject *args, PyObject *kwds);

// Bezier class
static int        bezier_init(bezier *self, PyObject *args, PyObject *kwds);
static void       bezier_dealloc(bezier* self);
static PyObject  *bezier_new(PyObject *self_, PyObject *args, PyObject *kwds);
static PyObject  *bezier_setLine(bezier* self, PyObject *args, PyObject *kwds);
static PyObject  *bezier_curve_point(bezier* self, PyObject *args);

static PyObject  *fast_inverse_sqrt(PyObject *self, PyObject *args);
static PyObject  *angle(PyObject *self, PyObject *args);
static PyObject  *coordinates(PyObject *self, PyObject *args);
static PyObject  *in_polygon(PyObject *self, PyObject *args);
static PyObject  *distance(PyObject *self, PyObject *args);


static PyMethodDef point_methods[] = {
  { "linepoint", (PyCFunction)point_linepoint, METH_VARARGS, ""},
    {NULL}  /* Sentinel */
};

static PyMemberDef point_members[] = {
  {"X", T_OBJECT_EX, offsetof(point, X), 0, ""},
  {"Y", T_OBJECT_EX, offsetof(point, Y), 0, ""},
  {NULL}  /* Sentinel */
};

static PyTypeObject pointType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "cGeometry.point",                   /*tp_name*/
    sizeof(point),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)point_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "point object",          /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    point_methods,             /* tp_methods */
    point_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,
    0,
    0,
    //(initproc)point_init,      /* tp_init */
    //0,                         /* tp_alloc */
    //point_new,                 /* tp_new */
};

static PyMethodDef polygon_methods[] = {
  {"add_line", (PyCFunction)polygon_addLine, METH_VARARGS|METH_KEYWORDS, ""},
    {NULL}  /* Sentinel */
};

static PyMemberDef polygon_members[] = {
  {"line_set", T_OBJECT_EX, offsetof(polygon, line_set), 0, ""},
  {NULL}  /* Sentinel */
};

static PyTypeObject polygonType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "cGeometry.polygon",       /*tp_name*/
    sizeof(polygon),           /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)polygon_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "polygon object",          /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    polygon_methods,           /* tp_methods */
    polygon_members,           /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                         /* tp_init */
    0,                         /* tp_alloc */
    polygon_new,               /* tp_new */
};
// Bezier
static PyMethodDef bezier_methods[] = {
  {"add_line",    (PyCFunction)bezier_setLine, METH_VARARGS|METH_KEYWORDS, ""},
  {"curve_point", (PyCFunction)bezier_curve_point, METH_VARARGS|METH_KEYWORDS, ""},
    {NULL}  /* Sentinel */
};

static PyMemberDef bezier_members[] = {
  {"X0", T_OBJECT_EX, offsetof(bezier, X0), 0, ""},
  {"Y0", T_OBJECT_EX, offsetof(bezier, Y0), 0, ""},
  {"X1", T_OBJECT_EX, offsetof(bezier, X1), 0, ""},
  {"Y1", T_OBJECT_EX, offsetof(bezier, Y1), 0, ""},
  {"X2", T_OBJECT_EX, offsetof(bezier, X2), 0, ""},
  {"Y2", T_OBJECT_EX, offsetof(bezier, Y2), 0, ""},
  {NULL}  /* Sentinel */
};

static PyTypeObject bezierType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "cGeometry.bezier",       /*tp_name*/
    sizeof(bezier),           /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)bezier_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "polygon object",          /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    bezier_methods,           /* tp_methods */
    bezier_members,           /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                         /* tp_init */
    0,                         /* tp_alloc */
    bezier_new,               /* tp_new */
};


static PyMethodDef geometry_methods[]={ 
    { "fast_inverse_sqrt", fast_inverse_sqrt, METH_VARARGS },
    { "angle", angle, METH_VARARGS }, 
    { "distance", distance, METH_VARARGS }, 
    { "coordinates", coordinates, METH_VARARGS },  
    { "in_polygon", in_polygon, METH_VARARGS, "Test whether or not a point is in a polygon"},  
    { "point", (PyCFunction) point_new, METH_VARARGS},
    { "polygon", (PyCFunction) polygon_new, METH_VARARGS|METH_KEYWORDS},
    { "bezier", (PyCFunction) bezier_new, METH_VARARGS|METH_KEYWORDS},
    { NULL, NULL, 0, NULL}
};
