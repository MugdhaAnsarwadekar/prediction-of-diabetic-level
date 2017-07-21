import numpy as np
from scipy.optimize import minimize
from scipy.io import loadmat
from numpy.linalg import det, inv
from math import sqrt, pi
import scipy.io
import matplotlib.pyplot as plt
import pickle
import sys

def ldaLearn(X,y):
    # Inputs
    # X - a N x d matrix with each row corresponding to a training example
    # y - a N x 1 column vector indicating the labels for each training example
    #
    # Outputs
    # means - A d x k matrix containing learnt means for each of the k classes
    # covmat - A single d x d learnt covariance matrix
	
    k=int(np.max(y))
    d=int(X.shape[1])
    means=np.zeros((k,d))
    y=y.flatten()
    for i in range(0,k):
        means[i,:]=np.mean(X[y==i+1],axis=0)
    means=means.T
    covmat=np.cov(X.T)

    return means,covmat

def qdaLearn(X,y):
    # Inputs
    # X - a N x d matrix with each row corresponding to a training example
    # y - a N x 1 column vector indicating the labels for each training example
    #
    # Outputs
    # means - A d x k matrix containing learnt means for each of the k classes
    # covmats - A list of k d x d learnt covariance matrices for each of the k classes
	
    k=int(np.max(y))
    d=int(X.shape[1])
    means=np.zeros((k,d))
    covmats=[np.zeros((d,d))]*k
    y=y.flatten()
    for i in range(0,k):
        means[i,:]=np.mean(X[y==i+1],axis=0)
        covmats[i]=np.cov(X[y==i+1].T)
    means=means.T    

    return means,covmats

def ldaTest(means,covmat,Xtest,ytest):

    # Inputs
    # means, covmat - parameters of the LDA model
    # Xtest - a N x d matrix with each row corresponding to a test example
    # ytest - a N x 1 column vector indicating the labels for each test example
    # Outputs
    # acc - A scalar accuracy value
    # ypred - N x 1 column vector indicating the predicted labels
	
    N = int(Xtest.shape[0])
    ypred=np.zeros((N,1))
    k = int(means.shape[1])
    Correct = 0.0
    covmatinv = inv(covmat)
    ytest = ytest.astype(int)
    for i in range (0,N):
        predict=np.zeros((1,k))
        for j in range (0,k):
            predict[0,j] = np.exp((-1.0/2)*np.dot(np.dot(np.transpose(Xtest[i,:].T - means[:, j]),covmatinv),(Xtest[i,:].T - means[:, j])))
        m=np.max(predict)
        predict=list(predict.ravel())
        ypred[i]=predict.index(m)+1
        if (ypred[i] == ytest[i]):
            Correct = Correct + 1
    acc = Correct/N*100
    ypred=ypred.flatten()
    ypred = ypred.astype(int)
    return acc,ypred

def qdaTest(means,covmats,Xtest,ytest):

    # Inputs
    # means, covmats - parameters of the QDA model
    # Xtest - a N x d matrix with each row corresponding to a test example
    # ytest - a N x 1 column vector indicating the labels for each test example
    # Outputs
    # acc - A scalar accuracy value
    # ypred - N x 1 column vector indicating the predicted labels
	
    N = int(Xtest.shape[0])
    ypred=np.zeros((N,1))
    k = int(means.shape[1])
    d= np.zeros(k)
    Correct = 0.0
    for i in range (0,k):
        d[i] = 1.0/(np.power(2 * pi, np.size(Xtest, 1) / 2.0) * np.power(det(covmats[i]),1/2.0));
        covmats[i] = inv(covmats[i])
    ytest = ytest.astype(int)
    for i in range (0,N):
        predict=np.zeros((1,k))
        for j in range (0,k):
            predict[0,j] = (np.exp(-(1.0/2)*np.dot(np.dot(np.transpose(Xtest[i,:].T - means[:, j]),covmats[j]),(Xtest[i,:].T - means[:, j])))) * d[j]
        m=np.max(predict)
        predict=list(predict.ravel())
        ypred[i]=predict.index(m)+1
        if (ypred[i] == ytest[i]):
            Correct = Correct + 1
    acc = Correct/N*100
    ypred=ypred.flatten()
    ypred = ypred.astype(int)

    return acc,ypred

