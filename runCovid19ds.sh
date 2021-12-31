# !/bin/bash
# run nginx
cd /etc/nginx/sites-enabled 
sudo service nginx restart

# run apache-tomcat for lod
cd /opt/tomcat/apache-tomcat-9.0.11
sudo ./bin/catalina.sh start

# run ES
cd ~/elasticsearch-6.6.0/bin
nohup ./elasticsearch &

# run AGDISTIS
cd /home/user/Documents/work/COVID19DS/entityRecognition/AGDISTIS
nohup mvn exec:java -D"exec.mainClass"="org.aksw.agdistis.webapp.RunApp" -DskipTests &

# run Virtuoso
cd /home/user/Documents/work
sudo docker run --rm --name COVID19DS -e DBA_PASSWORD=XXXX -it -v /home/user/Documents/work/vos19/database:/database -v /home/user/Documents/work/COVID19DS/rdf:/rdfData -t -p 1111:1111 -p 8890:8890 -i openlink/virtuoso-opensource-7