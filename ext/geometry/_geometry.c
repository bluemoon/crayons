// gcc -dynamiclib  -I/usr/include/python2.3/ -lpython2.3 -o _geometry.dylib _geometry.c
// Rename .dylib to .so

#include <Python.h>
#include <math.h>
#include "types.h"

// FAST INVERSE SQRT
// Chris Lomont, http://www.math.purdue.edu/~clomont/Math/Papers/2003/InvSqrt.pdf
float _fast_inverse_sqrt(float x) { 
    float xhalf = 0.5f*x; 
    int i = *(int*)&x;
    i = 0x5f3759df - (i>>1);
    x = *(float*)&i;
    x = x*(1.5f-xhalf*x*x);
    return x; 
}
static PyObject *fast_inverse_sqrt(PyObject *self, PyObject *args) {
    double x;   
    if (!PyArg_ParseTuple(args, "d", &x))
        return NULL;
    x = _fast_inverse_sqrt(x);
    return Py_BuildValue("d", x);
}

// ANGLE
void _angle(double x0, double y0, double x1, double y1, double *a) {
    *a = atan2(y1-y0, x1-x0) / M_PI * 180;
}
static PyObject *angle(PyObject *self, PyObject *args) {
    double x0, y0, x1, y1, a;    
    if (!PyArg_ParseTuple(args, "dddd", &x0, &y0, &x1, &y1))
        return NULL;
    _angle(x0, y0, x1, y1, &a);
    return Py_BuildValue("d", a);
}

// DISTANCE
void _distance(double x0, double y0, double x1, double y1, double *d) {
    *d = sqrt((x1-x0)*(x1-x0) + (y1-y0)*(y1-y0));
}
static PyObject *distance(PyObject *self, PyObject *args) {
    double x0, y0, x1, y1, d;   
    if (!PyArg_ParseTuple(args, "dddd", &x0, &y0, &x1, &y1))
        return NULL;
    _distance(x0, y0, x1, y1, &d);
    return Py_BuildValue("d", d);
}

// COORDINATES
void _coordinates(double x0, double y0, double d, double a, double *x1, double *y1) {
    *x1 = x0 + cos(a/180*M_PI) * d;
    *y1 = y0 + sin(a/180*M_PI) * d;
}
static PyObject *coordinates(PyObject *self, PyObject *args) {
    double x0, y0, d, a, x1, y1;   
    if (!PyArg_ParseTuple(args, "dddd", &x0, &y0, &d, &a))
        return NULL;
    _coordinates(x0, y0, d, a, &x1, &y1);
    return Py_BuildValue("dd", x1, y1);
}

static PyObject *in_polygon(PyObject *self, PyObject *args){
  PyObject *VertX;
  PyObject *VertY;

  double TestX;
  double TestY;
  double nVerts;

  if (!PyArg_ParseTuple(args, "dddOO", &nVerts, &TestX, &TestY, &VertX, &VertY))
    return NULL;
  
  int  i, j = 0;
  long C = 0;

  for (i = 0, j = nVerts - 1; i < nVerts; j = i++){
    double vertYsubI  = PyFloat_AsDouble(PyList_GetItem(VertY, i));
    double vertYsubJ  = PyFloat_AsDouble(PyList_GetItem(VertY, j));

    double vertXsubI  = PyFloat_AsDouble(PyList_GetItem(VertX, i));
    double vertXsubJ  = PyFloat_AsDouble(PyList_GetItem(VertX, j));

    if (((vertYsubI > TestY) != (vertYsubJ > TestY)) && (TestX < (vertXsubJ - vertXsubI) * ((TestY - vertYsubI) / (vertYsubJ - vertYsubI) + vertXsubI))){
        C = !C;
      }
  }
  return PyBool_FromLong(C);
}

static void point_dealloc(point* self){
  Py_XDECREF(self->X);
  Py_XDECREF(self->Y);
  self->ob_type->tp_free((PyObject*)self);
}

