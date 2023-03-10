# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/riccati_bm.ipynb.

# %% auto 0
__all__ = ['R_BM_sig', 'R_BM_pow', 'model_sig', 'model_pow', 'riccati_sol_sig', 'riccati_sol_pow', 'appr_exp_sig', 'appr_exp_pow',
           'MC', 'CoD', 'A_M', 'vTu']

# %% ../nbs/riccati_bm.ipynb 4
import numpy as np
import math 
import scipy.special
import cmath
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from tqdm.auto import tqdm

# %% ../nbs/riccati_bm.ipynb 6
def R_BM_sig(u,K):
    argument=np.concatenate((u,(0,0)), axis=None)
    Rseq=np.zeros(K+1, dtype=complex)
    for k in range(K+1):
        x=0
        for j in range(0,k+1):
            x=x+scipy.special.comb(k,j)*argument[j+1]*argument[k-j+1]
        y=1/2*(argument[k+2]+x)
        Rseq[k]=y
    return Rseq

# %% ../nbs/riccati_bm.ipynb 8
def R_BM_pow(u,K):
    argument=np.concatenate((u,(0,0)), axis=None)
    Rseq=np.zeros(K+1, dtype=complex)
    for k in range(K+1):
        x=0
        for j in range(0,k+1):
            x=x+(j+1)*(k-j+1)*argument[j+1]*argument[k-j+1]
        y=1/2*((k+1)*(k+2)*argument[k+2]+x)
        Rseq[k]=y
    return Rseq

# %% ../nbs/riccati_bm.ipynb 10
def model_sig(psi,t,K):
    dpsidt = R_BM_sig(psi,K).real
    return dpsidt

# %% ../nbs/riccati_bm.ipynb 11
def model_pow(psi,t,K):
    dpsidt = R_BM_pow(psi,K).real
    return dpsidt

# %% ../nbs/riccati_bm.ipynb 13
def riccati_sol_sig(u_sig,timegrid,K):
    """Sig lift"""
    psi0_sig = np.concatenate((u_sig,np.zeros(K+1-len(u_sig), dtype=complex)))
    return odeint(model_sig,psi0_sig.real,timegrid,args=(K,))

# %% ../nbs/riccati_bm.ipynb 14
def riccati_sol_pow(u_pow,timegrid,K):
    """Pow lift"""
    psi0_pow = np.concatenate((u_pow,np.zeros(K+1-len(u_pow), dtype=complex)))
    return odeint(model_pow,psi0_pow.real,timegrid,args=(K,))

# %% ../nbs/riccati_bm.ipynb 16
def appr_exp_sig(u_sig,timegrid,K):
    """Sig lift"""
    return np.exp(riccati_sol_sig(u_sig,timegrid,K)[:,0])

# %% ../nbs/riccati_bm.ipynb 17
def appr_exp_pow(u_pow,timegrid,K):
    """Pow lift"""
    return np.exp(riccati_sol_pow(u_pow,timegrid,K)[:,0])

# %% ../nbs/riccati_bm.ipynb 19
def MC(u_sig,T,n_MC,N):
    tt=0
    Lap = np.zeros(n_MC, dtype=complex)

    for i in tqdm(range(n_MC)):
        B_run= np.zeros((1,N))
        B_run=np.random.normal(0,np.sqrt(tt), (1,N))
        #print(B)
        exponent_run=u_sig[0]
        for k in range(1,len(u_sig)):
            exponent_run=exponent_run+u_sig[k]/math.factorial(k)*B_run**k 
        Lap[i]=np.mean(np.exp(exponent_run))
        tt+=T/n_MC
    return Lap

# %% ../nbs/riccati_bm.ipynb 21
def CoD(old_vector,n_old, n_new):
    #ChangeofDiscretisation
    new_vector = np.zeros(n_new)
    for i in range(n_new):
        index=int(min(i*n_old/n_new,n_new-1))
        new_vector[i] = old_vector[index]
    return new_vector 

# %% ../nbs/riccati_bm.ipynb 56
def A_M(M,u_sig,K):
  #Operator A_M
    step=u_sig+R_BM_sig(u_sig,K)/M
    return step

# %% ../nbs/riccati_bm.ipynb 57
def vTu(u,T,N,M):
    K=2*N
    u_running=np.concatenate((u.real,np.zeros(K+1-len(u.real))))
    v0n=np.zeros(N+1)
    space = np.zeros(N)
    lam = T*M/N
    for n in range(N):
        v0last=np.exp(u_running.real[0])
        v0n[n]=v0last
        u_running=A_M(M,u_running,K)
        for m in range(n+1):
            space[n]+=v0n[m]*(1-lam)**(n-m)*lam**(m)*scipy.special.comb(n,m)
    return space
