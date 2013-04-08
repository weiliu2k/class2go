%COMPUTEPI estimate the value of pi using the algorithm as given in the code.
%
%Input parameter:
% thres - the threshold value used for terminating the iteration.
%
%Output parameter:
% mypi - the estimated value of pi.
%
%Du Huynh, June 2012.

function mypi = computePi(thres)

a = 1;
b = 1/sqrt(2);
t = 1/4;
x = 1;

% note that a is always larger than b in the computation
while a-b > thres
    y = a;
    a = (a+b)/2;
    b = sqrt(b*y);
    t = t - x*(y-a)^2;
    x = 2*x;
end
mypi = (a + b)^2 / (4*t);
end