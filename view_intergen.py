from intergen.player import Player


DATASET_PATH = 'res/InterGen'
SMPL_PATH = DATASET_PATH + '/smpl.pkl'

player = Player(dataset_dir=DATASET_PATH, smpl_path=SMPL_PATH)
player.run()
