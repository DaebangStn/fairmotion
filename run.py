from fairmotion.viz.bvh_visualizer import MocapViewer
from fairmotion.data.amass import load_body_model

from intergen import create_motion_from_amass_data


MOCAP_FILE = 'InterGen/motions/22.pkl'

bm = load_body_model('smpl.pkl')
motions = []
motion1 = create_motion_from_amass_data(filename=MOCAP_FILE, bm=bm, motion_key='person1')
motions.append(motion1)
motion2 = create_motion_from_amass_data(filename=MOCAP_FILE, bm=bm, motion_key='person2')
motions.append(motion2)

view = MocapViewer(motions, scale=0.1)
view.run()
