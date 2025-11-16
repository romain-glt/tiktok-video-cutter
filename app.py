import streamlit as st
import subprocess
import os


# ---------------------- UI -----------------------
st.set_page_config(page_title="TikTok Extractor", page_icon="🎬", layout="centered")

st.title("🎬 TikTok Clip Extractor")
st.write("Transforme n'importe quelle vidéo YouTube en format vertical optimisé pour TikTok.")

url = st.text_input("🔗 Lien YouTube :")

col1, col2 = st.columns(2)
with col1:
    start_time = st.text_input("⏳ Début (HH:MM:SS)", "00:00:00")
with col2:
    end_time = st.text_input("⏳ Fin (HH:MM:SS)", "00:00:10")

quality = st.selectbox(
    "📌 Choix de qualité de sortie",
    ["720p", "1080p (recommandé)", "4K"],
    index=1
)

generate_thumbnail = st.checkbox("📸 Générer une miniature automatique")

progress = st.progress(0)
log = st.empty()

def update(step, text):
    progress.progress(step)
    log.write(text)

# ---------------------- ACTION -----------------------
if st.button("Créer la vidéo"):
    if not url:
        st.error("Merci de coller un lien YouTube.")
        st.stop()

    # Nettoyage
    for f in ["video.mp4", "clip.mp4", "clip_9_16.mp4", "thumb.jpg"]:
        if os.path.exists(f):
            os.remove(f)

    # Résolution
    if quality == "720p":
        scale = (720, 1280)
    elif quality.startswith("1080"):
        scale = (1080, 1920)
    else:
        scale = (2160, 3840)

    # 1️⃣ Téléchargement
    update(10, "⏬ Téléchargement YouTube en cours...")
    subprocess.run([
        "python", "-m", "yt_dlp",
        "-f", "bestvideo+bestaudio/best",
        "--merge-output-format", "mp4",
        "-o", "video.mp4",
        url
    ], check=True)

    # 2️⃣ Découpe
    update(40, "✂️ Découpage de l'extrait...")
    subprocess.run([
        "ffmpeg",
        "-ss", start_time,
        "-to", end_time,
        "-i", "video.mp4",
        "-c", "copy",
        "clip.mp4",
        "-y"
    ], check=True)

    # 3️⃣ Format vertical TikTok
    update(70, "📱 Conversion au format TikTok (9:16)...")
    w, h = scale
    subprocess.run([
        "ffmpeg",
        "-i", "clip.mp4",
        "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2",
        "clip_9_16.mp4",
        "-y"
    ], check=True)

    # 4️⃣ Miniature (option)
    if generate_thumbnail:
        update(85, "📸 Génération de la miniature...")
        subprocess.run([
            "ffmpeg",
            "-i", "clip_9_16.mp4",
            "-ss", "00:00:01",
            "-vframes", "1",
            "thumb.jpg",
            "-y"
        ], check=True)

    update(100, "🎉 Vidéo créée avec succès !")

    st.video("clip_9_16.mp4")

    with open("clip_9_16.mp4", "rb") as f:
        st.download_button("⬇️ Télécharger la vidéo", f, file_name="tiktok_video.mp4")
    
    if generate_thumbnail and os.path.exists("thumb.jpg"):
        st.image("thumb.jpg", caption="Miniature générée")
        with open("thumb.jpg", "rb") as f:
            st.download_button("⬇️ Télécharger la miniature", f, file_name="thumbnail.jpg", mime="image/jpeg")
