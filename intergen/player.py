import re
from pathlib import Path
from glob import glob
from OpenGL.GL import *
from OpenGL.GLUT import *
from fairmotion.data.amass import load_body_model
from fairmotion.viz import gl_render
from fairmotion.viz.bvh_visualizer import MocapViewer
from intergen.motion import create_motion_from_amass_data


class Player(MocapViewer):
    def __init__(self, dataset_dir: str, smpl_path='smpl.pkl'):
        self._inited = False
        self._bm = load_body_model(smpl_path)
        self._dataset_dir = Path(dataset_dir)
        self._seek_dataset()
        self._load_motion(1)
        super().__init__(self.loaded_motion, scale=0.1, render_overlay=True)
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

    def overlay_callback(self):
        if self.render_overlay:
            self._render_player_state()
            self._render_motion_text()

    def _load_motion(self, idx: int):
        motion_filename, text_filename = self._get_filename(idx)

        m1 = create_motion_from_amass_data(filename=motion_filename, bm=self._bm, motion_key='person1')
        m2 = create_motion_from_amass_data(filename=motion_filename, bm=self._bm, motion_key='person2')
        self.loaded_motion = [m1, m2]

        with open(text_filename, 'r') as f:
            self.text = f.read()

        self.idx = int(os.path.basename(motion_filename).split('.')[0])

        if self._inited:
            self.motions = self.loaded_motion

    def _render_player_state(self):
        w, h = self.window_size
        t = self.cur_time % self.motions[0].length()
        frame = self.motions[0].time_to_frame(t)
        gl_render.render_text(
            f"Motion[{self.idx}] Frame number: {frame}",
            pos=[0.05 * w, 0.05 * h],
            font=GLUT_BITMAP_TIMES_ROMAN_24,
        )

    def _render_motion_text(self):
        TEXT_H = 0.025
        num_lines = len(self.text.split('\n'))
        w, h = self.window_size
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        gl_render.render_quad_2D(
            [0, (1 - TEXT_H * num_lines) * h], [0, h], [w, h], [w, (1 - TEXT_H * num_lines) * h],
            color=[1, 1, 1, 1]
        )
        for i, line in enumerate(self.text.split('\n')):
            gl_render.render_text(
                line,
                pos=[10, (1 - TEXT_H * (num_lines - i - 1)) * h],
                font=GLUT_BITMAP_HELVETICA_12,
            )

    def _get_filename(self, idx: int):
        if idx not in self.motion_ids:
            print(f"Motion[{idx}] not found in the dataset.")
            idx = self.motion_ids[0]
        motion_filename = self._dataset_dir / "motions" / f"{idx}.pkl"
        text_filename = self._dataset_dir / "annots" / f"{idx}.txt"
        return motion_filename, text_filename

    def _seek_dataset(self):
        motions = glob(str(self._dataset_dir / "motions" / "*.pkl"))
        motions = [os.path.basename(motion) for motion in motions]
        self.motion_ids = []
        for bn in motions:
            idx = bn.split('.')[0]
            if re.match(r'^\d+$', idx):
                self.motion_ids.append(int(idx))
