# Daily Learning — VPS Setup Runbook

Reproduces the full VPS setup from scratch if the Droplet is ever destroyed or needs rebuilding.

**Live system:** `157.230.224.143` — DigitalOcean NYC1, Ubuntu 24.04, $6/month (1 GB RAM)

---

## Prerequisites

- DigitalOcean account
- Local ed25519 SSH key at `~/.ssh/id_ed25519` (generate with `ssh-keygen -t ed25519 -C "lfornefett@gmail.com" -f ~/.ssh/id_ed25519` if missing)
- Google Cloud project with a service account that has access to the Bank tab spreadsheet
- SendGrid account with a verified sender (lfornefett@gmail.com) and an API key

---

## Phase 4: Provision Droplet + Harden + Docker

### 1. Create Droplet

In DigitalOcean web UI:
- Image: Ubuntu 24.04 LTS x64
- Plan: Basic, Regular, $6/month (1 GB RAM / 1 vCPU / 25 GB SSD)
- Region: NYC1 (or closest)
- Authentication: SSH Key — paste contents of `~/.ssh/id_ed25519.pub`
- Hostname: `daily-learning-n8n`
- Everything else: off

Note the public IPv4 address (referred to as `VPS_IP` below).

### 2. Verify SSH access

```bash
ssh -i ~/.ssh/id_ed25519 root@VPS_IP
whoami          # root
lsb_release -d  # Ubuntu 24.04
exit
```

### 3. Create non-root sudo user

```bash
ssh -i ~/.ssh/id_ed25519 root@VPS_IP
adduser lennart          # set a strong password
usermod -aG sudo lennart
rsync --archive --chown=lennart:lennart ~/.ssh /home/lennart
```

In a separate terminal, verify key login as lennart:
```bash
ssh -i ~/.ssh/id_ed25519 lennart@VPS_IP
whoami   # lennart
sudo whoami  # root (enter lennart's password)
```

### 4. Disable SSH password authentication

In the lennart session:
```bash
sudo sed -i.bak 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo grep -E '^PasswordAuthentication' /etc/ssh/sshd_config  # must print: PasswordAuthentication no
sudo systemctl reload ssh
```

Verify from a third terminal: `ssh -i ~/.ssh/id_ed25519 lennart@VPS_IP 'echo ok'`

### 5. Configure ufw firewall

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 5678/tcp
sudo ufw status numbered   # confirm 22 and 5678 listed before enabling
sudo ufw enable
sudo ufw status verbose    # Status: active, only 22 and 5678 ALLOW IN
```

### 6. Add DOCKER-USER chain (prevents Docker bypassing ufw)

```bash
sudo cp /etc/ufw/after.rules /etc/ufw/after.rules.bak
sudo sh -c 'echo "" >> /etc/ufw/after.rules'
sudo sh -c 'echo "*filter" >> /etc/ufw/after.rules'
sudo sh -c 'echo ":DOCKER-USER - [0:0]" >> /etc/ufw/after.rules'
sudo sh -c 'echo "-A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j RETURN" >> /etc/ufw/after.rules'
sudo sh -c 'echo "-A DOCKER-USER -m conntrack --ctstate INVALID -j DROP" >> /etc/ufw/after.rules'
sudo sh -c 'echo "-A DOCKER-USER -i docker0 -o docker0 -j ACCEPT" >> /etc/ufw/after.rules'
sudo sh -c 'echo "-A DOCKER-USER -j RETURN" >> /etc/ufw/after.rules'
sudo sh -c 'echo "COMMIT" >> /etc/ufw/after.rules'
sudo ufw reload
```

### 7. Enable swap

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo sh -c 'echo "/swapfile none swap sw 0 0" >> /etc/fstab'
sudo sysctl vm.swappiness=10
sudo sh -c 'echo "vm.swappiness=10" >> /etc/sysctl.conf'
```

### 8. Install Docker

```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo sh -c 'echo "Types: deb" > /etc/apt/sources.list.d/docker.sources'
sudo sh -c 'echo "URIs: https://download.docker.com/linux/ubuntu" >> /etc/apt/sources.list.d/docker.sources'
sudo sh -c 'echo "Suites: noble" >> /etc/apt/sources.list.d/docker.sources'
sudo sh -c 'echo "Components: stable" >> /etc/apt/sources.list.d/docker.sources'
sudo sh -c 'echo "Architectures: amd64" >> /etc/apt/sources.list.d/docker.sources'
sudo sh -c 'echo "Signed-By: /etc/apt/keyrings/docker.asc" >> /etc/apt/sources.list.d/docker.sources'
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
sudo usermod -aG docker lennart
```

Log out and back in, then verify:
```bash
docker run --rm hello-world   # prints "Hello from Docker!"
docker compose version
```

---

## Phase 5: Deploy n8n Container

### 1. Copy compose file and start n8n

From local machine:
```bash
ssh -i ~/.ssh/id_ed25519 lennart@VPS_IP 'mkdir -p ~/n8n'
scp -i ~/.ssh/id_ed25519 deploy/docker-compose.yml lennart@VPS_IP:~/n8n/docker-compose.yml
ssh -i ~/.ssh/id_ed25519 lennart@VPS_IP
cd ~/n8n && docker compose up -d
docker compose logs --tail=20   # look for "Editor is now accessible via:"
```

### 2. Verify browser access

Open `http://VPS_IP:5678` in a browser. Complete the owner account setup (email + password — save these).

**Note:** If you see "secure cookie" error, add `N8N_SECURE_COOKIE=false` to the environment in `docker-compose.yml` and run `docker compose up -d` again.

### 3. Test persistence and auto-restart

```bash
docker compose restart   # data should survive
sudo reboot              # after ~60s, docker ps should show n8n Up automatically
```

---

## Phase 6: Wire Credentials + Workflow

### 1. Create credentials in hosted n8n

In n8n (http://VPS_IP:5678) → Settings → Credentials:

**Google Sheets Service Account:**
- Type: Google Service Account API
- Service Account Email: from `.secrets/service-account.json` (`client_email` field)
- Private Key: from `.secrets/service-account.json` (`private_key` field)
- Name: `Google Sheets Service Account`

**SendGrid:**
- Type: SendGrid
- API Key: from SendGrid → Settings → API Keys (Full Access key)
- Name: `SendGrid`
- Before first send: verify sender at SendGrid → Settings → Sender Authentication → Single Sender Verification

### 2. Import workflow

Workflows → + → Import from file → select `n8n-workflow.json` from repo root.

Map credentials on each node:
- Read Bank → `Google Sheets Service Account`
- Send Email → `SendGrid`
- Mark Sent → `Google Sheets Service Account`

In the Send Email node, set Subject to `{{ $json.subject }}` and Message/Body to `{{ $json.body }}` (expression mode, no leading `=`).

### 3. Test and publish

Click **Test workflow** — all 6 nodes should turn green, email arrives at lfornefett@gmail.com, 3 rows in Bank tab show `status=sent`.

Click **Publish** to arm the 06:30 schedule.

---

## Verification Checklist

- [ ] `ssh -i ~/.ssh/id_ed25519 lennart@VPS_IP 'echo ok'` works
- [ ] `sudo ufw status verbose` shows only 22 and 5678 ALLOW IN
- [ ] `docker ps` shows n8n container Up
- [ ] `http://VPS_IP:5678` loads n8n login screen
- [ ] After `sudo reboot`, n8n comes back automatically
- [ ] Manual workflow test sends email + updates sheet
- [ ] Workflow is Published (schedule armed)
