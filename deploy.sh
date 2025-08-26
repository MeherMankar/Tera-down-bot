#!/bin/bash
# VPS deployment script

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip aria2 -y

# Clone your bot
git clone https://github.com/yourusername/Tera-down-bot
cd Tera-down-bot

# Install Python requirements
pip3 install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/terabot.service > /dev/null <<EOF
[Unit]
Description=Terabox Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Tera-down-bot
ExecStart=/usr/bin/python3 run_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable terabot
sudo systemctl start terabot