static PyObject *point_new(PyObject* self_, PyObject *args, PyObject *kwds){
  PyObject *X, *Y;
  point* self = PyObject_NEW(point, &pointType);
  static char *kwlist[] = {"x", "y", NULL};
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist, &X, &Y))
    return -1; 
  
  self->X = X;
  self->Y = Y;

  return (PyObject *)self;
}


// Polygon Class
static void polygon_dealloc(polygon* self){
  Py_XDECREF(self->line_set);
  self->ob_type->tp_free((PyObject*)self);
}

static PyObject *polygon_new(PyObject *self_, PyObject *args, PyObject *kwds){
  polygon *self = PyObject_NEW(polygon, &polygonType);
  return (PyObject *)self;
}

static int polygon_init(polygon *self, PyObject *args, PyObject *kwds){
  PyObject *line_set = NULL;

  static char *kwlist[] = {"line_set", NULL};
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O", kwlist, &line_set))
    return -1; 

  if (line_set == NULL){
    self->line_set = PyList_New(0);
  }
  
  return 0;
} 


static PyObject *polygon_addLine(polygon* self, PyObject *args, PyObject *kwds){
  PyObject *P1;
  PyObject *P2;

  PyObject *line;

  static char *kwlist[] = {"point_1", "point_2", NULL};
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist, &P1, &P2))
    return NULL;
  
  line =  Py_BuildValue("(OO)", P1, P2);
  PyList_Append(self->line_set, line);

  return Py_None;
}

// Bezier Class
static void bezier_dealloc(bezier* self){
  Py_XDECREF(self->X0);
  Py_XDECREF(self->Y0);
  Py_XDECREF(self->X1);
  Py_XDECREF(self->Y1);
  Py_XDECREF(self->X2);
  Py_XDECREF(self->Y2);
  Py_XDECREF(self->X3);
  Py_XDECREF(self->Y3);

  self->ob_type->tp_free((PyObject*)self);
}

static PyObject *bezier_new(PyObject *self_, PyObject *args, PyObject *kwds){
  bezier *self = PyObject_NEW(bezier, &bezierType);
  double m = 0;

  self->X0 = PyFloat_FromDouble(m);
  self->Y0 = PyFloat_FromDouble(m);  
  self->X1 = PyFloat_FromDouble(m);
  self->Y1 = PyFloat_FromDouble(m);
  self->X2 = PyFloat_FromDouble(m);
  self->Y2 = PyFloat_FromDouble(m);
  self->X3 = PyFloat_FromDouble(m);
  self->Y3 = PyFloat_FromDouble(m);

  return (PyObject *)self;
}



static PyObject *bezier_setLine(bezier* self, PyObject *args, PyObject *kwds){
  point *P1;
  point *P2;
  point *P3;
  point *P4;


  PyObject *line;

  static char *kwlist[] = {"point_1", "point_2", "point_3", "point_4", NULL};
  
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O!O!O!", kwlist, &pointType, &P1, &pointType, &P2, &pointType, &P3, &pointType, &P4))
    return NULL;

  self->X0 = P1->X;
  self->Y0 = P1->Y;
  self->X1 = P2->X;
  self->Y1 = P2->Y;
  self->X2 = P3->X;
  self->Y2 = P3->Y;
  self->X3 = P4->X;
  self->Y3 = P4->Y;

  return Py_None;
}

