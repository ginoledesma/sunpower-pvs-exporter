SystemD unit service script
---------------------------

sudo cp systemd.defaults /etc/defaults/prometheus-sunpower-pvs-exporter
sudo cp systemd.service /lib/systemd/system/prometheus-sunpower-pvs-exporter
sudo systemctl enable prometheus-sunpower-pvs-exporter.service
sudo systemctl start prometheus-sunpower-pvs-exporter
