"""
Script Name: AB ColorChecker
Script Version: 3.8.3
Flame Version: 2026
Written by: AB
Creation Date: 06.01.26
Update Date: 06.15.26

Description:

    Camera matching via Macbeth ColorChecker chart in ACEScg scene-linear.

Usage:

    Load reference (Camera A) and source (Camera B) frames, click all 24
    colour patches on each, then apply a correction that maps Camera B to
    look like Camera A.

    Standard mode uses a pure 3x3 colour matrix — zero always maps to zero,
    full dynamic range preserved, clean shadows. Exports corrected EXR,
    3D LUT (.cube), or both. The LUT closely matches the EXR output.

    HDR / 360 mode uses a Thin-Plate Spline RBF for better colour accuracy
    with wide-gamut cameras that produce negative channel values.

    Sessions can be saved and recalled — Camera A patches never need to be
    re-clicked. Load a session, load a new Camera B frame, click 24 patches,
    and apply.

To Install:
  
    Install Required Python packages
    ----------------------------------------------------------------
    This script requires numpy and opencv-python. Run the following command 
    in Terminal before running the script:

    Mac / Linux (Terminal):
        /opt/Autodesk/python/<Flame Version>/bin/python3 -m pip install numpy opencv-python --break-system-packages

    Example:
        /opt/Autodesk/python/2026.2/bin/python3 -m pip install numpy opencv-python --break-system-packages

    After installing, restart Flame or reload Python scripts.
    ----------------------------------------------------------------

Menus:

    Right-click in Batch -> AB ColorChecker -> Match Cameras...
    Right-click in Media Panel -> AB ColorChecker -> Match Cameras...

Updates:

    3.8.2 06.15.26
        - Apply Correction button now shows export dialog (EXR, LUT, or Both).
        - Session save no longer defaults to a fixed path.
        - Minor UI refinements.

    3.8.0 06.14.26
        - Standard mode now offers EXR, 3D LUT, or both on export.
        - Auto-installs required Python packages on first launch.

    3.7.0 06.12.26
        - Standard mode switched to pure 3x3 colour matrix for clean shadow handling.
        - HDR mode uses single-stage TPS RBF for wide-gamut camera accuracy.
        - Session save and load fixed.
"""

SCRIPT_NAME    = 'AB ColorChecker'
SCRIPT_VERSION = '3.8.3'

PATCH_NAMES = [
    'Dark Skin','Light Skin','Blue Sky','Foliage','Blue Flower','Bluish Green',
    'Orange','Purplish Blue','Moderate Red','Purple','Yellow Green','Orange Yellow',
    'Blue','Green','Red','Yellow','Magenta','Cyan',
    'White','Neutral 8','Neutral 6.5','Neutral 5','Neutral 3.5','Black',
]

PATCH_DISPLAY_COLORS = [
    (115,82,68),(194,150,130),(98,122,157),(87,108,67),(133,128,177),(103,190,170),
    (214,126,44),(80,91,166),(193,90,99),(94,60,108),(224,186,46),(247,162,24),
    (35,63,147),(67,149,74),(180,49,57),(239,198,51),(190,85,141),(0,162,194),
    (243,243,243),(200,200,200),(160,160,160),(122,122,122),(85,85,85),(52,52,52),
]



def _find_flame_python():
    import glob
    candidates = glob.glob('/opt/Autodesk/python/*/lib/python*/site-packages')
    if candidates:
        candidates.sort(reverse=True)
        return candidates[0]
    return None


def _ensure_packages():
    import sys, subprocess
    missing = []
    try: import numpy
    except ImportError: missing.append('numpy')
    try: import cv2
    except ImportError: missing.append('opencv-python')
    if not missing: return True
    print(f'[AB ColorChecker] Installing: {missing}')
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--break-system-packages', '--quiet'] + missing,
            timeout=120)
        print('[AB ColorChecker] Installed. Please restart Flame.')
        return False
    except Exception as e:
        print(f'[AB ColorChecker] Auto-install failed: {e}')
        print('[AB ColorChecker] Install manually — see docstring for instructions.')
        return False


