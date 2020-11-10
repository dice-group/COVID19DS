import annotateStringsFromEndpoint

filepath = './java/coronaAnnotations.txt'
with open(filepath, encoding='utf-8') as fp:
   line = fp.readline()
   cnt = 1
   while line:
       dat=line.split(" ::: ")
       annotateStringsFromEndpoint.annotate_nif_string(dat[1].replace("\n",""),dat[0]);
       line = fp.readline()
       cnt=cnt+1
       print(cnt)  