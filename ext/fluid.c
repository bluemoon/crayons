#include <rfftw.h>
#include <stdio.h>
#include <Python.h>
#include "structmember.h"

typedef struct {
  PyObject_HEAD
  double * u;
  double * v;
  double * u0;
  double * v0;
  int dim;
  double scale;
} fluid_object;

static PyObject *cFluid_new(PyObject *self_, PyObject *args);
static void fluid_dealloc(fluid_object* self);
static PyObject *cFluid_add_force(fluid_object *self, PyObject *args);
static PyObject *cFluid_vectors(fluid_object *self, PyObject *args);
static PyObject *cFluid_solver(fluid_object *self, PyObject *args);

static PyMethodDef fluid_methods[] = {
    { "add_force", (PyCFunction) cFluid_add_force, METH_VARARGS|METH_KEYWORDS},
    { "vectors", (PyCFunction) cFluid_vectors, METH_VARARGS|METH_KEYWORDS},
    { "solve", (PyCFunction) cFluid_solver, METH_VARARGS|METH_KEYWORDS},
    {NULL, NULL}
};

static PyTypeObject fluidType = {
  PyObject_HEAD_INIT(NULL)
  0,                           /*ob_size*/
  "",           /*tp_name*/
  sizeof(fluidType),                /*tp_basicsize*/
  0,                           /*tp_itemsize*/
  (destructor)fluid_dealloc,    /*tp_dealloc*/
  0,                  /*tp_print*/
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
  "",               /* tp_doc */
  0, //(traverseproc)path_traverse, /* tp_traverse */
  0, //(inquiry)path_clear,         /* tp_clear */
  0,		               /* tp_richcompare */
  0,		               /* tp_weaklistoffset */
  0,		               /* tp_iter */
  0,		               /* tp_iternext */
  fluid_methods,                /* tp_methods */
  0,                /* tp_members */
  0,                           /* tp_getset */
  0,                           /* tp_base */
  0,                           /* tp_dict */
  0,                           /* tp_dict */
  0,                           /* tp_descr_get */
  0,                           /* tp_descr_set */
  0,                           /* tp_dictoffset */
  0,         /* tp_init */
  0,                           /* tp_alloc */
  cFluid_new,                    /* tp_new */
};

static rfftwnd_plan plan_rc, plan_cr;

void init_FFT(int n){
  plan_rc = rfftw2d_create_plan(n, n, FFTW_REAL_TO_COMPLEX, FFTW_IN_PLACE);
  plan_cr = rfftw2d_create_plan(n, n, FFTW_COMPLEX_TO_REAL, FFTW_IN_PLACE);
}


#define FFT(s,u)\
  if (s==1) rfftwnd_one_real_to_complex(plan_rc, (fftw_real *)u, (fftw_complex *)u); \
  else rfftwnd_one_complex_to_real(plan_cr, (fftw_complex *)u, (fftw_real *)u);
#define floor(x) ((x)>=0.0?((int)(x)):(-((int)(1-(x)))))

void stable_solve(int n, float * u, float * v, float * u0, float * v0, float visc, float dt){
  float x, y, x0, y0, f, r, U[2], V[2], s, t;
  int i, j, i0, j0, i1, j1;

  for (i=0; i<n*n; i++ ){
    u[i] += dt*u0[i]; 
    u0[i] = u[i];
    v[i] += dt*v0[i]; 
    v0[i] = v[i];
  }

  for (x=0.5/n, i=0; i<n; i++,x+=1.0/n){
    for (y=0.5/n,j=0; j<n; j++,y+=1.0/n){
      x0 = n*(x-dt*u0[i+n*j])-0.5; 
      y0 = n*(y-dt*v0[i+n*j])-0.5;
      i0 = floor(x0); 
      s = x0-i0; 
      i0 = (n+(i0%n))%n; 
      i1 = (i0+1)%n;
      j0 = floor(y0); 
      t = y0-j0; 
      j0 = (n+(j0%n))%n; 
      j1 = (j0+1)%n;

      u[i+n*j] = (1-s)*((1-t)*u0[i0+n*j0]+t*u0[i0+n*j1])+
        s *((1-t)*u0[i1+n*j0]+t*u0[i1+n*j1]);
      
      v[i+n*j] = (1-s)*((1-t)*v0[i0+n*j0]+t*v0[i0+n*j1])+
        s *((1-t)*v0[i1+n*j0]+t*v0[i1+n*j1]);
    }
  }
  for(i=0; i<n; i++){
    for(j=0; j<n; j++){
      u0[i+(n+2)*j] = u[i+n*j]; 
      v0[i+(n+2)*j] = v[i+n*j];
    }
  }

  FFT(1, u0);
  FFT(1, v0);
  
  for (i=0; i<=n; i+=2){
    x = 0.5*i;
    for (j=0; j<n; j++){              
      y = j<=n/2 ? j : j-n;
      r = x*x+y*y;                
      if (r == 0.0) continue;                
      f = exp(-r*dt*visc);
      U[0] = u0[i +(n+2)*j]; 
      V[0] = v0[i +(n+2)*j];                
      U[1] = u0[i+1+(n+2)*j]; 
      V[1] = v0[i+1+(n+2)*j];

      u0[i +(n+2)*j]  = f*( (1-x*x/r)*U[0]-x*y/r *V[0]);
      u0[i+1+(n+2)*j] = f*((1-x*x/r)*U[1]-x*y/r *V[1]);
      v0[i+ (n+2)*j]  = f*(-y*x/r*U[0]+(1-y*y/r)*V[0]);
      v0[i+1+(n+2)*j] = f*(-y*x/r*U[1]+(1-y*y/r)*V[1]);
    }
  }
  FFT(-1, u0); 
  FFT(-1, v0);

  f = 1.0/(n*n);
  for (i=0; i<n; i++){
    for (j=0; j<n; j++){
      u[i+n*j] = f*u0[i+(n+2)*j]; 
      v[i+n*j] = f*v0[i+(n+2)*j];
    }
  }
}

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


static PyObject *cFluid_solver(fluid_object *self, PyObject *args){
  float dt = 0.01;
  float visc = 0.001;
  stable_solve(self->dim, self->u, self->v, self->u0, self->v0, visc, dt);

  Py_INCREF(Py_None);
  return Py_None;
}
static PyObject *cFluid_new(PyObject *self_, PyObject *args){
  int dim, i;
  int height, width = 0;

  if (!PyArg_ParseTuple(args, "i|ii", &dim, &width, &height))
    return NULL;

  fluid_object *self;
  self = (fluid_object *)PyObject_NEW(fluid_object, &fluidType);
  self->u  = (double *)malloc((dim * dim) * sizeof(double));
  self->v  = (double *)malloc((dim * dim) * sizeof(double));
  self->u0 = (double *)malloc((dim * 2 * (dim/2+1)) * sizeof(double));
  self->v0 = (double *)malloc((dim * 2 * (dim/2+1)) * sizeof(double));

  init_FFT(dim);
  for (i = 0; i < dim * dim; i++) {
    self->u[i] = self->v[i] = self->u0[i] = self->v0[i] = 0.0f;
  }

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
static PyMethodDef fluidMethods[] = {
    { "fluid", (PyCFunction) cFluid_new, METH_VARARGS|METH_KEYWORDS},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC initcFluid(void){
    PyObject *m;

    fluidType.ob_type = &PyType_Type;
    if (PyType_Ready(&fluidType) < 0)
        return;
    m = Py_InitModule("cFluid", fluidMethods);

}
