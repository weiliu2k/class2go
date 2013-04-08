#! /usr/local/bin/octave -qf


factor = genRandFactor();

arg_list = argv ();

submitted = arg_list{1};
solution = arg_list{2};

fname = 'computePi.m';

copyfile(submitted, fname);

% computePi_test.m
% test student code

sub_test1_thres = 0.0;
sub_test1_pi = 0.0;
sub_test2_thres = 0.0;
sub_test2_pi = 0.0;

sol_test1_thres = 0.0;
sol_test1_pi = 0.0;
sol_test2_thres = 0.0;
sol_test2_pi = 0.0;

sub_test1_thres = factor*1;
sub_test1_pi = computePi(sub_test1_thres);

sub_test2_thres = factor*1e-5;
sub_test2_pi = computePi(sub_test2_thres);

unlink(fname);
clear computePi;

% running sample solution code

copyfile(solution, fname);

sol_test1_thres = factor*1;
sol_test1_pi = computePi(sol_test1_thres);

sol_test2_thres = factor*1e-5;
sol_test2_pi = computePi(sol_test2_thres);

unlink(fname);

disp('Start of Feedback');

disp("<table border=\"1\" style=\"width:600px;  font-size:80%%; padding: 1px;border-spacing: 0px; border-collapse: separate\">");
disp("<tr><td >Test</td><td>Your Results</td><td>Solution</td></tr>");
fprintf("<tr ><td>Test 1<//td><td  >Thres: %f pi: %f<//td><td>Thres: %f pi: %f<//td><//tr>", sub_test1_thres, sub_test1_pi, sol_test1_thres, sol_test1_pi);
fprintf("<tr><td>Test 2<//td><td>Thres: %f pi: %f<//td><td>Thres: %f pi: %f<//td><//tr>", sub_test2_thres, sub_test2_pi, sol_test2_thres, sol_test2_pi);
disp("</table>");

disp('End of Feedback');

% marking

total_test = 10;
thres=1e-5;
count = 0;

for i=1:total_test/2
    factor = genRandFactor();
    thres = factor*1;

    clear computePi;
    unlink(fname);
    copyfile(solution, fname);

    samplepi = computePi(thres);

    clear computePi;
    unlink(fname);
    copyfile(submitted, fname);

    mypi = computePi(thres);

    if(abs(mypi- samplepi)<=thres)
      count=count+1;
    end
    unlink(fname);
end

for i=1:total_test/2
    factor = genRandFactor();
    thres = factor*1e-3;

    clear computePi;
    copyfile(submitted, fname);

    mypi = computePi(thres);

    unlink(fname);
    clear computePi;
    copyfile(solution, fname);

    samplepi = computePi(thres);

    if(abs(mypi - samplepi)<=thres)
      count=count+1;
    end
    unlink(fname);
end

fprintf('<score>%1.f</score>', count/total_test);
    


