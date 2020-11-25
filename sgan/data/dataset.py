import os
import torch
import zipfile
import subprocess

from pathlib import Path
from typing import Sequence

from torch.utils.data import Dataset
from torch.utils.data.sampler import SubsetRandomSampler

from torchvision.datasets import ImageFolder
from torchvision.transforms import transforms
from sklearn.model_selection import train_test_split

image_size = (64, 64)

# transform
default_transforms = transforms.Compose([
    transforms.Resize(image_size),
    transforms.CenterCrop(image_size),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])


# extract + transform
class CelebDataset(ImageFolder):
    def __init__(self, *args, download=False, root='~/celeba', transform=default_transforms, **kwargs):
        root = Path(root).expanduser()

        if download:
            os.makedirs(root, exist_ok=True)
            # download dataset
            download_command = ['kaggle', 'datasets', 'download', 'jessicali9530/celeba-dataset', '-p', f'{str(root)}']
            subprocess.run(download_command)

            with zipfile.ZipFile(root / 'celeba-dataset.zip', "r") as f:
                f.extractall(root)

            # remove zip file
            os.remove(root / 'celeba-dataset.zip')

        root = root / 'img_align_celeba'
        super().__init__(*args, root=root, **kwargs, transform=transform)


class InfiniteIterator(object):
    def __init__(self, dataset: Dataset, indices: Sequence, *, batch_size):
        self.loader = torch.utils.data.DataLoader(
            dataset, sampler=SubsetRandomSampler(indices), batch_size=batch_size)
        self.loader = iter(self.loader)

    def __iter__(self):
        return self.loader


def split_data(dataset, train_size=0.6, val_size=0.2, test_size=0.2, shuffle=True, random_state=42):
    assert train_size + test_size + val_size == 1.

    split_kwargs = dict(random_state=random_state, shuffle=shuffle)
    indices = list(range(len(dataset)))
    train_indices, test_indices = train_test_split(indices, test_size=test_size, **split_kwargs)
    train_indices, val_indices = train_test_split(train_indices, test_size=val_size / train_size, **split_kwargs)
    return train_indices, val_indices, test_indices


def create_iterators(dataset, train_indices, val_indices, batch_size=64):
    train_iterator = iter(InfiniteIterator(dataset, train_indices, batch_size=batch_size))
    val_iterator = iter(InfiniteIterator(dataset, val_indices, batch_size=batch_size))
    return train_iterator, val_iterator