# BigVGAN + Semantic-VAE Audit — Sept 22, 2026

> Casey wants us to learn paradigms, not fork heavy PyTorch models.

## BigVGAN

**URL**: https://github.com/NVIDIA/BigVGAN
**Paper**: https://arxiv.org/abs/2206.04658
**Paradigm**: Universal neural vocoder with large-scale training. Maps mel-spectrograms → raw audio waveforms via a generator network with anti-aliased up/downsampling.

**Core innovation**: Anti-aliased activation (upsample → activation → downsample fused into a single CUDA kernel). Custom CUDA kernels give 1.5-3x speedup on A100.

**Killer feature**: Single model handles speech, music, environmental sounds — universal across audio types. Pretrained checkpoints for 22kHz, 24kHz, 32kHz, 44kHz.

**File structure**:
```
bigvgan.py            # Generator (main model)
discriminators.py     # Multi-period + multi-scale discriminators
meldataset.py         # Mel-spectrogram dataset loader
activations.py        # Custom Snake + anti-aliased activations
alias_free_activation/ # CUDA kernels
train.py              # Training loop
inference.py          # Inference
inference_e2e.py      # End-to-end inference (text → audio)
env.py                # Env vars, paths
utils.py              # Logging, checkpointing
loss.py               # Multi-scale mel loss + STFT loss
configs/              # YAML configs for different sample rates
```

**Routing/inference flow**:
1. Input: mel-spectrogram (T × 80 frequencies)
2. Generator: 1D conv stack with anti-aliased up/downsampling → raw waveform (T × upsample_factor)
3. Discriminator (training only): multi-period + multi-scale → real/fake
4. Loss: mel-spectrogram L1 + STFT loss + adversarial

**Quilt-mapping**:
| BigVGAN concept | Substrate Walker equivalent |
|------------------|------------------------------|
| Generator | lore composer (takes seed + voice → prose) |
| Mel-spectrogram input | polygon vertex sequence |
| Raw waveform output | rendered lore |
| Discriminator | JEV canon-gate |
| Multi-period discriminator | multi-voice JEV (structuralist / lyricist / noir etc.) |
| Adversarial training | composite lore mining (mine + score + filter) |
| Anti-aliased activation | FNV-1a canary (substrate-independent witness) |

**Lean variant proposal** (200-line Python):

```python
"""
poly_vocoder.py — A 200-line universal vocoder for the Quilt substrate.

Not a literal port of BigVGAN. We steal the *pattern*: a universal model that
handles multiple input types via a single shared backbone + a typed head.

The "audio" in our case is lore rhythm — the syllable/stress pattern of prose.
We encode it as a 1D signal, push it through a simple conv stack, and decode
to a different modality (e.g., visual cadence).
"""
import torch
import torch.nn as nn

class PolyVocoder(nn.Module):
    """Universal head: any input modality → any output modality."""
    
    def __init__(self, in_dim=80, out_dim=256, hidden=128, n_layers=4):
        super().__init__()
        self.embed = nn.Linear(in_dim, hidden)
        self.backbone = nn.Sequential(*[
            nn.Conv1d(hidden, hidden, 3, padding=1) for _ in range(n_layers)
        ])
        self.head = nn.Linear(hidden, out_dim)
    
    def forward(self, x):
        # x: (B, T, in_dim)
        h = self.embed(x).transpose(1, 2)  # (B, hidden, T)
        h = self.backbone(h).transpose(1, 2)  # (B, T, hidden)
        return self.head(h)  # (B, T, out_dim)

# Usage: rhythm → image
vocoder = PolyVocoder(in_dim=80, out_dim=256)
lore_rhythm = torch.randn(1, 100, 80)  # 100 tokens × 80 rhythm features
visual = vocoder(lore_rhythm)  # 100 × 256 visual cadence
```

This is what we'd actually build for Quilt — a 200-line poly-vocoder that any substrate cell can use as a head.

---

## Semantic-VAE

**URL**: https://github.com/ZhikangNiu/Semantic-VAE
**Paradigm**: Semantic VAE for audio. Compresses audio into a semantic latent space, then reconstructs. The latent space is structured by SSL (self-supervised learning) features.

**File structure** (partial):
```
semantic_vae/
├── dac/                # Descriptive Audio Codec
├── conf/               # Configs
├── ckpts/              # Pretrained checkpoints
├── examples/
├── scripts/
├── recon_wave.sh       # Reconstruct waveform
├── extract_latent.sh   # Extract latents
└── extract_ssl_feature.sh # Extract SSL features
```