def launch_ui(selection):
    if not _ensure_packages():
        try:
            import flame
            flame.messages.show_in_console(
                '[AB ColorChecker] Required packages installed. Please restart Flame.',
                'info', 10)
        except: pass
        return
    import os
    import sys
    import json

    os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'

    pkgs = _find_flame_python()
    if pkgs and pkgs not in sys.path:
        sys.path.insert(0, pkgs)

    import numpy as np
    import cv2
    import flame
    from PySide6 import QtWidgets, QtCore, QtGui

    # Session directory
    SESSION_DIR = os.path.expanduser('~/AB_ColorChecker_Sessions')
    os.makedirs(SESSION_DIR, exist_ok=True)

    # ----------------------------------------------------------------
    # Source type dialog
    # ----------------------------------------------------------------

    class SourceTypeDialog(QtWidgets.QDialog):
        def __init__(self):
            super().__init__()
            self.hdr_mode = None
            self.setWindowTitle(SCRIPT_NAME)
            self.setFixedSize(460, 160)
            self.setStyleSheet('''
                QDialog,QWidget{background:#232323;color:#cccccc;font-size:12px;}
                QLabel{color:#cccccc;}
                QLabel#title{font-size:13px;font-weight:bold;color:#ffffff;}
                QLabel#sub{font-size:10px;color:#888888;margin-bottom:4px;}
                QPushButton{background:#3c3c3c;color:#cccccc;border:1px solid #505050;
                            padding:8px 20px;border-radius:3px;}
                QPushButton:hover{background:#4a4a4a;}
                QPushButton#blue{background:#1a5fa8;color:#ffffff;border:1px solid #2070c0;}
                QPushButton#blue:hover{background:#2272cc;}
            ''')
            root = QtWidgets.QVBoxLayout(self)
            root.setSpacing(10)
            root.setContentsMargins(20,16,20,16)
            title = QtWidgets.QLabel(f'{SCRIPT_NAME}  <span style="color:#666;font-size:10px;">{SCRIPT_VERSION}</span>')
            title.setObjectName('title')
            root.addWidget(title)
            sub = QtWidgets.QLabel('What is Camera B (source)?')
            sub.setObjectName('sub')
            root.addWidget(sub)
            btns = QtWidgets.QHBoxLayout()
            btns.setSpacing(10)
            btn_std = QtWidgets.QPushButton('Standard Camera')
            btn_std.setObjectName('blue')
            btn_std.setFixedHeight(44)
            btn_hdr = QtWidgets.QPushButton('HDR / 360')
            btn_hdr.setFixedHeight(44)
            btn_cancel = QtWidgets.QPushButton('Cancel')
            btn_cancel.setFixedHeight(44)
            btns.addWidget(btn_std)
            btns.addWidget(btn_hdr)
            btns.addWidget(btn_cancel)
            root.addLayout(btns)
            btn_std.clicked.connect(lambda: self._select(False))
            btn_hdr.clicked.connect(lambda: self._select(True))
            btn_cancel.clicked.connect(self.reject)

        def _select(self, hdr):
            self.hdr_mode = hdr
            self.accept()

    class ExportChoiceDialog(QtWidgets.QDialog):
        def __init__(self):
            super().__init__()
            self.choice = None
            self.setWindowTitle(SCRIPT_NAME)
            self.setFixedSize(440, 160)
            self.setStyleSheet('''
                QDialog,QWidget{background:#232323;color:#cccccc;font-size:12px;}
                QLabel{color:#cccccc;}
                QLabel#title{font-size:13px;font-weight:bold;color:#ffffff;}
                QLabel#sub{font-size:10px;color:#888888;margin-bottom:4px;}
                QPushButton{background:#3c3c3c;color:#cccccc;border:1px solid #505050;
                            padding:8px 16px;border-radius:3px;}
                QPushButton:hover{background:#4a4a4a;}
                QPushButton#blue{background:#1a5fa8;color:#ffffff;border:1px solid #2070c0;}
                QPushButton#blue:hover{background:#2272cc;}
            ''')
            root = QtWidgets.QVBoxLayout(self)
            root.setSpacing(10); root.setContentsMargins(20,16,20,16)
            title = QtWidgets.QLabel('Export As')
            title.setObjectName('title'); root.addWidget(title)
            sub = QtWidgets.QLabel('Choose output format — LUT exactly matches EXR for standard mode.')
            sub.setObjectName('sub'); root.addWidget(sub)
            btns = QtWidgets.QHBoxLayout(); btns.setSpacing(8)
            btn_exr  = QtWidgets.QPushButton('EXR')
            btn_exr.setObjectName('blue'); btn_exr.setFixedHeight(44)
            btn_lut  = QtWidgets.QPushButton('3D LUT (.cube)')
            btn_lut.setFixedHeight(44)
            btn_both = QtWidgets.QPushButton('Both')
            btn_both.setFixedHeight(44)
            btn_cancel = QtWidgets.QPushButton('Cancel')
            btn_cancel.setFixedHeight(44)
            btns.addWidget(btn_exr); btns.addWidget(btn_lut)
            btns.addWidget(btn_both); btns.addWidget(btn_cancel)
            root.addLayout(btns)
            btn_exr.clicked.connect(lambda: self._pick('exr'))
            btn_lut.clicked.connect(lambda: self._pick('lut'))
            btn_both.clicked.connect(lambda: self._pick('both'))
            btn_cancel.clicked.connect(self.reject)

        def _pick(self, c):
            self.choice = c; self.accept()

    src_dlg = SourceTypeDialog()
    if src_dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
        return
    hdr_mode = src_dlg.hdr_mode
    print(f'[AB ColorChecker] Mode: {"HDR/360" if hdr_mode else "Standard"}')

    # ----------------------------------------------------------------
    # Thin-plate spline RBF (numpy only)
    # ----------------------------------------------------------------

    def tps_kernel(r):
        with np.errstate(divide='ignore', invalid='ignore'):
            return np.where(r == 0, 0.0, r**2 * np.log(r + 1e-10))

    class ThinPlateRBF:
        def __init__(self, src_pts, tgt_pts, smoothing=0.01):
            N = len(src_pts)
            self.src_pts = src_pts.copy()
            diff = src_pts[:, np.newaxis] - src_pts[np.newaxis]
            r = np.sqrt((diff**2).sum(axis=2))
            K = tps_kernel(r) + np.eye(N) * smoothing
            P = np.hstack([np.ones((N,1)), src_pts])
            A = np.vstack([np.hstack([K, P]), np.hstack([P.T, np.zeros((4,4))])])
            rhs = np.vstack([tgt_pts, np.zeros((4, tgt_pts.shape[1]))])
            self.coeffs = np.linalg.lstsq(A, rhs, rcond=None)[0]
            self.w = self.coeffs[:N]; self.c = self.coeffs[N:]

        def __call__(self, query_pts):
            query_pts = np.asarray(query_pts, dtype=np.float64)
            diff = query_pts[:, np.newaxis] - self.src_pts[np.newaxis]
            r = np.sqrt((diff**2).sum(axis=2))
            K = tps_kernel(r)
            P = np.hstack([np.ones((len(query_pts),1)), query_pts])
            return K @ self.w + P @ self.c

    # ----------------------------------------------------------------
    # Image utils
    # ----------------------------------------------------------------

    def load_image(path):
        img = cv2.imread(path, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
        if img is None:
            raise ValueError(f'Cannot load: {path}')
        img = img.astype(np.float32)
        if img.ndim == 3 and img.shape[2] >= 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    def save_exr(img, path):
        out = cv2.cvtColor(img.astype(np.float32), cv2.COLOR_RGB2BGR)
        if not cv2.imwrite(path, out):
            raise ValueError(f'Failed to write EXR: {path}')

    def to_display(img):
        d = np.clip(img, 0, None)
        p = np.percentile(d, 99)
        if p > 0: d = d / p
        d = np.power(np.clip(d, 0, 1), 1/2.2)
        return (d * 255).astype(np.uint8)

    def sample_at_points(img, points, radius=8):
        h, w = img.shape[:2]
        samples = []
        for (px, py) in points:
            x, y = int(px), int(py)
            x1,x2 = max(0,x-radius), min(w,x+radius)
            y1,y2 = max(0,y-radius), min(h,y+radius)
            patch = img[y1:y2, x1:x2]
            samples.append(patch.mean(axis=(0,1)) if patch.size > 0 else np.zeros(3,np.float32))
        return np.array(samples, dtype=np.float64)

    # ----------------------------------------------------------------
    # Correction engine
    # ----------------------------------------------------------------

    def build_correction(src_patches, ref_patches, hdr=False):
        """
        Standard: pure 3x3 colour matrix — no offset, zero maps to zero.
        HDR/360:  single-stage TPS RBF — handles negative patch values,
                  better colour accuracy for wide-gamut cameras.
        """
        if hdr:
            # Single-stage RBF — normalise by white patch, no linear stage
            src_max = src_patches[18].mean()
            ref_max = ref_patches[18].mean()
            src_norm = src_patches / src_max
            ref_norm = ref_patches / ref_max
            src_all = np.vstack([src_norm, [[10000,10000,10000]]])
            ref_all = np.vstack([ref_norm, [[10000,10000,10000]]])
            rbf = ThinPlateRBF(src_all, ref_all, smoothing=0.01)
            return ('rbf', rbf, src_max, ref_max)
        else:
            # Pure 3x3 matrix — zero maps to zero, preserves dynamic range
            M, _, _, _ = np.linalg.lstsq(src_patches, ref_patches, rcond=None)
            return ('matrix', M)

    def apply_to_image(img, correction):
        h, w = img.shape[:2]
        flat = img.reshape(-1, 3).astype(np.float64)
        if correction[0] == 'matrix':
            _, M = correction
            corrected = flat @ M
        else:
            _, rbf, src_max, ref_max = correction
            flat_norm = flat / src_max
            chunk = 200000
            results = []
            for i in range(0, len(flat_norm), chunk):
                results.append(rbf(flat_norm[i:i+chunk]))
            corrected = np.vstack(results) * ref_max
        # No clipping — preserves full dynamic range
        return corrected.reshape(h, w, 3).astype(np.float32)


    def build_lut_from_matrix(M, lut_size=33, domain_max=1.0):
        """
        Build a .cube 3D LUT from a 3x3 colour matrix.
        Since the matrix is linear, the LUT exactly matches the EXR output.
        Domain is set from the source white patch value * 2 for headroom.
        """
        coords = np.linspace(0, domain_max, lut_size)
        r_g, g_g, b_g = np.meshgrid(coords, coords, coords, indexing='ij')
        grid_pts = np.stack([r_g.ravel(), g_g.ravel(), b_g.ravel()], axis=1)
        lut_vals = grid_pts @ M  # pure matrix — exact match to EXR

        lines = [
            '# AB ColorChecker — 3x3 Matrix LUT',
            f'# Version: {SCRIPT_VERSION}',
            '# Input:  Camera B ACEScg scene-linear',
            '# Output: Matched to Camera A ACEScg scene-linear',
            '# Apply:  Flame Colour Management > 3D LUT > 32-bit > ACEScg',
            f'TITLE "AB Camera Match"',
            f'LUT_3D_SIZE {lut_size}',
            f'DOMAIN_MIN 0.000000 0.000000 0.000000',
            f'DOMAIN_MAX {domain_max:.6f} {domain_max:.6f} {domain_max:.6f}',
            '',
        ]
        for bi in range(lut_size):
            for gi in range(lut_size):
                for ri in range(lut_size):
                    idx = ri*lut_size*lut_size + gi*lut_size + bi
                    rv, gv, bv = lut_vals[idx]
                    lines.append(f'{rv:.6f} {gv:.6f} {bv:.6f}')
        return '\n'.join(lines)

    def verify_patches(src_patches, ref_patches, correction):
        if correction[0] == 'matrix':
            _, M = correction
            pred = src_patches @ M
        else:
            _, rbf, src_max, ref_max = correction
            pred = rbf(src_patches / src_max) * ref_max
        print('[AB ColorChecker] Patch verification:')
        for i in range(24):
            p = pred[i]; r = ref_patches[i]
            err = np.abs(p-r).mean()/(r.mean()+1e-6)*100
            print(f'  {i+1:02d} {PATCH_NAMES[i]:20s} pred=({p[0]:.4f},{p[1]:.4f},{p[2]:.4f}) ref=({r[0]:.4f},{r[1]:.4f},{r[2]:.4f}) err={err:.1f}%')

    # ----------------------------------------------------------------
    # Session save/load
    # ----------------------------------------------------------------

    def save_session(name, ref_patches, src_patches, hdr_mode):
        path = os.path.join(SESSION_DIR, f'{name}.json')
        data = {
            'version': SCRIPT_VERSION,
            'name': name,
            'hdr_mode': hdr_mode,
            'ref_patches': ref_patches.tolist(),
            'src_patches': src_patches.tolist(),
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f'[AB ColorChecker] Session saved: {path}')
        return path

    def list_sessions():
        if not os.path.exists(SESSION_DIR):
            return []
        sessions = []
        for fn in sorted(os.listdir(SESSION_DIR)):
            if fn.endswith('.json'):
                try:
                    with open(os.path.join(SESSION_DIR, fn)) as f:
                        data = json.load(f)
                    sessions.append({
                        'name': data.get('name', fn[:-5]),
                        'hdr_mode': data.get('hdr_mode', False),
                        'ref_patches': np.array(data['ref_patches']),
                        'src_patches': np.array(data['src_patches']),
                        'path': os.path.join(SESSION_DIR, fn),
                    })
                except:
                    pass
        return sessions

    # ----------------------------------------------------------------
    # Reference chart widget
    # ----------------------------------------------------------------

    class ChartReference(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()
            self._current = 0
            self.setFixedHeight(72)

        def set_current(self, idx):
            self._current = idx
            self.update()

        def paintEvent(self, ev):
            p = QtGui.QPainter(self)
            p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            w, h = self.width(), self.height()
            cols, rows = 6, 4
            sw, sh = w/cols, h/rows
            for i, (r, g, b) in enumerate(PATCH_DISPLAY_COLORS):
                col, row = i%cols, i//cols
                x, y = col*sw, row*sh
                p.fillRect(QtCore.QRectF(x,y,sw,sh), QtGui.QColor(r,g,b))
                if i < self._current:
                    p.fillRect(QtCore.QRectF(x,y,sw,sh), QtGui.QColor(0,0,0,120))
                    p.setPen(QtGui.QPen(QtGui.QColor(255,255,255,200),1.5))
                    p.drawText(QtCore.QRectF(x,y,sw,sh),
                               QtCore.Qt.AlignmentFlag.AlignCenter,'✓')
                elif i == self._current:
                    p.setPen(QtGui.QPen(QtGui.QColor(255,255,255),2))
                    p.drawRect(QtCore.QRectF(x+1,y+1,sw-2,sh-2))
                    p.setPen(QtGui.QPen(QtGui.QColor(255,210,0),2))
                    p.drawRect(QtCore.QRectF(x+2,y+2,sw-4,sh-4))
                p.setPen(QtGui.QPen(QtGui.QColor(255,255,255,160),1))
                p.setFont(QtGui.QFont('Helvetica',7))
                p.drawText(QtCore.QRectF(x+2,y+2,sw-4,sh-4),
                           QtCore.Qt.AlignmentFlag.AlignTop|QtCore.Qt.AlignmentFlag.AlignLeft,
                           str(i+1))
            p.end()

    # ----------------------------------------------------------------
    # Image picker widget
    # ----------------------------------------------------------------

    class ImagePicker(QtWidgets.QLabel):
        point_added = QtCore.Signal(int)
        point_moved = QtCore.Signal(int)
        all_done    = QtCore.Signal(list)
        DRAG_R = 12

        def __init__(self):
            super().__init__()
            self._img8=None; self._base_pix=None; self._points=[]
            self._zoom=1.0; self._pan_x=0.0; self._pan_y=0.0
            self._drag_pt=None; self._panning=False
            self._pan_start=None; self._pan_origin=None
            self.setMinimumSize(620,380)
            self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.setStyleSheet('background:#1c1c1c;border:1px solid #3a3a3a;')
            self.setText('Load frame')
            self.setMouseTracking(True)

        def load(self, img_float):
            self._img8=to_display(img_float)
            h,w=self._img8.shape[:2]
            qi=QtGui.QImage(self._img8.tobytes(),w,h,w*3,QtGui.QImage.Format.Format_RGB888)
            self._base_pix=QtGui.QPixmap.fromImage(qi)
            self._points=[]; self._zoom=1.0; self._pan_x=0.0; self._pan_y=0.0
            self._paint()

        def reset(self): self._points=[]; self._paint()
        def undo_last(self):
            if self._points: self._points.pop(); self._paint()

        @property
        def points(self): return list(self._points) if len(self._points)==24 else None
        @property
        def count(self): return len(self._points)

        def _i2w(self,ix,iy):
            lw,lh=self.width(),self.height()
            ih,iw=self._img8.shape[:2]
            s=min(lw/iw,lh/ih)*self._zoom
            cx,cy=lw/2+self._pan_x,lh/2+self._pan_y
            return cx-iw*s/2+ix*s, cy-ih*s/2+iy*s

        def _w2i(self,wx,wy):
            lw,lh=self.width(),self.height()
            ih,iw=self._img8.shape[:2]
            s=min(lw/iw,lh/ih)*self._zoom
            cx,cy=lw/2+self._pan_x,lh/2+self._pan_y
            return (wx-(cx-iw*s/2))/s,(wy-(cy-ih*s/2))/s

        def _nearest(self,wx,wy):
            best_d,best_i=float('inf'),None
            for i,(ix,iy) in enumerate(self._points):
                px,py=self._i2w(ix,iy)
                d=((wx-px)**2+(wy-py)**2)**0.5
                if d<self.DRAG_R and d<best_d: best_d,best_i=d,i
            return best_i

        def _paint(self):
            if self._base_pix is None: return
            lw,lh=self.width(),self.height()
            ih,iw=self._img8.shape[:2]
            s=min(lw/iw,lh/ih)*self._zoom
            sw,sh=int(iw*s),int(ih*s)
            scaled=self._base_pix.scaled(sw,sh,
                QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation)
            cx,cy=lw/2+self._pan_x,lh/2+self._pan_y
            ox,oy=int(cx-sw/2),int(cy-sh/2)
            canvas=QtGui.QPixmap(lw,lh)
            canvas.fill(QtGui.QColor('#1c1c1c'))
            p=QtGui.QPainter(canvas)
            p.drawPixmap(ox,oy,scaled)
            p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            for i,(ix,iy) in enumerate(self._points):
                wx,wy=self._i2w(ix,iy)
                r,g,b=PATCH_DISPLAY_COLORS[i]
                p.setPen(QtGui.QPen(QtGui.QColor(r,g,b),2))
                p.setBrush(QtGui.QBrush(QtGui.QColor(r,g,b,180)))
                p.drawEllipse(QtCore.QPointF(wx,wy),7,7)
                p.setPen(QtGui.QPen(QtGui.QColor(255,255,255)))
                p.setFont(QtGui.QFont('Helvetica',7,QtGui.QFont.Weight.Bold))
                p.drawText(int(wx)+9,int(wy)+4,str(i+1))
            if len(self._points)<24:
                p.setPen(QtGui.QPen(QtGui.QColor(255,210,0)))
                p.setFont(QtGui.QFont('Helvetica',10))
                p.drawText(8,18,f'Next: {len(self._points)+1}. {PATCH_NAMES[len(self._points)]}')
            p.end()
            self.setPixmap(canvas)

        def mousePressEvent(self,ev):
            if self._img8 is None: return
            if ev.button()==QtCore.Qt.MouseButton.RightButton:
                self._panning=True
                self._pan_start=(ev.position().x(),ev.position().y())
                self._pan_origin=(self._pan_x,self._pan_y)
                return
            if ev.button()==QtCore.Qt.MouseButton.LeftButton:
                wx,wy=ev.position().x(),ev.position().y()
                near=self._nearest(wx,wy)
                if near is not None: self._drag_pt=near; return
                if len(self._points)<24:
                    ix,iy=self._w2i(wx,wy)
                    self._points.append((ix,iy))
                    idx=len(self._points)-1
                    self._paint()
                    self.point_added.emit(idx)
                    if len(self._points)==24:
                        self.all_done.emit(list(self._points))

        def mouseMoveEvent(self,ev):
            wx,wy=ev.position().x(),ev.position().y()
            if self._panning and self._pan_start:
                dx=wx-self._pan_start[0]; dy=wy-self._pan_start[1]
                self._pan_x=self._pan_origin[0]+dx; self._pan_y=self._pan_origin[1]+dy
                self._paint()
            elif self._drag_pt is not None:
                ix,iy=self._w2i(wx,wy)
                self._points[self._drag_pt]=(ix,iy)
                self._paint(); self.point_moved.emit(self._drag_pt)

        def mouseReleaseEvent(self,ev):
            if ev.button()==QtCore.Qt.MouseButton.RightButton: self._panning=False
            if ev.button()==QtCore.Qt.MouseButton.LeftButton: self._drag_pt=None

        def wheelEvent(self,ev):
            f=1.15 if ev.angleDelta().y()>0 else 1/1.15
            self._zoom=max(0.5,min(20.0,self._zoom*f)); self._paint()

        def resizeEvent(self,ev): self._paint()

    # ----------------------------------------------------------------
    # Main window
    # ----------------------------------------------------------------

    mode_label = 'HDR / 360' if hdr_mode else 'Standard Camera'

    STYLE='''
    QDialog,QWidget{background:#232323;color:#cccccc;font-size:12px;}
    QLabel{color:#cccccc;}
    QLabel#title{font-size:14px;font-weight:bold;color:#ffffff;}
    QFrame#line{background:#3a3a3a;max-height:1px;}
    QPushButton{background:#3c3c3c;color:#cccccc;border:1px solid #505050;
                padding:5px 14px;border-radius:3px;min-width:80px;}
    QPushButton:hover{background:#4a4a4a;}
    QPushButton:disabled{background:#2c2c2c;color:#555555;}
    QPushButton#blue{background:#1a5fa8;color:#ffffff;border:1px solid #2070c0;}
    QPushButton#blue:hover{background:#2272cc;}
    QPushButton#blue:disabled{background:#1a3a5a;color:#557799;}
    QPushButton#green{background:#1a6e3c;color:#ffffff;border:1px solid #22883c;}
    QPushButton#green:hover{background:#22883c;}
    QProgressBar{background:#2c2c2c;border:1px solid #444;border-radius:3px;height:6px;}
    QProgressBar::chunk{background:#1a5fa8;border-radius:3px;}
    QListWidget{background:#1c1c1c;border:1px solid #3a3a3a;color:#cccccc;}
    QListWidget::item:selected{background:#1a5fa8;}
    QLineEdit{background:#1c1c1c;border:1px solid #3a3a3a;color:#cccccc;padding:4px;}
    '''

    win=QtWidgets.QDialog()
    win.setWindowTitle(f'{SCRIPT_NAME}  {SCRIPT_VERSION}  —  {mode_label}')
    win.setMinimumSize(1400,820)
    win.setStyleSheet(STYLE)

    root=QtWidgets.QVBoxLayout(win)
    root.setSpacing(6); root.setContentsMargins(14,14,14,14)

    tl=QtWidgets.QLabel(
        f'{SCRIPT_NAME}  <span style="color:#666;font-size:10px;">{SCRIPT_VERSION}</span>  '
        f'<span style="color:#1a5fa8;font-size:10px;">— {mode_label}</span>'
    )
    tl.setObjectName('title'); root.addWidget(tl)

    def hline():
        f=QtWidgets.QFrame(); f.setObjectName('line'); return f

    root.addWidget(hline())

    instr=QtWidgets.QLabel(
        'Scroll to zoom.  Right-click drag to pan.  '
        'Click patch centres 1→24 in order.  '
        'Drag any point to adjust.  Undo removes last point.'
    )
    instr.setStyleSheet('font-size:10px;color:#888888;')
    root.addWidget(instr)
    root.addWidget(hline())

    panels=QtWidgets.QHBoxLayout(); panels.setSpacing(10)

    state={
        'ref_img':None,'src_img':None,
        'ref_path':None,'src_path':None,
        'ref_points':None,'src_points':None,
        'ref_patches':None,'src_patches':None,
        'correction_built':False,
        'session_loaded':False,
        'rbf':None,'src_max':None,'ref_max':None,
        'linear_scale':None,'linear_offset':None,
    }

    def make_panel(label_text, points_key, path_key, img_key):
        col=QtWidgets.QVBoxLayout(); col.setSpacing(4)
        hdr=QtWidgets.QHBoxLayout()
        lbl=QtWidgets.QLabel(label_text)
        lbl.setStyleSheet('font-size:11px;font-weight:bold;color:#aaaaaa;')
        hdr.addWidget(lbl); hdr.addStretch()
        load_btn=QtWidgets.QPushButton('Load Frame...')
        undo_btn=QtWidgets.QPushButton('Undo')
        reset_btn=QtWidgets.QPushButton('Reset All')
        undo_btn.setEnabled(False); reset_btn.setEnabled(False)
        hdr.addWidget(load_btn); hdr.addWidget(undo_btn); hdr.addWidget(reset_btn)
        col.addLayout(hdr)
        picker=ImagePicker(); col.addWidget(picker)
        chart=ChartReference(); col.addWidget(chart)
        status=QtWidgets.QLabel('No frame loaded')
        status.setStyleSheet('font-size:10px;color:#888888;')
        col.addWidget(status)

        def on_load():
            path,_=QtWidgets.QFileDialog.getOpenFileName(
                win,'Load Frame','',
                'Images (*.exr *.tif *.tiff *.dpx *.png *.jpg);;All Files (*)')
            if not path: return
            try:
                img=load_image(path)
                state[img_key]=img; state[path_key]=path; state[points_key]=None
                picker.load(img); chart.set_current(0)
                reset_btn.setEnabled(True); undo_btn.setEnabled(False)
                status.setText(f'{os.path.basename(path)}  —  click patch 1: Dark Skin')
                status.setStyleSheet('font-size:10px;color:#888888;')
                state['correction_built']=False
                update_buttons()
            except Exception as e:
                status.setText(f'Error: {e}')
                status.setStyleSheet('font-size:11px;color:#cc5555;')

        def on_point_added(idx):
            undo_btn.setEnabled(True); chart.set_current(idx+1)
            if idx+1<24:
                status.setText(f'{os.path.basename(state[path_key])}  —  click patch {idx+2}: {PATCH_NAMES[idx+1]}')
                status.setStyleSheet('font-size:10px;color:#888888;')
            else:
                status.setText('✓  All 24 patches placed')
                status.setStyleSheet('font-size:11px;color:#66cc66;')

        def on_all_done(points):
            state[points_key]=points; update_buttons()

        def on_undo():
            picker.undo_last(); state[points_key]=None
            n=picker.count; chart.set_current(n); undo_btn.setEnabled(n>0)
            status.setText(f'{os.path.basename(state[path_key])}  —  click patch {n+1}: {PATCH_NAMES[n]}')
            status.setStyleSheet('font-size:10px;color:#888888;')
            update_buttons()

        def on_reset():
            picker.reset(); state[points_key]=None; chart.set_current(0)
            undo_btn.setEnabled(False)
            status.setText(f'{os.path.basename(state[path_key])}  —  click patch 1: Dark Skin')
            status.setStyleSheet('font-size:10px;color:#888888;')
            update_buttons()

        load_btn.clicked.connect(on_load); undo_btn.clicked.connect(on_undo)
        reset_btn.clicked.connect(on_reset); picker.point_added.connect(on_point_added)
        picker.all_done.connect(on_all_done)
        return col

    panels.addLayout(make_panel('REFERENCE  —  Camera A  (target)','ref_points','ref_path','ref_img'))
    panels.addLayout(make_panel('SOURCE  —  Camera B  (to correct)','src_points','src_path','src_img'))
    root.addLayout(panels)
    root.addWidget(hline())

    # Session bank row
    session_row = QtWidgets.QHBoxLayout()
    session_row.setSpacing(8)

    session_label = QtWidgets.QLabel('Session:')
    session_label.setStyleSheet('font-size:10px;color:#888888;')
    session_row.addWidget(session_label)

    session_combo = QtWidgets.QComboBox()
    session_combo.setFixedHeight(28)
    session_combo.setMinimumWidth(220)
    session_combo.setStyleSheet('background:#1c1c1c;border:1px solid #3a3a3a;color:#cccccc;padding:2px 6px;')
    session_row.addWidget(session_combo)

    session_name_edit = QtWidgets.QLineEdit()
    session_name_edit.setPlaceholderText('Session name...')
    session_name_edit.setFixedHeight(28)
    session_name_edit.setMinimumWidth(180)
    session_row.addWidget(session_name_edit)

    save_session_btn = QtWidgets.QPushButton('Save Session')
    save_session_btn.setFixedHeight(28)
    save_session_btn.setEnabled(False)
    session_row.addWidget(save_session_btn)

    load_session_btn = QtWidgets.QPushButton('Load Session')
    load_session_btn.setFixedHeight(28)

    browse_session_btn = QtWidgets.QPushButton('Browse...')
    browse_session_btn.setFixedHeight(28)
    session_row.addWidget(browse_session_btn)
    session_row.addWidget(load_session_btn)

    session_row.addStretch()
    root.addLayout(session_row)

    root.addWidget(hline())

    progress=QtWidgets.QProgressBar()
    progress.setRange(0,100); progress.setValue(0); progress.setVisible(False)
    root.addWidget(progress)

    # Bottom bar
    bar=QtWidgets.QHBoxLayout()
    match_status=QtWidgets.QLabel('Load both frames and click all 24 patches on each chart.')
    match_status.setStyleSheet('font-size:10px;color:#888888;')
    bar.addWidget(match_status,1)

    apply_btn=QtWidgets.QPushButton('Apply Correction')
    apply_btn.setObjectName('blue'); apply_btn.setEnabled(False)
    bar.addWidget(apply_btn)


    close_btn=QtWidgets.QPushButton('Close')
    close_btn.clicked.connect(win.close); bar.addWidget(close_btn)
    root.addLayout(bar)

    # Populate session combo
    def refresh_sessions():
        session_combo.clear()
        session_combo.addItem('— select saved session —', None)
        for s in list_sessions():
            label = f'{"[HDR] " if s["hdr_mode"] else ""}{s["name"]}'
            session_combo.addItem(label, s)

    refresh_sessions()

    def update_buttons():
        ref_ready = (
            (state['ref_points'] is not None and state['ref_img'] is not None) or
            state.get('session_loaded', False)
        )
        src_ready = state['src_points'] is not None and state['src_img'] is not None
        patches_ready = ref_ready and src_ready
        apply_btn.setEnabled(patches_ready)
        save_session_btn.setEnabled(patches_ready)
        if patches_ready:
            match_status.setText('Ready — click Apply Correction & Export EXR.')
            match_status.setStyleSheet('font-size:11px;color:#66cc66;')

    def on_save_session():
        name = session_name_edit.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(win, 'Name Required', 'Please enter a session name.')
            return

        # Use stored patches if available, otherwise sample from image
        if state.get('session_loaded') and state['ref_patches'] is not None:
            ref_p = state['ref_patches']
        elif state['ref_img'] is not None and state['ref_points'] is not None:
            ref_p = sample_at_points(state['ref_img'], state['ref_points'])
        else:
            QtWidgets.QMessageBox.warning(win, 'No Reference', 'No reference patches available to save.')
            return

        if state['src_img'] is not None and state['src_points'] is not None:
            src_p = sample_at_points(state['src_img'], state['src_points'])
        elif state['src_patches'] is not None:
            src_p = state['src_patches']
        else:
            QtWidgets.QMessageBox.warning(win, 'No Source', 'No source patches available to save.')
            return

        # Ask where to save — no default path, user chooses freely
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            win, 'Save Session',
            f'{name}.json',
            'Session Files (*.json);;All Files (*)')
        if not save_path: return
        if not save_path.lower().endswith('.json'):
            save_path += '.json'

        data = {
            'version': SCRIPT_VERSION,
            'name': name,
            'hdr_mode': hdr_mode,
            'ref_patches': ref_p.tolist(),
            'src_patches': src_p.tolist(),
        }
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f'[AB ColorChecker] Session saved: {save_path}')
        refresh_sessions()
        match_status.setText(f'✓  Session "{name}" saved to {os.path.basename(save_path)}')
        match_status.setStyleSheet('font-size:11px;color:#66cc66;')

    def on_load_session():
        session = session_combo.currentData()
        if session is None:
            QtWidgets.QMessageBox.warning(win, 'No Session', 'Please select a saved session.')
            return

        state['ref_patches']    = session['ref_patches']
        state['ref_points']     = None
        state['ref_img']        = None
        state['ref_path']       = f"[Session: {session['name']}]"
        state['session_loaded'] = True
        match_status.setText(
            f'✓  Session "{session["name"]}" loaded — A side ready. '
            f'Now load a new Camera B frame and click 24 patches.'
        )
        match_status.setStyleSheet('font-size:11px;color:#22883c;')
        update_buttons()

    def on_apply():
        try:
            match_status.setText('Sampling patches...')
            match_status.setStyleSheet('font-size:10px;color:#aaaaaa;')
            progress.setVisible(True); progress.setValue(10)
            QtWidgets.QApplication.processEvents()

            if state.get('session_loaded') and state['ref_patches'] is not None:
                ref_p = state['ref_patches']
                print('[AB ColorChecker] Using A patches from saved session')
            else:
                ref_p = sample_at_points(state['ref_img'], state['ref_points'])
                state['ref_patches'] = ref_p

            src_p = sample_at_points(state['src_img'], state['src_points'])
            state['src_patches'] = src_p

            print('[AB ColorChecker] Reference patches:')
            for i in range(24):
                print(f'  {i+1:02d} {PATCH_NAMES[i]:20s} R={ref_p[i,0]:.4f} G={ref_p[i,1]:.4f} B={ref_p[i,2]:.4f}')
            print('[AB ColorChecker] Source patches:')
            for i in range(24):
                print(f'  {i+1:02d} {PATCH_NAMES[i]:20s} R={src_p[i,0]:.4f} G={src_p[i,1]:.4f} B={src_p[i,2]:.4f}')

            progress.setValue(20)
            match_status.setText('Building correction...')
            QtWidgets.QApplication.processEvents()

            correction = build_correction(src_p, ref_p, hdr=hdr_mode)

            if correction[0] == 'matrix':
                print(f'[AB ColorChecker] Colour matrix:')
                M = correction[1]
                print(f'  R: {M[0,0]:.6f}  {M[1,0]:.6f}  {M[2,0]:.6f}')
                print(f'  G: {M[0,1]:.6f}  {M[1,1]:.6f}  {M[2,1]:.6f}')
                print(f'  B: {M[0,2]:.6f}  {M[1,2]:.6f}  {M[2,2]:.6f}')

            verify_patches(src_p, ref_p, correction)

            progress.setValue(40)
            match_status.setText('Applying correction to image...')
            QtWidgets.QApplication.processEvents()

            corrected = apply_to_image(state['src_img'], correction)

            progress.setValue(75)

            src_dir = os.path.dirname(state['src_path'])
            src_base = os.path.splitext(os.path.basename(state['src_path']))[0]

            # For standard mode offer EXR / LUT / Both choice
            if not hdr_mode:
                exp_dlg = ExportChoiceDialog()
                if exp_dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted or exp_dlg.choice is None:
                    match_status.setText('Cancelled.')
                    match_status.setStyleSheet('font-size:10px;color:#888888;')
                    progress.setVisible(False); return
                export_choice = exp_dlg.choice
            else:
                export_choice = 'exr'  # HDR always exports EXR

            saved_files = []

            # Export EXR
            if export_choice in ('exr', 'both'):
                out_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                    win, 'Save Corrected EXR',
                    os.path.join(src_dir, f'{src_base}_matched.exr'),
                    'OpenEXR (*.exr);;All Files (*)')
                if out_path:
                    if not out_path.lower().endswith('.exr'):
                        out_path += '.exr'
                    save_exr(corrected, out_path)
                    print(f'[AB ColorChecker] EXR saved: {out_path}')
                    saved_files.append(os.path.basename(out_path))
                    try:
                        flame.batch.import_clip(out_path, 'Schematic Reel 1')
                        print('[AB ColorChecker] Imported into Batch')
                    except Exception as e:
                        print(f'[AB ColorChecker] Auto-import skipped: {e}')

            # Export LUT (standard mode only — matrix is linear so LUT == EXR exactly)
            if export_choice in ('lut', 'both'):
                lut_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                    win, 'Save 3D LUT',
                    os.path.join(src_dir, f'{src_base}_matched.cube'),
                    'LUT Cube (*.cube);;All Files (*)')
                if lut_path:
                    if not lut_path.lower().endswith('.cube'):
                        lut_path += '.cube'
                    # Domain = source white patch value * 2 for headroom
                    # Domain must cover full image range including highlights
                    # Matrix is linear so any domain size gives exact interpolation
                    _, M = correction
                    cube_str = build_lut_from_matrix(M, lut_size=33, domain_max=100.0)
                    with open(lut_path, 'w') as f:
                        f.write(cube_str)
                    print(f'[AB ColorChecker] LUT saved: {lut_path}')
                    saved_files.append(os.path.basename(lut_path))

            progress.setValue(100)
            if saved_files:
                match_status.setText(f'✓  Saved: {", ".join(saved_files)}  —  Session can now be saved for reuse.')
                match_status.setStyleSheet('font-size:11px;color:#66cc66;')
                save_session_btn.setEnabled(True)
            else:
                match_status.setText('Cancelled.')
                match_status.setStyleSheet('font-size:10px;color:#888888;')
                progress.setVisible(False)


        except Exception as e:
            import traceback; traceback.print_exc()
            match_status.setText(f'Error: {e}')
            match_status.setStyleSheet('font-size:11px;color:#cc5555;')
            progress.setVisible(False)


    def on_browse_session():
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            win, 'Load Session File', SESSION_DIR,
            'Session Files (*.json);;All Files (*)')
        if not path: return
        try:
            with open(path) as f:
                data = json.load(f)
            session = {
                'name': data.get('name', os.path.basename(path)),
                'hdr_mode': data.get('hdr_mode', False),
                'ref_patches': np.array(data['ref_patches']),
                'src_patches': np.array(data['src_patches']),
                'path': path,
            }
            # Temporarily add to combo and select it
            label = f'{"[HDR] " if session["hdr_mode"] else ""}{session["name"]}'
            session_combo.addItem(label, session)
            session_combo.setCurrentIndex(session_combo.count()-1)
        except Exception as e:
            match_status.setText(f'Error loading session: {e}')
            match_status.setStyleSheet('font-size:11px;color:#cc5555;')

    apply_btn.clicked.connect(on_apply)
    save_session_btn.clicked.connect(on_save_session)
    load_session_btn.clicked.connect(on_load_session)
    browse_session_btn.clicked.connect(on_browse_session)

    win.exec()


def get_batch_custom_ui_actions():
    return [{'name': SCRIPT_NAME, 'actions': [{
        'name': 'Match Cameras...', 'execute': launch_ui, 'minimumVersion': '2025'}]}]

def get_media_panel_custom_ui_actions():
    return [{'name': SCRIPT_NAME, 'actions': [{
        'name': 'Match Cameras...', 'execute': launch_ui, 'minimumVersion': '2025'}]}]
