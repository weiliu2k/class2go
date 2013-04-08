#! /usr/bin/octave -qf

% Du Huynh, June 2012
% Wei Liu, August 2012

arg_list = argv ();

submitted = arg_list{1};
solution = arg_list{2};

fname='homeloan.m';

factor = genRandFactor();


price = round(factor*300000);
deposit = round(factor*60000);
interest_rate = 0.01;
loanPeriod = 30*12; % 30 years loan

sub_test_interest = 0.0;
sub_test_payment = 0.0;
sol_test_interest = 0.0;
sol_test_payment = 0.0;

% ---- test student ----
copyfile(submitted, fname);

try
    [sub_test_payment, sub_test_interest] = homeloan(price, deposit, interest_rate, loanPeriod);
catch
    disp(lasterr);
end    

unlink(fname);
clear homeloan;

% ---- Solution ----

copyfile(solution, fname);

try
    [sol_test_payment, sol_test_interest] = homeloan(price, deposit, interest_rate, loanPeriod);
catch
    disp(lasterr);
end

clear homeloan;
unlink(fname);

disp('Start of Feedback');

disp("<table class=\"feedback\">");
disp("<tr><th >Test</th><th>Your Results</th><th>Solution</th></tr>");
fprintf("<tr ><td>Test 1<//td><td>Payment: %7.2f<br/>Interest: %7.2f<//td><td>Payment: %7.2f <br/>Interest: %7.2f<//td><//tr>", \
         sub_test_payment, sub_test_interest, sol_test_payment, sol_test_interest);
disp("</table>");

disp('End of Feedback');

% ---- marking ----

total_test = 10; 
count = 0;
thres = 1e-5;
for ii=1:total_test/2
    factor = genRandFactor();
    price = round(factor*300000);
    deposit = price*0.22;
    interest_rate = 0.01;
    loanPeriod = 20*12; % 20 years loan

    clear homeloan;
    copyfile(submitted, fname);
    [samplePayment, sampleInterest] = homeloan(price, deposit, interest_rate, loanPeriod);

    unlink(fname);
    clear homeloan;
    copyfile(solution, fname);

    try
      [myPayment, myInterest] = homeloan(price, deposit, interest_rate, loanPeriod);

      if(abs(myPayment- samplePayment)<=thres && abs(myInterest- sampleInterest)<=thres )
         count=count+1;
      end
    catch
      if(count>0)
         count=count-1
      end
    end

    unlink(fname);
    clear homeloan;
end

% for ii=1:total_test/2
%    factor = genRandFactor();
%    price = round(factor*300000);
%    deposit = price*0.15;
%    interest_rate = 0.01;
%    loanPeriod = 20*12; % 30 years loan
%    try
%       [myPayment, myInterest] = homeloan(price, deposit, interest_rate, loanPeriod);
%    catch
%       count = count + 1;
%    end
% end

fprintf('<score>%1.f</score>',count*100/total_test);
% fprintf('\n%4.0f %% correct\n',count*100/total_test);
 
% example 1
%price = 300000
%interest_rate = 0.01
%deposit = 60000
% loanPeriod = 30*12   % 30-year loan
% [monthly_payment, total_interest] = ...
%     homeloan(price, deposit, interest_rate, loanPeriod);
% fprintf('monthly payment = %1.2f, total interest paid = %1.2f\n', ...
%     monthly_payment, total_interest);
% 
% disp(' ');
% loanPeriod = 20*12   % 20-year loan
% [monthly_payment, total_interest] = ...
%     homeloan(price, deposit, interest_rate, loanPeriod);
% fprintf('monthly payment = %1.2f, total interest paid = %1.2f\n', ...
%     monthly_payment, total_interest);
% 
% disp('----------------');
% 
% % example 2
% price = 200000
% interest_rate = 0.008
% deposit = 70000
% loanPeriod = 20*12   % 20-year loan
% [monthly_payment, total_interest] = ...
%     homeloan(price, deposit, interest_rate, loanPeriod);
% fprintf('monthly payment = %1.2f, total interest paid = %1.2f\n', ...
%     monthly_payment, total_interest);
% 
% disp('----------------');
% 
% % example 3
% % error checking
% price = 300000
% interest_rate = 0.001
% deposit = 4000
% loanPeriod = 30*12   % 30-year loan
% [monthly_payment, total_interest] = ...
%     homeloan(price, deposit, interest_rate, loanPeriod);
% fprintf('monthly payment = %1.2f, total interest paid = %1.2f\n', ...
%     monthly_payment, total_interest);

% Output:
%
% >> homeloan_test
% price =
%       300000
% interest_rate =
%    0.010000000000000
% deposit =
%        60000
% loanPeriod =
%    360
% monthly payment = 2468.67, total interest paid = 648721.28
%  
% loanPeriod =
%    240
% monthly payment = 2642.61, total interest paid = 394225.61
% ----------------
% price =
%       200000
% interest_rate =
%    0.008000000000000
% deposit =
%        70000
% loanPeriod =
%    240
% monthly payment = 1220.27, total interest paid = 162865.36
% ----------------
% price =
%       300000
% interest_rate =
%      1.000000000000000e-03
% deposit =
%         4000
% loanPeriod =
%    360
% ??? Error using ==> homeloan at 30
% compound_interest: deposit must be at least 20%% of the house price
% 
% Error in ==> homeloan_test at 42
% [monthly_payment, total_interest] = ...
