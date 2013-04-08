%HOME_LOAN computes the monthly payment and interest for home loan using the compound interest.
%
%[montlyPayment, interest] = homeloan(price, deposit, intRate, lengthOfLoan)
%
%Input parameters:
%  price - price of the house in dollars
%  deposit - amount in dollars to be paid as deposit. The deposit amount
%    must be at least 20% of the house price.
%  intRate - the monthly compound interest rate. This should be a small
%    floating point number less than 1, e.g., a 1% interest rate would have
%    intRate = 0.01.
%  lengthOfLoan - duration of the loan in months.
%
%Output parameters:
%  montlyPayment - the monthly payment
%  interest - the total interest paid to the bank.
%
%Argument checking:
%  - deposit must be at least 20% of the house price.
%  - further checking can be imposed but currently not implemented.
%
%Du Huynh, June 2012

% Some background on compound interest calculation can be found on the
% wikipedia: http://en.wikipedia.org/wiki/Mortgage_calculator
% The implementation below is based on the formula given there.

function [monthlyPayment, interest] = homeloan(price, deposit, intRate, lengthOfLoan)

if deposit < 0.2*price
    error('homeloan: deposit must be at least 20% of the house price');
end

% initial loan
loan = price-deposit;

% total amount owed for the whole loan duration
monthlyPayment = intRate*loan / (1 - (1+intRate)^(-lengthOfLoan));
interest = monthlyPayment*lengthOfLoan - loan;

end