def learnOLERegression(X,y):
    # Inputs:
    # X = N x d
    # y = N x 1
    # Output:
    # w = d x 1
    #N,d = X.shape
    w = np.dot(np.dot(np.linalg.inv(np.dot(np.transpose(X),X)),np.transpose(X)),y)
    return w

def learnRidgeRegression(X,y,lambd):
    # Inputs:
    # X = N x d
    # y = N x 1
    # lambd = ridge parameter (scalar)
    # Output:
    # w = d x 1
    d=X.shape[1]
    w=np.dot(np.dot(np.linalg.inv((lambd*np.identity(d))+np.dot(X.T, X)), np.transpose(X)),y)
    return w

def testOLERegression(w,Xtest,ytest):
    # Inputs:
    # w = d x 1
    # Xtest = N x d
    # ytest = X x 1
    # Output:
    # mse
    N,d = Xtest.shape
    mse = np.divide(np.sum(np.power(np.subtract(ytest, np.dot(Xtest,w)),2)),N)
    return mse

def regressionObjVal(w, X, y, lambd):

    # compute squared error (scalar) and gradient of squared error with respect
    # to w (vector) for the given data X and y and the regularization parameter
    # lambda
	
    y = y.flatten()
    error_grad = np.dot(np.transpose(X),np.subtract(np.dot(X,w),y))+lambd*w
    error_grad = error_grad.flatten()
    error= np.sum(np.power(y-np.dot(w,X.T),2))/2+lambd*(np.dot(w.T,w))/2
    error_grad=error_grad.flatten()

    return error, error_grad

def mapNonLinear(x,p):
    # Inputs:
    # x - a single column vector (N x 1)
    # p - integer (>= 0)
    # Outputs:
    # Xd - (N x (d+1))
    Xd=np.zeros((x.shape[0],p+1))
    for j in range (p+1):
        Xd[:,j]= np.power(x,j)
    return Xd


# load the sample data
if sys.version_info.major == 2:
    X,y,Xtest,ytest = pickle.load(open('F:\Mugdha\Projects\ML\Assignment2\sample.pickle','rb'))
else:
    X,y,Xtest,ytest = pickle.load(open('F:\Mugdha\Projects\ML\Assignment2\sample.pickle','rb'),encoding = 'latin1')

# LDA
means,covmat = ldaLearn(X,y)
ldaacc,ldares = ldaTest(means,covmat,Xtest,ytest)
print('LDA Accuracy = '+str(ldaacc))
# QDA
means,covmats = qdaLearn(X,y)
qdaacc,qdares = qdaTest(means,covmats,Xtest,ytest)
print('QDA Accuracy = '+str(qdaacc))

# plotting boundaries
x1 = np.linspace(-5,20,100)
x2 = np.linspace(-5,20,100)
xx1,xx2 = np.meshgrid(x1,x2)
xx = np.zeros((x1.shape[0]*x2.shape[0],2))
xx[:,0] = xx1.ravel()
xx[:,1] = xx2.ravel()

fig = plt.figure(figsize=[12,6])
plt.subplot(1, 2, 1)

zacc,zldares = ldaTest(means,covmat,xx,np.zeros((xx.shape[0],1)))
plt.contourf(x1,x2,zldares.reshape((x1.shape[0],x2.shape[0])),alpha=0.3)
plt.scatter(Xtest[:,0],Xtest[:,1],c=ytest)
plt.title('LDA')

plt.subplot(1, 2, 2)

zacc,zqdares = qdaTest(means,covmats,xx,np.zeros((xx.shape[0],1)))
plt.contourf(x1,x2,zqdares.reshape((x1.shape[0],x2.shape[0])),alpha=0.3)
plt.scatter(Xtest[:,0],Xtest[:,1],c=ytest)
plt.title('QDA')

plt.show()
# Linear Regression
if sys.version_info.major == 2:
    X,y,Xtest,ytest = pickle.load(open('F:\Mugdha\Projects\ML\Assignment2\diabetes.pickle','rb'))
else:
    X,y,Xtest,ytest = pickle.load(open('F:\Mugdha\Projects\ML\Assignment2\diabetes.pickle','rb'),encoding = 'latin1')

