#include <rfftw.h>
#include <stdio.h>
#include <math.h>
#include <Python.h>

#include "structmember.h"

/// Defines
#define FFT(s, u)                                                  \
  if (s==1) rfftwnd_one_real_to_complex(plan_rc, (fftw_real *)u, (fftw_complex*)u); \
  else rfftwnd_one_complex_to_real(plan_cr, (fftw_complex *)u, (fftw_real *)u);
#define floor(x) ((x)>=0.0?((int)(x)):(-((int)(1-(x)))))


/// Struct for python object
typedef struct {
  PyObject_HEAD
  // velocity field
  double *u, *v, *u0, *v0;
  // user-induced forces
  double *u_u0, *u_v0;
  //double * u;
  //double * v;

  //double * u0;
  //double * v0;

  //double * u_u0;
  //double * u_v0;

  float    dt;
  int      dim;
  double   scale;

  double   last_x;
  double   last_y;

  double   last_delta_x;
  double   last_delta_y;

} fluid_object;

static rfftwnd_plan plan_rc;
static rfftwnd_plan plan_cr;

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



void init_FFT(int n){
  plan_rc = rfftw2d_create_plan(n, n, FFTW_REAL_TO_COMPLEX, FFTW_IN_PLACE);
  plan_cr = rfftw2d_create_plan(n, n, FFTW_COMPLEX_TO_REAL, FFTW_IN_PLACE);
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
void drag(fluid_object *self, double nx, double ny, double dnx, double dny){
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
  printf("dnx:%f dny:%f\n", self->u_u0[Y * n + X], self->u_u0[Y * n + X]);
  // Add force at the cursor location
  len = sqrt(dnx * dnx + dny * dny);
  if (len != 0.0){ 
      dnx *= 0.1 / len;
      dny *= 0.1 / len;
  }

  printf("X:%d Y:%d dnx:%f dny:%f pos:%d\n", X, Y, dnx, dny, (Y*n+X));
  self->u_u0[Y * n + X] += dnx;
  self->u_v0[Y * n + X] += dny;

}

void addValue(double *p_in, float x, float y, float v, int dim){
  // get fractional parts
  float fx = x-(int)x;
  float fy = y-(int)y;
  // get the corner cell (a)
  int cell = ((int)x + (int)y*dim);
  // get fractions of the values for each target cell
  float ia = (1.0f-fy)*(1.0f-fx) * v;
  float ib = (1.0f-fy)*(fx)      * v;
  float ic = (fy)     *(1.0f-fx) * v;
  float id = (fy)     *(fx)      * v;

  /// printf("ia:%f\n", ia);
  /// printf("p_in[cell]: %f\n", p_in[cell]);  
  p_in[cell] += ia;
  p_in[cell+1] += ib;
  p_in[cell+dim] += ic;
  p_in[cell+dim+1] += id;
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
  float time, f, x0, y0;
  double x1;
  double y1;
  double x2;
  double y2;
  double dx, dy;

  if (!PyArg_ParseTuple(args, "dddd|f", &x1, &y1, &x2, &y2, &time))
    return NULL;

  dx = x2-x1;
  dy = y2-y1;


  //if (x2 < x1) dx = x1-x2;
  //if (y2 < y1) dy = y1-y2;       
  if(1){
    printf("X:%f Y:%f dX:%f dY:%f \n", x1, y1, dx, dy);
  }

  double k = 0.0;
  double c = sqrt((dx*dx) + (dy*dy));
  while(k <= 100.0){
    double cx = x1 - ((k/100.0) * (x1 - x2));
    double cy = y1 - ((k/100.0) * (y1 - y2));

    printf("cx:%f cy:%f\n", cx, cy);

    double cdx = 0.1 - ((k/100.0) * (0.1 - dx));
    double cdy = 0.1 - ((k/100.0) * (0.1 - dy));
    
    // don't draw the last position twice
    if (cx == x2 && cy == y2 ) { break; }
    drag(self, cx, 1-cy, cdx, (-1*cdy));
    k +=  1/(c*2);
  }
  


  /*
  float f_step = 0.025f; // steps along the stroke
  float r_step = 0.05f; // steps across circle
  float step_scale = f_step * r_step * r_step;

  for (f = 0.0f; f<1.0f; f+=0.01f){
    float xc = x1 + f *(x2-x1);
    float yc = y1 + f *(y2-y1);
    
    for (x0 = -1.0f; x0 < 1.0f; x0+=r_step){
      for (y0 = -1.0f; y0 < 1.0f;y0+=r_step){
        /// Get coordinates relative to the center
        float rr = sqrtf(x0*x0 + y0*y0);
        if (rr < 1.0f){
          /// Inside the circle
          if (rr == 0.0f){
            rr = r_step;
          }

          float r_drag = 0.06f * self->dim;
          float drag = 5.0f;
          
          float ndx = 0.1 + f*(dx-0.1);
          float ndy = 0.1 + f *(dy-0.1);
          addValue(self->u_u0, x0*r_drag+xc, y0*r_drag+yc, ndx, self->dim);
          addValue(self->u_v0, x0*r_drag+xc, y0*r_drag+yc, ndy, self->dim);
        }
      }
    }
  }
  */

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
  float dt = 0.1f;
  float visc = 0.001f;
  int i;

  for (i = 0; i < (self->dim * self->dim); i++) {
    //self->u_u0[i] *= 0.85;
    //self->u_v0[i] *= 0.85;

    self->u0[i] = self->u_u0[i];
    self->v0[i] = self->u_v0[i];

    //printf("u0:%f v0:%f\n", self->u_u0, self->u_v0);
    printf("u0:%f v0:%f\n", self->u0[i], self->v0[i]);

  }

  stable_solve(self, visc);
  zero_boundary(self, args);
  //vector_print(self);

  self->dt += dt;
  printf("time:%f\n", self->dt);

  Py_INCREF(Py_None);
  return Py_None;
}
static PyObject *cFluid_new(PyObject *self_, PyObject *args){
  int dim, i;
  int height, width = 0;
  if (!PyArg_ParseTuple(args, "i|ii", &dim, &width, &height))
    return NULL;

  init_FFT(dim);


  fluid_object *self;
  self = (fluid_object *)PyObject_NEW(fluid_object, &fluidType);
  self->dt = 0.0f;

  self->u     = (double *)malloc((dim * 2 * (dim/2+1)) * sizeof(double));
  self->v     = (double *)malloc((dim * 2 * (dim/2+1)) * sizeof(double));
  self->u0    = (double *)malloc((dim * 2 * (dim/2+1)) * sizeof(double));
  self->v0    = (double *)malloc((dim * 2 * (dim/2+1)) * sizeof(double));
  self->u_u0  = (double *)malloc((dim * 2 * (dim/2+1)) * sizeof(double));
  self->u_v0  = (double *)malloc((dim * 2 * (dim/2+1)) * sizeof(double));

  
  //printf("malloc size: %d\n", (dim * 2 * (dim/2+1)));
  /// Initialize the table


  for (i = 0; i < (dim * dim); i++) {
    self->u[i] = self->v[i] = self->u0[i] = self->v0[i] = 0.0;
  }

  self->dim = dim;
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
