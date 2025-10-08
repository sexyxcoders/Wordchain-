<p align="center">
  <b>ᴛɴᴄ-ᴡᴏʀᴅᴄʜᴀɪɴ ᴜꜱᴇʀʙᴏᴛ</b><br>
  ᴛᴜʀɴ-ʙᴀꜱᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴡᴏʀᴅᴄʜᴀɪɴ ᴜꜱᴇʀʙᴏᴛ ᴄᴏɴᴛʀᴏʟʟᴇʀ
</p>

<p align="center">
  <a href="https://heroku.com/deploy?template=https://github.com/USERNAME/REPO">
    <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy">
  </a>
</p>

---

## 🧩 ᴀʙᴏᴜᴛ

ᴛʜɪꜱ ʀᴇᴘᴏ ᴄᴏɴᴛᴀɪɴꜱ ᴛʜᴇ **ᴛɴᴄ ᴡᴏʀᴅᴄʜᴀɪɴ** ᴜꜱᴇʀʙᴏᴛ ᴄᴏɴᴛʀᴏʟʟᴇʀ ᴀɴᴅ ᴘʟᴀʏᴇʀ.  
ᴛʜᴇ ᴄᴏɴᴛʀᴏʟʟᴇʀ (ᴘʏʀᴏɢʀᴀᴍ) ʜᴀɴᴅʟᴇꜱ ᴜꜱᴇʀꜱ’ ᴛᴇʟᴇᴛʜᴏɴ ꜱᴛʀɪɴɢꜱ ᴀɴᴅ ꜱᴛᴀʀᴛꜱ ᴘᴇʀꜱᴏɴᴀʟ ʙᴏᴛꜱ ᴛᴏ ᴘʟᴀʏ ᴡᴏʀᴅᴄʜᴀɪɴ.

---

## ⚙️ ꜰᴇᴀᴛᴜʀᴇꜱ

- 🔹 ᴘᴇʀꜱᴏɴᴀʟ ᴜꜱᴇʀʙᴏᴛꜱ ꜱᴛᴀʀᴛᴇᴅ ꜰʀᴏᴍ ꜱᴛʀɪɴɢꜱᴇꜱꜱɪᴏɴ  
- 🔹 ᴘʟᴀʏꜱ ᴏɴʟʏ ᴏɴ ᴛʜᴇ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴜꜱᴇʀ’ꜱ ᴛᴜʀɴ  
- 🔹 ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴍᴇꜱꜱᴀɢᴇꜱ (ᴏᴡɴᴇʀ ᴏɴʟʏ)  
- 🔹 ꜱǫʟɪᴛᴇ ᴏʀ ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇ  
- 🔹 ᴀᴜᴛᴏ ᴄʟᴇᴀɴᴜᴘ ᴏɴ ᴅɪꜱᴄᴏɴɴᴇᴄᴛ  
- 🔹 ʟᴀʀɢᴇ **ᴡᴏʀᴅꜱ.ᴛxᴛ** ꜱᴜᴘᴘᴏʀᴛ  

---

## 🚀 ǫᴜɪᴄᴋ ᴅᴇᴘʟᴏʏ (ʜᴇʀᴏᴋᴜ)

1️⃣ ᴄʟɪᴄᴋ ᴛʜᴇ ᴅᴇᴘʟᴏʏ ʙᴜᴛᴛᴏɴ ᴀʙᴏᴠᴇ.  
2️⃣ ꜰɪʟʟ ᴛʜᴇ ᴄᴏɴꜰɪɢ ᴠᴀʀꜱ:

BOT_TOKEN=123456:ABC-DEF... API_ID=1234567 API_HASH=abcd1234... OWNER_ID=8157752411 LOG_GROUP_ID=-1003111446920 WORDS_PATH=words.txt MONGO_URI=your_mongo_uri_here DB_NAME=your_db_name

> 📝 ɪꜰ ɴᴏ ᴍᴏɴɢᴏᴅʙ, ɪᴛ ᴜꜱᴇꜱ ꜱǫʟɪᴛᴇ ʙʏ ᴅᴇꜰᴀᴜʟᴛ.

---

## 💻 ʟᴏᴄᴀʟ ꜱᴇᴛᴜᴘ

```bash
git clone https://github.com/USERNAME/REPO.git
cd REPO
pip install -r requirements.txt
python start.py

ᴄʀᴇᴀᴛᴇ .env:

BOT_TOKEN=xxxx
API_ID=xxxx
API_HASH=xxxx
OWNER_ID=xxxx
LOG_GROUP_ID=xxxx


---

🧠 ʜᴏᴡ ɪᴛ ᴡᴏʀᴋꜱ

/connect STRING_SESSION → ꜱᴀᴠᴇꜱ ꜱᴇꜱꜱɪᴏɴ

ᴜꜱᴇʀʙᴏᴛ ᴊᴏɪɴꜱ ᴡᴏʀᴅᴄʜᴀɪɴ ɢʀᴏᴜᴘ

ᴘʟᴀʏꜱ ᴏɴʟʏ ᴡʜᴇɴ ɪᴛ’ꜱ ᴛʜᴇɪʀ ᴛᴜʀɴ

/disconnect ᴛᴏ ꜱᴛᴏᴘ

/broadcast ᴏᴡɴᴇʀ ᴄᴏᴍᴍᴀɴᴅ



---

🛡️ ꜱᴇᴄᴜʀɪᴛʏ ɴᴏᴛᴇꜱ

ᴋᴇᴇᴘ ꜱᴛʀɪɴɢꜱ ᴘʀɪᴠᴀᴛᴇ.

ᴜꜱᴇ ʜᴇʀᴏᴋᴜ ᴇɴᴠ ᴠᴀʀꜱ ꜰᴏʀ ꜱᴇᴄʀᴇᴛꜱ.

ᴜꜱᴇ ᴘʀᴏᴘᴇʀ ᴅʙ ᴄʀᴇᴅᴇɴᴛɪᴀʟꜱ.



---

📊 ꜱᴛᴀᴛꜱ & ᴄᴏᴍᴍᴀɴᴅꜱ

ᴄᴏᴍᴍᴀɴᴅ	ᴅᴇꜱᴄʀɪᴘᴛɪᴏɴ

/start	ꜱʜᴏᴡꜱ ɪɴᴛʀᴏ ᴍᴇꜱꜱᴀɢᴇ
/connect	ᴄᴏɴɴᴇᴄᴛ ᴜꜱᴇʀʙᴏᴛ
/disconnect	ꜱᴛᴏᴘꜱ ᴜꜱᴇʀʙᴏᴛ
/broadcast	ᴏᴡɴᴇʀ ʙʀᴏᴀᴅᴄᴀꜱᴛ
/listusers	ꜱʜᴏᴡꜱ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴜꜱᴇʀꜱ
/stats	ᴅʙ ᴜꜱᴇʀ ꜱᴛᴀᴛꜱ



---

🧾 ᴄʀᴇᴅɪᴛꜱ

ᴅᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ [ᴛᴇᴄʜɴᴏᴅᴇᴄᴏᴅᴇʀ](https://t.me/TNCmeetup)

---