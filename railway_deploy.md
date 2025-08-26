# Railway Deployment Steps

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/Tera-down-bot.git
   git push -u origin main
   ```

2. **Deploy on Railway:**
   - Go to https://railway.app
   - Sign up/Login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-deploy

3. **Add Environment Variables:**
   In Railway dashboard → Variables tab, add:
   - `BOT_TOKEN`: 8246935117:AAHvbAj83CMYWQvniaMxL_tIpzq7ajjuCjg
   - `TELEGRAM_API`: 25401847
   - `TELEGRAM_HASH`: ca8a79df8704ed676fca6891b7bc08ce
   - `FSUB_ID`: -1002231787083
   - `DUMP_CHAT_ID`: -1002231787083
   - `MONGO_URL`: mongodb+srv://hegodal811:rsRu17pspZAcp6V7@cluster0.prsvqax.mongodb.net/?retryWrites=true&w=majority
   - `ADMINS`: 6121637257

4. **Deploy:** Railway will automatically redeploy with new variables.

Your bot will be live 24/7!