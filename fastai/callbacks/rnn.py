"Regroups lr adjustment to seq_len, AR and TAR"
from ..torch_core import *
from ..callback import *
from ..basic_train import Learner

__all__ = ['RNNTrainer']

@dataclass
class RNNTrainer(Callback):
    "`Callback` that regroups lr adjustment to seq_len, AR and TAR."
    learn:Learner
    bptt:int
    alpha:float=0.
    beta:float=0.
    adjust:bool=True
        
    def on_epoch_begin(self, **kwargs):
        "Reset the hidden state of the model."
        self.learn.model.reset()

    def on_loss_begin(self, last_output:Tuple[Tensor,Tensor,Tensor], **kwargs):
        "Save the extra outputs for later and only returns the true output."
        self.raw_out,self.out = last_output[1],last_output[2]
        return last_output[0]

    def on_backward_begin(self, last_loss:Rank0Tensor, last_input:Tensor, **kwargs):
        "Adjusts the lr to the sequence length and applies AR and TAR to `last_loss`."
        if self.adjust: self.learn.opt.lr *= last_input.size(1) / self.bptt
        #AR and TAR
        if self.alpha != 0.:  last_loss += (self.alpha * self.out[-1].pow(2).mean()).sum().float()
        if self.beta != 0.:
            h = self.raw_out[-1]
            if len(h)>1: last_loss += (self.beta * (h[1:] - h[:-1]).pow(2).mean()).sum().float()
        return last_loss
