#include <rfftw.h>
#include <stdio.h>
#include <Python.h>
#include "fluid2d.h"
#include "structmember.h"

/// Defines
#define FFT(self, s, u)                                                  \
  if (s==1) rfftwnd_one_real_to_complex(self->plan_rc, (fftw_real *)u, (fftw_complex *)u); \
  else rfftwnd_one_complex_to_real(self->plan_cr, (fftw_complex *)u, (fftw_real *)u);
#define floor(x) ((x)>=0.0?((int)(x)):(-((int)(1-(x)))))


/// Struct for python object
typedef struct {
  PyObject_HEAD
  int      dim;
  double   scale;
  Fluid2d *fluid;

} fluid_object;

/// Definitions
static PyObject *cFluid_new(PyObject *self_, PyObject *args);
static void fluid_dealloc(fluid_object* self);
static PyObject *cFluid_add_force(fluid_object *self, PyObject *args);
static PyObject *cFluid_vectors(fluid_object *self, PyObject *args);
static PyObject *cFluid_solver(fluid_object *self, PyObject *args);

static PyMethodDef fluid_methods[] = {
  { "add_force", (PyCFunction) cFluid_add_force, METH_VARARGS|METH_KEYWORDS},
  { "vectors",   (PyCFunction) cFluid_vectors,   METH_VARARGS|METH_KEYWORDS},
  { "solve",     (PyCFunction) cFluid_solver,    METH_VARARGS|METH_KEYWORDS},
  {NULL, NULL}
};

static PyMethodDef fluidMethods[] = {
    { "fluid", (PyCFunction) cFluid_new, METH_VARARGS|METH_KEYWORDS},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};



static PyTypeObject fluidType = {
  PyObject_HEAD_INIT(NULL)
  0,                           /*ob_size*/
  "",                          /*tp_name*/
  sizeof(fluidType),           /*tp_basicsize*/
  0,                           /*tp_itemsize*/
  (destructor)fluid_dealloc,   /*tp_dealloc*/
  0,                           /*tp_print*/
  0,                           /*tp_getattr*/
  0,                           /*tp_setattr*/
  0,                           /*tp_compare*/
  0,                           /*tp_repr*/
  0,                           /*tp_as_number*/
  0,                           /*tp_as_sequence*/
  0,                           /*tp_as_mapping*/
  0,                           /*tp_hash */
  0,                           /*tp_call*/
  0,                           /*tp_str*/
  0,                           /*tp_getattro*/
  0,                           /*tp_setattro*/
  0,                           /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /*tp_flags*/
  "",                          /* tp_doc */
  0,                           /* tp_traverse */
  0,                           /* tp_clear */
  0,		               /* tp_richcompare */
  0,		               /* tp_weaklistoffset */
  0,		               /* tp_iter */
  0,		               /* tp_iternext */
  fluid_methods,               /* tp_methods */
  0,                           /* tp_members */
  0,                           /* tp_getset */
  0,                           /* tp_base */
  0,                           /* tp_dict */
  0,                           /* tp_dict */
  0,                           /* tp_descr_get */
  0,                           /* tp_descr_set */
  0,                           /* tp_dictoffset */
  0,                           /* tp_init */
  0,                           /* tp_alloc */
  cFluid_new,                  /* tp_new */
};

static PyObject *cFluid_add_force(fluid_object *self, PyObject *args){
  int x, y;
  double dx, dy;

  if (!PyArg_ParseTuple(args, "iidd", &x, &y, &dx, &dy))
    return NULL;
  
  self->u0[y * self->dim + x] += dx;
  self->v0[y * self->dim + x] += dy;

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject *cFluid_solve(fluid_object *self, PyObject *args){
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *cFluid_new(PyObject *self_, PyObject *args){
  int dim, i;

  int height  = 0;
  int width   = 0;
  float dt    = 0.01;
  float visc  = 0.001;


  if (!PyArg_ParseTuple(args, "i|ii", &dim, &width, &height))
    return NULL;

  Fluid2D *fluid = new Fluid2D(dim, dt, visc);
  fluid_object *self;
  
  self = (fluid_object *)PyObject_NEW(fluid_object, &fluidType);
  self->fluid = fluid;

  self->dim = dim;
  if (height > 0 && width > 0){
    double hn = height/(dim+1);
    double wn = width/(dim+1);
    double scale = (height+width)/2;
    self->scale = scale;
  } else {
    self->scale = 0.08;
  }

  return (PyObject *)self;
}

static void fluid_dealloc(fluid_object* self){
  free(self->u);
  free(self->v);
  free(self->u0);
  free(self->v0);
}

static PyObject *cFluid_vectors(fluid_object *self, PyObject *args){
  int i;
  PyObject *V_tmp  = PyList_New(0);
  PyObject *U_tmp  = PyList_New(0);
  PyObject *V0_tmp = PyList_New(0);
  PyObject *U0_tmp = PyList_New(0);

  for(i=0; i<self->dim; i++){
    PyList_Append(U_tmp, PyFloat_FromDouble(self->u[i]*self->scale));
  }
  for(i=0; i<self->dim; i++){
    PyList_Append(V_tmp, PyFloat_FromDouble(self->v[i]*self->scale));
  }
  for(i=0; i<self->dim; i++){
    PyList_Append(U0_tmp, PyFloat_FromDouble(self->u0[i]*self->scale));
  }
  for(i=0; i<self->dim; i++){
    PyList_Append(V0_tmp, PyFloat_FromDouble(self->v0[i]*self->scale));
  }

  return Py_BuildValue("OOOO", U_tmp, V_tmp, U0_tmp, V0_tmp);
}

PyMODINIT_FUNC initcFluid(void){
    PyObject *m;

    fluidType.ob_type = &PyType_Type;
    if (PyType_Ready(&fluidType) < 0)
        return;
    m = Py_InitModule("cFluid", fluidMethods);

}
