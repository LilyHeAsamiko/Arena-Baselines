import imageio
import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd

from .utils import *
from .constants import policy_i2id

sns.set()


def vis_result_matrix(result_matrix):

    if len(np.shape(result_matrix)) == 3:

        for policy_i in range(result_matrix.shape[2]):

            policy_id = policy_i2id(policy_i)

            fig = plt.figure()
            sns.heatmap(
                pd.DataFrame(result_matrix[:, :, policy_i]),
            )
            plt.close()

            img = get_img_from_fig(fig)

            save_img(
                img=img,
                dir='result_matrix-{}.jpg'.format(policy_id),
            )
    else:
        raise NotImplementedError


def get_img_from_fig(fig, dpi=180):
    """Returns an image as numpy array from figure
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180)
    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()
    img = cv2.imdecode(img_arr, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def save_img(img, dir):
    imageio.imwrite(dir, img)
