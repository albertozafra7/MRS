function colMap = getColormap(minPerc,maxPerc)
    colMap = [repmat([0 0 0],[round(minPerc*100) 1])
        repmat([0 1 0],[round((maxPerc-minPerc)*100) 1])
        repmat([1 0 0],[round((1-maxPerc)*100) 1])];
end

