#include <rfftw.h>
#include <stdio.h>
#include <math.h>
#include <Python.h>

#include "structmember.h"


/// Defines
#define FFT(s, u)                                                  \
  if (s==1) rfftwnd_one_real_to_complex(self->plan_rc, (fftw_real *)u, (fftw_complex*)u); \
  else rfftwnd_one_complex_to_real(self->plan_cr, (fftw_complex *)u, (fftw_real *)u);
#define floor(x) ((x)>=0.0?((int)(x)):(-((int)(1-(x)))))



/// Struct for python object
typedef struct {
  PyObject_HEAD
  // velocity field
  double *u, *v, *u0, *v0;
  // user-induced forces
  double *u_u0, *u_v0;
  // density field for colour r
  double *r, *r0;
  // density field for colour g  
  double *g, *g0;
  // density field for colour b
  double *b, *b0;

  float    dt;
  int      dim;
  double   scale;
  double   visc;

  rfftwnd_plan plan_rc;
  rfftwnd_plan plan_cr;

} fluid_object;

static rfftwnd_plan plan_rc;
static rfftwnd_plan plan_cr;

/// Definitions
static PyObject *cFluid_new(PyObject *self_, PyObject *args, PyObject *kwargs);
static void fluid_dealloc(fluid_object* self);
static PyObject *cFluid_add_force(fluid_object *self, PyObject *args);
static PyObject *cFluid_vectors(fluid_object *self, PyObject *args);
static PyObject *cFluid_RGB(fluid_object *self, PyObject *args);
static PyObject *cFluid_solver(fluid_object *self, PyObject *args);

static PyMethodDef fluid_methods[] = {
  { "add_force", (PyCFunction) cFluid_add_force, METH_VARARGS|METH_KEYWORDS},
  { "vectors",   (PyCFunction) cFluid_vectors,   METH_VARARGS|METH_KEYWORDS},
  { "rgb",       (PyCFunction) cFluid_RGB,   METH_VARARGS|METH_KEYWORDS},
  { "solve",     (PyCFunction) cFluid_solver,    METH_VARARGS|METH_KEYWORDS},
  {NULL, NULL}
};

