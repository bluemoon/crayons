
class Image(Grob, TransformMixin):
    stateAttributes = ('_transform', '_transformmode')
    kwargs = ()

    def __init__(self, ctx, path=None, x=0, y=0, width=None, height=None, alpha=1.0, image=None, data=None):
        """
        Parameters:
         - path: A path to a certain image on the local filesystem.
         - x: Horizontal position.
         - y: Vertical position.
         - width: Maximum width. Images get scaled according to this factor.
         - height: Maximum height. Images get scaled according to this factor.
              If a width and height are both given, the smallest 
              of the two is chosen.
         - alpha: transparency factor
         - image: optionally, an image.               
         - data: a stream of bytes of image data.
        """
        super(Image, self).__init__(ctx)
        TransformMixin.__init__(self)
        if data is not None:
            self._nsImage = QImage(data)
            if self._qimage is None:
                raise NodeBoxError, "can't read image %r" % path
        elif image is not None:
            if isinstance(image, QImage):
                self._qimage = image
            else:
                raise NodeBoxError, "Don't know what to do with %s." % image
        elif path is not None:
            if not os.path.exists(path):
                raise NodeBoxError, 'Image "%s" not found.' % path
            curtime = os.path.getmtime(path)
            try:
                image, lasttime = self._ctx._imagecache[path]
                if lasttime != curtime:
                    image = None
            except KeyError:
                pass
            if image is None:
                image = QImage(path)
                if image is None:
                    raise NodeBoxError, "Can't read image %r" % path
                self._ctx._imagecache[path] = (image, curtime)
            self._qimage = image
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.alpha = alpha
        self.debugImage = False

    def _get_image(self):
        warnings.warn("The 'image' attribute is deprecated. Please use _qimage instead.", DeprecationWarning, stacklevel=2)
        return self._qimage
    image = property(_get_image)

    def copy(self):
        new = self.__class__(self._ctx)
        _copy_attrs(self, new, ('image', 'x', 'y', 'width', 'height', '_transform', '_transformmode', 'alpha', 'debugImage'))
        return new

    def getSize(self):
        return self._nsImage.size()

    size = property(getSize)

    def _draw(self, painter):
        """Draw an image on the given coordinates."""

        srcW, srcH = self._qimage.width(), self._qimage.height()
        srcRect = ((0, 0), (srcW, srcH))

        # Width or height given
        if self.width is not None or self.height is not None:
            if self.width is not None and self.height is not None:
                factor = min(self.width / srcW, self.height / srcH)
            elif self.width is not None:
                factor = self.width / srcW
            elif self.height is not None:
                factor = self.height / srcH
            painter.save()

            # Center-mode transforms: translate to image center
            if self._transformmode == CENTER:
                # This is the hardest case: center-mode transformations with given width or height.
                # Order is very important in this code.

                # Set the position first, before any of the scaling or transformations are done.
                # Context transformations might change the translation, and we don't want that.
                t = Transform()
                t.translate(self.x, self.y)
                t.concat(painter)

                # Set new width and height factors. Note that no scaling is done yet: they're just here
                # to set the new center of the image according to the scaling factors.
                srcW = srcW * factor
                srcH = srcH * factor

                # Move image to newly calculated center.
                dX = srcW / 2
                dY = srcH / 2
                t = Transform()
                t.translate(dX, dY)
                t.concat(painter)

                # Do current transformation.
                self._transform.concat(painter)

                # Move back to the previous position.
                t = Transform()
                t.translate(-dX, -dY)
                t.concat(painter)

                # Finally, scale the image according to the factors.
                t = Transform()
                t.scale(factor)
                t.concat(painter)
            else:
                # Do current transformation
                #self._transform.concat()
                # Scale according to width or height factor
                t = Transform()
                t.translate(self.x, self.y) # Here we add the positioning of the image.
                t.scale(factor)
                t.concat(painter)

            # A debugImage draws a black rectangle instead of an image.
            if self.debugImage:
                painter.setBrush(QBrush(Qt.SolidPattern))
                painter.fillRect(QRectF(0, 0, srcW / factor, srcH / factor))
            else:
                # TODO: Stuff with composition modes to allow for alpha transparency
                painter.drawImage(QPointF(0, 0), self._qimage, QRectF(0, 0, srcW, srcH))
            painter.restore()
        # No width or height given
        else:
            painter.save()
            x,y = self.x, self.y
            # Center-mode transforms: translate to image center
            if self._transformmode == CENTER:
                deltaX = srcW / 2
                deltaY = srcH / 2
                t = Transform()
                t.translate(x+deltaX, y+deltaY)
                t.concat(painter)
                x = -deltaX
                y = -deltaY
            # Do current transformation
            self._transform.concat(painter)
            # A debugImage draws a black rectangle instead of an image.
            if self.debugImage:
                painter.setBrush(QBrush(Qt.SolidPattern))
                painter.fillRect(QRectF(0, 0, srcW, srcH))
            else:
                # TODO: Stuff with composition modes to allow for alpha transparency
                painter.drawImage(QPointF(0, 0), self._qimage, QRectF(0, 0, srcW, srcH))
            painter.restore()
