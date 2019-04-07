# --coding:utf-8--
'''
@author: cailikun
@time: 19-3-27 上午10:26
'''
import torch
import torch.nn.functional as F
from attack_utils import gen_adv_loss
import numpy as np

EVAL_FREQUENCY = 100

def train(epoch, batch_idx, model, data, labels, optimizer, x_advs=None):
    model.train()
    optimizer.zero_grad()
    logits = model(data)
    preds = logits.max(1)[1]
    loss1 = gen_adv_loss(logits, labels, mean=True)
    if x_advs is not None:
        idx = np.random.randint(len(x_advs))
        logits_adv = model(x_advs[idx])
        loss2 = gen_adv_loss(logits_adv, labels, mean=True)
        loss = 0.5 * (loss1 + loss2)
    else:
        loss2 = torch.zeros(loss1.size())
        loss = loss1
    loss.backward()
    optimizer.step()
    if batch_idx % EVAL_FREQUENCY == 0:
        print('Step: {}(epoch: {})\tLoss: {:.6f}<=({:.6f}, {:.6f})\tError: {:.2f}%'.format(
            batch_idx, epoch+1, loss.item(), loss1.item(), loss2.item(), error_rate(preds, labels)
        ))

def test_error_rate(model, test_loader, cuda=True):
    device = torch.device('cuda' if cuda else 'cpu')
    model.eval()
    correct = 0
    with torch.no_grad():
        for data, labels in test_loader:
            data, labels = data.to(device), labels.to(device)
            logits = model(data)
            preds = logits.max(1)[1]
            correct += preds.eq(labels).sum().item()
    error_rate = 100. - 100. * correct / len(test_loader.dataset)
    return error_rate

def error_rate(preds, labels):
    '''
    Run the error rate
    '''
    assert preds.size() == labels.size()
    return 100.0 - (100.0 * preds.eq(labels).sum().item()) / preds.size(0)





