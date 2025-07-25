from fasthtml.common import *
import yt_dlp
import re
import logging
import traceback
from io import BytesIO
from starlette.responses import StreamingResponse
import os
from moviepy.editor import VideoFileClip

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastHTML app with Tailwind CSS and viewport meta tag
app, rt = fast_app(
    hdrs=(
        Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"),
        Meta(name="viewport", content="width=device-width, initial-scale=1")
    )
)

def download_youtube(url, output_format, quality=None):
    try:
        # Sanitize filename to avoid issues with special characters
        safe_title = lambda title: re.sub(r'[^\w\s-]', '', title.replace(' ', '_'))
        
        # Initialize yt-dlp options with authentication
        ydl_opts = {
            'noplaylist': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'username': 'medobkh6@gmail.com',  # Replace with your Gmail email
            'password': 'aaa1998aaa',  # Replace with your password or app password
            'http_headers': {
                'Referer': 'https://www.youtube.com',
                'Accept-Language': 'en-US,en;q=0.9',
                'Origin': 'https://www.youtube.com',
            },
            'retries': 3,  # Retry up to 3 times for network issues
        }

        if output_format.lower() == "mp4":
            # Adjust format for specified quality
            ydl_opts['format'] = f'bestvideo[height<={quality[:-1]}]+bestaudio/best' if quality else 'bestvideo[height<=720]+bestaudio/best'
            ydl_opts['outtmpl'] = '%(title)s.%(ext)s'  # Output filename template
            buffer = BytesIO()
            ydl_opts['outtmpl'] = '-'  # Stream to buffer
            ydl_opts['quiet'] = True

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                filename = f"{safe_title(info['title'])}.mp4"
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    buffer.seek(0)
                return {"success": True, "buffer": buffer, "filename": filename, "ext": "mp4"}

        elif output_format.lower() == "mp3":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['outtmpl'] = 'temp_audio.%(ext)s'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            buffer = BytesIO()
            ydl_opts['outtmpl'] = '-'  # Stream to buffer
            ydl_opts['quiet'] = True

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                filename = f"{safe_title(info['title'])}.mp3"
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    buffer.seek(0)
                return {"success": True, "buffer": buffer, "filename": filename, "ext": "mp3"}

        else:
            return {"success": False, "message": "Invalid format. Choose 'mp3' or 'mp4'."}

    except Exception as e:
        logger.error(f"Error in download_youtube: {str(e)}")
        logger.error(traceback.format_exc())
        return {"success": False, "message": f"An error occurred: {str(e)}"}

@rt("/")
def get():
    try:
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
                Div(
                    Div(
                        H1("YouTube Video & Audio Downloader", cls="text-4xl md:text-5xl font-bold text-gray-800 mb-4 text-center"),
                        P(
                            "Download YouTube videos in MP4 or MP3 format with ease. Built with FastHTML and deployable on Vercel.",
                            cls="text-lg text-gray-600 mb-6 text-center max-w-2xl mx-auto"
                        ),
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
    except Exception as e:
        logger.error(f"Error in / route: {str(e)}")
        logger.error(traceback.format_exc())
        return Div(P(f"Server Error: {str(e)}", cls="text-red-600 text-center"), cls="container mx-auto py-12")

@rt("/download")
async def post(url: str, output_format: str, quality: str = None):
    try:
        result = download_youtube(url, output_format, quality)
        if result["success"]:
            media_type = "video/mp4" if output_format.lower() == "mp4" else "audio/mpeg"
            headers = {
                "Content-Disposition": f'attachment; filename="{result["filename"]}"'
            }
            return StreamingResponse(
                content=iter([result["buffer"].getvalue()]),
                media_type=media_type,
                headers=headers
            )
        else:
            return Div(P(result["message"], cls="text-red-600"), cls="text-center")
    except Exception as e:
        logger.error(f"Error in /download: {str(e)}")
        logger.error(traceback.format_exc())
        return Div(P(f"Error: {str(e)}", cls="text-red-600"), cls="text-center")

serve()