# add intercept
X_i = np.concatenate((np.ones((X.shape[0],1)), X), axis=1)
Xtest_i = np.concatenate((np.ones((Xtest.shape[0],1)), Xtest), axis=1)

w = learnOLERegression(X,y)
mle = testOLERegression(w,Xtest,ytest)

w_i = learnOLERegression(X_i,y)
mle_i = testOLERegression(w_i,Xtest_i,ytest)

print('P2: MSE without intercept for test data '+str(mle))
print('P2: MSE with intercept for test data '+str(mle_i))

w_train = learnOLERegression(X,y)
mle_train = testOLERegression(w_train,X,y)

w_itrain = learnOLERegression(X_i,y)
mle_itrain = testOLERegression(w_itrain,X_i,y)

print('P2: MSE without intercept for train data '+str(mle_train))
print('P2: MSE with intercept for train data '+str(mle_itrain))

# Ridge Regression
k = 101
lambdas = np.linspace(0, 1, num=k)
i = 0
mses3_train = np.zeros((k,1))
mses3 = np.zeros((k,1))
for lambd in lambdas:
    w_l = learnRidgeRegression(X_i,y,lambd)
    mses3_train[i] = testOLERegression(w_l,X_i,y)
    mses3[i] = testOLERegression(w_l,Xtest_i,ytest)
    i = i + 1
fig = plt.figure(figsize=[12,6])
plt.subplot(1, 2, 1)
plt.plot(lambdas,mses3_train)
plt.title('P3: MSE for Train Data')
plt.subplot(1, 2, 2)
plt.plot(lambdas,mses3)
plt.title('P3: MSE for Test Data')

plt.show()
# Gradient descent for Ridge Regression
k = 101
lambdas = np.linspace(0, 1, num=k)
i = 0
mses4_train = np.zeros((k,1))
mses4 = np.zeros((k,1))
opts = {'maxiter' : 20}    # Preferred value.
w_init = np.ones((X_i.shape[1],1))
for lambd in lambdas:
    args = (X_i, y, lambd)
    w_l = minimize(regressionObjVal, w_init, jac=True, args=args,method='CG', options=opts)
    w_l = np.transpose(np.array(w_l.x))
    w_l = np.reshape(w_l,[len(w_l),1])
    mses4_train[i] = testOLERegression(w_l,X_i,y)
    mses4[i] = testOLERegression(w_l,Xtest_i,ytest)
    i = i + 1


fig = plt.figure(figsize=[12,6])
plt.subplot(1, 2, 1)
plt.plot(lambdas,mses4_train)
plt.plot(lambdas,mses3_train)
plt.title('P4: MSE for Train Data')
plt.legend(['P4: Using scipy.minimize','Direct minimization'])

plt.subplot(1, 2, 2)
plt.plot(lambdas,mses4)
plt.plot(lambdas,mses3)
plt.title('P4: MSE for Test Data')
plt.legend(['P4: Using scipy.minimize','Direct minimization'])
plt.show()


# Non-Linear Regression
pmax = 7
lambda_opt = lambdas[np.argmin(mses3)] 
print("Optimal value of lambda is " + str(lambda_opt))
mses5_train = np.zeros((pmax,2))
mses5 = np.zeros((pmax,2))
for p in range(pmax):
    Xd = mapNonLinear(X[:,2],p)
    Xdtest = mapNonLinear(Xtest[:,2],p)
    w_d1 = learnRidgeRegression(Xd,y,0)
    mses5_train[p,0] = testOLERegression(w_d1,Xd,y)
    mses5[p,0] = testOLERegression(w_d1,Xdtest,ytest)
    w_d2 = learnRidgeRegression(Xd,y,lambda_opt)
    mses5_train[p,1] = testOLERegression(w_d2,Xd,y)
    mses5[p,1] = testOLERegression(w_d2,Xdtest,ytest)

fig = plt.figure(figsize=[12,6])
plt.subplot(1, 2, 1)
plt.plot(range(pmax),mses5_train)
plt.title('P5: MSE for Train Data')
plt.legend(('P5: No Regularization','Regularization'))
plt.subplot(1, 2, 2)
plt.plot(range(pmax),mses5)
plt.title('P5: MSE for Test Data')
plt.legend(('P5: No Regularization','Regularization'))
plt.show()import numpy as np
from scipy.optimize import minimize
from scipy.io import loadmat
from numpy.linalg import det, inv
from math import sqrt, pi
import scipy.io
import matplotlib.pyplot as plt
import pickle
import sys

