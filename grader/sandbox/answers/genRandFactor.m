function factor = genRandFactor()

while true
  factor = randn(1)+1;
  if(factor>0 && factor<=1)
     break;
  end
end

endfunction