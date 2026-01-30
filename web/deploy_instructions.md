# How to Deploy to Cloudflare Pages ☁️

Your landing page is ready! Follow these steps to host `ledgermcp.kpruthvi.com` for free.

## 1. Cloudflare Setup
1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com).
2. Go to **Compute (Workers & Pages)** -> **Pages**.
3. Click **Connect to Git**.

## 2. Connect Repository
1. Select your GitHub repository: `pruthvi2805/Ledger-MCP`.
2. Click **Begin setup**.

## 3. Build Configuration
Since this is a simple static site, the configuration is very easy:
- **Project Name**: `ledgermcp` (This will create `ledgermcp.pages.dev`)
- **Production Branch**: `main`
- **Framework Preset**: `None` (Select "None" or leave empty)
- **Build Command**: `(leave empty)`
- **Build Output Directory**: `web` (⚠️ Important: Tell Cloudflare to serve the `web` folder)

## 4. Deploy
1. Click **Save and Deploy**.
2. Wait ~30 seconds.
3. Your site will be live at `https://ledgermcp.pages.dev`.

## 5. Custom Domain (ledgermcp.kpruthvi.com)
1. Go to your Pages project settings -> **Custom Domains**.
2. Click **Set up a custom domain**.
3. Enter `ledgermcp.kpruthvi.com`.
4. Cloudflare will automatically update your DNS records if you manage `kpruthvi.com` on Cloudflare.

---

## 📹 Adding a Real Video
Currently, the site has a placeholder for the demo video.
To add a real video:
1. Record a quick demo using **Screen Studio** or **Loom**.
2. Upload it to YouTube (Unlisted) or generate an MP4 file.
3. Edit `web/index.html`:
   - **For YouTube:** Replace the placeholder `<div>` with an `<iframe>` embed code.
   - **For MP4:** Use a `<video>` tag.