def ldaLearn(X,y):
    # Inputs
    # X - a N x d matrix with each row corresponding to a training example
    # y - a N x 1 column vector indicating the labels for each training example
    #
    # Outputs
    # means - A d x k matrix containing learnt means for each of the k classes
    # covmat - A single d x d learnt covariance matrix
	
    k=int(np.max(y))
    d=int(X.shape[1])
    means=np.zeros((k,d))
    y=y.flatten()
    for i in range(0,k):
        means[i,:]=np.mean(X[y==i+1],axis=0)
    means=means.T
    covmat=np.cov(X.T)

    return means,covmat

def qdaLearn(X,y):
    # Inputs
    # X - a N x d matrix with each row corresponding to a training example
    # y - a N x 1 column vector indicating the labels for each training example
    #
    # Outputs
    # means - A d x k matrix containing learnt means for each of the k classes
    # covmats - A list of k d x d learnt covariance matrices for each of the k classes
	
    k=int(np.max(y))
    d=int(X.shape[1])
    means=np.zeros((k,d))
    covmats=[np.zeros((d,d))]*k
    y=y.flatten()
    for i in range(0,k):
        means[i,:]=np.mean(X[y==i+1],axis=0)
        covmats[i]=np.cov(X[y==i+1].T)
    means=means.T    

    return means,covmats

def ldaTest(means,covmat,Xtest,ytest):

    # Inputs
    # means, covmat - parameters of the LDA model
    # Xtest - a N x d matrix with each row corresponding to a test example
    # ytest - a N x 1 column vector indicating the labels for each test example
    # Outputs
    # acc - A scalar accuracy value
    # ypred - N x 1 column vector indicating the predicted labels
	
    N = int(Xtest.shape[0])
    ypred=np.zeros((N,1))
    k = int(means.shape[1])
    Correct = 0.0
    covmatinv = inv(covmat)
    ytest = ytest.astype(int)
    for i in range (0,N):
        predict=np.zeros((1,k))
        for j in range (0,k):
            predict[0,j] = np.exp((-1.0/2)*np.dot(np.dot(np.transpose(Xtest[i,:].T - means[:, j]),covmatinv),(Xtest[i,:].T - means[:, j])))
        m=np.max(predict)
        predict=list(predict.ravel())
        ypred[i]=predict.index(m)+1
        if (ypred[i] == ytest[i]):
            Correct = Correct + 1
    acc = Correct/N*100
    ypred=ypred.flatten()
    ypred = ypred.astype(int)
    return acc,ypred

def qdaTest(means,covmats,Xtest,ytest):

    # Inputs
    # means, covmats - parameters of the QDA model
    # Xtest - a N x d matrix with each row corresponding to a test example
    # ytest - a N x 1 column vector indicating the labels for each test example
    # Outputs
    # acc - A scalar accuracy value
    # ypred - N x 1 column vector indicating the predicted labels
	
    N = int(Xtest.shape[0])
    ypred=np.zeros((N,1))
    k = int(means.shape[1])
    d= np.zeros(k)
    Correct = 0.0
    for i in range (0,k):
        d[i] = 1.0/(np.power(2 * pi, np.size(Xtest, 1) / 2.0) * np.power(det(covmats[i]),1/2.0));
        covmats[i] = inv(covmats[i])
    ytest = ytest.astype(int)
    for i in range (0,N):
        predict=np.zeros((1,k))
        for j in range (0,k):
            predict[0,j] = (np.exp(-(1.0/2)*np.dot(np.dot(np.transpose(Xtest[i,:].T - means[:, j]),covmats[j]),(Xtest[i,:].T - means[:, j])))) * d[j]
        m=np.max(predict)
        predict=list(predict.ravel())
        ypred[i]=predict.index(m)+1
        if (ypred[i] == ytest[i]):
            Correct = Correct + 1
    acc = Correct/N*100
    ypred=ypred.flatten()
    ypred = ypred.astype(int)

    return acc,ypred