**Core innovation**: Compress audio using SSL features (e.g., from HuBERT, WavLM) rather than mel-spectrograms. The resulting latent space is "semantic" — it captures what the audio *means*, not just its acoustic features.

**Routing/inference flow**:
1. Input: raw audio
2. SSL feature extractor (frozen) → semantic features
3. VAE encoder → μ, σ
4. Sample z ~ N(μ, σ)
5. Decoder → reconstructed semantic features
6. DAC (Descriptive Audio Codec) → raw audio

**Quilt-mapping**:
| Semantic-VAE concept | Substrate Walker equivalent |
|----------------------|------------------------------|
| SSL feature extractor | FNV-1a canary hash |
| VAE encoder | lore composer (seed + voice → latent concept) |
| μ, σ | lore probability distribution |
| Latent z | single lore instance |
| DAC decoder | lore renderer (latent → prose) |
| Reconstruction loss | substrate fidelity |

**Lean variant proposal**:
```python
"""
semantic_vae_lore.py — Compress lores into a semantic latent space.

The key insight from Semantic-VAE: use a strong pretrained model to extract
"semantic features" first, then VAE on top. For Quilt, the pretrained model
is JEV — it already knows what's canon and what's not.

JEV scores a lore → that's our "SSL feature" → we VAE-compress the score
distribution → we can sample new "canon-likely" lores from the latent.
"""
import torch
import torch.nn as nn

class SemanticLoreVAE(nn.Module):
    """JEV-scored lore → semantic latent → new lore concept."""
    
    def __init__(self, jev_dim=64, latent_dim=16, hidden=64):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(jev_dim, hidden), nn.ReLU(),
            nn.Linear(hidden, 2 * latent_dim)  # μ and σ
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden), nn.ReLU(),
            nn.Linear(hidden, jev_dim)
        )
    
    def encode(self, jev_scores):
        h = self.encoder(jev_scores)
        mu, log_sigma = h.chunk(2, dim=-1)
        return mu, log_sigma
    
    def reparameterize(self, mu, log_sigma):
        sigma = log_sigma.exp()
        eps = torch.randn_like(sigma)
        return mu + sigma * eps
    
    def decode(self, z):
        return self.decoder(z)
    
    def forward(self, jev_scores):
        mu, log_sigma = self.encode(jev_scores)
        z = self.reparameterize(mu, log_sigma)
        return self.decode(z), mu, log_sigma
```

This gives us a "lore diffusion model" — we can sample from the latent space and decode back to JEV scores, then use those scores to guide lore generation.

---

## Synthesis

### Common design patterns
1. **Pretrained backbone + pluggable head**: BigVGAN has anti-aliased conv stack + per-sample-rate config. Semantic-VAE has SSL extractor + DAC decoder. Both separate the "smart" part from the "data-format" part.
2. **Anti-aliasing as a first-class concern**: BigVGAN's killer feature. The substrate walker already does this with FNV-1a canary.
3. **Multi-loss training**: BigVGAN uses mel loss + STFT loss + adversarial. Quilt canon-promotion is similar (JEV score + paraphrase check + density).

### What we can borrow without copying
- The **universal head** pattern (any in_dim → any out_dim via a shared backbone) → our cell kinds should be polymorphic heads over a shared cell state
- **Anti-aliasing** at every level (input, intermediate, output) → our witness log should hash at every cell transition
- **Multi-loss training** → our composite lore v9+ uses 7-voice scoring, similar idea

### A new repo idea: `quilt-polyvocoder`
A 200-500 line Python package that:
- Takes any substrate cell (lore, polygon, audio rhythm)
- Encodes via JEV → semantic features (the "SSL extractor")
- VAE-compresses to a shared latent space
- Decodes to any output modality (prose, image, audio)

This is the "fusion" repo that combines BigVGAN's universality + Semantic-VAE's semantic latent + Quilt's substrate walker cells.

**Use case**: 
1. Generate lore as prose (ZAI/DeepSeek)
2. Score with JEV
3. Compress to latent
4. Sample nearby lores → "canon-likely variants"
5. Render to multiple modalities simultaneously

This is the "future-GAN" Casey was asking about — an army of APIs generating variants, JEV judging, the substrate cell-graph mediating.

