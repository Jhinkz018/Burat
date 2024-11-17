# UPDATE
![photo_2024-11-14_05-57-39](https://github.com/user-attachments/assets/d6e5bb3e-26c9-43a7-a8ab-b5c9a78b80fb)

# BOT NODEPAY AUTO FARMING
- MULTI ACCOUNT
- FIXED ERROR

# HOW TO RUN
- Step 1:
```Bash
git clone https://github.com/Jhinkz018/Burat.git]
```
- Step 2:
```Bash
cd NodepayBot
```
- Step 3:
```
pip install -r requirements.txt
```
## Setup Tutorial
```
- Open Nodepay and login to dashboard
- Press F12 or CTRL + SHIFT + I
- Select APPLICATION >> LOCALSTORAGE
- np_token = copy the value code
```
<img width="758" alt="Screenshot 1403-08-26 at 1 42 43 PM" src="https://github.com/user-attachments/assets/894c50a3-7087-4b92-a6e1-7f94e48a63ec">
<img width="758" alt="Screenshot 1403-08-26 at 1 42 18 PM" src="https://github.com/user-attachments/assets/adcc46c0-dfea-4620-8d0c-5571d48b1212">


# Edit tokens.txt with your nodepay token
- example format
- token1
- token2
```bash
nano token.txt
```

# Edit local_proxies.txt with your proxies
- example format
```text
http://user:pass@ip:port
```

- To edit run command
```bash
nano local_proxies.txt
```

- Step 4: Create a Screen
```bash
apt install screen 
screen -S nodepay
```


- Step 5: Run Nodepay-bot
```
python3 run_proxy.py
```
- Success logs 
<img width="671" alt="Screenshot 1403-08-26 at 1 52 59 PM" src="https://github.com/user-attachments/assets/0a3f75aa-e6db-4449-baec-660a9858d62e">