def learnOLERegression(X,y):
    # Inputs:
    # X = N x d
    # y = N x 1
    # Output:
    # w = d x 1
    #N,d = X.shape
    w = np.dot(np.dot(np.linalg.inv(np.dot(np.transpose(X),X)),np.transpose(X)),y)
    return w

def learnRidgeRegression(X,y,lambd):
    # Inputs:
    # X = N x d
    # y = N x 1
    # lambd = ridge parameter (scalar)
    # Output:
    # w = d x 1
    d=X.shape[1]
    w=np.dot(np.dot(np.linalg.inv((lambd*np.identity(d))+np.dot(X.T, X)), np.transpose(X)),y)
    return w

def testOLERegression(w,Xtest,ytest):
    # Inputs:
    # w = d x 1
    # Xtest = N x d
    # ytest = X x 1
    # Output:
    # mse
    N,d = Xtest.shape
    mse = np.divide(np.sum(np.power(np.subtract(ytest, np.dot(Xtest,w)),2)),N)
    return mse

def regressionObjVal(w, X, y, lambd):

    # compute squared error (scalar) and gradient of squared error with respect
    # to w (vector) for the given data X and y and the regularization parameter
    # lambda
	
    y = y.flatten()
    error_grad = np.dot(np.transpose(X),np.subtract(np.dot(X,w),y))+lambd*w
    error_grad = error_grad.flatten()
    error= np.sum(np.power(y-np.dot(w,X.T),2))/2+lambd*(np.dot(w.T,w))/2
    error_grad=error_grad.flatten()

    return error, error_grad

def mapNonLinear(x,p):
    # Inputs:
    # x - a single column vector (N x 1)
    # p - integer (>= 0)
    # Outputs:
    # Xd - (N x (d+1))
    Xd=np.zeros((x.shape[0],p+1))
    for j in range (p+1):
        Xd[:,j]= np.power(x,j)
    return Xd


# load the sample data
if sys.version_info.major == 2:
    X,y,Xtest,ytest = pickle.load(open('F:\Mugdha\Projects\ML\Assignment2\sample.pickle','rb'))
else:
    X,y,Xtest,ytest = pickle.load(open('F:\Mugdha\Projects\ML\Assignment2\sample.pickle','rb'),encoding = 'latin1')

# LDA
means,covmat = ldaLearn(X,y)
ldaacc,ldares = ldaTest(means,covmat,Xtest,ytest)
print('LDA Accuracy = '+str(ldaacc))
# QDA
means,covmats = qdaLearn(X,y)
qdaacc,qdares = qdaTest(means,covmats,Xtest,ytest)
print('QDA Accuracy = '+str(qdaacc))

# plotting boundaries
x1 = np.linspace(-5,20,100)
x2 = np.linspace(-5,20,100)
xx1,xx2 = np.meshgrid(x1,x2)
xx = np.zeros((x1.shape[0]*x2.shape[0],2))
xx[:,0] = xx1.ravel()
xx[:,1] = xx2.ravel()

fig = plt.figure(figsize=[12,6])
plt.subplot(1, 2, 1)

zacc,zldares = ldaTest(means,covmat,xx,np.zeros((xx.shape[0],1)))
plt.contourf(x1,x2,zldares.reshape((x1.shape[0],x2.shape[0])),alpha=0.3)
plt.scatter(Xtest[:,0],Xtest[:,1],c=ytest)
plt.title('LDA')

plt.subplot(1, 2, 2)

zacc,zqdares = qdaTest(means,covmats,xx,np.zeros((xx.shape[0],1)))
plt.contourf(x1,x2,zqdares.reshape((x1.shape[0],x2.shape[0])),alpha=0.3)
plt.scatter(Xtest[:,0],Xtest[:,1],c=ytest)
plt.title('QDA')

plt.show()
# Linear Regression
if sys.version_info.major == 2:
    X,y,Xtest,ytest = pickle.load(open('F:\Mugdha\Projects\ML\Assignment2\diabetes.pickle','rb'))
else:
    X,y,Xtest,ytest = pickle.load(open('F:\Mugdha\Projects\ML\Assignment2\diabetes.pickle','rb'),encoding = 'latin1')

