"""
Train a non-autoregressive FastSpeech 2 model on the german single speaker eva_k dataset by MAILabs

This requires having a trained TransformerTTS model in the right directory to knowledge distill the durations.
"""

import os

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "6"
import random
import warnings

import torch

from FastSpeech2.FastSpeech2 import FastSpeech2
from FastSpeech2.FastSpeechDataset import FastSpeechDataset
from FastSpeech2.fastspeech2_train_loop import train_loop
from Utility.path_to_transcript_dicts import build_path_to_transcript_dict_eva

warnings.filterwarnings("ignore")

torch.manual_seed(13)
random.seed(13)

if __name__ == '__main__':
    print("Preparing")
    cache_dir = os.path.join("Corpora", "Eva")
    save_dir = os.path.join("Models", "FastSpeech2_Eva")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    path_to_transcript_dict = build_path_to_transcript_dict_eva()

    device = torch.device("cuda")

    train_set = FastSpeechDataset(path_to_transcript_dict,
                                  train=True,
                                  acoustic_model_name="TransformerTTS_Eva/best.pt",
                                  diagonal_attention_head_id=None,
                                  cache_dir=cache_dir, lang="de",
                                  min_len_in_seconds=1,
                                  max_len_in_seconds=10,
                                  device=device)
    valid_set = FastSpeechDataset(path_to_transcript_dict,
                                  train=False,
                                  acoustic_model_name="TransformerTTS_Eva/best.pt",
                                  diagonal_attention_head_id=None,
                                  cache_dir=cache_dir,
                                  lang="de",
                                  min_len_in_seconds=1,
                                  max_len_in_seconds=10,
                                  device=device)

    model = FastSpeech2(idim=133, odim=80, spk_embed_dim=None)

    print("Training model")
    train_loop(net=model,
               train_dataset=train_set,
               valid_dataset=valid_set,
               device=device,
               save_directory=save_dir,
               steps=400000,
               batch_size=32,
               gradient_accumulation=1,
               epochs_per_save=10,
               use_speaker_embedding=False,
               lang="de",
               lr=0.01,
               warmup_steps=8000)