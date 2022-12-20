
class Transf:

    def __init__(self) -> None:
        self._zoom = 0
        self._zoomf = 1
        self._zoom_incr = 0.02

        self._trans_x = 0
        self._trans_y = 0

    def zoom_factor(self) -> float:
        return float(self._zoomf)

    def zoom_in(self,):
        self._set_zoom(self._zoom+1)

    def zoom_out(self, ):
        self._set_zoom(self._zoom-1)

    def panning(self, dx, dy):
        self._trans_x += dx
        self._trans_y += dy

    def _set_zoom(self, zoom:float):
        self._zoom = min(max(-0.9 * 1 / self._zoom_incr, zoom), 100 / self._zoom_incr)
        self._zoomf = 1 + zoom * self._zoom_incr

    def forward(self, x:float, y:float):
        x += self._trans_x
        y += self._trans_y
        x *= self._zoomf
        y *= self._zoomf
        return x,y

    def backward(self, x:float, y:float):
        x /= self._zoomf
        y /= self._zoomf
        x -= self._trans_x
        y -= self._trans_y
        return x,y
    


    