static PyObject *bezier_curve_point(bezier* self, PyObject *args){
  double t;
  double mint, X01, Y01, X12, Y12, X23, Y23, out_c1x, out_c1y, out_c2x, out_c2y, out_x, out_y;

  if (!PyArg_ParseTuple(args, "f", &t))
        return NULL;
  
  double X0 = PyFloat_AsDouble(self->X0);
  double Y0 = PyFloat_AsDouble(self->Y0);
  double X1 = PyFloat_AsDouble(self->X1);
  double Y1 = PyFloat_AsDouble(self->Y1);
  double X2 = PyFloat_AsDouble(self->X2);
  double Y2 = PyFloat_AsDouble(self->Y2);
  double X3 = PyFloat_AsDouble(self->X3);
  double Y3 = PyFloat_AsDouble(self->Y3);

  mint  = 1 - t;
  X01 = X0 * mint + X1 * t;
  Y01 = Y0 * mint + Y1 * t;
  X12 = X1 * mint + X2 * t;
  Y12 = Y1 * mint + Y2 * t;
  X23 = X2 * mint + X3 * t;
  Y23 = Y2 * mint + Y3 * t;
  
  out_c1x = X01 * mint + X12 * t;
  out_c1y = Y01 * mint + Y12 * t;
  out_c2x = X12 * mint + X23 * t;
  out_c2y = Y12 * mint + Y23 * t;
  out_x = out_c1x * mint + out_c2x * t;
  out_y = out_c1y * mint + out_c2y * t;

  return Py_BuildValue("(dddddddddd)", out_x, out_y, out_c1x, out_c1y, out_c2x, out_c2y, X01, Y01, X23, Y23);
  
}


void _linelength(double x0, double y0, double x1, double y1,
                double *out_length
                )
{
    double a, b;
    a = pow(fabs(x0 - x1), 2);
    b = pow(fabs(y0 - y1), 2);
    *out_length = sqrt(a + b);
}




void _curvelength(double x0, double y0, double x1, double y1, 
                  double x2, double y2, double x3, double y3, int n, 
                  double *out_length
                  )
{
    double xi, yi, t, c;
    double pt_x, pt_y, pt_c1x, pt_c1y, pt_c2x, pt_c2y;
    int i;
    double length = 0;
    
    xi = x0;
    yi = y0;
    
    for (i=0; i<n; i++) {
        t = 1.0 * (i+1.0) / (float) n;
        
        _curvepoint(t, x0, y0, x1, y1, x2, y2, x3, y3,
                    &pt_x, &pt_y, &pt_c1x, &pt_c1y, &pt_c2x, &pt_c2y);
        c = sqrt(pow(fabs(xi-pt_x), 2.0) + pow(fabs(yi-pt_y), 2.0));
        length += c;
        xi = pt_x;
        yi = pt_y; 
    }
    *out_length = length;
}

static PyObject *point_linepoint(point *self, PyObject *args){
    double t, X0, Y0, X1, Y1;
    double out_x, out_y;

    point *P1;

    if (!PyArg_ParseTuple(args, "dO!:linepoint", &t, &pointType, &P1))
        return NULL;

    X0 = PyFloat_AsDouble(self->X);
    Y0 = PyFloat_AsDouble(self->Y);
    X1 = PyFloat_AsDouble(P1->X);
    Y1 = PyFloat_AsDouble(P1->Y);
    
    out_x = X0 + t * (X1-X0);
    out_y = Y0 + t * (Y1-Y0);

    return Py_BuildValue("dd", out_x, out_y);
}

static PyObject *cPathmatics_linelength(PyObject *self, PyObject *args){
    double x0, y0, x1, y1;
    double out_length;
    
    if (!PyArg_ParseTuple(args, "dddd", &x0, &y0, &x1, &y1))
        return NULL;
        
    _linelength(x0, y0, x1, y1,
                &out_length);

    return Py_BuildValue("d", out_length);
}



PyMODINIT_FUNC initcGeometry(void){ 
    PyObject *m;

    polygonType.ob_type = &PyType_Type;
    pointType.ob_type   = &PyType_Type;
    bezierType.ob_type  = &PyType_Type;
    
    if (PyType_Ready(&pointType) < 0)
        return;

    if (PyType_Ready(&polygonType) < 0)
        return;

    if (PyType_Ready(&bezierType) < 0)
        return;


    m = Py_InitModule("cGeometry", geometry_methods); 
    if (m == NULL)
        return;
    
}


