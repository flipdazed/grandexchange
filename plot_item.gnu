set term qt enhanced font "verdana,8"
set title "Data scraped from runescape.com"
set xdata time
set timefmt "%s"
set format x "%d-%b-%y"
set xlabel "Time"
set ylabel "Price"
unset key
plot 'item_id28642.dat' using 1:2 w l smooth unique