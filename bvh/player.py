from pathlib import Path
from glob import glob
from OpenGL.GLUT import *
from fairmotion.data import bvh
from fairmotion.viz import gl_render
from fairmotion.viz.bvh_visualizer import MocapViewer


class Player(MocapViewer):
    def __init__(self, dataset_dir: str):
        self._inited = False
        self._play_speed_memo = 1.0
        self._dataset_dir = Path(dataset_dir)
        self._seek_dataset()
        self._load_motion(0)
        super().__init__(self.motions, scale=0.1, render_overlay=True)
        self._inited = True

    def keyboard_callback(self, key):
        super().keyboard_callback(key)
        if key == b'n':
            self._load_motion(self.idx + 1)
        elif key == b'p':
            self._load_motion(self.idx - 1)
        elif key == b'i':
            motion_id = int(input("Enter motion id: "))
            self._load_motion(motion_id)
        elif key == b' ':
            if self.play_speed == 0:
                self.play_speed = self._play_speed_memo
            else:
                self._play_speed_memo = self.play_speed
                self.play_speed = 0

    def overlay_callback(self):
        if self.render_overlay:
            pass
            # self._render_player_state()

    def _load_motion(self, idx: int):
        self.idx = idx
        self.motions = [bvh.load(self._dataset_dir / self.motion_names[self.idx])]

    def _render_player_state(self):
        w, h = self.window_size
        t = self.cur_time % self.motion_set[0].length()
        frame = self.motions[0].time_to_frame(t)
        gl_render.render_text(
            f"Motion[{self.idx}] Frame number: {frame}",
            pos=[0.05 * w, 0.05 * h],
            font=GLUT_BITMAP_TIMES_ROMAN_24,
        )

    def _seek_dataset(self):
        motions = glob(str(self._dataset_dir / "*.bvh"))
        self.motion_names = [os.path.basename(motion) for motion in motions]