static PyMethodDef fluidMethods[] = {
    { "fluid", (PyCFunction) cFluid_new,  METH_VARARGS|METH_KEYWORDS},
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



void init_FFT(fluid_object *self, int n){
  self->plan_rc = rfftw2d_create_plan(n, n, FFTW_REAL_TO_COMPLEX, FFTW_IN_PLACE);
  self->plan_cr = rfftw2d_create_plan(n, n, FFTW_COMPLEX_TO_REAL, FFTW_IN_PLACE);
}

void new_solve(fluid_object *self, float visc){
  double *u   = self->u;
  double *v   = self->v;
  double *u0  = self->u0;
  double *v0  = self->v0;
  int     n   = self->dim;
  float   dt  = self->dt;

  double x, y, x0, y0, f, r, U[2], V[2], s, t;
  int i, j, i0, j0, i1, j1;
  
  for (i=0; i<n*n; i++){
      u[i] += dt*u0[i]; 
      u0[i] = u[i];
      v[i] += dt*v0[i]; 
      v0[i] = v[i];
  }
  
  for (x=0.5f/n, i=0; i<n; i++,x+=1.0f/n){
    for (y=0.5f/n, j=0; j<n; j++,y+=1.0f/n){
      x0 = n*(x-dt*u0[i+n*j])-0.5f; 
      y0 = n*(y-dt*v0[i+n*j])-0.5f;
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

  for (i=0; i<n; i++)
    for (j=0; j<n; j++){ 
      u0[i+(n+2)*j] = u[i+n*j]; 
      v0[i+(n+2)*j] = v[i+n*j];
    }
  
  FFT(1, u0);
  FFT(1, v0);
  
  for (i=0; i<=n; i+=2){
      x = 0.5f*i;
      for (j=0; j<n; j++){
          y = j<=n/2 ? (double)j : (double)j-n;
          r = x*x+y*y;
          if ( r==0.0f ) continue;
          f = (double)exp(-r*dt*visc);
          U[0] = u0[i  +(n+2)*j]; V[0] = v0[i  +(n+2)*j];
          U[1] = u0[i+1+(n+2)*j]; V[1] = v0[i+1+(n+2)*j];
          
          u0[i  +(n+2)*j] = f*( (1-x*x/r)*U[0]     -x*y/r *V[0] );
          u0[i+1+(n+2)*j] = f*( (1-x*x/r)*U[1]     -x*y/r *V[1] );
          v0[i+  (n+2)*j] = f*(   -y*x/r *U[0] + (1-y*y/r)*V[0] );
          v0[i+1+(n+2)*j] = f*(   -y*x/r *U[1] + (1-y*y/r)*V[1] );
        }    
    }
  
  FFT(-1, u0); 
  FFT(-1, v0);
  
  f = 1.0/(n*n);
  for ( i=0 ; i<n ; i++ )
    for ( j=0 ; j<n ; j++ )
      {
        u[i+n*j] = f*u0[i+(n+2)*j]; 
        v[i+n*j] = f*v0[i+(n+2)*j]; 
      }
}
void stable_solve(fluid_object *self, float visc){
  double *u   = self->u;
  double *v   = self->v;
  double *u0  = self->u0;
  double *v0  = self->v0;
  int     n   = self->dim;
  float   dt  = self->dt;

  
  double x, y, x0, y0, f, r, U[2], V[2], s, t;
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
void diffuse_matter(fluid_object *self){
  double x, y, x0, y0, s, t;
  int i, j, i0, j0, i1, j1;
  int n = self->dim;

  for (x=0.5f/n,i=0; i<n; i++,x+=1.0f/n) {
    for (y=0.5f/n,j=0; j<n; j++,y+=1.0f/n) {
      x0 = n*(x-self->dt*self->u[i+n*j])-0.5f; 
      y0 = n*(y-self->dt*self->v[i+n*j])-0.5f;
      i0 = floor(x0);
      s = x0-i0;
      i0 = (n+(i0%n))%n;
      i1 = (i0+1)%n;
      j0 = floor(y0);
      t = y0-j0;
      j0 = (n+(j0%n))%n;
      j1 = (j0+1)%n;

      self->r[i+n*j] = (1-s)*((1-t)*self->r0[i0+n*j0]+t*self->r0[i0+n*j1])+
        s *((1-t)*self->r0[i1+n*j0]+t*self->r0[i1+n*j1]);

      self->g[i+n*j] = (1-s)*((1-t)*self->g0[i0+n*j0]+t*self->g0[i0+n*j1])+
        s *((1-t)*self->g0[i1+n*j0]+t*self->g0[i1+n*j1]);

      self->b[i+n*j] = (1-s)*((1-t)*self->b0[i0+n*j0]+t*self->b0[i0+n*j1])+
        s *((1-t)*self->b0[i1+n*j0]+t*self->b0[i1+n*j1]);
    }   
  }

}
void drag(fluid_object *self, double nx, double ny, double dnx, double dny, float rfactor, float gfactor, float bfactor){
  int     xi;
  int     yi;
  double  len;
  int     X, Y;
  int n = self->dim;

  
  //printf("nx:%f ny:%f\n", nx, ny);
  xi = (int)floor((float)(n + 1) * nx);
  yi = (int)floor((float)(n + 1) * ny);
  //printf("xi:%d yi:%d\n", xi, yi);

  X = xi;
  Y = yi;

  if (X > (n - 1)) {
    X = n - 1;
  }
  if (Y > (n - 1)) {
    Y = n - 1;
  }
  if (X < 0) {
    X = 0;
  }
  if (Y < 0) {
    Y = 0;
  }
  //printf("dnx:%f dny:%f\n", self->u_u0[Y*n+X], self->u_v0[Y*n+X]);
  // Add force at the cursor location
  len = sqrt(dnx * dnx + dny * dny);
  if (len != 0.0){ 
      dnx *= 0.1 / len;
      dny *= 0.1 / len;
  }

  //printf("X:%d Y:%d dnx:%f dny:%f pos:%d\n", X, Y, dnx, dny, (Y*n+X));
  self->u_u0[Y * n + X] += dnx;
  self->u_v0[Y * n + X] += dny;

  self->r[Y * n + X] = 10.0f * rfactor; 
  self->r0[Y * n + X] = self->r[Y * n + X];
  self->g[Y * n + X] = 10.0f * gfactor; 
  self->g0[Y * n + X] = self->g[Y * n + X];
  self->b[Y * n + X] = 10.0f * bfactor; 
  self->b0[Y * n + X] = self->b[Y * n + X];

}



static PyObject *zero_boundary(fluid_object *self, PyObject *args){
  int i;
  int n = self->dim;
  for(i=0; i<n; i++){
    // bottom edge
    self->u[0*n + i] = 0.0;
    self->v[0*n + i] = 0.0;
    self->u0[0*n + i] = 0.0;
    self->v0[0*n + i] = 0.0;
    // top edge
    self->u[(n-1)*n + i] = 0.0;
    self->v[(n-1)*n + i] = 0.0;
    self->u0[(n-1)*n + i] = 0.0;
    self->v0[(n-1)*n + i] = 0.0;
    // left edge
    self->u[i*n + 0] = 0.0;
    self->v[i*n + 0] = 0.0;
    self->u0[i*n + 0] = 0.0;
    self->v0[i*n + 0] = 0.0;
    // right edge
    self->u[i*n + n-1] = 0.0;
    self->v[i*n + n-1] = 0.0;
    self->u0[i*n + n-1] = 0.0;
    self->v0[i*n + n-1] = 0.0;
  }
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject *cFluid_add_force(fluid_object *self, PyObject *args){
  int n = self->dim;
  float  accel_start = 0.0f;
  float  accel_end   = 0.1f;
  float  f, x0, y0;
  double x1;
  double y1;
  double x2;
  double y2;
  double dx, dy;
  float r, g, b;

  r = (float) (rand() % 255);
  b = (float) (rand() % 255);
  g = (float) (rand() % 255);
  
  if (!PyArg_ParseTuple(args, "dddd|fffff", &x1, &y1, &x2, &y2, &accel_start, &accel_end, &r, &g, &b))
    return NULL;

  dx = x2-x1;
  dy = y2-y1;

  if (x2 < x1) dx = x1-x2;
  if (y2 < y1) dy = y1-y2;

  if(1){
    printf("X:%f Y:%f dX:%f dY:%f \n", x1, y1, dx, dy);
  }

  double k = 0.0;
  double c = sqrt((dx*dx) + (dy*dy));
  while(k <= 100.0){
    double cx = x1 - ((k/100.0) * (x1 - x2));
    double cy = y1 - ((k/100.0) * (y1 - y2));
    //printf("cx:%f cy:%f\n", cx, cy);
    double cdx = accel_end - ((k/100.0) * (accel_end - accel_start));
    double cdy = accel_end - ((k/100.0) * (accel_end - accel_start));
    // don't draw the last position twice
    if (cx == x2 && cy == y2 ) { break; }
    drag(self, cx, cy, cdx, cdy, r, g, b);
    k +=  1/(c*2);
  }

  Py_INCREF(Py_None);
  return Py_None;
}


void vector_print(fluid_object *self){
  int i, j, idx;
  for (i = 0; i < self->dim; i++) {
    for (j = 0; j < self->dim; j++) {
      idx = (j * self->dim) + i;
      printf("vector:%d x1:%d y1:%d x2:%f y2:%f\n", i*(j+1), i,  j, (i+(1000*self->u[idx])), (j+(1000*self->v[idx])));
    }
  }
}

static PyObject *cFluid_solver(fluid_object *self, PyObject *args){
  float dt = 0.001f;
  int i;

  for (i = 0; i < (self->dim * self->dim); i++) {
    self->u_u0[i] *= 0.85;
    self->u_v0[i] *= 0.85;
    self->u0[i] = self->u_u0[i];
    self->v0[i] = self->u_v0[i];
    self->r0[i] = 0.995 * self->r[i]; 
    self->g0[i] = 0.995 * self->g[i]; 
    self->b0[i] = 0.995 * self->b[i]; 
  }
  diffuse_matter(self);
  new_solve(self, self->visc);
  zero_boundary(self, args);
  //vector_print(self);

  self->dt += dt;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *cFluid_new(PyObject *self_, PyObject *args, PyObject *kwargs){
  int dim, i;
  int height, width = 0;
  double visc;
  visc = 0.001;

  fluid_object *self;
  self = (fluid_object *)PyObject_NEW(fluid_object, &fluidType);
  

  if (!PyArg_ParseTuple(args,"i|d", &dim, &visc))
    return NULL;

  self->dim = dim;
  self->visc = visc;
  // Make the delta time 0.0 so it doesnt make a NaN
  self->dt   = 0.0f;
  init_FFT(self, self->dim);

  self->u     = (double *)malloc((dim * 2 * (dim/2+1)) * sizeof(double));
  self->v     = (double *)malloc((dim * 2 * (dim/2+1)) * sizeof(double));
  self->u0    = (double *)malloc((dim * 2 * (dim/2+1)) * sizeof(double));
  self->v0    = (double *)malloc((dim * 2 * (dim/2+1)) * sizeof(double));
  self->u_u0  = (double *)malloc((dim * 2 * (dim/2+1)) * sizeof(double));
  self->u_v0  = (double *)malloc((dim * 2 * (dim/2+1)) * sizeof(double));

  self->r   = (double *)malloc((dim * dim) * sizeof(double));
  self->r0  = (double *)malloc((dim * dim) * sizeof(double));
  self->g   = (double *)malloc((dim * dim) * sizeof(double));
  self->g0  = (double *)malloc((dim * dim) * sizeof(double));
  self->b   = (double *)malloc((dim * dim) * sizeof(double));
  self->b0  = (double *)malloc((dim * dim) * sizeof(double));

  /// Initialize the table
  for (i = 0; i < (dim * dim); i++) {
    self->u[i] = self->v[i] = self->u0[i] = self->v0[i] = self->u_u0[i] = \
      self->u_v0[i] = self->r[i] = self->r0[i] = self->g[i] = self->g0[i] =\
      self->b[i] = self->b0[i] = 0.0;
  }

  if (height > 0 && width > 0){
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
  free(self->u_u0);
  free(self->u_v0);
  free(self->r);
  free(self->g);
  free(self->b);
  free(self->r0);
  free(self->g0);
  free(self->b0);
}



static PyObject *cFluid_RGB(fluid_object *self, PyObject *args){
  int i;
  PyObject *RGB_tmp  = PyList_New(0);
  int n = (self->dim * self->dim);

  for(i=0; i<n; i++){
    PyObject *tmp  = PyList_New(0);
    PyList_Append(tmp, PyFloat_FromDouble((double)self->r[i]/255.0));
    PyList_Append(tmp, PyFloat_FromDouble((double)self->g[i]/255.0));
    PyList_Append(tmp, PyFloat_FromDouble((double)self->b[i]/255.0));
    PyList_Append(RGB_tmp, tmp);
    
  }
  return RGB_tmp;
}

static PyObject *cFluid_vectors(fluid_object *self, PyObject *args){
  int i;
  PyObject *V_tmp  = PyList_New(0);
  PyObject *U_tmp  = PyList_New(0);
  int n = (self->dim * self->dim);

  for(i=0; i<n; i++){
    PyList_Append(U_tmp, PyFloat_FromDouble((double)self->u[i]));
  }
  for(i=0; i<n; i++){
    PyList_Append(V_tmp, PyFloat_FromDouble((double)self->v[i]));
  }

  if(0){
    PyObject *V0_tmp  = PyList_New(0);
    PyObject *U0_tmp  = PyList_New(0);
    for(i=0; i<n; i++){
      PyList_Append(U0_tmp, PyFloat_FromDouble((double)self->u0[i]));
    }
    for(i=0; i<n; i++){
      PyList_Append(V0_tmp, PyFloat_FromDouble((double)self->v0[i]));
    }
    return Py_BuildValue("OOOO", U_tmp, V_tmp, U0_tmp, V0_tmp);
  } else{
    return Py_BuildValue("OO", U_tmp, V_tmp);
  }
  
}

PyMODINIT_FUNC initcFluid(void){
    PyObject *m;

    fluidType.ob_type = &PyType_Type;
    if (PyType_Ready(&fluidType) < 0)
        return;

    m = Py_InitModule("cFluid", fluidMethods);

}
