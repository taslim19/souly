
## 🛠️ DEPLOYMENT ON LOCAL HOST / VPS

Initiate deployment with these sophisticated steps:

```bash
sudo apt-get update && sudo apt-get upgrade -y           # 1. Upgrade and Update System

sudo apt-get install python3-pip -y          # 2. Install Required Packages

sudo pip3 install -U pip          # 3. Upgrade Pip

git clone https://github.com/Infamous-Hydra/YaeMiko && cd YaeMiko           # 4. Clone the Repository

pip3 install -U -r requirements.txt          # 5. Install Required Packages

vi variables.py           # 6. Modify Variables
# Press `I` to begin editing. Press `Ctrl+C` to save, then `:wq` or `:qa` to exit.

sudo apt install tmux && tmux           # 7. Install Tmux (Optional)

python3 -m Mikobot         # 8. Run the Bot
# Press `Ctrl+b` and then `d` to exit Tmux Session
```
━━━━━━━━━━━━━━━━━━━━

