from fasthtml.common import *
import yt_dlp
import os
import re

# Initialize FastHTML app with Tailwind CSS and viewport meta tag
app, rt = fast_app(
    hdrs=(
        Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"),
        Meta(name="viewport", content="width=device-width, initial-scale=1")
    )
)

# Ensure downloads directory exists
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube(url, output_format, quality=None):
    try:
        # Sanitize filename to avoid issues with special characters
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'noplaylist': True,
            'merge_output_format': 'mp4' if output_format.lower() == "mp4" else None,
        }

        if output_format.lower() == "mp4":
            if quality:
                ydl_opts['format'] = f'bestvideo[height<={quality[:-1]}]+bestaudio/best'
            else:
                ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                output_path = ydl.prepare_filename(info)
                if not output_path.endswith('.mp4'):
                    output_path = output_path.rsplit('.', 1)[0] + '.mp4'
                return {"success": True, "message": f"Downloaded to: {output_path}", "file_path": output_path}

        elif output_format.lower() == "mp3":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['outtmpl'] = f'{DOWNLOAD_DIR}/%(title)s.%(ext)s'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                audio_path = f"{DOWNLOAD_DIR}/{info['title']}.mp3"
                return {"success": True, "message": f"Converted to MP3 and saved as: {audio_path}", "file_path": audio_path}

        else:
            return {"success": False, "message": "Invalid format. Choose 'mp3' or 'mp4'."}

    except Exception as e:
        return {"success": False, "message": f"An error occurred: {str(e)}"}

@rt("/")
def get():
    return (
        Socials(
            title="YouTube Downloader with FastHTML",
            site_name="FastHTML",
            description="Download YouTube videos as MP4 or MP3 with a modern web interface built using FastHTML and Vercel.",
            image="https://vercel.fyi/fasthtml-og",
            url="https://fasthtml-template.vercel.app",
            twitter_site="@vercel",
        ),
        Div(
            # Navigation Bar
            Nav(
                Div(
                    A("YouTube Downloader", href="/", cls="text-2xl font-bold text-white"),
                    Div(
                        A("Home", href="/", cls="text-white hover:text-gray-300 mx-4"),
                        A("FastHTML Docs", href="https://docs.fastht.ml/", cls="text-white hover:text-gray-300 mx-4"),
                        A("Deploy", href="https://vercel.com/templates/python/fasthtml-python-boilerplate", cls="text-white hover:text-gray-300 mx-4"),
                        cls="flex space-x-4"
                    ),
                    cls="container mx-auto flex justify-between items-center py-4"
                ),
                cls="bg-gray-900 shadow-md"
            ),
            # Hero Section
            Div(
                Div(
                    H1("YouTube Video & Audio Downloader", cls="text-4xl md:text-5xl font-bold text-gray-800 mb-4 text-center"),
                    P(
                        "Download YouTube videos in MP4 or MP3 format with ease. Built with FastHTML and deployable on Vercel.",
                        cls="text-lg text-gray-600 mb-6 text-center max-w-2xl mx-auto"
                    ),
                    # Download Form
                    Form(
                        Input(
                            type="text",
                            name="url",
                            placeholder="Enter YouTube URL",
                            cls="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        ),
                        Select(
                            Option("MP4", value="mp4"),
                            Option("MP3", value="mp3"),
                            name="output_format",
                            cls="w-full p-3 border rounded-lg mt-4"
                        ),
                        Input(
                            type="text",
                            name="quality",
                            placeholder="Resolution (e.g., 720p, 1080p, blank for 720p)",
                            cls="w-full p-3 border rounded-lg mt-4 hidden mp4-only"
                        ),
                        Button(
                            "Download",
                            type="submit",
                            cls="w-full bg-blue-600 text-white p-3 rounded-lg mt-4 hover:bg-blue-700 transition"
                        ),
                        hx_post="/download",
                        hx_target="#result",
                        hx_swap="innerHTML",
                        cls="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md"
                    ),
                    Div(id="result", cls="mt-6 text-center"),
                    cls="container mx-auto py-12 px-4"
                ),
                cls="bg-gray-100"
            ),
            # Footer
            Div(
                P(
                    "Built with ",
                    A("FastHTML", href="https://docs.fastht.ml/", cls="text-blue-600 hover:underline"),
                    " | ",
                    A("Deploy on Vercel", href="https://vercel.com/templates/python/fasthtml-python-boilerplate", cls="text-blue-600 hover:underline"),
                    cls="text-gray-600"
                ),
                cls="bg-gray-900 text-center py-6 text-white"
            ),
            cls="min-h-screen flex flex-col"
        ),
        # JavaScript to toggle resolution input visibility
        Script("""
            document.querySelector('select[name="output_format"]').addEventListener('change', function() {
                const qualityInput = document.querySelector('input[name="quality"]');
                if (this.value === 'mp4') {
                    qualityInput.classList.remove('hidden');
                } else {
                    qualityInput.classList.add('hidden');
                }
            });
        """)
    )

@rt("/download")
async def post(url: str, output_format: str, quality: str = None):
    result = download_youtube(url, output_format, quality)
    if result["success"]:
        # Extract filename from file_path
        filename = os.path.basename(result["file_path"])
        return Div(
            P(result["message"], cls="text-green-600"),
            A(
                "Download File",
                href=f"/{DOWNLOAD_DIR}/{filename}",
                cls="inline-block bg-blue-600 text-white p-2 rounded-lg mt-4 hover:bg-blue-700 transition"
            ),
            cls="text-center"
        )
    else:
        return Div(P(result["message"], cls="text-red-600"), cls="text-center")

@rt(f"/{DOWNLOAD_DIR}/{{filename}}")
def get(filename: str):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return Div(P("File not found.", cls="text-red-600"), cls="text-center")

serve()