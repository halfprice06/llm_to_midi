import os
import subprocess
import shutil
import glob
import music21

def convert_midi_to_musicxml(midi_path: str) -> str:
    """
    Convert a MIDI file to MusicXML using music21.
    
    Args:
        midi_path (str): Path to the MIDI file.
    
    Returns:
        str: Path to the generated MusicXML file.
    
    Raises:
        Exception: If the conversion fails.
    """
    score = music21.converter.parse(midi_path)
    xml_path = os.path.splitext(midi_path)[0] + '.xml'
    score.write('musicxml', fp=xml_path)
    return xml_path

def convert_musicxml_to_image(xml_path: str, output_format: str = 'png') -> list[str]:
    """
    Convert a MusicXML file to images using LilyPond.
    
    Args:
        xml_path (str): Path to the MusicXML file.
        output_format (str, optional): Format of the output images (e.g., 'png', 'pdf'). Defaults to 'png'.
    
    Returns:
        list[str]: List of paths to the generated image files.
    
    Raises:
        RuntimeError: If LilyPond is not installed or not found in the system PATH.
        subprocess.CalledProcessError: If LilyPond fails to execute.
    """
    if not shutil.which('lilypond'):
        raise RuntimeError("LilyPond is not installed or not in the system PATH.")
    
    base_dir = os.path.dirname(xml_path)
    images_dir = os.path.join(base_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    base_name = os.path.splitext(os.path.basename(xml_path))[0]
    output_base = os.path.join(images_dir, base_name)
    
    cmd = ['lilypond', f'--{output_format}', '-o', output_base, xml_path]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"LilyPond error: {e.stderr}")
        raise
    
    # Collect generated image files (LilyPond generates files like 'base_name-1.png', 'base_name-2.png', etc.)
    image_files = glob.glob(f"{output_base}-*.{output_format}")
    return image_files