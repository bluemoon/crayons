import Image
import StringIO
import gtk
import gobject
import time

class paint_gtk(gtk.Window):
    def __init__(self, width=100, height=100, callback=None, timer_rate=10, one_frame=False, threaded=False):
        super(paint_gtk, self).__init__()
        
        self.callback    = callback
        self.timer_rate  = timer_rate
        self.width       = width
        self.height      = height
        self.one_frame   = one_frame
        self.threaded    = threaded

        self.main()

        
        gtk.main()

    def main(self):
        self.set_size_request(self.width, self.height)
        self.set_position(gtk.WIN_POS_CENTER)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(6400, 6400, 6440))

        if not self.one_frame and not self.threaded:
            gobject.timeout_add(self.timer_rate, self.timer_cb)

        self.vbox = gtk.VBox(False, 0)
        self.add(self.vbox)
        self.vbox.show()

        self.image = gtk.Image()
        self.pixbuf = self.update2(self.callback())
        self.image.set_from_pixbuf(self.pixbuf)
        self.image.show()

        self.vbox.pack_end(self.image, True, True, 2)

        self.connect("destroy", gtk.main_quit)
        self.show()

    def timer_cb(self):
        if self.window:
            start = time.time()
            self.image.set_from_pixbuf(self.update2(self.callback()))
            self.image.show()
            end = time.time()

            print "fps: %f" % (1.0/(end-start))

            self.window.process_updates(True)
            return True

    def update2(self, handle):
        pixbuf = gtk.gdk.pixbuf_new_from_data(handle, gtk.gdk.COLORSPACE_RGB,  True, 8, self.width, self.height, self.width*4)
        return pixbuf

    def update_image(self, pil_handle):
        f_handle = StringIO.StringIO()  
        pil_handle.save(f_handle, "ppm")  
        contents = f_handle.getvalue()  
        f_handle.close()  
        
        loader = gtk.gdk.PixbufLoader("pnm")  
        loader.write(contents, len(contents))  
        pixbuf = loader.get_pixbuf()  
        loader.close()

        return pixbuf  


#PyApp()
#gtk.main()