# add intercept
X_i = np.concatenate((np.ones((X.shape[0],1)), X), axis=1)
Xtest_i = np.concatenate((np.ones((Xtest.shape[0],1)), Xtest), axis=1)

w = learnOLERegression(X,y)
mle = testOLERegression(w,Xtest,ytest)

w_i = learnOLERegression(X_i,y)
mle_i = testOLERegression(w_i,Xtest_i,ytest)

print('P2: MSE without intercept for test data '+str(mle))
print('P2: MSE with intercept for test data '+str(mle_i))

w_train = learnOLERegression(X,y)
mle_train = testOLERegression(w_train,X,y)

w_itrain = learnOLERegression(X_i,y)
mle_itrain = testOLERegression(w_itrain,X_i,y)

print('P2: MSE without intercept for train data '+str(mle_train))
print('P2: MSE with intercept for train data '+str(mle_itrain))

# Ridge Regression
k = 101
lambdas = np.linspace(0, 1, num=k)
i = 0
mses3_train = np.zeros((k,1))
mses3 = np.zeros((k,1))
for lambd in lambdas:
    w_l = learnRidgeRegression(X_i,y,lambd)
    mses3_train[i] = testOLERegression(w_l,X_i,y)
    mses3[i] = testOLERegression(w_l,Xtest_i,ytest)
    i = i + 1
fig = plt.figure(figsize=[12,6])
plt.subplot(1, 2, 1)
plt.plot(lambdas,mses3_train)
plt.title('P3: MSE for Train Data')
plt.subplot(1, 2, 2)
plt.plot(lambdas,mses3)
plt.title('P3: MSE for Test Data')

plt.show()
# Gradient descent for Ridge Regression
k = 101
lambdas = np.linspace(0, 1, num=k)
i = 0
mses4_train = np.zeros((k,1))
mses4 = np.zeros((k,1))
opts = {'maxiter' : 20}    # Preferred value.
w_init = np.ones((X_i.shape[1],1))
for lambd in lambdas:
    args = (X_i, y, lambd)
    w_l = minimize(regressionObjVal, w_init, jac=True, args=args,method='CG', options=opts)
    w_l = np.transpose(np.array(w_l.x))
    w_l = np.reshape(w_l,[len(w_l),1])
    mses4_train[i] = testOLERegression(w_l,X_i,y)
    mses4[i] = testOLERegression(w_l,Xtest_i,ytest)
    i = i + 1


fig = plt.figure(figsize=[12,6])
plt.subplot(1, 2, 1)
plt.plot(lambdas,mses4_train)
plt.plot(lambdas,mses3_train)
plt.title('P4: MSE for Train Data')
plt.legend(['P4: Using scipy.minimize','Direct minimization'])

plt.subplot(1, 2, 2)
plt.plot(lambdas,mses4)
plt.plot(lambdas,mses3)
plt.title('P4: MSE for Test Data')
plt.legend(['P4: Using scipy.minimize','Direct minimization'])
plt.show()


# Problem 5
pmax = 7
lambda_opt = lambdas[np.argmin(mses3)] 
print("Optimal value of lambda is " + str(lambda_opt))
mses5_train = np.zeros((pmax,2))
mses5 = np.zeros((pmax,2))
for p in range(pmax):
    Xd = mapNonLinear(X[:,2],p)
    Xdtest = mapNonLinear(Xtest[:,2],p)
    w_d1 = learnRidgeRegression(Xd,y,0)
    mses5_train[p,0] = testOLERegression(w_d1,Xd,y)
    mses5[p,0] = testOLERegression(w_d1,Xdtest,ytest)
    w_d2 = learnRidgeRegression(Xd,y,lambda_opt)
    mses5_train[p,1] = testOLERegression(w_d2,Xd,y)
    mses5[p,1] = testOLERegression(w_d2,Xdtest,ytest)

fig = plt.figure(figsize=[12,6])
plt.subplot(1, 2, 1)
plt.plot(range(pmax),mses5_train)
plt.title('P5: MSE for Train Data')
plt.legend(('P5: No Regularization','Regularization'))
plt.subplot(1, 2, 2)
plt.plot(range(pmax),mses5)
plt.title('P5: MSE for Test Data')
plt.legend(('P5: No Regularization','Regularization'))
plt.show()