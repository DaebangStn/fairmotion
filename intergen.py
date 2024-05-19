import torch
import numpy as np
from fairmotion.core import motion as motion_class
from fairmotion.ops import conversions
from fairmotion.data.amass import create_skeleton_from_amass_bodymodel, joint_names


def create_motion_from_amass_data(filename, bm, motion_key, override_betas=None):
    bdata = np.load(filename, allow_pickle=True)
    fps = float(bdata["mocap_framerate"])
    bdata = bdata[motion_key]

    if override_betas is not None:
        betas = torch.Tensor(override_betas[:10][np.newaxis]).to("cpu")
    else:
        betas = torch.Tensor(bdata["betas"][:10][np.newaxis]).to("cpu")

    skel = create_skeleton_from_amass_bodymodel(
        bm, betas, len(joint_names), joint_names,
    )

    root_orient = bdata["root_orient"]  # controls the global root orientation
    pose_body = bdata["pose_body"]  # controls body joint angles
    trans = bdata["trans"]  # controls the finger articulation

    motion = motion_class.Motion(skel=skel, fps=fps)

    num_joints = skel.num_joints()
    parents = bm.kintree_table[0].long()[:num_joints]

    for frame in range(pose_body.shape[0]):
        pose_body_frame = pose_body[frame]
        root_orient_frame = root_orient[frame]
        root_trans_frame = trans[frame]
        pose_data = []
        for j in range(num_joints):
            if j == 0:
                T = conversions.Rp2T(
                    conversions.A2R(root_orient_frame), root_trans_frame
                )
            else:
                T = conversions.R2T(
                    conversions.A2R(
                        pose_body_frame[(j - 1) * 3: (j - 1) * 3 + 3]
                    )
                )
            pose_data.append(T)
        motion.add_one_frame(pose_data)

    return motion